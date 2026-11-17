import axiosService from '@/server/api/http';
import { DevUCAuthError, notificationService, openDevUCAuth } from '@/utils/common';

const knowledgeHost: string = import.meta.env.VITE_APP_CORE_INSIGHT_CHAT_URL
    ? import.meta.env.VITE_APP_CORE_INSIGHT_CHAT_URL + '/chat'
    : '/chat';
const BASE = knowledgeHost + '/knowledgeCenter';

// knowledge-engineering 后端主机（用于 codebase/tasks 等任务接口）
const keHost: string = import.meta.env.VITE_APP_CORE_INSIGHT_URL
    ? import.meta.env.VITE_APP_CORE_INSIGHT_URL + '/knowledge-engineering'
    : 'https://coreinsight.rnd.huawei.com/backend/knowledge-engineering';

// ---- 类型定义 ----

/** 统一分页结构 (3.4节) */
interface PageResult<T> {
  total: number;
  page: number;
  page_size: number;
  pages: number;
  items: T[];
}

/** API-01 overall */
interface Overall {
  kb_nums: number;
  knowledge_nums: number;
  code_success_nums: number;
  code_total_nums: number;
  operating_nums: number;
  design_rule_nums: number;
  develop_rule_nums: number;
  test_rule_nums: number;
  skill_total_nums: number;
  skill_success_nums: number;
  product_nums: number;
  center_knowledge_nums: number;
}

/** API-01 scenarios 元素 */
interface ScenarioMetrics {
  scenario: 'design' | 'develop' | 'test';
  code_success_nums: number;
  code_total_nums: number;
  operating_nums: number;
  rule_nums: number;
  skill_total_nums: number;
  skill_success_nums: number;
  domain_knowledge_nums: number;
  center_knowledge_nums: number;
}

/** API-01 hierarchy 产品节点 */
interface ProductAssetRow {
  offering_id: string;
  product_name: string;
  owner_name?: string | null;
  owner_id?: string | null;
  knowledge_nums: number;
  code_success_nums: number;
  code_total_nums: number;
  rule_nums: number;
  skill_total_nums: number;
  skill_success_nums: number;
  skill_connected: boolean;
  center_knowledge_nums: number;
}

/** API-01 hierarchy 开发部节点 */
interface DepartmentNode {
  department: string;
  product_nums: number;
  knowledge_nums: number;
  code_success_nums: number;
  code_total_nums: number;
  rule_nums: number;
  skill_total_nums: number;
  skill_success_nums: number;
  center_knowledge_nums: number;
  products: ProductAssetRow[];
}

/** API-01 hierarchy PDU节点 */
interface PduNode {
  pdu: string;
  product_nums: number;
  knowledge_nums: number;
  code_success_nums: number;
  code_total_nums: number;
  rule_nums: number;
  skill_total_nums: number;
  skill_success_nums: number;
  center_knowledge_nums: number;
  departments: DepartmentNode[];
}

/** API-01 完整响应 (嵌套hierarchy，不分页) */
interface DashboardSummary {
  overall: Overall;
  scenarios: ScenarioMetrics[];
  hierarchy: PduNode[];
}

/** 纯结构树产品节点（management/hierarchy 接口） */
interface HierarchyProduct {
  offering_id: string;
  product_name: string;
  owner_name: string | null;
  owner_id: string | null;
}

/** 纯结构树部门节点 */
interface HierarchyDepartment {
  department: string;
  product_nums: number;
  products: HierarchyProduct[];
}

/** 纯结构树 PDU 节点 */
interface HierarchyPdu {
  pdu: string;
  product_nums: number;
  departments: HierarchyDepartment[];
}

/** API-02 产业知识总览 */
interface KbGlobalInfo {
  kb_nums: number;
  knowledge_nums: number;
}

/** API-03 items 元素 */
interface KbItem {
  kb_id: string;
  kb_name: string;
  kb_url: string;
  knowledge_num: number;
  product_name: string;
}

/** API-07 items 元素 */
interface RepoItem {
  repo_name: string;
  repo_url: string | null;
  spec_status: string;
}

/** API-07 列表响应（含 spec_status_options） */
interface RepoListResult extends PageResult<RepoItem> {
  spec_status_options?: string[];
}

