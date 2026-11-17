"""独立回归测试，不依赖公司数据库或评测服务：python -m unittest discover -s tests -v。"""
import copy
import logging
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

from skill_eval_center import (
    RESULT_MODES, SkillEvaluationHttpClient, SkillEvaluationService,
    TaskStatePolicy, ThreadLocalHttpTransport, default_mode_registry,
)


def task(name, number, modes=RESULT_MODES, state="COMPLETED"):
    return {"task_id": str(number), "skill_name": name, "eval_modes": list(modes),
            "current_state": state, "version": str(number),
            "created_at": f"2026-11-17T00:00:{number % 60:02d}Z",
            "updated_at": f"2026-11-17T00:00:{number % 60:02d}Z"}


class Catalog:
    def __init__(self, count=100):
        self.items = [{"skill_id": str(index), "skill_name": f"skill-{index:03d}",
                       "skill_status": "已完成", "offering_ids": ["product"]}
                      for index in range(count)]
        self.calls = []
        self.ambiguous = False

    def query_scope_offering_ids(self, offering_id, pdu, department):
        return [offering_id or "product"]

    def query_skill_eval_result_skills(self, offering_ids, keyword=None,
                                      page=1, page_size=10, skill_ids=None):
        self.calls.append((offering_ids, skill_ids))
        rows = [item for item in self.items if set(offering_ids).intersection(item["offering_ids"])
                and (skill_ids is None or item["skill_id"] in skill_ids)
                and (not keyword or keyword in item["skill_name"])]
        return {"total": len(rows), "page": page, "page_size": page_size,
                "pages": (len(rows) + page_size - 1) // page_size,
                "items": copy.deepcopy(rows[(page - 1) * page_size:page * page_size])}

    def query_skill_eval_name_owners(self, names):
        return {name: ["first", "second"] if self.ambiguous else [name] for name in names}


class Response:
    def __init__(self, data, status_code=200):
        self.data, self.status_code, self.text = data, status_code, "json"

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("upstream unavailable")

    def json(self):
        return copy.deepcopy(self.data)


class Http:
    def __init__(self, tasks, report_delay=0):
        self.tasks, self.report_delay = tasks, report_delay
        self.task_calls, self.report_calls = [], []
        self.lock = threading.Lock()
        self.report_status = 200
        self.post_error = False

    def get(self, url, **kwargs):
        if url.endswith("/api/v1/tasks"):
            params = kwargs["params"]
            with self.lock:
                self.task_calls.append(dict(params))
            rows = [entry for entry in self.tasks if not params.get("skill_name")
                    or params["skill_name"] in entry["skill_name"]]
            page, size = params["page"], params["page_size"]
            return Response({"tasks": rows[(page - 1) * size:page * size],
                             "total": len(rows), "page": page, "page_size": size})
        with self.lock:
            self.report_calls.append(url)
        time.sleep(self.report_delay)
        data = {"passed_cases": 1, "failed_cases": 0}
        return Response({"report": data} if "static-eval/report" in url else data,
                        self.report_status)

    def post(self, url, **kwargs):
        if self.post_error:
            raise TimeoutError("response lost after submission")
        return Response({"task_id": "new"})


