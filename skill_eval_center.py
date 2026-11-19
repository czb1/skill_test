"""Skill 评测：按范围内的 Skill 聚合外部服务各维度最新结果。

无本地批次、任务或报告写入；外部 task_id 仅在单次请求内取报告。
"""
from abc import ABC, abstractmethod
from collections import OrderedDict
import copy
import json
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
import threading
from typing import Any, Tuple

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol


class SkillCatalog(Protocol):
    def query_scope_offering_ids(self, offering_id=None, pdu=None, department=None):
        ...

    def query_product_by_offering_id(self, offering_id):
        ...

    def query_evaluable_skills(self, offering_ids, keyword=None, page=1, page_size=10):
        ...

    def query_skill_eval_result_skills(self, offering_ids, keyword=None, page=1, page_size=10,
                                      skill_ids=None):
        ...

    def query_skill_eval_name_owners(self, skill_names):
        ...

    def query_skill_infos_by_ids(self, skill_ids):
        ...

    def query_skill_scope_products(self, skill_ids, offering_ids):
        ...

    def update_skill_package_info(self, skill_id, skill_package_url, version):
        ...


class PackageResolver(Protocol):
    def resolve(self, skill_info: dict, offering_ids: list) -> Tuple[str, str]:
        ...


class HarnessGateway(Protocol):
    def fetch_skills(self, first_scene, second_scene, dim_type, dim_name):
        ...

    def fetch_scenes(self, dim_code):
        ...


class EvaluationGateway(Protocol):
    def trigger(self, mode, skill, creator, model=None, agent=None, description=None):
        ...

    def fetch_all_tasks(self, skill_name=None, eval_mode=None):
        ...

    def fetch_latest_tasks(self, skill_names):
        ...

    def fetch_report(self, mode, external_task_id, updated_at=None):
        ...


class HttpTransport(Protocol):
    def get(self, url: str, **kwargs) -> Any:
        ...

    def post(self, url: str, **kwargs) -> Any:
        ...


class EvaluationModeStrategy(ABC):
    """新增模式实现此契约并注册，应用服务无需增加分支。"""

    @property
    @abstractmethod
    def key(self):
        ...

    @property
    @abstractmethod
    def name(self):
        ...

    @property
    @abstractmethod
    def submit_path(self):
        ...

    @abstractmethod
    def fields(self, common, model=None, agent=None, description=None):
        ...

    @abstractmethod
    def report_path(self, task_id):
        ...

    @abstractmethod
    def extract_report(self, data):
        ...


class StaticEvaluationStrategy(EvaluationModeStrategy):
    key = "STATIC"
    name = "静态评测"
    submit_path = "/api/v1/guard/tasks/static-eval"

    def fields(self, common, model=None, agent=None, description=None):
        fields = dict(common)
        if model:
            fields["model_name"] = model
        return fields

    def report_path(self, task_id):
        return f"/api/v1/guard/tasks/{task_id}/static-eval/report"

    def extract_report(self, data):
        return data.get("report")


class DynamicEvaluationStrategy(EvaluationModeStrategy):
    """触发、质量评测共享契约，差异由注册参数表达。"""

    def __init__(self, key, name, submit_path):
        self._key = key
        self._name = name
        self._submit_path = submit_path

    @property
    def key(self):
        return self._key

    @property
    def name(self):
        return self._name

    @property
    def submit_path(self):
        return self._submit_path

    def fields(self, common, model=None, agent=None, description=None):
        fields = dict(common)
        if agent:
            fields["agent"] = agent
        if model:
            fields["model"] = model
        if description:
            fields["description"] = description
        return fields

    def report_path(self, task_id):
        return f"/api/v1/tasks/{task_id}/report?mode={self.key}"

    def extract_report(self, data):
        return data


class ModeRegistry:
    def __init__(self, strategies, allowed_modes):
        self._strategies = {strategy.key: strategy for strategy in strategies}
        self._allowed_modes = tuple(allowed_modes)

    def get(self, mode):
        try:
            return self._strategies[mode]
        except KeyError:
            raise ValueError(f"不支持的评测模式: {mode}") from None

    def validate(self, modes):
        if not modes:
            raise ValueError("modes 不能为空")
        result = []
        for mode in modes:
            mode = str(mode).upper()
            if mode not in self._allowed_modes:
                raise ValueError(
                    f"非法评测模式: {mode}（允许: {list(self._allowed_modes)}）")
            if mode not in result:
                result.append(mode)
        return result

    def describe(self):
        return {"modes": [{"key": s.key, "name": s.name}
                           for s in self._strategies.values()]}


def default_mode_registry(allowed_modes):
    return ModeRegistry((
        StaticEvaluationStrategy(),
        DynamicEvaluationStrategy("TRIGGER", "触发评测", "/api/v1/e2e-eval/trigger"),
        DynamicEvaluationStrategy("QUALITY", "质量评测", "/api/v1/e2e-eval/quality"),
    ), allowed_modes)


# ── 状态映射规则 ──