/** API-07-tree 代码仓树节点 */
interface RepoTreeNode {
  name: string;                  // 节点显示名（路径段名称）
  path: string;                  // 当前节点累积路径（如 "5gcore/mse"）
  type: 'directory' | 'repo';   // directory=目录节点，repo=叶子代码仓节点
  // directory 节点字段：
  success_count?: number;        // 已生成spec数量
  total_count?: number;          // 该分组下代码仓总数
  // repo叶子节点字段：
  repo_url?: string | null;
  spec_status?: string;
  scenario?: string;             // design/develop/test
  languages?: string;            // 代码仓语言（逗号分隔，如 "Python,Shell"）
  manage_status?: boolean | null; // 治理状态：true=已治理, false=未治理, null=未设置
  manage_ddl?: string | null;    // 治理期限（"2026-09-10 12:00:00" 格式）
  priority?: string | null;      // 优先级："重点仓" / "非重点仓" / null
  manager?: string | null;       // 责任人
  branch?: string | null;        // 代码仓分支
  download_count?: number;       // 下载次数
}

/** API-07-tree 树形列表响应 */
interface RepoTreeResult {
  nodes: RepoTreeNode[];
  spec_status_options?: string[];
}

/** API: 代码仓 spec 文件列表响应 */
interface CodebaseSpecListResult {
  source_type: string;       // 如 "codewiki_generate"
  docs: string[];            // 文件路径，如 ["design.md", "spec.md"]
}

/** API: 代码仓 spec 文件正文响应 */
interface CodebaseSpecContentResult {
  content: string;           // Markdown 原文
}

/** API: codebase/repos items 元素 */
interface CodebaseRepoItem {
  repo_name: string;
  repo_url: string;
  languages: string[];
  source_type: string;          // e.g. "uploaded_zip", "gitlab"
  create_time: string | null;   // ISO datetime "2026-08-21T22:23:24"
  spec_status: string;          // 已生成 | 生成中 | 生成失败 | 未生成
  branch: string;
  download_count: number;
}

/** API: codebase/repos 列表响应 */
interface CodebaseReposResult extends PageResult<CodebaseRepoItem> {}

/** API: codebase/repo/versions commit 元素 */
interface CodebaseCommitInfo {
  commit_id: string;
  workspace_id: string;
  spec_status: string;          // 已生成 | 生成中 | 生成失败 | 未生成
  create_time: string | null;
  download_count: number;
  source_type: string;
}

/** API: codebase/repo/versions branch 元素 */
interface CodebaseBranchInfo {
  branch: string;
  latest_commit_id: string;
  latest_workspace_id: string;
  commits: CodebaseCommitInfo[];
}

/** API: codebase/repo/versions 响应 */
interface CodebaseRepoVersionsResult {
  repo_url: string;
  branches: CodebaseBranchInfo[];
}

/** API: codebase/status 响应 */
interface CodebaseStatusResult {
  total: number;
  已生成: number;
  生成失败: number;
  未生成: number;
}

/** codebase API 查询参数 */
interface CodebaseQueryParams extends PageScopeParams {
  status?: string | null;
  keyword?: string | null;
}

/** API-07-search 代码仓搜索结果项（平铺列表，非树形） */
interface RepoSearchResultItem {
  path: string;
  repo_name: string;
  repo_url: string | null;
  spec_status: string;
  scenario: string;
  languages: string;
  manage_status?: boolean | null; // 治理状态：true=已治理, false=未治理, null=未设置
  manage_ddl?: string | null;    // 治理期限（"2026-09-10 12:00:00" 格式）
  priority?: string | null;      // 优先级："重点仓" / "非重点仓" / null
  manager?: string | null;       // 责任人
  branch?: string | null;        // 代码仓分支
  download_count?: number;       // 下载次数
}

/** Spec 自进化任务 */
interface EvoTask {
  id: string;
  repo_url: string;
  mr_url: string;                // 触发 Spec 自进化的 MR 链接
  spec_diff: string;             // Spec 自进化 diff（unified diff 文本）
  baseline_report: string;  // 基线评测报告（html 字符串）
  verify_report: string; // 自进化后评测报告（html 字符串）
  delta_metric: number | null;   // 知识改进效果指标变化值，如 0.12 / -0.4
  created_at: string;            // 创建时间 "2026-09-10 12:00:00"
  status: 'pending' | 'processing' | 'processed'; // 处理状态
  improvement_overview: string | null;  // 改进概览
  knowledge_mr_url: string | null;     // 已创建知识改进MR链接
}

/** API-08 规范数量 */
// 返回 { count: number }，与其他数量接口一致

/** API-12 items 元素 */
interface SkillItem {
  skill_id: string;
  name: string;
  description: string | null;
  level1: string | null;
  level2: string | null;
  process: string | null;
  sub_process: string | null;
  department: string | null;
  owner: string | null;
  status: string | null;
}

/** API-14 items 元素 */
interface OperatingItem {
  id: string;
  operating_system: string;
  is_used: boolean;
}