class ResultsTests(unittest.TestCase):
    def make_service(self, count=100, tasks=None):
        catalog = Catalog(count)
        http = Http(tasks if tasks is not None else
                    [task(item["skill_name"], index) for index, item in enumerate(catalog.items)])
        modes = default_mode_registry(RESULT_MODES)
        logger = logging.getLogger("skill-eval-tests")
        gateway = SkillEvaluationHttpClient(http, lambda: "https://eval", modes,
                                            lambda: 30, logger, task_cache_ttl=60)
        service = SkillEvaluationService(catalog, None, gateway, modes,
                                        TaskStatePolicy({"EXECUTING": "running"}), logger)
        self.addCleanup(gateway._page_executor.shutdown)
        self.addCleanup(service._report_executor.shutdown)
        return catalog, http, gateway, service

    def test_status_list_avoids_all_reports_and_current_page_loads_only_30(self):
        catalog, http, gateway, service = self.make_service()
        metadata = service.get_skill_eval_results(offering_id="product", page_size=100,
                                                  include_reports=False)
        self.assertEqual(100, metadata["total"])
        self.assertEqual([], http.report_calls)
        self.assertEqual("completed", metadata["items"][0]["modes"]["STATIC"]["status"])
        self.assertEqual("unloaded", metadata["items"][0]["modes"]["STATIC"]["report_status"])
        ids = [item["skill_id"] for item in metadata["items"][:10]]
        reports = service.get_skill_eval_results(offering_id="product", skill_ids=ids,
                                                 page_size=100)
        self.assertEqual(10, len(reports["items"]))
        self.assertEqual(30, len(http.report_calls))
        self.assertEqual(1, len(http.task_calls), "复用状态查询的任务索引")
        self.assertEqual("ready", reports["items"][0]["modes"]["STATIC"]["report_status"])
        service.get_skill_eval_results(offering_id="product", skill_ids=ids, page_size=100)
        self.assertEqual(30, len(http.report_calls), "报告缓存命中后不重复 HTTP 请求")

    def test_legacy_defaults_still_include_reports(self):
        _, http, _, service = self.make_service(2)
        result = service.get_skill_eval_results(offering_id="product")
        self.assertEqual(6, len(http.report_calls))
        self.assertTrue(all(value["report"] for item in result["items"]
                            for value in item["modes"].values()))

    def test_id_filter_keeps_scope_and_empty_ids_do_not_mean_all(self):
        catalog, http, _, service = self.make_service(3)
        catalog.items[2]["offering_ids"] = ["another-product"]
        result = service.get_skill_eval_results(offering_id="product", skill_ids=["0", "2"])
        self.assertEqual(["0"], [item["skill_id"] for item in result["items"]])
        self.assertEqual((["product"], ["0", "2"]), catalog.calls[-1])
        result = service.get_skill_eval_results(offering_id="product", skill_ids=[])
        self.assertEqual([], result["items"])
        with self.assertRaises(ValueError):
            service.get_skill_eval_results(offering_id="product", skill_ids=["0"] * 101)

    def test_latest_is_per_mode_and_never_falls_back_after_failure(self):
        old = task("skill-000", 1)
        newer = task("skill-000", 2, ["STATIC"], "EXECUTING")
        newer["mode_states"] = {"STATIC": {"state": "FAILED", "error": "invalid"}}
        newest = task("skill-000", 3, ["QUALITY"], "EXECUTING")
        _, http, _, service = self.make_service(1, [old, newer, newest])
        modes = service.get_skill_eval_results(offering_id="product")["items"][0]["modes"]
        self.assertEqual("failed", modes["STATIC"]["status"])
        self.assertEqual("2", modes["STATIC"]["external_task_id"])
        self.assertEqual("running", modes["QUALITY"]["status"])
        self.assertEqual("1", modes["TRIGGER"]["external_task_id"])
        self.assertEqual(1, len(http.report_calls))

    def test_cross_scope_name_ambiguity_is_not_matched(self):
        catalog, http, _, service = self.make_service(1)
        catalog.ambiguous = True
        result = service.get_skill_eval_results(offering_id="product")
        self.assertEqual("ambiguous", result["items"][0]["match_status"])
        self.assertEqual([], http.task_calls)
        self.assertEqual([], http.report_calls)

    def test_all_task_pages_use_all_platforms_and_single_flight_index(self):
        _, http, gateway, _ = self.make_service(250)
        names = ["skill-000", "skill-200"]
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(lambda _: gateway.fetch_latest_tasks(names), range(4)))
        self.assertTrue(all(len(rows) == 2 for rows in results))
        self.assertEqual(3, len(http.task_calls))
        self.assertEqual({1, 2, 3}, {call["page"] for call in http.task_calls})
        self.assertTrue(all(call["platform_type"] == "all" for call in http.task_calls))
        self.assertTrue(all("creator" not in call and "state" not in call for call in http.task_calls))
        results[0][0]["skill_name"] = "mutated"
        self.assertNotEqual("mutated", gateway.fetch_latest_tasks(names)[0]["skill_name"])

    def test_submission_timeout_invalidates_task_index(self):
        _, http, gateway, _ = self.make_service(2)
        names = ["skill-000", "skill-001"]
        gateway.fetch_latest_tasks(names)
        http.post_error = True
        with self.assertRaises(TimeoutError):
            gateway.trigger("STATIC", {"skill_package_url": "url", "version": "1"}, "user")
        gateway.fetch_latest_tasks(names)
        self.assertEqual(2, len(http.task_calls))

    def test_missing_report_and_report_error_are_not_ready(self):
        for code, expected in ((404, "pending"), (500, "error")):
            with self.subTest(code=code):
                _, http, _, service = self.make_service(1)
                http.report_status = code
                result = service.get_skill_eval_results(offering_id="product")
                self.assertTrue(all(value["report_status"] == expected and value["report"] is None
                                    for value in result["items"][0]["modes"].values()))

    def test_bad_timestamp_in_other_skill_does_not_break_page(self):
        bad = task("another-skill", 2)
        bad["created_at"] = bad["updated_at"] = None
        _, _, gateway, _ = self.make_service(2, [task("skill-000", 1), bad])
        self.assertEqual(1, len(gateway.fetch_latest_tasks(["skill-000", "skill-001"])))
        with self.assertRaises(RuntimeError):
            gateway.fetch_latest_tasks(["skill-000", "another-skill"])

    def test_transport_reuses_sessions_without_sharing_across_threads(self):
        sessions, barrier = [], threading.Barrier(2)

        class Session:
            def __init__(self):
                sessions.append(self)

            def get(self, url, **kwargs):
                return self

        transport = ThreadLocalHttpTransport(Session)

        def work(_):
            first = transport.get("url")
            barrier.wait(timeout=5)
            self.assertIs(first, transport.get("url"))
            return first

        with ThreadPoolExecutor(max_workers=2) as executor:
            result = list(executor.map(work, range(2)))
        self.assertEqual(2, len(sessions))
        self.assertIsNot(result[0], result[1])


if __name__ == "__main__":
    unittest.main()