class TaskStatePolicy:
    def __init__(self, state_map):
        self.state_map = dict(state_map)

    def normalize(self, raw_state) -> str:
        """外部状态统一转小写本地状态。"""
        if not raw_state:
            return "queuing"
        return self.state_map.get(str(raw_state).upper(), str(raw_state).lower())

    def resolve(self, detail: dict, mode: str) -> str:
        """解析任务状态：优先取该评测模式的状态，缺失时回退到任务顶层状态。

        外部服务在静态评测失败时顶层 current_state 仍停留在 EXECUTING，
        只有 mode_states[<mode>].state 会变成 FAILED；只看顶层状态会导致
        任务永久停在 running。
        """
        mode_states = detail.get("mode_states") or {}
        mode_state = (mode_states.get(mode) or {}).get("state")
        return self.normalize(mode_state or detail.get("current_state"))


class ServerUrlProvider:
    """进程内惰性缓存；保留配置中心优先、默认地址兜底的行为。"""

    def __init__(self, config_reader, default_url, logger):
        self.config_reader = config_reader
        self.default_url = default_url
        self.logger = logger
        self._cached_url = None

    def __call__(self):
        if self._cached_url:
            return self._cached_url
        url = None
        try:
            url = self.config_reader("coreinsight.skill.eval.url")
        except Exception as e:
            self.logger.warning(f"读取 Skill 评测服务地址配置失败，使用默认地址: {e}")
        self._cached_url = (url or self.default_url()).rstrip("/")
        return self._cached_url


class ExpiringReadCache:
    """有限大小的进程内只读缓存；同键并发合并，失效后不回填旧请求。"""

    def __init__(self, max_entries=256, max_bytes=32 * 1024 * 1024, clock=time.monotonic,
                 copy_value=copy.deepcopy):
        self.max_entries = max(1, int(max_entries))
        self.max_bytes = max(1, int(max_bytes))
        self.clock = clock
        self._copy_value = copy_value
        self._lock = threading.Lock()
        self._entries = OrderedDict()
        self._inflight = {}
        self._generation = 0
        self._bytes = 0

    def clear(self):
        with self._lock:
            self._generation += 1
            self._entries.clear()
            self._bytes = 0

    def get_cached(self, key):
        with self._lock:
            entry = self._entries.get(key)
            if not entry or entry[0] <= self.clock() or entry[2] is not None:
                return None
            self._entries.move_to_end(key)
        return self._copy_value(entry[1])

    def get(self, key, loader, ttl, empty_ttl=None, error_ttl=0):
        while True:
            with self._lock:
                entry = self._entries.get(key)
                if entry and entry[0] > self.clock():
                    self._entries.move_to_end(key)
                    if entry[2] is not None:
                        raise entry[2]
                    return self._copy_value(entry[1])
                if entry:
                    self._bytes -= self._entries.pop(key)[3]
                event = self._inflight.get(key)
                if event is None:
                    event = threading.Event()
                    self._inflight[key] = event
                    generation = self._generation
                    break
            event.wait()
        value, error, weight = None, None, 0
        duration = max(float(ttl), 0)
        try:
            value = loader()
            if (value is None or value == []) and empty_ttl is not None:
                duration = max(float(empty_ttl), 0)
            weight = len(json.dumps(value, ensure_ascii=False, default=str).encode("utf-8"))
        except Exception as caught:
            error = caught
            duration = max(float(error_ttl), 0)
        finally:
            with self._lock:
                if generation == self._generation and duration > 0 and weight <= self.max_bytes:
                    self._entries[key] = (self.clock() + duration, value, error, weight)
                    self._bytes += weight
                    while len(self._entries) > self.max_entries or self._bytes > self.max_bytes:
                        self._bytes -= self._entries.popitem(last=False)[1][3]
                self._inflight.pop(key, None)
                event.set()
        if error is not None:
            raise error
        return self._copy_value(value)


class ThreadLocalHttpTransport:
    """每个工作线程复用连接；requests.Session 不在线程之间共享。"""

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._local = threading.local()

    def get(self, url, **kwargs):
        return self._session().get(url, **kwargs)

    def post(self, url, **kwargs):
        return self._session().post(url, **kwargs)

    def _session(self):
        if not hasattr(self._local, "session"):
            self._local.session = self.session_factory()
        return self._local.session