/** API-10 规范正文响应（返回 Markdown 原文字符串） */
type RuleContent = string;

// ---- 知识评测与回流类型 ----

type EvalType = 'code_gen' | 'test_gen' | 'skill';
type EvalConclusion = 'up' | 'down';
type ReflowStatus = 'pending' | 'processing' | 'done' | 'ignored';
type ReflowMRStatus = 'merged' | 'open' | 'closed';
type Scenario = 'design' | 'develop' | 'test';
type SceneKey = 'baseline' | 'init' | 'coreinsight' | 'corealm' | 'full' | 'improved';

interface EvalMetricRow {
  scene: SceneKey;
  metric_key: string;
  metric_value: number;
}

interface EvalRow {
  id: string;
  task_name: string;
  task_source: string;
  eval_type: EvalType;
  status: 'done' | 'processing' | 'failed';
  creator: string;
  created_at: string;
  eval_duration?: number;
  reflow_duration?: number;
  trigger_mode?: 'auto' | 'manual';
  reflow_expect?: EvalConclusion;
  reflow_status: ReflowStatus;
  reflow_opinions?: EvalReflowOpinion[];
  metrics?: EvalMetricRow[];
  has_reflow?: number; // 0=无回流阶段, 1=有回流阶段
}

/** 功能覆盖率详情 - 单个特性（大颗粒或小颗粒） */
interface EvalFeatureItem {
  description: string;
  score: number;
}

/** 功能覆盖率详情
 * features: 大颗粒特性列表
 * hunk_features: 小颗粒特性列表
 * coverage = (features得分总和 / features总数 * 0.7) + (hunk_features得分总和 / hunk_features总数 * 0.3)
 */
interface EvalCoverageDetail {
  features: EvalFeatureItem[];
  hunk_features: EvalFeatureItem[];
}

/** taskDetail 接口返回的评测指标（按场景嵌套） */
interface EvalMetricSet {
  coverage: number;
  token: number;
  duration: number;
  coverage_detail: EvalCoverageDetail | null;
}

/** taskDetail 接口返回结构（基础信息 + 评测指标） */
interface EvalTaskDetail {
  base_info: {
    eval_type: EvalType;
    status: 'done' | 'processing' | 'failed';
    eval_duration: number | null;
    reflow_duration: number | null;
    trigger_mode: 'auto' | 'manual';
    creator: string;
    created_at: string;
    task_source: string;
  };
  metrics: Record<SceneKey, EvalMetricSet>;
  diffs?: EvalDiffRow[];
}

interface EvalReflowOpinion {
  file: string;
  opinion: string;
}

interface EvalEffectCompareItem {
  metric_key: string;
  metric_label: string;
  before_val: number;
  after_val: number;
  before_coverage_detail?: EvalCoverageDetail | null;
  after_coverage_detail?: EvalCoverageDetail | null;
}

interface EvalRepoSuggestion {
  file_name: string;
  change_desc: string;
  diff: string;
}

interface EvalNonRepoSuggestion {
  knowledge_id?: string;
  knowledge_name?: string;
  source?: string;
  problem_category?: string;
  uri?: string;
  suggestion?: string;
  is_gap?: boolean;
  original_content?: string;
  improved_content?: string;
  content_summary?: string;
  reason?: string;
  remediation?: string;
  triage_reason?: string;
}

interface EvalRepoReflow {
  suggestions: EvalRepoSuggestion[];
  effect_compare: EvalEffectCompareItem[];
  reflow_mr?: { title: string; url: string; status: ReflowMRStatus; desc: string };
}

interface EvalNonRepoReflow {
  suggestions: EvalNonRepoSuggestion[];
}

/** 评测/回流 diff 行（按场景行存） */
interface EvalDiffRow {
  id: string;
  task_id: string;
  diff_type: 'eval' | 'reflow';
  scene: string;  // baseline/corealm/coreinsight/full/improved/gold
  diff_content: string | null;
  created_at?: string;
}

interface EvalReflowDetail {
  reflow_status: ReflowStatus;
  reflow_expect?: EvalConclusion;
  reflow_duration?: number | null;
  reflow_opinions: EvalReflowOpinion[];
  repo_reflow: EvalRepoReflow;
  non_repo_reflow: EvalNonRepoReflow;
  diffs?: EvalDiffRow[];
}

interface EvalStageSummary {
  count: number;
  avgCoverage: number | null;
  coverageGain: number | null;
  avgDuration: number | null;
}

interface EvalSummary {
  design: EvalStageSummary;
  develop: EvalStageSummary;
  test: EvalStageSummary;
}

/** 用户关注产品/部门 */
interface FollowedProduct {
  id?: string;
  user_id?: string;
  follow_type?: 'product' | 'department' | 'pdu';
  offering_id?: string;
  pdu?: string;
  department?: string;
  product_name?: string;
  created_at?: string;
}

/** 评测回流全景统计 */
interface EvalSceneAvgMetric {
  scene: string;
  label: string;
  sample_count: number;
  coverage: number;   // 0~1
  token: number;
  duration: number;   // 秒
}

interface KnowledgeConsumeStats {
  total_use_cnt: number;   // 累计消费总次数
  satisf_rate: number;     // 消费满足度 %
}

interface EvalOverviewStats {
  eval_task_count: number;
  coverage_gain_pct: number;
  verify_passed: number;
  verify_failed: number;
  reflow_by_type: { name: string; value: number }[];
  scene_avg_metrics: EvalSceneAvgMetric[];
}

// ---- Skill 评测类型 ----

/** Skill 可评测范围参数（三选一） */
interface SkillEvalScopeParams {
  offering_id?: string;
  pdu?: string;
  department?: string;
}

/** 可评测 Skill 项 */
interface SkillEvalSkillItem {
  skill_name?: string;
  skill_id: string;
  name: string;
  description: string | null;
  level1: string | null;
  level2: string | null;
  process: string | null;
  sub_process: string | null;
  department: string | null;
  owner: string | null;
  status: string | null;
  skill_package_url: string | null;
  version: string | null;
  offering_ids: string[];
}

/** 每种模式的最新执行记录与报告；执行完成不等于通过。 */
interface SkillEvalModeResult {
  status: string;
  external_task_id: string | null;
  version: string | null;
  report: Record<string, any> | null;
  report_status: 'ready' | 'pending' | 'unloaded' | 'error' | 'not_available' | string;
  error: unknown | null;
  report_error: string | null;
  created_at: string | null;
  updated_at: string | null;
}
interface SkillEvalSkillResult {
  skill_id: string;
  skill_name: string;
  name?: string;
  description?: string | null;
  skill_status: string | null;
  version: string | null;
  offering_ids: string[];
  status: string;
  match_status: string;
  match_error: string | null;
  modes: Record<string, SkillEvalModeResult>;
}
interface SkillEvalSubmissionResult {
  submission_status: 'submitted' | 'unconfirmed' | string;
  error: unknown | null;
}
interface SkillEvalCreateResult {
  skill_count: number;
  total_count: number;
  submitted_count: number;
  unconfirmed_count: number;
  modes: string[];
  items: { skill_id: string; skill_name: string; version: string | null; modes: Record<string, SkillEvalSubmissionResult> }[];
}
interface SkillEvalQueryParams extends SkillEvalScopeParams {
  keyword?: string | null;
  page?: number;
  page_size?: number;
}
interface SkillEvalResultsParams extends SkillEvalQueryParams {
  include_reports?: boolean;
  skill_ids?: string[];
}
interface SkillEvalCreateParams extends SkillEvalScopeParams {
  skill_ids: string[];
  modes: string[];
  creator?: string | null;
  model?: string | null;
  agent?: string | null;
  description?: string | null;
}

/** 产品责任人搜索结果项（fuyao hw-userinfo） */
interface UserInfoItem {
  user_no: string | null;   // 工号
  user_name: string | null; // 中文姓名
  name: string | null;      // 拼音姓名 + 工号
}

// ---- 通用请求封装 ----

async function kcPost<T>(path: string, data?: any, signal?: AbortSignal): Promise<T> {
  const res = await axiosService.post(path, data, undefined, undefined, signal);
  if (res && typeof res === 'object' && 'code' in res) {
    if (res.code !== 200) {
      throw new Error((res as any).msg || `请求失败（code: ${res.code}）`);
    }
    return res.data as T;
  }
  return res as T;
}

async function kcGet<T>(path: string, params?: any): Promise<T> {
  const res = await axiosService.get(path, params);
  if (res && typeof res === 'object' && 'code' in res) {
    if (res.code !== 200) {
      throw new Error((res as any).msg || `请求失败（code: ${res.code}）`);
    }
    return res.data as T;
  }
  return res as T;
}

async function kcDelete<T>(path: string, params?: any): Promise<T> {
  const res = await axiosService.delete(path, params);
  if (res && typeof res === 'object' && 'code' in res) {
    if (res.code !== 200) {
      throw new Error(res.msg || `请求失败（code: ${res.code}）`);
    }
    return res.data as T;
  }
  return res as T;
}

// ---- Scope 参数 (3.2节: pdu/department/offering_id 三选一) ----