class SkillEvaluationHttpClient:
    _MAX_FILTERED_SKILL_NAMES = 4

    def __init__(self, http: HttpTransport, server_url, modes: ModeRegistry,
                 timeout, logger, task_cache_ttl=10, report_cache_ttl=300,
                 empty_report_ttl=3, page_workers=4, report_concurrency=8,
                 report_cache_max_entries=2048, report_cache_max_bytes=64 * 1024 * 1024):
        self.http = http
        self.server_url = server_url
        self.modes = modes
        self.timeout = timeout
        self.logger = logger
        self.task_cache_ttl = task_cache_ttl
        self.report_cache_ttl = report_cache_ttl
        self.empty_report_ttl = empty_report_ttl
        self.page_workers = max(1, int(page_workers))
        self.task_cache = ExpiringReadCache(max_entries=32)
        # 索引只在内部读取，按所需名称选出任务后再复制。
        self.task_index_cache = ExpiringReadCache(max_entries=32, copy_value=lambda index: index)
        self._page_executor = ThreadPoolExecutor(max_workers=self.page_workers)
        self._name_executor = ThreadPoolExecutor(max_workers=self._MAX_FILTERED_SKILL_NAMES)
        self.report_cache = ExpiringReadCache(max_entries=report_cache_max_entries,
                                             max_bytes=report_cache_max_bytes)
        self._report_slots = threading.BoundedSemaphore(max(1, int(report_concurrency)))

    def trigger(self, mode, skill, creator, model=None, agent=None, description=None):
        base = self.server_url()
        package_url = skill.get("skill_package_url")
        version = skill.get("version")
        if not package_url or not version:
            raise ValueError("Skill 缺少包地址或版本号，无法评测")
        strategy = self.modes.get(mode)
        fields = strategy.fields({
            "skill_package_url": package_url,
            "version": version,
            "creator": creator,
        }, model=model, agent=agent, description=description)
        files = {key: (None, str(value)) for key, value in fields.items()}
        url = base + strategy.submit_path
        self.logger.info(f"触发 Skill 评测: mode={mode}, skill_id={skill.get('skill_id')}, "
                         f"version={version}, url={url}")
        try:
            resp = self.http.post(url, files=files, verify=False, timeout=self.timeout())
        finally:
            # 超时也可能已创建任务；随后查询应绕过本进程的旧任务快照。
            self.task_cache.clear()
            self.task_index_cache.clear()
        self.logger.info(f"Skill 评测服务响应: mode={mode}, skill_id={skill.get('skill_id')}, "
                         f"status_code={resp.status_code}, text={resp.text[:1000]}")
        resp.raise_for_status()
        result = resp.json() if resp.text else {}
        return result

    def fetch_all_tasks(self, page_size=100, skill_name=None, eval_mode=None):
        """始终查询 all 来源；名称/模式可缩小范围，名称仍须由业务层精确校验。

        不按全局 state 或 creator 过滤，避免丢失某一模式的最新任务。
        """
        page_size = min(max(int(page_size), 1), 100)
        filters = {"skill_name": skill_name, "eval_mode": eval_mode}
        key = (self.server_url(), page_size, skill_name, eval_mode, "all")
        return self.task_cache.get(
            key, lambda: self._collect_tasks(page_size, filters),
            ttl=self.task_cache_ttl, error_ttl=1)

    def fetch_report(self, mode, external_task_id, updated_at=None):
        key = (self.server_url(), mode, external_task_id, str(updated_at or ""))

        def fetch():
            strategy = self.modes.get(mode)
            with self._report_slots:
                resp = self.http.get(self.server_url() + strategy.report_path(external_task_id),
                                     verify=False, timeout=self.timeout())
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json() if resp.text else {}
            if not isinstance(data, dict):
                raise RuntimeError("评测报告格式错误")
            report = strategy.extract_report(data)
            return report if report else None

        return self.report_cache.get(key, fetch, ttl=self.report_cache_ttl,
                                     empty_ttl=self.empty_report_ttl, error_ttl=2)

    def fetch_latest_tasks(self, skill_names):
        """复用全量索引，冷缓存下只为少量指定名称并行查询外部任务。"""
        names = set(skill_names)
        if not names:
            return []
        if len(names) > self._MAX_FILTERED_SKILL_NAMES:
            indexes = [self._task_index(None)]
        else:
            global_index = self.task_index_cache.get_cached((self.server_url(), None, "all"))
            if global_index is not None:
                indexes = [global_index]
            elif len(names) == 1:
                indexes = [self._task_index(next(iter(names)))]
            else:
                # 名称查询可能继续分页，分页使用独立线程池。
                indexes = self._name_executor.map(self._task_index, names)
        tasks = {}
        for index in indexes:
            if names.intersection(index["invalid_names"]):
                raise RuntimeError("匹配的评测任务缺少有效 updated_at/created_at，无法判断最新记录")
            for name in names:
                for task in index["latest"].get(name, {}).values():
                    tasks[str(task["task_id"])] = task
        return copy.deepcopy(list(tasks.values()))

    def _fetch_task_page(self, page, page_size, filters):
        params = {"page": page, "page_size": page_size, "platform_type": "all"}
        params.update({key: value for key, value in filters.items() if value is not None})
        resp = self.http.get(f"{self.server_url()}/api/v1/tasks", params=params,
                             verify=False, timeout=self.timeout())
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
            raise RuntimeError("评测服务 tasks 列表格式错误")
        if data.get("page") is not None and int(data["page"]) != page:
            raise RuntimeError("评测服务未正确执行分页，无法获取完整任务列表")
        if data.get("total") is not None and int(data["total"]) < 0:
            raise RuntimeError("评测服务 total 不能为负数")
        for task in data["tasks"]:
            if not isinstance(task, dict) or not task.get("task_id"):
                raise RuntimeError("评测任务缺少 task_id 或结构错误")
        return data

    def _collect_tasks(self, page_size, filters):
        first = self._fetch_task_page(1, page_size, filters)
        tasks = {}
        expected = None

        def merge(data):
            nonlocal expected
            if data.get("total") is not None:
                expected = max(expected or 0, int(data["total"]))
            for task in data["tasks"]:
                key = str(task["task_id"])
                if key not in tasks or _task_order(task) > _task_order(tasks[key]):
                    tasks[key] = task

        merge(first)
        if expected is not None and len(tasks) >= expected:
            return list(tasks.values())
        # 有完整分页元数据时并发抓取后续页；兼容旧返回缺少 page_size/total 的情况。
        effective_size = first.get("page_size")
        if expected is not None and effective_size and int(effective_size) > 0:
            effective_size = int(effective_size)
            next_page = 2
            while next_page <= (expected + effective_size - 1) // effective_size:
                last_page = (expected + effective_size - 1) // effective_size
                if last_page > 10000:
                    raise RuntimeError("评测服务任务分页超过上限")
                for data in self._page_executor.map(
                        lambda page: self._fetch_task_page(page, effective_size, filters),
                        range(next_page, last_page + 1)):
                    merge(data)
                next_page = last_page + 1
            if len(tasks) < expected:
                raise RuntimeError("评测服务分页重复或发生变更，任务列表不完整，请刷新重试")
            return list(tasks.values())
        for page in range(2, 10001):
            before = len(tasks)
            data = self._fetch_task_page(page, page_size, filters)
            merge(data)
            if expected is not None and len(tasks) >= expected:
                return list(tasks.values())
            if not data["tasks"]:
                if expected is None:
                    return list(tasks.values())
                raise RuntimeError("评测服务分页提前结束，任务列表不完整，请刷新重试")
            if len(tasks) == before:
                raise RuntimeError("评测服务返回重复分页，任务列表不完整，请刷新重试")
        raise RuntimeError("评测服务任务分页超过上限，未返回不完整结果")

    def _task_index(self, name_filter):
        def build_index():
            latest, orders, invalid_names = {}, {}, set()
            for task in self._collect_tasks(100, {"skill_name": name_filter}):
                name = task.get("skill_name")
                if not name or (name_filter is not None and name != name_filter):
                    continue
                task_modes = _result_task_modes(task)
                if not task_modes:
                    continue
                order = _task_order(task)
                if order[0] == float("-inf"):
                    invalid_names.add(name)
                    continue
                modes = latest.setdefault(name, {})
                for mode in task_modes:
                    key = (name, mode)
                    if key not in orders or order > orders[key]:
                        orders[key] = order
                        modes[mode] = task
            return {"latest": latest, "invalid_names": list(invalid_names)}

        return self.task_index_cache.get(
            (self.server_url(), name_filter, "all"), build_index,
            ttl=self.task_cache_ttl, error_ttl=1)