interface ScopeParams {
  pdu?: string | null;
  department?: string | null;
  offering_id?: string | null;
  scenario?: string | null;
}

interface PageScopeParams extends ScopeParams {
  page?: number;
  page_size?: number;
}

// ---- API 方法 ----

const kcService = {
  // API-01: 管理首页（不分页，一次返回完整三级树）
  getDashboardSummary: (params: {
    scenario?: string | null;
    offering_id?: string | null;
    pdu?: string | null;
    department?: string | null;
  }): Promise<DashboardSummary> =>
      kcPost<DashboardSummary>(`${BASE}/management/global_info`, {
        scenario: params.scenario || null,
        offering_id: params.offering_id || null,
        pdu: params.pdu || null,
        department: params.department || null,
      }),

  // 纯结构树（pdu→department→product，不带统计字段，GET）
  getManagementHierarchy: (): Promise<HierarchyPdu[]> =>
      kcGet<HierarchyPdu[]>(`${BASE}/management/hierarchy`),

  // 知识消费统计（累计消费总次数 / 消费满足度）—— 调用 bicloud
  getKnowledgeConsumeStats: (params: {
    offering_id?: string | null;
    pdu?: string | null;
    department?: string | null;
  }): Promise<KnowledgeConsumeStats> =>
      kcPost<KnowledgeConsumeStats>(`${BASE}/management/consumeStats`, {
        offering_id: params.offering_id || null,
        pdu: params.pdu || null,
        department: params.department || null,
      }),

  // API-02: 产业知识总览
  getKbGlobalInfo: (params: ScopeParams): Promise<KbGlobalInfo> =>
      kcPost<KbGlobalInfo>(`${BASE}/productKnowledge/GlobalInfo`, params),

  // API-03: 产业知识集列表
  getKbList: (params: PageScopeParams): Promise<PageResult<KbItem>> =>
      kcPost<PageResult<KbItem>>(`${BASE}/productKnowledge/kb_list`, params),

  // API-04: 新增产品知识集（成功返回 null）
  addKb: (data: { offering_id: string; kb_id: string; kb_url: string }): Promise<void> =>
      kcPost<void>(`${BASE}/productKnowledge/add_kb`, data),

  // API-05: 解除产品知识集
  deleteKb: (data: { offering_id: string; kb_id: string }): Promise<void> =>
      kcPost<void>(`${BASE}/productKnowledge/delete_kb`, data),

  // API-06: 代码仓数量
  getCodeStatus: (params: ScopeParams): Promise<{ code_success_nums: number; code_total_nums: number }> =>
      kcPost<{ code_success_nums: number; code_total_nums: number }>(`${BASE}/code/status`, params),

  // API-07: 代码仓列表
  getCodeList: (params: PageScopeParams & { spec_status?: string }): Promise<RepoListResult> =>
      kcPost<RepoListResult>(`${BASE}/code/list`, params),

  // API-07-tree: 代码仓树形列表（懒加载，复用 code/list 接口）
  getCodeTree: (params: ScopeParams & {
    scenario?: string | null;
    spec_status?: string;
    language?: string;
    node_path?: string;
  }): Promise<RepoTreeResult> =>
      kcPost<RepoTreeResult>(`${BASE}/code/list`, params),

  // API-07-search: 代码仓搜索（平铺列表）
  searchRepos: (params: ScopeParams & {
    keyword: string;
    scenario?: string | null;
    spec_status?: string;
    language?: string;
  }, signal?: AbortSignal): Promise<RepoSearchResultItem[]> =>
      kcPost<RepoSearchResultItem[]>(`${BASE}/code/search`, params, signal),

  // API-15: 代码仓治理信息管理
  manageCode: (data: {
    repo_url: string;
    manage_status?: boolean | null;
    manage_ddl?: string | null;
    priority?: string | null;
    manager?: string | null;
  }): Promise<{ updated_count: number }> =>
      kcPost<{ updated_count: number }>(`${BASE}/code/manage`, data),

  // API: 下载已生成的代码仓 spec（返回二进制流）
  downloadCode: (data: { repo_url: string; branch: string; workspace_id?: string }) =>
      axiosService.downloadFile(`${BASE}/codebase/download`, data),

  // API: 代码仓 spec 文件列表（预览用，返回 {source_type, docs}）
  getCodebaseSpecList: (data: { repo_url: string; branch?: string | null; workspace_id?: string }): Promise<CodebaseSpecListResult> =>
      kcPost<CodebaseSpecListResult>(`${BASE}/codebase/spec/list`, data),

  // API: 代码仓 spec 文件正文（预览用，返回 {content}）
  getCodebaseSpecContent: (data: { source_type: string; path: string; repo_url: string; branch?: string | null }): Promise<CodebaseSpecContentResult> =>
      kcPost<CodebaseSpecContentResult>(`${BASE}/codebase/spec/content`, data),

  // API: codebase/repos 代码仓列表（分页）
  getCodebaseRepos: (params: CodebaseQueryParams): Promise<CodebaseReposResult> =>
      kcPost<CodebaseReposResult>(`${BASE}/codebase/repos`, {
        pdu: params.pdu || null,
        department: params.department || null,
        offering_id: params.offering_id || null,
        status: params.status || null,
        keyword: params.keyword || null,
        page: params.page ?? 1,
        page_size: params.page_size ?? 20,
      }),

  // API: codebase/status 代码仓生成状态汇总
  getCodebaseStatus: (params: ScopeParams): Promise<CodebaseStatusResult> =>
      kcPost<CodebaseStatusResult>(`${BASE}/codebase/status`, {
        pdu: params.pdu || null,
        department: params.department || null,
        offering_id: params.offering_id || null,
      }),

  // API: codebase/repo/versions 代码仓版本历史（分支 + commit 列表）
  getCodebaseRepoVersions: (data: { repo_url: string }): Promise<CodebaseRepoVersionsResult> =>
      kcPost<CodebaseRepoVersionsResult>(`${BASE}/codebase/repo/versions`, data),

  // API: 创建/重生成/更新 逆向任务（统一入口）
  // 入参：repoUrl / branch / scenario(默认 develop，可选 design|test) / generation_mode(默认 server_generate)
  // 返回：{ workspaceId, status, createTime }
  // 注意：该接口要求携带 Cookie，使用 postWithCookie
  createCodebaseTask: async (data: {
    repoUrl: string;
    branch: string;
    scenario: 'develop' | 'design' | 'test';
    generation_mode?: string;
  }): Promise<{ workspaceId: string; status: string; createTime: string }> => {
    const res = await axiosService.postWithCookie(`${keHost}/codebase/tasks`, {
      generation_mode: 'server_generate',
      ...data,
    });
    if (res && typeof res === 'object' && 'code' in res) {
      // DevUC 授权失效（未授权 / 过期无法续期）：打开授权页 + warning，抛 DevUCAuthError
      // 让调用方 catch 识别后跳过默认的"提交失败"通知
      if (res.code === 401) {
        const msgCh = (res as any).messageCh || '';
        const msgEn = (res as any).messageEn || '';
        const isDevUC = msgEn.includes('DevUC authorization unavailable')
            || msgCh.includes('DevUC 授权不可用');
        if (isDevUC) {
          openDevUCAuth();
          notificationService(
              'DevUC 授权',
              'DevUC 授权已失效，已为您打开授权页面，请完成授权后重试',
              'warning',
          );
          throw new DevUCAuthError(msgCh || msgEn || 'DevUC 授权不可用，请重新授权');
        }
      }
      if (res.code !== 200) {
        throw new Error((res as any).messageCh || (res as any).messageEn || (res as any).msg || `请求失败（code: ${res.code}）`);
      }
      return (res as any).data as { workspaceId: string; status: string; createTime: string };
    }
    return res as { workspaceId: string; status: string; createTime: string };
  },

  // API-08: 规范数量
  getRuleStatus: (params: ScopeParams): Promise<{ count: number }> =>
      kcPost<{ count: number }>(`${BASE}/rule/status`, params),

  // API-09: 规范路径列表 (返回路径字符串数组)
  getRuleList: (params: ScopeParams): Promise<string[]> =>
      kcPost<string[]>(`${BASE}/rule/list`, params),

  // API-10: 规范正文 (复用现有接口)
  getRuleContent: (filePath: string): Promise<RuleContent> =>
      kcPost<RuleContent>(`${BASE}/rule/content`, { file_path: filePath }),

  // API-11: Skill数量
  getSkillStatus: (params: ScopeParams): Promise<{ skill_total_nums: number; skill_success_nums: number }> =>
      kcPost<{ skill_total_nums: number; skill_success_nums: number }>(`${BASE}/skill/status`, params),

  // API: 中心仓知识数（按范围统计绑定代码仓 .raw 叶子目录文件总数）
  getCenterKnowledgeNums: (params: ScopeParams): Promise<{ center_knowledge_nums: number }> =>
      kcPost<{ center_knowledge_nums: number }>(`${BASE}/okf/center_knowledge`, params),

  // API-12: Skill列表
  getSkillList: (params: PageScopeParams): Promise<PageResult<SkillItem>> =>
      kcPost<PageResult<SkillItem>>(`${BASE}/skill/list`, params),

  // API-13: 作业系统数量
  getOperatingStatus: (params: ScopeParams): Promise<{ count: number }> =>
      kcPost<{ count: number }>(`${BASE}/operating/status`, params),

  // API-14: 作业系统列表
  getOperatingList: (params: PageScopeParams): Promise<PageResult<OperatingItem>> =>
      kcPost<PageResult<OperatingItem>>(`${BASE}/operating/list`, params),

  // 产品责任人：按姓名/工号关键字搜索人员
  searchUser: (info: string): Promise<UserInfoItem[]> =>
      kcGet<UserInfoItem[]>(`${BASE}/user/search`, { info }),

  // 更新产品责任人（owner_name/owner_id 传 null 表示清空）
  updateProductOwner: (data: {
    offering_id: string;
    owner_name: string | null;
    owner_id: string | null;
  }): Promise<{ updated_count: number }> =>
      kcPost<{ updated_count: number }>(`${BASE}/product/owner`, data),

  // ---- Spec 自进化任务 ----

  // 获取代码仓自进化任务总数量（合并待处理与已处理）
  getEvoTaskCount: (repo_url: string): Promise<{ total_count: number }> =>
      kcPost<{ total_count: number }>(`${BASE}/code/evoTaskCount`, { repo_url }),

  // 获取代码仓自进化任务列表（不区分状态，返回全部）
  getEvoTaskList: (repo_url: string, status?: string): Promise<EvoTask[]> =>
      kcPost<EvoTask[]>(`${BASE}/code/evoTaskList`, { repo_url, status: status ?? null }),

  // 更新自进化任务 spec 内容（编辑后保存）
  updateSpecDiff: (data: { task_id: string; new_spec_content: string }): Promise<void> =>
      kcPost<void>(`${BASE}/code/evoTaskUpdateSpec`, data),

  // 自进化任务入库（自动接受）
  insertEvoTask: (data: { repo_url: string; mr_url?: string; spec_diff?: string; baseline_report?: string; verify_report?: string; improvement_overview?: string }): Promise<{ task_id: string }> =>
      kcPost<{ task_id: string }>(`${BASE}/code/evoTaskInsert`, data),

  // ── 知识评测与回流 ──

  // 新建评测任务
  createEvalTask: (data: {
    task_type: string;
    trigger_mode: string;  // auto/manual
    task_name?: string;
    task_source?: string;
    modes?: string[];
    dept_name?: string;
    product_id?: string;
    pdu_name?: string;
    creator?: string;
    reflow_expect?: string;
    has_reflow?: number;
  }): Promise<{ task_id: string; status: string }> =>
      kcPost<{ task_id: string; status: string }>(`${BASE}/eval/taskCreate`, data),

  // 评测任务列表
  getEvalTaskList: (params: {
    dept_name?: string;
    product_id?: string;
    pdu_name?: string;
    status?: string;
    reflow_status?: string;
    keyword?: string;
    creator?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ total: number; list: EvalRow[] }> =>
      kcPost<{ total: number; list: EvalRow[] }>(`${BASE}/eval/taskList`, params),

  // 评测任务详情（主表 + metrics）
  getEvalTaskDetail: (task_id: string): Promise<EvalTaskDetail> =>
      kcGet<EvalTaskDetail>(`${BASE}/eval/taskDetail`, { task_id }),

  // 评测任务回流详情
  getEvalTaskReflow: (task_id: string): Promise<EvalReflowDetail> =>
      kcGet<EvalReflowDetail>(`${BASE}/eval/taskReflow`, { task_id }),

  // 标记回流完成
  markEvalReflowDone: (task_id: string): Promise<void> => {
    const query = `?task_id=${encodeURIComponent(task_id)}`;
    return kcPost<void>(`${BASE}/eval/reflowDone${query}`);
  },

  // 拒绝回流
  rejectEvalReflow: (task_id: string): Promise<void> => {
    const query = `?task_id=${encodeURIComponent(task_id)}`;
    return kcPost<void>(`${BASE}/eval/reflowReject${query}`);
  },

  // 评测任务汇总
  getEvalSummary: (params: { dept_name?: string; product_id?: string; pdu_name?: string }): Promise<EvalSummary> =>
      kcGet<EvalSummary>(`${BASE}/eval/summary`, params),

  // 删除评测任务（逻辑删除）
  deleteEvalTask: (task_id: string): Promise<void> =>
      kcDelete<void>(`${BASE}/eval/taskDelete`, { task_id }),

  // ---- 用户关注产品/部门 ----
  // 查询用户关注的产品/部门列表
  getFollowedProducts: (user_id?: string): Promise<FollowedProduct[]> =>
      kcGet<FollowedProduct[]>(`${BASE}/follow/products`, user_id ? { user_id } : undefined),

  // 关注产品/部门/PDU
  followProduct: (params: { follow_type?: 'product' | 'department' | 'pdu'; offering_id?: string; user_id?: string; pdu?: string; department?: string; product_name?: string }): Promise<FollowedProduct> =>
      kcPost<FollowedProduct>(`${BASE}/follow/product`, { follow_type: 'product', ...params }),

  // 取消关注产品/部门/PDU
  unfollowProduct: (params: { follow_type?: 'product' | 'department' | 'pdu'; offering_id?: string; department?: string; pdu?: string; user_id?: string }): Promise<void> => {
    const ft = params.follow_type || 'product';
    const parts = [`follow_type=${encodeURIComponent(ft)}`];
    if (params.offering_id) parts.push(`offering_id=${encodeURIComponent(params.offering_id)}`);
    if (params.department) parts.push(`department=${encodeURIComponent(params.department)}`);
    if (params.pdu) parts.push(`pdu=${encodeURIComponent(params.pdu)}`);
    if (params.user_id) parts.push(`user_id=${encodeURIComponent(params.user_id)}`);
    return kcDelete<void>(`${BASE}/follow/product?${parts.join('&')}`);
  },

  // ---- 评测回流全景统计 ----
  getEvalOverviewStats: (params: { dept_name?: string; product_id?: string; pdu_name?: string }): Promise<EvalOverviewStats> =>
      kcGet<EvalOverviewStats>(`${BASE}/eval/overviewStats`, params),

  // ---- Skill 评测：按 Skill 查询三个模式的最新结果 ----
  getSkillEvalModes: (): Promise<{ modes: { key: string; name: string }[] }> =>
      kcGet<{ modes: { key: string; name: string }[] }>(`${BASE}/skillEval/modes`),

  getEvaluableSkills: (params: SkillEvalQueryParams): Promise<PageResult<SkillEvalSkillItem>> =>
      kcPost<PageResult<SkillEvalSkillItem>>(`${BASE}/skillEval/evaluableSkills`, params),

  getSkillEvalResults: (params: SkillEvalResultsParams, signal?: AbortSignal): Promise<PageResult<SkillEvalSkillResult>> =>
      kcPost<PageResult<SkillEvalSkillResult>>(`${BASE}/skillEval/results`, params, signal),

  createSkillEvaluation: (data: SkillEvalCreateParams): Promise<SkillEvalCreateResult> =>
      kcPost<SkillEvalCreateResult>(`${BASE}/skillEval/taskCreate`, data),
};

export default kcService;
export type {
  DashboardSummary,
  Overall,
  ScenarioMetrics,
  PduNode,
  DepartmentNode,
  ProductAssetRow,
  HierarchyPdu,
  HierarchyDepartment,
  HierarchyProduct,
  KbGlobalInfo,
  KbItem,
  RepoItem,
  RepoListResult,
  RepoTreeNode,
  RepoTreeResult,
  RepoSearchResultItem,
  CodebaseSpecListResult,
  CodebaseSpecContentResult,
  CodebaseRepoItem,
  CodebaseReposResult,
  CodebaseStatusResult,
  CodebaseQueryParams,
  CodebaseCommitInfo,
  CodebaseBranchInfo,
  CodebaseRepoVersionsResult,
  EvoTask,
  SkillItem,
  OperatingItem,
  UserInfoItem,
  RuleContent,
  PageResult,
  ScopeParams,
  PageScopeParams,
  EvalType,
  EvalConclusion,
  ReflowStatus,
  ReflowMRStatus,
  Scenario,
  SceneKey,
  EvalMetricRow,
  EvalRow,
  EvalMetricSet,
  EvalCoverageDetail,
  EvalFeatureItem,
  EvalTaskDetail,
  EvalReflowOpinion,
  EvalEffectCompareItem,
  EvalRepoSuggestion,
  EvalNonRepoSuggestion,
  EvalReflowDetail,
  EvalRepoReflow,
  EvalNonRepoReflow,
  EvalDiffRow,
  EvalStageSummary,
  EvalSummary,
  FollowedProduct,
  EvalOverviewStats,
  EvalSceneAvgMetric,
  KnowledgeConsumeStats,
  SkillEvalScopeParams,
  SkillEvalSkillItem,
  SkillEvalModeResult,
  SkillEvalSkillResult,
  SkillEvalCreateResult,
  SkillEvalQueryParams,
  SkillEvalResultsParams,
  SkillEvalCreateParams,
  SkillEvalSubmissionResult,
};