class HarnessHttpClient:
    def __init__(self, http: HttpTransport, base_url, headers_factory, timeout, logger):
        self.http = http
        self.base_url = base_url
        self.headers_factory = headers_factory
        self.timeout = timeout
        self.logger = logger
        self._skills_cache = {}
        self._scenes_cache = {}

    def fetch_skills(self, first_scene, second_scene, dim_type, dim_name):
        """调用 harness 场景技能接口，返回该场景下的 Skill 列表。"""
        if not first_scene or not second_scene or not dim_name:
            return []
        cache_key = (first_scene, second_scene, dim_type, dim_name)
        if cache_key in self._skills_cache:
            return self._skills_cache[cache_key]

        params = {
            "firstScene": first_scene,
            "secondScene": second_scene,
            "dimType": dim_type,
            "dimName": dim_name,
        }
        resp = self.http.get(
            f"{self.base_url()}/scene-activity/scene/skills",
            params=params, headers=self.headers_factory(), verify=False, timeout=self.timeout())
        self.logger.info(f"[harness] Skill 包信息查询: params={params}, status_code={resp.status_code}")
        resp.raise_for_status()
        data = resp.json() if resp.text else {}
        skills = data.get("data") or []
        self._skills_cache[cache_key] = skills
        return skills

    def fetch_scenes(self, dim_code):
        """查询产品在 harness 中的场景列表（一级/二级场景）。"""
        if not dim_code:
            return []
        if dim_code in self._scenes_cache:
            return self._scenes_cache[dim_code]

        resp = self.http.get(
            f"{self.base_url()}/scene-activity/scenes",
            params={"dimCode": dim_code}, headers=self.headers_factory(),
            verify=False, timeout=self.timeout())
        self.logger.info(f"[harness] 场景列表查询: dimCode={dim_code}, status_code={resp.status_code}")
        resp.raise_for_status()
        data = resp.json() if resp.text else {}
        scenes = data.get("data") or []
        self._scenes_cache[dim_code] = scenes
        return scenes


# ── Skill 包解析 ──

class HarnessPackageResolver:
    def __init__(self, catalog: SkillCatalog, harness: HarnessGateway, logger):
        self.catalog = catalog
        self.harness = harness
        self.logger = logger

    def resolve(self, skill_info, offering_ids):
        """优先使用库内包信息，缺失时查询 harness 并回填。"""
        package_url = skill_info.get("skill_package_url")
        version = skill_info.get("version")
        if package_url and version:
            return package_url, version

        package_url, version = self._resolve_harness_package(skill_info, offering_ids)
        skill_id = skill_info.get("skill_id")
        try:
            self.catalog.update_skill_package_info(skill_id, package_url, version)
        except Exception as error:
            self.logger.warning(f"回填 Skill 包信息失败: {skill_id}, {error}")
        return package_url, version

    def _find_package(self, skill_name, scenes, product_name) -> Tuple[str, str]:
        """返回最新可用包的下载地址和版本，未找到时两项均为空字符串。"""
        for scene in scenes:
            first_scene = scene.get("firstScene")
            second_scene = scene.get("secondScene")
            skills = self.harness.fetch_skills(
                first_scene=first_scene, second_scene=second_scene,
                dim_type="产品级", dim_name=product_name)
            matched = next((s for s in skills if s.get("skillName") == skill_name), None)
            if not matched:
                continue
            versions = matched.get("versions") or []
            if not versions:
                continue
            # 接口按上传时间倒序返回，取第一个最新版本
            latest = versions[0]
            package_url = latest.get("downloadUrl")
            version = latest.get("version")
            if package_url and version:
                return package_url, version
        return "", ""

    def _resolve_harness_package(self, skill_info, offering_ids):
        skill_name = skill_info.get("name")
        products = self._products_for_offerings(offering_ids)
        if not products:
            raise ValueError(f"Skill {skill_name} 未找到关联产品，无法在 harness 中定位评测包")

        first_scene = skill_info.get("level1")
        second_scene = skill_info.get("level2")
        preferred_scenes = []
        if first_scene and second_scene:
            preferred_scenes.append({"firstScene": first_scene, "secondScene": second_scene})

        for offering_id, product_name in products:
            package = self._find_product_package(
                skill_name, offering_id, product_name, preferred_scenes)
            if all(package):
                return package

        product_names = ", ".join(name for _, name in products)
        scene_hint = (f"{first_scene}/{second_scene}" if preferred_scenes else
                      "库内场景为空，已按产品全部场景查询")
        raise ValueError(
            f"Skill {skill_name} 在 harness 中未找到可用包"
            f"（产品: {product_names}，场景: {scene_hint}）")

    def _products_for_offerings(self, offering_ids):
        products = []
        for offering_id in offering_ids or []:
            product = self.catalog.query_product_by_offering_id(offering_id)
            if not product or not product.get("product_name"):
                continue
            pair = (offering_id, product["product_name"])
            if pair not in products:
                products.append(pair)
        return products

    def _find_product_package(self, skill_name, offering_id, product_name,
                              preferred_scenes) -> Tuple[str, str]:
        package = self._find_package(skill_name, preferred_scenes, product_name)
        if all(package):
            return package
        try:
            other_scenes = [
                scene
                for scene in self.harness.fetch_scenes(offering_id)
                if scene not in preferred_scenes
            ]
        except Exception as error:
            self.logger.warning(f"查询 harness 场景列表失败: offering_id={offering_id}, {error}")
            return package
        return self._find_package(skill_name, other_scenes, product_name)


# ── 按 Skill 查询与直接提交 ──

RESULT_MODES = ("STATIC", "TRIGGER", "QUALITY")
_TERMINAL_STATES = {"completed", "failed", "cancelled", "canceled"}


def _skill_name(info):
    return info.get("name") or info.get("skill_name") or ""


def _timestamp(value):
    """ISO 时间统一成 UTC 数值；列表中的无时区时间按同一 UTC 基准比较。"""
    if not value:
        return float("-inf")
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return float("-inf")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def _task_order(task):
    # 列表按创建时间返回；按接口说明，以更新时间确定最近变化的评测记录。
    created = _timestamp(task.get("created_at"))
    updated = _timestamp(task.get("updated_at"))
    return (updated if updated != float("-inf") else created,
            created, str(task.get("task_id") or ""))


def _result_task_modes(task):
    modes = set(task.get("eval_modes") or ())
    modes.update((task.get("mode_states") or {}).keys())
    modes.intersection_update(RESULT_MODES)
    return modes


def _empty_mode():
    return {"status": "not_evaluated", "external_task_id": None,
            "version": None, "report": None, "report_status": "not_available",
            "error": None, "report_error": None, "created_at": None, "updated_at": None}


def _skill_status(modes):
    statuses = [value["status"] for value in modes.values()]
    if any(s not in _TERMINAL_STATES and s != "not_evaluated" for s in statuses):
        return "processing"
    if any(s in {"failed", "cancelled", "canceled"} for s in statuses):
        return "failed"
    if all(s == "not_evaluated" for s in statuses):
        return "not_evaluated"
    return "done" if all(s == "completed" for s in statuses) else "partial"


class SkillEvaluationService:
    def __init__(self, catalog: SkillCatalog, packages: PackageResolver,
                 gateway: EvaluationGateway, modes: ModeRegistry,
                 states: TaskStatePolicy, logger, max_workers=6):
        self.catalog = catalog
        self.packages = packages
        self.gateway = gateway
        self.modes = modes
        self.states = states
        self.logger = logger
        self.max_workers = max(1, int(max_workers))
        self._report_executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def get_evaluable_skills(self, offering_id=None, pdu=None, department=None,
                             keyword=None, page=1, page_size=10):
        offering_ids = self._validate_scope(offering_id, pdu, department)
        return self.catalog.query_evaluable_skills(
            offering_ids, keyword=keyword, page=page, page_size=page_size)

    def get_skill_eval_modes(self):
        return self.modes.describe()

    def get_skill_eval_results(self, offering_id=None, pdu=None, department=None,
                               keyword=None, page=1, page_size=10,
                               include_reports=True, skill_ids=None):
        """查询目录开发已完成的 Skill；分页及 total 由目录状态过滤后的查询提供。

        每个维度单独选择最新任务，未评测也占一个固定维度。

        不按 creator 过滤；同一 Skill 的不同维度允许来自不同任务、不同版本。
        最新任务失败/运行中时不回退旧的成功报告，以免把旧结果当成新结果。
        """
        started = time.monotonic()
        offering_ids = self._validate_scope(offering_id, pdu, department)
        result = self._query_result_page(offering_ids, keyword, page, page_size, skill_ids)
        skills = result["items"]
        if not skills:
            return result
        by_name = self._matchable_result_skills(skills)
        if not by_name:
            return result

        catalog_done = time.monotonic()
        latest = self._latest_result_tasks(by_name)
        tasks_done = time.monotonic()
        report_count = self._apply_result_tasks(by_name, latest, include_reports)
        for item in by_name.values():
            item["status"] = _skill_status(item["modes"])

        finished = time.monotonic()
        self.logger.info(
            f"Skill 评测结果查询耗时: include_reports={include_reports}, skills={len(skills)}, "
            f"reports={report_count}, catalog_ms={(catalog_done - started) * 1000:.0f}, "
            f"tasks_ms={(tasks_done - catalog_done) * 1000:.0f}, "
            f"reports_ms={(finished - tasks_done) * 1000:.0f}, "
            f"total_ms={(finished - started) * 1000:.0f}")
        return result

    def create_skill_eval_batch(self, skill_ids, modes, offering_id=None, pdu=None,
                                department=None, batch_name=None, creator=None,
                                model=None, agent=None, description=None):
        """兼容旧入口名称；直接提交，不创建本地批次或任务。

        提交超时不自动重试：服务端可能已接收，避免重复触发。
        """
        offering_ids = self._validate_scope(offering_id, pdu, department)
        modes = self.modes.validate(modes)
        infos, scope_map = self._validate_selected_skills(skill_ids, offering_ids)
        prepared = []
        errors = []
        # 所有包在提交前统一校验；校验失败时尚未触发任何外部评测。
        for skill_id, info in infos.items():
            try:
                package_url, version = self.packages.resolve(info, scope_map.get(skill_id, []))
                if not package_url or not version:
                    raise ValueError("缺少包地址或版本号")
                prepared.append({"skill_id": skill_id, "skill_name": _skill_name(info),
                                 "skill_package_url": package_url, "version": version})
            except Exception as error:
                errors.append(f"{_skill_name(info) or skill_id}({error})")
        if errors:
            raise ValueError("以下 Skill 无法解析评测包: " + ", ".join(errors))

        items = [{"skill_id": skill["skill_id"], "skill_name": skill["skill_name"],
                  "version": skill["version"], "modes": {}} for skill in prepared]
        work = [
            (index, mode, skill)
            for index, skill in enumerate(prepared)
            for mode in modes
        ]

        def submit(entry):
            index, mode, skill = entry
            try:
                response = self.gateway.trigger(
                    mode, skill, creator or "system", model=model, agent=agent,
                    description=description)
                if not isinstance(response, dict) or not response.get("task_id"):
                    raise RuntimeError("评测服务未返回 task_id，需刷新确认是否已接收")
                # ID 只用于确认本次响应是否有效，不持久化，也不要求前端保存。
                return index, mode, {"submission_status": "submitted", "error": None}
            except Exception as error:
                self.logger.error(f"提交 Skill 评测未确认: skill_id={skill['skill_id']}, "
                                  f"mode={mode}, error={error}")
                return index, mode, {
                    "submission_status": "unconfirmed",
                    "error": "未确认提交成功，请先刷新结果，再决定是否重试",
                }

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for index, mode, value in executor.map(submit, work):
                items[index]["modes"][mode] = value
        submitted = sum(value["submission_status"] == "submitted"
                        for item in items for value in item["modes"].values())
        return {"skill_count": len(items), "total_count": len(work),
                "submitted_count": submitted, "unconfirmed_count": len(work) - submitted,
                "modes": modes, "items": items}

    def _validate_scope(self, offering_id=None, pdu=None, department=None):
        if sum(bool(value) for value in (offering_id, pdu, department)) != 1:
            raise ValueError("pdu、department、offering_id必须且只能传一个")
        offering_ids = self.catalog.query_scope_offering_ids(offering_id, pdu, department)
        if not offering_ids:
            raise ValueError("指定范围内没有产品")
        return offering_ids

    def _validate_selected_skills(self, skill_ids, offering_ids):
        if not skill_ids:
            raise ValueError("skill_ids 不能为空")
        ordered_ids = list(dict.fromkeys(skill_ids))
        infos = self.catalog.query_skill_infos_by_ids(ordered_ids)
        scope_map = self.catalog.query_skill_scope_products(ordered_ids, offering_ids)
        invalid = []
        for skill_id in ordered_ids:
            info = infos.get(skill_id)
            if not info:
                invalid.append(f"{skill_id}(不存在)")
            elif not scope_map.get(skill_id):
                invalid.append(f"{skill_id}(不属于当前范围)")
            elif info.get("status") != "已完成":
                invalid.append(f"{skill_id}(状态非已完成)")
            elif not _skill_name(info):
                invalid.append(f"{skill_id}(缺少 Skill 名称)")
        if invalid:
            raise ValueError("以下 Skill 不可评测: " + ", ".join(invalid))
        owners = self.catalog.query_skill_eval_name_owners(
            [_skill_name(infos[skill_id]) for skill_id in ordered_ids])
        ambiguous = [name for name, ids in owners.items() if len(set(ids)) > 1]
        if ambiguous:
            raise ValueError("外部任务仅含 skill_name，以下名称对应多个 Skill，无法可靠关联: "
                             + ", ".join(sorted(ambiguous)))
        return {skill_id: infos[skill_id] for skill_id in ordered_ids}, scope_map

    def _mode_result(self, task, mode):
        value = _empty_mode()
        value.update({
            "status": self.states.resolve(task, mode),
            "external_task_id": task["task_id"],
            "version": task.get("version"),
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at"),
        })
        context = task.get("state_context") or {}
        if isinstance(context, dict):
            error = context.get(mode) or context.get("error")
        else:
            error = context
        mode_state = (task.get("mode_states") or {}).get(mode) or {}
        value["error"] = mode_state.get("error") or error or None
        return value

    def _load_report(self, pair):
        mode, task_id, updated_at = pair
        try:
            report = self.gateway.fetch_report(mode, task_id, updated_at=updated_at)
            return pair, report, None
        except Exception as error:
            self.logger.warning(f"获取 Skill 评测报告失败: mode={mode}, task_id={task_id}, {error}")
            return pair, None, "获取报告失败，请稍后刷新"

    def _query_result_page(self, offering_ids, keyword, page, page_size, skill_ids):
        filters = {
            "keyword": keyword,
            "page": max(int(page), 1),
            "page_size": min(max(int(page_size), 1), 100),
        }
        if skill_ids is not None:
            if len(skill_ids) > 100:
                raise ValueError("skill_ids 一次最多传 100 个")
            filters["skill_ids"] = list(dict.fromkeys(skill_ids))
        result = dict(self.catalog.query_skill_eval_result_skills(offering_ids, **filters))
        skills = []
        for info in result.get("items", []):
            item = dict(info)
            item.update({
                "skill_id": info["skill_id"],
                "skill_name": _skill_name(info),
                "modes": {mode: _empty_mode() for mode in RESULT_MODES},
                "match_status": "unmatched",
                "match_error": None,
                "status": "not_evaluated",
            })
            skills.append(item)
        result["items"] = skills
        return result

    def _matchable_result_skills(self, skills):
        # 名称是否唯一要检查全库，不能只检查当前部门或当前页。
        owners = self.catalog.query_skill_eval_name_owners([item["skill_name"] for item in skills])
        by_name = {}
        for item in skills:
            name = item["skill_name"]
            if not name:
                item["match_status"] = "missing_name"
                item["match_error"] = "Skill 缺少名称，无法匹配评测任务"
            elif len(set(owners.get(name, []))) > 1:
                item["match_status"] = "ambiguous"
                item["match_error"] = "同名对应多个 Skill，外部任务缺少 skill_id，无法可靠关联"
            else:
                by_name[name] = item
        return by_name

    def _fetch_result_tasks(self, by_name):
        fetch_latest = getattr(self.gateway, "fetch_latest_tasks", None)
        if callable(fetch_latest):
            return fetch_latest(by_name)
        # 只匹配一个名称时利用服务端模糊筛选，随后仍按名称精确关联。
        name_filter = next(iter(by_name)) if len(by_name) == 1 else None
        return self.gateway.fetch_all_tasks(skill_name=name_filter)

    def _latest_result_tasks(self, by_name):
        latest, orders = {}, {}
        for task in self._fetch_result_tasks(by_name):
            name = task.get("skill_name")
            if name not in by_name:
                continue
            task_modes = _result_task_modes(task)
            if not task_modes:
                continue
            order = _task_order(task)
            if order[0] == float("-inf"):
                raise RuntimeError("匹配的评测任务缺少有效 updated_at/created_at，无法判断最新记录")
            for mode in RESULT_MODES:
                if mode not in task_modes:
                    continue
                key = (name, mode)
                if key not in orders or order > orders[key]:
                    orders[key] = order
                    latest[key] = task
        return latest

    def _apply_result_tasks(self, by_name, latest, include_reports):
        pending_reports = {}
        for (name, mode), task in latest.items():
            item = by_name[name]
            item["match_status"] = "matched"
            value = self._mode_result(task, mode)
            item["modes"][mode] = value
            if value["status"] != "completed":
                continue
            value["report_status"] = "unloaded"
            if include_reports:
                pair = (mode, task["task_id"], str(task.get("updated_at") or ""))
                pending_reports.setdefault(pair, []).append(value)
        # 只读当前页的最新报告，避免对所有历史任务逐个读取报告。
        if pending_reports:
            self._fill_reports(pending_reports)
        return len(pending_reports)

    def _fill_reports(self, pending_reports):
        for pair, report, error in self._report_executor.map(self._load_report, pending_reports):
            report_status = "error" if error else ("ready" if report is not None else "pending")
            for value in pending_reports[pair]:
                value.update(report=report, report_error=error, report_status=report_status)


# ── 惰性依赖装配 ──

@dataclass
class SkillEvaluationRuntime:
    service: SkillEvaluationService


_runtime = None
_runtime_lock = threading.Lock()


def _read_config(key):
    from utils.config_center_utils import get_config_by_key
    return get_config_by_key(key)


def _harness_base_url():
    from configs_info.settings import HARNESS_BASE_URL
    return HARNESS_BASE_URL


def _harness_headers():
    from configs_info.settings import HeaderConfig
    from utils.decrypt import kms_decrypt
    return {"X-HW-ID": HeaderConfig.X_HW_ID,
            "X-HW-APPKEY": kms_decrypt(HeaderConfig.X_HW_APPKEY),
            "Accept": "application/json"}


def build_runtime():
    import requests
    import urllib3
    from configs_info.constants import ALLOWED_SKILL_EVAL_MODES, SKILL_EVAL_STATE_MAP
    from configs_info.settings import SkillEvalConfig
    from db.operators.coreinsight_operator import CoreinsightOperator
    from logger import logger

    def get_timeout():
        return SkillEvalConfig.HTTP_TIMEOUT

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    operator = CoreinsightOperator()
    modes = default_mode_registry(ALLOWED_SKILL_EVAL_MODES)
    server_url = ServerUrlProvider(_read_config, lambda: SkillEvalConfig.SERVER_URL, logger)
    gateway = SkillEvaluationHttpClient(
        ThreadLocalHttpTransport(requests.Session), server_url, modes, get_timeout, logger,
        task_cache_ttl=getattr(SkillEvalConfig, "TASK_CACHE_TTL", 10),
        report_cache_ttl=getattr(SkillEvalConfig, "REPORT_CACHE_TTL", 300),
        empty_report_ttl=getattr(SkillEvalConfig, "EMPTY_REPORT_CACHE_TTL", 3),
        page_workers=getattr(SkillEvalConfig, "TASK_PAGE_WORKERS", 4),
        report_concurrency=getattr(SkillEvalConfig, "REPORT_HTTP_CONCURRENCY", 8),
        report_cache_max_entries=getattr(SkillEvalConfig, "REPORT_CACHE_MAX_ENTRIES", 2048),
        report_cache_max_bytes=getattr(SkillEvalConfig, "REPORT_CACHE_MAX_BYTES", 64 * 1024 * 1024))
    harness = HarnessHttpClient(requests, _harness_base_url, _harness_headers, get_timeout, logger)
    packages = HarnessPackageResolver(operator, harness, logger)
    states = TaskStatePolicy(SKILL_EVAL_STATE_MAP)
    service = SkillEvaluationService(operator, packages, gateway, modes, states, logger)
    return SkillEvaluationRuntime(service)


def get_runtime():
    global _runtime
    with _runtime_lock:
        if _runtime is None:
            _runtime = build_runtime()
        return _runtime


def get_evaluable_skills(offering_id=None, pdu=None, department=None,
                         keyword=None, page=1, page_size=10):
    return get_runtime().service.get_evaluable_skills(
        offering_id=offering_id, pdu=pdu, department=department,
        keyword=keyword, page=page, page_size=page_size)


def get_skill_eval_modes():
    return get_runtime().service.get_skill_eval_modes()


def get_skill_eval_results(offering_id=None, pdu=None, department=None,
                           keyword=None, page=1, page_size=10,
                           include_reports=True, skill_ids=None):
    return get_runtime().service.get_skill_eval_results(
        offering_id=offering_id, pdu=pdu, department=department,
        keyword=keyword, page=page, page_size=page_size,
        include_reports=include_reports, skill_ids=skill_ids)


def create_skill_eval_batch(skill_ids, modes, offering_id=None, pdu=None,
                            department=None, batch_name=None, creator=None,
                            model=None, agent=None, description=None):
    return get_runtime().service.create_skill_eval_batch(
        skill_ids=skill_ids, modes=modes, offering_id=offering_id, pdu=pdu,
        department=department, batch_name=batch_name, creator=creator,
        model=model, agent=agent, description=description)


def get_skill_eval_batch_list(dept_name=None, product_id=None, pdu_name=None,
                              status=None, keyword=None, creator=None,
                              page=1, page_size=10):
    """旧 Python 导入名兼容；返回 Skill 列表，前端应改用 results。"""
    if status or creator:
        raise ValueError("已改为查询部门开发已完成的 Skill，不再支持批次 status/creator 筛选")
    return get_skill_eval_results(
        offering_id=product_id, pdu=pdu_name, department=dept_name,
        keyword=keyword, page=page, page_size=page_size)


def get_skill_eval_batch_detail(batch_id):
    raise ValueError("已取消批次查询，请改用 /skillEval/results 按范围查询 Skill 结果")


def start_worker():
    """旧启动钩子兼容：不启动本地任务轮询线程，也不访问旧任务表。"""
    return None


def _poll_once():
    """旧诊断入口兼容：本地任务已停用，无需轮询。"""
    return None

