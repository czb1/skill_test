<script lang="ts" setup>
import { ref, reactive, computed, watch, nextTick, onBeforeUnmount } from 'vue';
import { use } from 'echarts/core';
import { BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import VChart from 'vue-echarts';
import kcService from '@/server/service/knowledgeCenterService';
import { vColResize } from '@/directives/colResize';
import type {
  EvalRow as ApiEvalRow,
  EvalMetricRow,
  EvalReflowDetail,
  SkillEvalSkillItem,
  SkillEvalCreateResult,
  SkillEvalSkillResult,
  SkillEvalModeResult,
} from '@/server/service/knowledgeCenterService';

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer]);

interface EvalScope {
  scopeType: string;   // 'pdu' | 'department' | 'offering_id'
  deptId: string | null;
  productId: string | null;
  pdu: string | null;
}
const props = defineProps<{ scope: EvalScope; currentUserId?: string }>();

// 兼容：从 scope 中提取用于过滤的参数（按 scopeType 传 pdu_name/product_id/dept_name）
function scopeFilterParams(): { dept_name?: string; product_id?: string; pdu_name?: string } {
  const s = props.scope;
  if (!s) return {};
  if (s.scopeType === 'offering_id' && s.productId) return { product_id: s.productId };
  if (s.scopeType === 'department' && s.deptId) return { dept_name: s.deptId };
  if (s.scopeType === 'pdu' && s.pdu) return { pdu_name: s.pdu };
  // 兜底：有 deptId 用 deptId
  if (s.deptId) return { dept_name: s.deptId };
  return {};
}

// Skill 评测范围参数（offering_id / pdu / department 三选一）
function skillScopeParams(): { offering_id?: string; pdu?: string; department?: string } {
  const scope = props.scope;
  if (scope?.scopeType === 'offering_id' && scope.productId) return { offering_id: scope.productId };
  if (scope?.scopeType === 'department' && scope.deptId) return { department: scope.deptId };
  if (scope?.scopeType === 'pdu' && scope.pdu) return { pdu: scope.pdu };
  return {};
}
function skillScopeValid(): boolean { return Object.values(skillScopeParams()).filter(Boolean).length === 1; }

// scope 是否有效（有可用的过滤标识）
function scopeValid(): boolean {
  const s = props.scope;
  if (!s) return false;
  return !!(s.deptId || s.productId || s.pdu);
}

// ============== 类型定义 ==============
interface FeatureItem {
  description: string;
  score: number;
}
interface CoverageDetail {
  features: FeatureItem[];
  hunk_features: FeatureItem[];
}
interface EvalMetrics {
  coverage: number;   // 0~1
  token: number;      // token 数
  duration: number;   // 秒
  coverage_detail?: CoverageDetail | null;
}
type EvalType = 'code_gen' | 'test_gen' | 'skill';
type EvalConclusion = 'up' | 'down' | '';
type ReflowStatus = 'pending' | 'processing' | 'done' | 'ignored';
interface ReflowOpinion { file: string; opinion: string }
interface EvalRow {
  task_name: string;
  task_source: string;         // 任务来源链接（MR 或 Skill 或 RAG 平台）
  eval_type: EvalType;
  status: 'done' | 'processing' | 'failed';
  creator: string;
  created_at: string;
  eval_duration: number;       // 评测耗时（秒）
  reflow_duration: number;     // 回流耗时（秒）
  trigger_mode: 'auto' | 'manual';  // 触发方式
  reflow_opinions: ReflowOpinion[];
  reflow_expect: EvalConclusion;
  reflow_status: ReflowStatus;
  has_reflow: number;          // 0=无回流阶段, 1=有回流阶段
  metrics: {
    baseline: EvalMetrics;
    init: EvalMetrics;
    coreinsight: EvalMetrics;
    corealm: EvalMetrics;
    full: EvalMetrics;
    improved: EvalMetrics;   // 知识改进后
  };
  _id?: string;               // 后端主键（对接接口用）
}
interface EvalStageSummary {
  count: number;
  avgCoverage: number;
  coverageGain: number;
  avgDuration: number;
}
interface EvalSummary {
  design: EvalStageSummary;
  develop: EvalStageSummary;
  test: EvalStageSummary;
}
type MetricKind = 'coverage' | 'token' | 'duration';
type SceneKey = 'init' | 'coreinsight' | 'corealm' | 'full' | 'improved';
type SummaryMetricKey = 'coverage' | 'token' | 'duration';

// ============== 新建评测任务弹窗 ==============
interface EvalMode { key: 'baseline' | 'init' | 'coreinsight' | 'corealm' | 'full'; label: string; disabled?: boolean }
type EvalTaskType = 'code_gen' | 'test_gen' | 'skill';

// 评测场景页签：知识增益评测 / Skill 评测
type EvalTab = 'knowledge' | 'skill';
const evalTab = ref<EvalTab>('knowledge');

const evalModalVisible = ref(false);
const evalModes: EvalMode[] = [
  { key: 'baseline', label: '无知识基线评测', disabled: true },
  { key: 'coreinsight', label: '仅产品知识增益评测' },
  { key: 'init', label: '仅作业知识增益评测' },
  { key: 'corealm', label: '仅领域知识增益评测' },
  { key: 'full', label: '全量知识增益评测', disabled: true },
];
const evalTaskTypes: { key: EvalTaskType; label: string; desc: string; disabled?: boolean; tip?: string }[] = [
  { key: 'code_gen', label: '代码生成场景知识增益评测', desc: '基于MR链接评测代码生成场景下产业/作业/领域知识的增益效果，对比功能覆盖率、Token消耗与完成时长' },
  { key: 'skill', label: 'Skill评测', desc: '勾选当前部门/产品下的 Skill，选择评测模式后发起评测，查看各 Skill 的评测报告' },
  { key: 'test_gen', label: '测试生成场景知识增益评测', desc: '基于MR链接评测测试生成场景下知识的增益效果，对比用例通过率、缺陷检出率、Token消耗与完成时长', disabled: true, tip: '该功能建设中' },
];
const evalForm = reactive<{ taskName: string; taskType: EvalTaskType | ''; taskSource: string; modes: Set<string>; hasReflow: boolean }>({
  taskName: '',
  taskType: '',
  taskSource: '',
  modes: new Set<string>(['baseline', 'full']),
  hasReflow: false,
});

// ============== Skill 评测 ==============
// Skill 结果以本地 skill_id 为行主键；三个模式各自保留最新记录。
const SKILL_MODE_KEYS = ['STATIC', 'TRIGGER', 'QUALITY'] as const;
const skillEvalModes = ref<{ key: string; label: string }[]>([
  { key: 'STATIC', label: '静态评测' }, { key: 'TRIGGER', label: '触发评测' }, { key: 'QUALITY', label: '质量评测' },
]);
let modesLoaded = false;
async function loadSkillModes() {
  if (modesLoaded) return;
  try {
    const response = await kcService.getSkillEvalModes();
    skillEvalModes.value = SKILL_MODE_KEYS.map(key => ({ key, label: response.modes.find(mode => mode.key === key)?.name || skillModeLabel(key) }));
    modesLoaded = true;
  } catch { /* 保留三种固定模式，后续打开时可重试。 */ }
}
function normalizeSkillMode(mode: string): string { return String(mode || '').trim().toUpperCase(); }
function normalizeSkillModeStatus(status: string): string { return String(status || 'not_evaluated').trim().toLowerCase(); }
function skillModeLabel(key: string): string {
  return skillEvalModes.value.find(mode => mode.key === normalizeSkillMode(key))?.label || key;
}
function skillModeResult(skill: SkillEvalSkillResult, mode: string): SkillEvalModeResult | null {
  return skill.modes?.[normalizeSkillMode(mode)] || null;
}
function skillModeStatusLabel(status: string): string {
  const key = normalizeSkillModeStatus(status);
  return ({ not_evaluated: '未评测', pending: '待处理', queuing: '排队中', running: '评测中', completed: '执行完成', failed: '执行失败', cancelled: '已取消', canceled: '已取消' } as Record<string, string>)[key] || `处理中（${key}）`;
}
function skillModeClass(mode: string): string {
  return ({ STATIC: 'mode-static', TRIGGER: 'mode-trigger', QUALITY: 'mode-quality' } as Record<string, string>)[mode] || 'mode-other';
}
function skillModeIcon(mode: string): string { return ({ STATIC: '静', TRIGGER: '触', QUALITY: '质' } as Record<string, string>)[mode] || '评'; }
function skillModeDescription(mode: string): string {
  return ({ STATIC: '检查结构、规范与静态规则', TRIGGER: '验证正向触发与负向误触发', QUALITY: '查看质量得分与用例表现' } as Record<string, string>)[mode] || '';
}
function skillStatusLabel(status: string): string {
  return ({ processing: '评测中', failed: '存在失败或取消', not_evaluated: '未评测', done: '三种模式执行完成', partial: '部分模式已完成' } as Record<string, string>)[status] || status || '未评测';
}
function skillErrorText(error: any): string {
  const detail = error?.response?.data?.detail ?? error?.data?.detail ?? error?.detail ?? error?.message ?? error;
  return typeof detail === 'string' ? detail : formatCellValue(detail);
}
function hasSkillMatchError(skill: SkillEvalSkillResult): boolean { return ['ambiguous', 'missing_name'].includes(skill.match_status); }
function isSkillModeTerminal(result: SkillEvalModeResult | null): boolean {
  return ['not_evaluated', 'completed', 'failed', 'cancelled', 'canceled'].includes(normalizeSkillModeStatus(result?.status || ''));
}
function hasReadySkillReport(result: SkillEvalModeResult | null): boolean {
  return result?.status === 'completed' && result.report_status === 'ready' && result.report != null;
}
function skillReportState(result: SkillEvalModeResult | null): string {
  if (!result) return '未评测';
  if (result.status === 'completed') {
    if (hasReadySkillReport(result)) return '报告已就绪';
    if (result.report_status === 'error') return '报告读取失败';
    return '报告生成中';
  }
  return skillModeStatusLabel(result.status);
}
function skillModeNotice(result: SkillEvalModeResult | null): string {
  if (result?.status === 'failed') return `执行失败：${skillErrorText(result.error || '评测服务未返回失败原因')}`;
  if (result?.report_status === 'error') return `报告读取失败：${result.report_error || '请刷新重试'}`;
  if (result?.status === 'completed' && !hasReadySkillReport(result)) return '执行已完成，报告生成中，可稍后刷新。';
  return `${skillModeStatusLabel(result?.status || 'not_evaluated')}，暂无可查看的报告。`;
}
function skillModeVersion(skill: SkillEvalSkillResult, mode: string): string { return skillModeResult(skill, mode)?.version || '—'; }
function skillLatestUpdated(skill: SkillEvalSkillResult): string {
  return SKILL_MODE_KEYS.map(key => skillModeResult(skill, key)?.updated_at || '').filter(Boolean).sort().pop() || '—';
}
function parsedSkillReports(skill: SkillEvalSkillResult, mode: string) {
  const source = skillModeResult(skill, mode);
  if (hasSkillMatchError(skill)) return [];
  return hasReadySkillReport(source) ? skillReportVariants(source!.report, mode) : [];
}
function skillModeGlance(skill: SkillEvalSkillResult, mode: string): SkillReportEntry[] {
  const source = skillModeResult(skill, mode), reports = parsedSkillReports(skill, mode);
  const preferred = source?.version?.replace(/^v/i, '');
  const report = reports.find(item => item.version.replace(/^v/i, '') === preferred) || reports[0];
  return report ? reportSummaryEntries(report.report, mode).slice(0, 2) : [];
}

const skillForm = reactive({ modes: new Set<string>(['STATIC']), selected: new Set<string>(), keyword: '', creator: '', description: '' });
const evaluableSkills = ref<SkillEvalSkillItem[]>([]);
const skillListLoading = ref(false), skillListError = ref('');
const skillListPage = ref(1), skillListPageSize = ref(10), skillListTotal = ref(0);
const skillListTotalPages = computed(() => Math.max(1, Math.ceil(skillListTotal.value / skillListPageSize.value)));
const selectingAllSkills = ref(false), skillSubmitting = ref(false), skillSubmitError = ref('');
let pickerRequest = 0, pickerSession = 0;
function toggleSkillMode(key: string) { if (skillForm.modes.has(key)) skillForm.modes.delete(key); else skillForm.modes.add(key); }
function toggleSkillSelect(id: string) { if (skillForm.selected.has(id)) skillForm.selected.delete(id); else skillForm.selected.add(id); }
const allCurrentPageSelected = computed(() => evaluableSkills.value.length > 0 && evaluableSkills.value.every(skill => skillForm.selected.has(skill.skill_id)));
const someCurrentPageSelected = computed(() => evaluableSkills.value.some(skill => skillForm.selected.has(skill.skill_id)));
function toggleSelectAllCurrentPage() {
  const remove = allCurrentPageSelected.value;
  evaluableSkills.value.forEach(skill => remove ? skillForm.selected.delete(skill.skill_id) : skillForm.selected.add(skill.skill_id));
}
function clearSelectedSkills() { skillForm.selected.clear(); }
async function loadEvaluableSkills() {
  if (!skillScopeValid()) return;
  const request = ++pickerRequest, session = pickerSession;
  skillListLoading.value = true; skillListError.value = '';
  try {
    const res = await kcService.getEvaluableSkills({ ...skillScopeParams(), keyword: skillForm.keyword.trim() || undefined, page: skillListPage.value, page_size: skillListPageSize.value });
    if (request !== pickerRequest || session !== pickerSession) return;
    evaluableSkills.value = res.items || []; skillListTotal.value = res.total || 0;
  } catch (error) {
    if (request !== pickerRequest || session !== pickerSession) return;
    evaluableSkills.value = []; skillListTotal.value = 0; skillListError.value = skillErrorText(error);
  } finally { if (request === pickerRequest && session === pickerSession) skillListLoading.value = false; }
}
async function selectAllSkills() {
  if (!skillScopeValid() || selectingAllSkills.value || skillSubmitting.value) return;
  const session = pickerSession, keyword = skillForm.keyword.trim(), scope = skillScopeParams(), ids: string[] = [];
  selectingAllSkills.value = true;
  try {
    for (let page = 1; ; page++) {
      const res = await kcService.getEvaluableSkills({ ...scope, keyword: keyword || undefined, page, page_size: 100 });
      if (session !== pickerSession || keyword !== skillForm.keyword.trim()) return;
      (res.items || []).forEach(skill => ids.push(skill.skill_id));
      if (!res.items?.length || page * 100 >= res.total) break;
    }
    if (session === pickerSession) ids.forEach(id => skillForm.selected.add(id));
  } catch (error) { if (session === pickerSession) skillListError.value = `全选失败：${skillErrorText(error)}`; }
  finally { if (session === pickerSession) selectingAllSkills.value = false; }
}
function searchEvaluableSkills() { if (skillSubmitting.value) return; pickerSession++; selectingAllSkills.value = false; skillListPage.value = 1; void loadEvaluableSkills(); }
function goSkillListPage(page: number) { if (page < 1 || page > skillListTotalPages.value || page === skillListPage.value) return; skillListPage.value = page; void loadEvaluableSkills(); }

// 只展示开发已完成的 Skill；收齐后按评测状态筛选、分页，避免漏掉后续页的有效结果。
const scopedSkillResults = ref<SkillEvalSkillResult[]>([]);
function shouldDisplaySkillResult(skill: SkillEvalSkillResult): boolean {
  if (skill.skill_status !== '已完成' || hasSkillMatchError(skill)) return false;
  return SKILL_MODE_KEYS.some(mode => {
    const result = skillModeResult(skill, mode);
    if (!result) return false;
    const status = normalizeSkillModeStatus(result.status);
    const evaluating = !isSkillModeTerminal(result);
    const generatingReport = status === 'completed' && result.report_status === 'pending';
    const hasReport = hasReadySkillReport(result) && hasReportValue(result.report);
    return evaluating || generatingReport || hasReport;
  });
}
const displayedSkillResults = computed(() => scopedSkillResults.value.filter(shouldDisplaySkillResult));
const skillResults = ref<SkillEvalSkillResult[]>([]), skillResultsLoading = ref(false), skillResultsError = ref('');
const skillFilter = reactive({ keyword: '' });
const skillPage = ref(1), skillPageSize = ref(10), skillTotal = ref(0), skillJumpPage = ref(1);
const skillTotalPages = computed(() => Math.max(1, Math.ceil(skillTotal.value / skillPageSize.value)));
const skillPageNumbers = computed<(number | string)[]>(() => {
  const total = skillTotalPages.value, current = skillPage.value;
  const pages: (number | string)[] = [];
  for (let page = 1; page <= total; page++) {
    if (total <= 7 || page === 1 || page === total || Math.abs(page - current) <= 1) pages.push(page);
    else if (pages[pages.length - 1] !== '...') pages.push('...');
  }
  return pages;
});
function applySkillResultPage() {
  const items = displayedSkillResults.value;
  skillTotal.value = items.length;
  skillPage.value = Math.min(skillPage.value, Math.max(1, Math.ceil(items.length / skillPageSize.value)));
  skillJumpPage.value = skillPage.value;
  const start = (skillPage.value - 1) * skillPageSize.value;
  skillResults.value = items.slice(start, start + skillPageSize.value);
}
async function collectScopedSkillResults(scope: ReturnType<typeof skillScopeParams>, keyword: string | undefined, signal: AbortSignal): Promise<SkillEvalSkillResult[]> {
  const byId = new Map<string, SkillEvalSkillResult>();
  for (let page = 1; ; page++) {
    const res = await kcService.getSkillEvalResults({ ...scope, keyword, page, page_size: 100 }, signal);
    for (const skill of res.items || []) byId.set(skill.skill_id, skill);
    if (!res.items?.length || page * 100 >= res.total) break;
  }
  return [...byId.values()];
}
const skillDrawerVisible = ref(false), skillDrawerPanel = ref<HTMLElement | null>(null);
const activeSkill = ref<SkillEvalSkillResult | null>(null), activeSkillMode = ref('STATIC');
const selectedSkillReportVersions = ref<Record<string, string>>({});
let skillDrawerTrigger: HTMLElement | null = null;
const skillSubmission = ref<SkillEvalCreateResult | null>(null);
const submissionIssues = computed(() => (skillSubmission.value?.items || []).flatMap(skill => Object.entries(skill.modes || {})
    .filter(([, mode]) => mode.submission_status !== 'submitted').map(([key, mode]) => ({ key: `${skill.skill_id}:${key}`, name: skill.skill_name, mode: key, error: skillErrorText(mode.error || '未确认提交成功，请先刷新结果') }))));
interface PendingSkillObservation { before: string; seen: boolean; expires: number; }
const skillObservationNotice = ref('');
const pendingSkillObservations = reactive<Record<string, Record<string, PendingSkillObservation>>>({});
function skillSourceIdentity(result: SkillEvalModeResult | null): string { return JSON.stringify([result?.external_task_id || null, result?.created_at || null]); }
function isAwaitingSkillSource(id: string, mode: string): boolean { return !!pendingSkillObservations[id]?.[mode] && !pendingSkillObservations[id][mode].seen; }
function observeSkillResults(items: SkillEvalSkillResult[]) {
  Object.entries(pendingSkillObservations).forEach(([id, modes]) => {
    Object.entries(modes).forEach(([mode, item]) => {
      if (Date.now() >= item.expires) {
        delete modes[mode];
        skillObservationNotice.value = '部分所选模式尚未确认新结果，已停止等待。可手动刷新查看，请先确认结果再决定是否重试。';
      }
    });
    if (!Object.keys(modes).length) delete pendingSkillObservations[id];
  });
  items.forEach(skill => {
    const entries = pendingSkillObservations[skill.skill_id];
    if (!entries) return;
    Object.keys(entries).forEach(mode => {
      const result = skillModeResult(skill, mode), item = entries[mode];
      if (skillSourceIdentity(result) !== item.before && result?.status !== 'not_evaluated') item.seen = true;
      if (item.seen && isSkillModeTerminal(result) && !(result?.status === 'completed' && result.report_status === 'pending')) delete entries[mode];
    });
    if (!Object.keys(entries).length) delete pendingSkillObservations[skill.skill_id];
  });
}
let skillPollTimer: ReturnType<typeof setTimeout> | null = null;
let skillContext = 0, skillDisposed = false, skillRefreshAgain = false;
let skillResultsRequest: Promise<void> | null = null;
let skillAbort = new AbortController();
function stopPollingSkillResults() { if (skillPollTimer) clearTimeout(skillPollTimer); skillPollTimer = null; }
function needsSkillRefresh(): boolean {
  return Object.keys(pendingSkillObservations).length > 0 || scopedSkillResults.value.some(skill => skill.skill_status === '已完成' && !hasSkillMatchError(skill) && SKILL_MODE_KEYS.some(key => {
    const result = skillModeResult(skill, key);
    return !isSkillModeTerminal(result) || (result?.status === 'completed' && result.report_status === 'pending');
  }));
}
function scheduleSkillRefresh() {
  stopPollingSkillResults();
  if (!skillSubmitting.value && !skillDisposed && evalTab.value === 'skill' && skillScopeValid() && needsSkillRefresh() && !skillResultsError.value) {
    skillPollTimer = setTimeout(() => void loadSkillResults(true), 10000);
  }
}
async function findScopedSkillResults(ids: Set<string>, scope: ReturnType<typeof skillScopeParams>, signal: AbortSignal): Promise<SkillEvalSkillResult[]> {
  const found: SkillEvalSkillResult[] = [];
  for (let page = 1; ids.size; page++) {
    const res = await kcService.getSkillEvalResults({ ...scope, page, page_size: 100 }, signal);
    (res.items || []).forEach(skill => { if (ids.delete(skill.skill_id)) found.push(skill); });
    if (!res.items?.length || page * 100 >= res.total) break;
  }
  return found;
}
function loadSkillResults(quiet = false): Promise<void> {
  if (!skillScopeValid() || skillDisposed || evalTab.value !== 'skill') return Promise.resolve();
  if (skillSubmitting.value) { skillRefreshAgain = true; return Promise.resolve(); }
  if (skillResultsRequest) { skillRefreshAgain = true; return skillResultsRequest; }
  stopPollingSkillResults();
  const context = skillContext, scope = skillScopeParams(), signal = skillAbort.signal;
  const params = { ...scope, keyword: skillFilter.keyword.trim() || undefined };
  const queryKey = JSON.stringify(params);
  skillResultsLoading.value = true; if (!quiet) skillResultsError.value = '';
  skillResultsRequest = (async () => {
    try {
      const all = await collectScopedSkillResults(scope, params.keyword, signal);
      if (context !== skillContext || skillDisposed || queryKey !== JSON.stringify({ ...skillScopeParams(), keyword: skillFilter.keyword.trim() || undefined })) return;
      // 仅在所有目录页读取成功后替换快照，失败时保留此前完整结果。
      scopedSkillResults.value = all;
      skillResultsError.value = '';
      observeSkillResults(all);
      applySkillResultPage();
      if (activeSkill.value) {
        const latest = displayedSkillResults.value.find(skill => skill.skill_id === activeSkill.value?.skill_id);
        if (latest) activeSkill.value = latest;
        else closeSkillDrawer();
      }
      const missing = new Set(Object.keys(pendingSkillObservations).filter(id => !all.some(skill => skill.skill_id === id)));
      if (missing.size) {
        const extra = await findScopedSkillResults(missing, scope, signal);
        if (context !== skillContext || skillDisposed) return;
        observeSkillResults(extra);
      }
    } catch (error) {
      if (context === skillContext && !skillDisposed && !signal.aborted) skillResultsError.value = `刷新失败，已保留上次结果：${skillErrorText(error)}`;
    } finally { if (context === skillContext) skillResultsLoading.value = false; }
  })().finally(() => {
    skillResultsRequest = null;
    if (skillRefreshAgain && !skillDisposed) { skillRefreshAgain = false; void loadSkillResults(); }
    else scheduleSkillRefresh();
  });
  return skillResultsRequest;
}
function onSkillFilterChange() { skillPage.value = 1; skillJumpPage.value = 1; closeSkillDrawer(); void loadSkillResults(); }
function clearSkillFilter() { skillFilter.keyword = ''; onSkillFilterChange(); }
function goToSkillPage(page: number | string) {
  const value = Number(page); if (!Number.isInteger(value) || value < 1 || value > skillTotalPages.value || value === skillPage.value) return;
  skillPage.value = value; skillJumpPage.value = value; closeSkillDrawer(); applySkillResultPage();
}
function onSkillPageSizeChange() { skillPage.value = 1; skillJumpPage.value = 1; closeSkillDrawer(); applySkillResultPage(); }
function skillResultKey(skillId: string): string { return JSON.stringify([activeSkillMode.value, skillId]); }
function selectSkillReportVersion(id: string, version: string) { selectedSkillReportVersions.value[skillResultKey(id)] = version; }
function selectSkillResultMode(mode: string) { activeSkillMode.value = normalizeSkillMode(mode); }
function openSkillDrawer(skill: SkillEvalSkillResult, mode = 'STATIC') {
  skillDrawerTrigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  activeSkill.value = skill; activeSkillMode.value = mode; skillDrawerVisible.value = true; selectedSkillReportVersions.value = {};
  nextTick(() => skillDrawerPanel.value?.focus());
}
function closeSkillDrawer() {
  skillDrawerVisible.value = false; activeSkill.value = null; selectedSkillReportVersions.value = {};
  skillDrawerTrigger?.focus(); skillDrawerTrigger = null;
}
function trapSkillDrawerFocus(event: KeyboardEvent) {
  const panel = skillDrawerPanel.value; if (!panel) return;
  const controls = Array.from(panel.querySelectorAll<HTMLElement>('button:not(:disabled), select:not(:disabled), summary, [tabindex="0"]')).filter(element => element.getClientRects().length > 0);
  const first = controls[0], last = controls[controls.length - 1];
  if (!first) { event.preventDefault(); panel.focus(); return; }
  if (event.shiftKey && (document.activeElement === first || document.activeElement === panel)) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && (document.activeElement === last || document.activeElement === panel)) { event.preventDefault(); first.focus(); }
}
const skillModeRows = computed(() => activeSkill.value ? [activeSkill.value].map(skill => {
  const source = skillModeResult(skill, activeSkillMode.value), reports = parsedSkillReports(skill, activeSkillMode.value);
  const selected = selectedSkillReportVersions.value[skillResultKey(skill.skill_id)], preferred = source?.version?.replace(/^v/i, '');
  const current = reports.find(report => report.version === selected) || reports.find(report => report.version.replace(/^v/i, '') === preferred) || reports[0];
  return { skill, reports, reportVersion: current?.version || '', result: source ? { ...source, report: current?.report || null } : null };
}) : []);

async function submitSkillEvaluation() {
  if (skillSubmitting.value || selectingAllSkills.value || !skillScopeValid()) return;
  if (!skillForm.modes.size || !skillForm.selected.size) { skillSubmitError.value = '请至少选择一个 Skill 和一种评测模式。'; return; }
  const context = skillContext, scope = skillScopeParams(), ids = [...skillForm.selected], modes = [...skillForm.modes];
  const creator = skillForm.creator.trim() || props.currentUserId || undefined, description = skillForm.description.trim() || undefined;
  skillSubmitting.value = true; skillSubmitError.value = ''; skillObservationNotice.value = '';
  const payload = { ...scope, skill_ids: ids, modes, creator, description };
  let submitted = false;
  try {
    stopPollingSkillResults();
    if (skillResultsRequest) await skillResultsRequest;
    // 提交前获取所选维度的来源快照，避免将旧的 completed 当成本次结果。
    const before = await findScopedSkillResults(new Set(ids), scope, skillAbort.signal);
    if (context !== skillContext || skillDisposed) return;
    const snapshots = new Map(before.map(skill => [skill.skill_id, skill]));
    const res = await kcService.createSkillEvaluation(payload);
    submitted = true;
    if (context !== skillContext || skillDisposed) return;
    skillSubmission.value = res;
    res.items.forEach(skill => Object.entries(skill.modes).forEach(([mode, result]) => {
      const previous = snapshots.get(skill.skill_id);
      if (!previous) return; // 没有可信快照时不推断新一轮评测状态。
      (pendingSkillObservations[skill.skill_id] ||= {})[mode] = { before: skillSourceIdentity(skillModeResult(previous, mode)), seen: false, expires: Date.now() + 5 * 60 * 1000 };
    }));
    evalModalVisible.value = false; pickerSession++; pickerRequest++; evalTab.value = 'skill';
    skillRefreshAgain = true;
  } catch (error) {
    if (context !== skillContext || skillDisposed) return;
    const rejected = error && typeof error === 'object' && 'response' in error && (error as any).response?.status === 400;
    skillSubmitError.value = rejected ? `提交校验失败：${skillErrorText(error)}` : submitted ? `已收到提交结果，刷新失败：${skillErrorText(error)}` : `未能确认提交结果：${skillErrorText(error)}。若请求超时，请先刷新结果再决定是否重试。`;
  } finally {
    skillSubmitting.value = false;
    if (!skillDisposed && context === skillContext) {
      if (skillRefreshAgain) { skillRefreshAgain = false; void loadSkillResults(true); }
      else scheduleSkillRefresh();
    }
  }
}

interface SkillReportVariant { version: string; report: Record<string, any> }
function isReportObject(value: any): value is Record<string, any> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}
// 实际报告既可能直接返回，也可能包裹在「版本 → trigger/quality/static」内。
// 只进入当前模式，多个版本分别查看，避免串用其他模式或把版本重复计数。
function skillReportVariants(raw: any, mode: string, version = '', depth = 0): SkillReportVariant[] {
  if (depth > 12 || raw === null || raw === undefined) return [];
  mode = normalizeSkillMode(mode);
  if (typeof raw === 'string') {
    const text = raw.replace(/^\uFEFF/, '').trim();
    try { return skillReportVariants(JSON.parse(text), mode, version, depth + 1); }
    catch { return [{ version, report: { content: raw } }]; }
  }
  if (Array.isArray(raw)) return [{ version, report: { results: raw } }];
  if (!isReportObject(raw)) return [{ version, report: { content: raw } }];
  const modeKeys = Object.keys(raw).filter(key => ['STATIC', 'TRIGGER', 'QUALITY'].includes(normalizeSkillMode(key)));
  if (modeKeys.length) {
    const key = modeKeys.find(key => normalizeSkillMode(key) === mode);
    return key ? skillReportVariants(raw[key], mode, version, depth + 1) : [];
  }
  const versionKeys = Object.keys(raw).filter(key => /^v?\d+\.\d+(?:\.\d+)*(?:[-+][\w.-]+)?$/i.test(key));
  if (versionKeys.length) return versionKeys.flatMap(key => skillReportVariants(raw[key], mode, key, depth + 1));
  // 报告接口可能将版本内容放在 results/report/data 中；外层的零值摘要不能阻止继续读取。
  for (const key of ['reports', 'report', 'report_data', 'report_json', 'evaluation_result', 'data', 'versions', 'result', 'results']) {
    const value = raw[key];
    if (value === null || value === undefined || Array.isArray(value)) continue;
    if (!isReportObject(value) && !(typeof value === 'string' && /^[\uFEFF\s]*[\[{]/.test(value))) continue;
    const variants = skillReportVariants(value, mode, version, depth + 1);
    const meaningful = variants.filter(item => hasStructuredSkillReport(item.report));
    if (meaningful.length) return meaningful.map(item => ({ ...item, report: {
        ...(raw.agent ? { agent: raw.agent } : {}), ...(raw.model ? { model: raw.model } : {}), ...item.report,
      } }));
  }
  return [{ version, report: normalizeSkillReport(raw) }];
}
function hasStructuredSkillReport(report: Record<string, any>): boolean {
  return Array.isArray(report.results)
      || Object.keys(REPORT_SUMMARY_LABELS).some(key => report[key] !== null && report[key] !== undefined && typeof report[key] !== 'object')
      || ['dimensions', 'findings', 'improvements', 'scores', 'dimension_scores', 'criteria'].some(key => report[key] !== undefined);
}
function normalizeSkillReport(raw: Record<string, any>): Record<string, any> {
  const report = { ...raw };
  // 将常见整体指标包裹层展开为当前模式的结构化字段。
  for (const key of ['summary', 'overall', 'metrics', 'result', 'results']) {
    const inner = raw[key];
    if (!isReportObject(inner)) continue;
    const structured = Object.keys(REPORT_SUMMARY_LABELS).some(field => inner[field] !== undefined)
        || ['dimensions', 'scores', 'dimension_scores', 'criteria', 'results'].some(field => inner[field] !== undefined);
    if (!structured) continue;
    Object.entries(inner).forEach(([field, value]) => { if (report[field] === undefined || field === key) report[field] = value; });
    if (key === 'results' && !Array.isArray(inner.results)) delete report.results;
    else if (key !== 'results') delete report[key];
  }
  return report;
}
// ---- Skill 报告渲染：每项内容归入对应区块，保留证据、零值与未知字段 ----
const REPORT_SUMMARY_LABELS: Record<string, string> = {
  grade: '等级', total: '总分', percent: '得分率',
  positive_trigger_rate: '正触发率', negative_false_trigger_rate: '负向误触发率',
  accuracy: '准确率', pass_rate: '通过率', total_cost_time: '总耗时',
  score: '得分', total_cases: '用例总数', passed_cases: '通过用例数', failed_cases: '失败用例数',
  total_score: '总分', overall_score: '整体得分', average_score: '平均分', avg_score: '平均分', max_score: '满分', max: '满分',
};
const REPORT_FIELD_LABELS: Record<string, string> = {
  ...REPORT_SUMMARY_LABELS,
  name: '名称', title: '标题', label: '名称', description: '描述', content: '内容',
  message: '信息', issue: '问题', suggestion: '建议', reason: '原因',
  severity: '严重程度', level: '级别', category: '分类', type: '类型',
  dimension: '维度', rule: '规则', file: '文件', line: '行号', weight: '权重',
  status: '状态', query: '输入 / 查询', input: '输入', expected: '期望结果',
  actual: '实际结果', triggered: '是否触发', passed: '是否通过', pass: '是否通过',
  result: '结果', output: '输出', case: '用例', case_name: '用例名称',
  cost_time: '耗时', token: 'Token', value: '内容', detail: '详情', details: '详情',
  id: 'ID', summary: '评测总结', conclusion: '结论', evidence: '证据',
  recommendation: '改进建议', max_score: '满分', check: '检查项',
  agent: '评测 Agent', model: '评测模型', task: '测试任务', case_id: '用例 ID',
  actual_trigger: '实际触发', expect_trigger: '预期触发', rationale: '评分依据', feedback: '反馈',
  pattern: '技能形态', confidence: '置信度', model_name: '评测模型', skill_name: 'Skill 名称',
  spec_source: '评分规范', evaluated_at: '评测时间', gate_blocked: '门禁阻断',
  d10_low_confidence_note: 'D10 低置信度说明', raw_score: '调整前得分',
  adjustment_reason: '调整原因', derivation_reason: '得分推导依据', adjusted_by_precheck: '经预检调整', low_confidence: '低置信度',
  knowledge_ratio: '知识构成', metric_glossary: '评分说明', dimensions: '维度评分标准',
  precheck_constraints: '预检信息', consistency_checks: '一致性检查',
  check_issues: '预检问题', critical_issues: '关键问题',
  A: '行动框架（A）', E: '独家知识（E）', R: '通用套话（R）',
  line_count: '正文行数', name_valid: '名称有效', score_caps: '维度得分上限', constraints: '评分约束',
  heading_count: '标题数量', heading_issues: '标题问题', frontmatter_valid: 'Frontmatter 有效',
  frontmatter_errors: 'Frontmatter 错误', description_present: '包含描述',
  issues: '检查问题', references_found: '引用文件', dependencies_found: '依赖项',
  resource_inventory: '资源清单', files_on_disk_count: '包内文件数', resource_mentions_found: '资源引用',
  python_dependencies_found: 'Python 依赖', reasons: '原因', path: '路径', source: '来源', kind: '类别',
};
interface SkillReportEntry { key: string; label: string; value: string; detail?: string }
function formatCellValue(value: any): string {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'boolean') return value ? '是' : '否';
  if (typeof value !== 'object') return String(value);
  try { return JSON.stringify(value, null, 2); } catch { return String(value); }
}
function formatReportValue(key: string, value: any): string {
  if (key === 'confidence') return ({ H: '高', M: '中', L: '低' } as Record<string, string>)[value] || formatCellValue(value);
  if (key === 'status' && ['pass', 'fail'].includes(value)) return value === 'pass' ? '通过' : '未通过';
  if (typeof value === 'boolean' && ['passed', 'pass'].includes(key)) return value ? '通过' : '未通过';
  if (typeof value === 'boolean' && ['actual_trigger', 'expect_trigger'].includes(key)) return value ? '触发' : '不触发';
  if (key === 'type' && value === 'positive') return '正向用例';
  if (key === 'type' && value === 'negative') return '负向用例';
  if (typeof value === 'string' && ['percent', 'positive_trigger_rate', 'negative_false_trigger_rate', 'accuracy', 'pass_rate'].includes(key)) {
    const fraction = value.trim().match(/^(\d+)\s*\/\s*(\d+)$/);
    if (fraction) return Number(fraction[2]) > 0 ? `${(Number(fraction[1]) / Number(fraction[2]) * 100).toFixed(2)}%（${fraction[1]}/${fraction[2]}）` : `—（${fraction[1]}/${fraction[2]}）`;
  }
  if (typeof value !== 'number' || !Number.isFinite(value)) return formatCellValue(value);
  if (['percent', 'positive_trigger_rate', 'negative_false_trigger_rate', 'accuracy', 'pass_rate'].includes(key)) {
    return (value >= 0 && value <= 1 ? value * 100 : value).toFixed(1) + '%';
  }
  if (key === 'total_cost_time' && value >= 0) {
    const seconds = Math.round(value);
    return `${Math.floor(seconds / 60)}分${seconds % 60}秒`;
  }
  return String(value);
}
function reportFieldLabel(key: string): string { return REPORT_FIELD_LABELS[key] || key; }
function hasReportValue(value: any): boolean {
  if (value === null || value === undefined || value === '') return false;
  if (Array.isArray(value)) return value.some(hasReportValue);
  if (isReportObject(value)) return Object.values(value).some(hasReportValue);
  return true;
}
function reportObjectEntries(obj: any, exclude: string[] = []): SkillReportEntry[] {
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return [];
  return Object.keys(obj)
      .filter(key => !exclude.includes(key) && hasReportValue(obj[key]))
      .map(key => ({ key, label: reportFieldLabel(key), value: formatReportValue(key, obj[key]) }));
}
function reportSummaryEntries(report: Record<string, any> | null, mode = ''): SkillReportEntry[] {
  if (!report) return [];
  const priority: Record<string, string[]> = {
    STATIC: ['total', 'max', 'grade', 'percent', 'score'],
    TRIGGER: ['passed_cases', 'failed_cases', 'pass_rate', 'total_cases', 'positive_trigger_rate', 'negative_false_trigger_rate', 'accuracy'],
    QUALITY: ['score', 'overall_score', 'total_score', 'total', 'average_score', 'avg_score', 'grade', 'percent', 'pass_rate'],
  };
  const derived = mode === 'TRIGGER' && Array.isArray(report.results) ? triggerStatsEntries(triggerCaseStats(report)) : [];
  const entries = [...new Set([...(priority[mode] || []), ...Object.keys(REPORT_SUMMARY_LABELS)])]
      .filter(key => !(mode === 'QUALITY' && key === 'total_cost_time') && report[key] !== undefined && report[key] !== null && typeof report[key] !== 'object' && !derived.some(entry => entry.key === key))
      .map(key => ({ key, label: REPORT_SUMMARY_LABELS[key], value: formatReportValue(key, report[key]) }));
  if (mode === 'QUALITY') {
    const summary = qualitySummaryEntries(report);
    summary.forEach(entry => { const index = entries.findIndex(item => item.key === entry.key); if (index >= 0) entries.splice(index, 1); });
    entries.push(...summary);
    if (reportDimensions(report).length) entries.push({ key: 'dimension_count', label: '评分维度', value: String(reportDimensions(report).length) });
  }
  return [...derived, ...entries].map(entry => {
    // 百分比和计数分别排版，避免「90.00%（9/10）」在窄卡片中随意断行。
    const rate = entry.value.match(/^\s*(\d+(?:\.\d+)?%|—)\s*[（(]\s*(\d+\s*\/\s*\d+)\s*[）)]\s*$/);
    return rate ? { ...entry, value: rate[1], detail: rate[2].replace(/\s/g, '') } : entry;
  });
}
function reportCases(report: Record<string, any> | null): Record<string, any>[] {
  return Array.isArray(report?.results) ? report.results.filter(isReportObject) : [];
}
function triggerCaseStats(report: Record<string, any> | null) {
  const cases = reportCases(report);
  const hasCases = Array.isArray(report?.results);
  const count = (key: string) => { const value = finiteScore(report?.[key]); return value !== null && Number.isInteger(value) && value >= 0 ? value : 0; };
  const passed = hasCases ? cases.filter(item => item.passed === true).length : count('passed_cases');
  const failed = hasCases ? cases.filter(item => item.passed === false).length : count('failed_cases');
  const judged = passed + failed;
  const total = hasCases ? report!.results.length : Math.max(count('total_cases'), judged);
  const groups = [{ type: 'positive', label: '正向用例' }, { type: 'negative', label: '负向用例' }].map(group => {
    const items = cases.filter(item => item.type === group.type);
    return { ...group, total: items.length, passed: items.filter(item => item.passed === true).length };
  }).filter(group => group.total);
  const available = hasCases || ['passed_cases', 'failed_cases', 'total_cases'].some(key => finiteScore(report?.[key]) !== null);
  return { total, passed, failed, available, unknown: total - judged,
    rate: judged ? passed / judged : null, groups };
}
function triggerStatsEntries(stats: ReturnType<typeof triggerCaseStats>): SkillReportEntry[] {
  const entries = [
    { key: 'passed_cases', label: '通过用例', value: stats.available ? String(stats.passed) : '—' },
    { key: 'failed_cases', label: '未通过用例', value: stats.available ? String(stats.failed) : '—' },
    { key: 'pass_rate', label: '通过率', value: stats.rate === null ? '—' : `${(stats.rate * 100).toFixed(2)}%` },
    { key: 'total_cases', label: '用例总数', value: stats.available ? String(stats.total) : '—' },
  ];
  if (stats.unknown) entries.push({ key: 'unknown_cases', label: '未判定用例', value: String(stats.unknown) });
  return entries;
}
function finiteScore(value: any): number | null {
  if (typeof value === 'string' && !/^[-+]?\d+(?:\.\d+)?$/.test(value.trim())) return null;
  if (typeof value !== 'string' && typeof value !== 'number') return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}
function formatScore(score: number): string { return String(Number(score.toFixed(2))); }
function qualityOverallScore(report: Record<string, any> | null): number | null {
  for (const key of ['score', 'overall_score', 'total_score', 'total', 'average_score', 'avg_score']) {
    const score = finiteScore(report?.[key]);
    if (score !== null) return score;
  }
  return null;
}
function qualityCaseStats(report: Record<string, any> | null) {
  const scores = reportCases(report).map(item => finiteScore(item.score ?? item.overall_score ?? item.total_score ?? item.result?.score)).filter((score): score is number => score !== null);
  return { count: scores.length, average: scores.length ? scores.reduce((sum, score) => sum + score, 0) / scores.length : null,
    minimum: scores.length ? scores.reduce((min, score) => Math.min(min, score)) : null,
    maximum: scores.length ? scores.reduce((max, score) => Math.max(max, score)) : null };
}
function assertionVerdict(value: any): string {
  const verdict = String(value || '').trim().toLowerCase();
  return verdict === 'pass' ? 'pass' : verdict === 'fail' ? 'fail' : 'unknown';
}
function qualitySummaryEntries(report: Record<string, any> | null): SkillReportEntry[] {
  const cases = reportCases(report);
  if (!Array.isArray(report?.results)) return [];
  const scores = qualityCaseStats(report), stats = triggerCaseStats(report);
  const assertions = cases.flatMap(item => Array.isArray(item.assertions) ? item.assertions.filter(isReportObject) : []);
  const passedAssertions = assertions.filter(item => assertionVerdict(item.verdict) === 'pass').length;
  const failedAssertions = assertions.filter(item => assertionVerdict(item.verdict) === 'fail').length;
  const failedMust = assertions.filter(item => String(item.priority).toLowerCase() === 'must' && assertionVerdict(item.verdict) === 'fail').length;
  const entries: SkillReportEntry[] = [];
  if (scores.count) entries.push({ key: 'average_case_score', label: '用例平均分', value: formatScore(scores.average!) });
  entries.push(...triggerStatsEntries(stats));
  if (scores.count) entries.push(
      { key: 'scored_cases', label: '评分用例数', value: String(scores.count) },
      { key: 'minimum_case_score', label: '用例最低分', value: formatScore(scores.minimum!) },
      { key: 'maximum_case_score', label: '用例最高分', value: formatScore(scores.maximum!) },
  );
  if (assertions.length) entries.push(
      { key: 'assertions_passed', label: '检查点通过', value: `${passedAssertions} / ${assertions.length}` },
      { key: 'assertions_failed', label: '检查点未通过', value: String(failedAssertions) },
      { key: 'must_failed', label: '必须检查点未通过', value: String(failedMust) },
  );
  return entries;
}
function triggerResultRows(report: Record<string, any> | null) {
  return reportCollectionItems(report, 'results').map(row => {
    const item = isReportObject(report?.results?.[row.index]) ? report!.results[row.index] : {};
    const titleKey = ['task', 'query', 'input', 'case_name', 'title', 'name'].find(key => hasReportValue(item[key]));
    const verdict = item.passed === true ? 'pass' : item.passed === false ? 'fail' : 'unknown';
    return { index: row.index, title: titleKey ? formatCellValue(item[titleKey]) : row.title,
      type: formatReportValue('type', item.type), expected: formatReportValue('expect_trigger', item.expect_trigger),
      actual: formatReportValue('actual_trigger', item.actual_trigger), verdict,
      verdictLabel: verdict === 'pass' ? '通过' : verdict === 'fail' ? '未通过' : '未判定',
      fields: row.entries.filter(entry => ![titleKey, 'type', 'expect_trigger', 'actual_trigger', 'passed'].includes(entry.key)) };
  });
}
function qualityResultRows(report: Record<string, any> | null) {
  return reportCases(report).map((item, index) => {
    const assertions = (Array.isArray(item.assertions) ? item.assertions : []).filter(isReportObject).map((assertion: Record<string, any>) => {
      const verdict = assertionVerdict(assertion.verdict);
      return { verdict, verdictLabel: verdict === 'pass' ? '通过' : verdict === 'fail' ? '未通过' : '未判定',
        priority: ({ must: '必须', should: '建议' } as Record<string, string>)[String(assertion.priority).toLowerCase()] || formatCellValue(assertion.priority),
        checkPoint: formatCellValue(assertion.check_point ?? assertion.item_id), reason: assertion.reason ? formatCellValue(assertion.reason) : '',
        confidence: finiteScore(assertion.confidence), evidenceTurn: finiteScore(assertion.evidence_turn_index) };
    });
    const fields = [
      { key: 'expect', label: '预期结果', value: item.expect ?? item.expected },
      { key: 'output', label: '实际输出', value: item.output ?? item.actual },
      { key: 'reason', label: '评分依据', value: item.reason },
    ].filter(field => field.value !== null && field.value !== undefined && field.value !== '').map(field => ({ ...field, value: formatCellValue(field.value) }));
    const score = finiteScore(item.score ?? item.overall_score ?? item.total_score ?? item.result?.score);
    const verdict = item.passed === true ? 'pass' : item.passed === false ? 'fail' : 'unknown';
    const duration = finiteScore(item.cost_time);
    return { index, title: formatCellValue(item.task || item.case_name || item.title || item.name || item.case_id || '未命名测试任务'),
      score: score === null ? '—' : formatScore(score), verdict, verdictLabel: verdict === 'pass' ? '通过' : verdict === 'fail' ? '未通过' : '未判定',
      assertionSummary: assertions.length ? `${assertions.filter((assertion: { verdict: string }) => assertion.verdict === 'pass').length} / ${assertions.length}` : '—',
      assertions, fields, caseId: item.case_id ? String(item.case_id) : '', duration: duration === null ? '' : `${formatScore(duration)} 秒`,
      expectItems: (Array.isArray(item.expect_items) ? item.expect_items : []).map((point: any) => formatCellValue(isReportObject(point) ? point.check_point : point)) };
  });
}
const REPORT_GROUPS = [
  { key: 'findings', label: '问题发现' },
  { key: 'improvements', label: '改进建议' },
  { key: 'results', label: '用例 / 结果明细' },
  { key: 'check_issues', label: '预检问题' },
  { key: 'critical_issues', label: '关键问题' },
];
const REPORT_SUPPLEMENT_GROUPS = [
  { key: 'knowledge_ratio', label: '知识构成' },
  { key: 'precheck_constraints', label: '预检信息' },
  { key: 'consistency_checks', label: '一致性检查' },
  { key: 'metric_glossary', label: '评分说明' },
];
const REPORT_NESTED_KEYS = ['dimensions', 'scores', 'dimension_scores', 'criteria', 'top3_improvements',
  ...REPORT_GROUPS.map(group => group.key), ...REPORT_SUPPLEMENT_GROUPS.map(group => group.key)];
function reportExtraEntries(report: Record<string, any> | null): SkillReportEntry[] {
  return reportObjectEntries(report, [...Object.keys(REPORT_SUMMARY_LABELS), ...REPORT_NESTED_KEYS]).filter(entry => typeof report?.[entry.key] !== 'object');
}
function reportAdditionalEntries(report: Record<string, any> | null): SkillReportEntry[] {
  const fields = Object.fromEntries(Object.entries(report || {})
      .filter(([key, value]) => !REPORT_NESTED_KEYS.includes(key) && typeof value === 'object'));
  return reportDetailEntries(fields);
}
// 嵌套检查结果展开为有名称的字段；空容器不占位，0 和 false 仍显示。
function reportDetailEntries(value: any, path: string[] = []): SkillReportEntry[] {
  if (!hasReportValue(value)) return [];
  if (Array.isArray(value)) {
    if (value.every(item => !isReportObject(item) && !Array.isArray(item))) {
      return [{ key: JSON.stringify(path), label: path.map(reportFieldLabel).join(' · '),
        value: value.filter(hasReportValue).map(item => formatCellValue(item)).join('\n') }];
    }
    return value.flatMap((item, index) => reportDetailEntries(item, [...path, String(index + 1)]));
  }
  if (isReportObject(value)) return Object.entries(value).flatMap(([key, item]) => reportDetailEntries(item, [...path, key]));
  return [{ key: JSON.stringify(path), label: path.map(reportFieldLabel).join(' · '), value: formatReportValue(path[path.length - 1] || '', value) }];
}
function reportSupplementSections(report: Record<string, any> | null) {
  return REPORT_SUPPLEMENT_GROUPS.map(group => {
    const raw = report?.[group.key];
    if (group.key === 'knowledge_ratio' && isReportObject(raw)) {
      return { ...group, entries: Object.entries(raw).filter(([, value]) => hasReportValue(value)).map(([key, value]) => {
          const ratio = finiteScore(value);
          return { key, label: reportFieldLabel(key), value: ratio !== null && ratio >= 0 && ratio <= 1 ? `${formatScore(ratio * 100)}%` : formatCellValue(value) };
        }) };
    }
    const fields = isReportObject(raw) ? { ...raw } : raw;
    if (isReportObject(fields) && group.key === 'precheck_constraints') {
      if (fields.name === report?.skill_name) delete fields.name;
      if (fields.description === report?.description) delete fields.description;
    }
    if (isReportObject(fields) && group.key === 'metric_glossary' && isReportObject(fields.dimensions)) {
      const shown = new Set(reportDimensions(report).map(dimension => dimension.id));
      fields.dimensions = Object.fromEntries(Object.entries(fields.dimensions).filter(([id]) => !shown.has(id)));
    }
    return { ...group, entries: reportDetailEntries(fields) };
  }).filter(group => group.entries.length);
}
function reportCollectionItems(report: Record<string, any> | null, key: string) {
  const value = report?.[key];
  const items: any[] = value === null || value === undefined || value === '' ? [] : Array.isArray(value) ? value : [value];
  // 字符串形式的关键问题若已作为 finding 的正文展示，无需再列一遍。
  const findingTexts = new Set(reportCollectionTexts(report?.findings));
  return items.map((item, index) => ({ item, index }))
      .filter(({ item }) => key !== 'critical_issues' || typeof item !== 'string' || !findingTexts.has(item.trim()))
      .map(({ item, index }) => {
        const object = item && typeof item === 'object' && !Array.isArray(item);
        const entries = object ? reportObjectEntries(item) : [{ key: 'value', label: '内容', value: formatCellValue(item) }];
        const title = object
            ? item.title || item.case_name || item.task || item.name || item.issue || item.description || item.suggestion || item.message
            : item;
        return { index, entries, title: formatCellValue(title ?? `第 ${index + 1} 条`) };
      });
}
function reportGroups(report: Record<string, any> | null, mode = '') {
  return REPORT_GROUPS.filter(group => group.key !== 'improvements' && !(['QUALITY', 'TRIGGER'].includes(mode) && group.key === 'results'))
      .map(group => ({ ...group, items: reportCollectionItems(report, group.key) })).filter(group => group.items.length);
}
function reportImprovementActions(report: Record<string, any> | null): string[] {
  const actions = [report?.improvements, report?.top3_improvements].flatMap(raw => {
    const items = Array.isArray(raw) ? raw : raw === null || raw === undefined ? [] : [raw];
    return items.map((item: any) => typeof item === 'string' ? item : isReportObject(item) ? item.action ?? item.suggestion ?? item.content ?? item.description : null);
  }).filter((action: any): action is string => typeof action === 'string' && !!action.trim()).map(action => action.trim());
  return [...new Set(actions)];
}
function reportCollectionTexts(raw: any): string[] {
  const items = Array.isArray(raw) ? raw : raw === null || raw === undefined ? [] : [raw];
  return items.flatMap(item => {
    if (typeof item === 'string') return [item.trim()];
    if (!isReportObject(item)) return [];
    return [item.message, item.issue, item.description, item.content].filter((text): text is string => typeof text === 'string').map(text => text.trim());
  });
}
interface SkillReportDimension {
  id: string;
  name: string;
  score: string;
  extra: SkillReportEntry[];
  raw: Record<string, any> | null;
}
function reportDimensions(report: Record<string, any> | null): SkillReportDimension[] {
  const raw = report?.dimensions ?? report?.dimension_scores ?? report?.scores ?? report?.criteria;
  const items: any[] = Array.isArray(raw) ? raw : raw && typeof raw === 'object'
      ? Object.entries(raw as Record<string, any>).map(([name, value]) => value && typeof value === 'object' && !Array.isArray(value) ? { ...value, id: value.id || name, name: value.name || name } : { id: name, name, value }) : [];
  return items.map(dimension => {
    if (!dimension || typeof dimension !== 'object' || Array.isArray(dimension)) {
      return { id: '', name: formatCellValue(dimension), score: '—', extra: [], raw: null };
    }
    const id = String(dimension.id || dimension.dimension || dimension.name || '');
    const scoringGuide = report?.metric_glossary?.dimensions?.[id];
    const rawScore = finiteScore(dimension.raw_score);
    const repeatedScore = rawScore !== null && rawScore === finiteScore(dimension.score ?? dimension.value);
    return {
      id: dimension.id || dimension.dimension || hasReportValue(scoringGuide) ? id : '',
      name: reportFieldLabel(String(dimension.name || dimension.dimension || dimension.label || dimension.title || '未命名维度')),
      score: dimension.max !== undefined || dimension.max_score !== undefined
          ? `${formatCellValue(dimension.score ?? dimension.value)} / ${formatCellValue(dimension.max ?? dimension.max_score)}` : formatCellValue(dimension.score ?? dimension.value),
      extra: [
        ...(hasReportValue(scoringGuide) ? [{ key: 'scoring_guide', label: '评分标准', value: formatCellValue(scoringGuide) }] : []),
        ...reportObjectEntries(dimension, ['id', 'name', 'dimension', 'label', 'title', 'score', 'value', 'max', 'max_score',
          ...(repeatedScore ? ['raw_score'] : []), 'top3_improvements', ...REPORT_GROUPS.map(group => group.key)]),
      ],
      raw: dimension,
    };
  });
}
function hasReportContent(report: Record<string, any> | null): boolean {
  return !!(reportSummaryEntries(report).length || reportExtraEntries(report).length || reportAdditionalEntries(report).length || reportSupplementSections(report).length || reportDimensions(report).length || reportGroups(report).length || reportImprovementActions(report).length || Array.isArray(report?.results));
}

function switchEvalTab(tab: EvalTab) {
  evalTab.value = tab;
  if (tab === 'skill') { void loadSkillModes(); void loadSkillResults(); }
  else { stopPollingSkillResults(); closeSkillDrawer(); loadEvalData(); }
}
const evalTaskNameError = computed<string>(() => {
  if (evalForm.taskType === 'skill') return '';
  const name = evalForm.taskName.trim();
  return name && evalRows.value.some(row => row.task_name === name) ? '该任务名称已存在，请重新输入' : '';
});
function openEvalModal() {
  if (skillSubmitting.value) return;
  pickerSession++; pickerRequest++; selectingAllSkills.value = false;
  evalForm.taskName = ''; evalForm.taskType = evalTab.value === 'skill' ? 'skill' : '';
  evalForm.taskSource = ''; evalForm.modes = new Set<string>(['baseline', 'full']); evalForm.hasReflow = false;
  skillForm.modes = new Set<string>(['STATIC']); skillForm.selected = new Set<string>(); skillForm.keyword = '';
  skillForm.creator = props.currentUserId || ''; skillForm.description = '';
  skillListPage.value = 1; evaluableSkills.value = []; skillListTotal.value = 0; skillListError.value = ''; skillSubmitError.value = '';
  evalModalVisible.value = true;
  if (evalTab.value === 'skill') { void loadSkillModes(); void loadEvaluableSkills(); }
}
function openSkillEvaluationFor(skill: SkillEvalSkillResult) {
  if (skillSubmitting.value || skill.skill_status !== '已完成') return;
  evalTab.value = 'skill'; openEvalModal(); skillForm.selected.add(skill.skill_id);
}
function closeEvalModal() {
  if (skillSubmitting.value) return;
  evalModalVisible.value = false; pickerSession++; pickerRequest++; selectingAllSkills.value = false;
}
function isModeChecked(key: string) {
  return evalForm.modes.has(key);
}
function toggleMode(key: string) {
  const k = key as 'init' | 'coreinsight' | 'corealm' | 'full';
  if (k === 'full') return;
  if (evalForm.modes.has(k)) evalForm.modes.delete(k);
  else evalForm.modes.add(k);
}
function submitEvalTask() {
  if (evalForm.taskType === 'skill') { void submitSkillEvaluation(); return; }
  // 任务名称必填 + 重复校验
  const taskName = evalForm.taskName.trim();
  if (!taskName) {
    alert('请输入任务名称');
    return;
  }
  if (evalTaskNameError.value) {
    alert(evalTaskNameError.value);
    return;
  }
  if (!evalForm.taskType) {
    alert('请选择任务类型');
    return;
  }
  const taskSource = evalForm.taskSource.trim();

  const modes = Array.from(evalForm.modes);
  // MR链接必填校验
  if (evalForm.taskType === 'code_gen' || evalForm.taskType === 'test_gen') {
    if (!taskSource) {
      alert('请填写MR链接');
      return;
    }
  }
  // 评测模式必选校验
  if (!modes.length) {
    alert('请至少选择一个评测模式');
    return;
  }
  kcService.createEvalTask({
    task_type: evalForm.taskType,
    trigger_mode: 'manual',
    task_name: taskName,
    task_source: taskSource || undefined,
    modes,
    dept_name: props.scope?.deptId || undefined,
    product_id: props.scope?.productId || undefined,
    pdu_name: props.scope?.pdu || undefined,
    has_reflow: evalForm.hasReflow ? 1 : 0,
    // creator 不传，由后端从请求 cookie 解析当前登录用户工号自动填充，兜底 "system"
  }).then(res => {
    evalModalVisible.value = false;
    // 新建后重置到第一页并重新加载列表
    evalPage.value = 1;
    evalJumpPage.value = 1;
    loadEvalData();
  }).catch(err => {
    console.error('新建评测任务失败', err);
    alert('新建评测任务失败：' + (err?.message || err));
  });
}

// ============== helpers ==============
function pct(v: number | null | undefined): string {
  if (v === null || v === undefined) return '—';
  return (v * 100).toFixed(1) + '%';
}
function fmtDur(sec: number | null | undefined): string {
  if (sec === null || sec === undefined) return '—';
  const m = Math.floor(sec / 60);
  const s = Math.round(sec % 60);
  return `${m}m${s.toString().padStart(2, '0')}s`;
}
function fmtToken(v: number | null | undefined): string {
  if (v === null || v === undefined) return '—';
  return (v / 1000).toFixed(1) + 'K';
}

// ============== 指标对比 ==============
function evalDiff(r: EvalRow, kind: MetricKind, scene: SceneKey): number {
  return r.metrics[scene][kind] - r.metrics.baseline[kind];
}
function isImprovement(kind: MetricKind, diff: number): boolean {
  if (kind === 'coverage') return diff > 0;
  return diff < 0;
}
function fmtDiff(kind: MetricKind, diff: number): string {
  if (kind === 'coverage') {
    const v = diff * 100;
    const sign = v > 0 ? '+' : '';
    return `${sign}${v.toFixed(1)}pp`;
  }
  if (kind === 'token') {
    const k = diff / 1000;
    const sign = k > 0 ? '+' : '';
    return `${sign}${k.toFixed(1)}K`;
  }
  const sign = diff > 0 ? '+' : '';
  return `${sign}${Math.round(diff)}s`;
}
function diffArrow(diff: number): string {
  if (diff > 0) return '▲';
  if (diff < 0) return '▼';
  return '–';
}

const evalRows = ref<EvalRow[]>([]);

// ============== 筛选 ==============
const evalFilter = reactive({ reqTitle: '', status: '', reflowStatus: '', creator: '' });

// ============== 分页 ==============
const evalPage = ref(1);
const evalPageSize = ref(10);
const evalTotal = ref(0);
const evalJumpPage = ref(1);
const evalTotalPages = computed(() => Math.max(1, Math.ceil(evalTotal.value / evalPageSize.value)));
const evalPageNumbers = computed<(number | string)[]>(() => {
  const total = evalTotalPages.value;
  const cur = evalPage.value;
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const pages: (number | string)[] = [1];
  if (cur > 4) pages.push('...');
  const start = Math.max(2, cur - 1);
  const end = Math.min(total - 1, cur + 1);
  for (let i = start; i <= end; i++) pages.push(i);
  if (cur < total - 3) pages.push('...');
  pages.push(total);
  return pages;
});

// ============== 后端数据转换 ==============
// 后端 metrics 为扁平数组 [{scene, metric_key, metric_value}]，coverage 存百分比数值；
// 前端 metrics 为嵌套对象 {scene: {coverage(0~1), token, duration}}
// 消融实验 5 个场景非必做，未做的场景后端不返回数据，此处用空对象填充并记录在 doneScenes 中。
function buildMetricsFromApi(apiMetrics: EvalMetricRow[] | undefined): EvalRow['metrics'] {
  const empty: EvalMetrics = { coverage: 0, token: 0, duration: 0 };
  const result: EvalRow['metrics'] = {
    baseline: { ...empty }, init: { ...empty }, coreinsight: { ...empty },
    corealm: { ...empty }, full: { ...empty }, improved: { ...empty },
  };
  if (!apiMetrics || !apiMetrics.length) return result;
  for (const m of apiMetrics) {
    const scene = m.scene as keyof EvalRow['metrics'];
    if (!result[scene]) continue;
    const key = m.metric_key;
    if (key !== 'coverage' && key !== 'token' && key !== 'duration') continue;
    let val = Number(m.metric_value) || 0;
    // coverage 后端存百分比(0~100)，前端用 0~1
    if (key === 'coverage') val = val / 100;
    result[scene][key] = val;
  }
  return result;
}

// 判断某场景是否已做（后端有返回数据）—— 后端未返回的场景视为"未评测"
function isSceneDone(row: EvalRow, scene: keyof EvalRow['metrics']): boolean {
  const m = row.metrics[scene];
  if (!m) return false;
  // 三个指标全为 0 视为未做（后端未返回该场景数据时 buildMetricsFromApi 填充为空对象）
  return m.coverage !== 0 || m.token !== 0 || m.duration !== 0;
}

function apiRowToLocal(api: ApiEvalRow): EvalRow {
  return {
    task_name: api.task_name,
    task_source: api.task_source,
    eval_type: api.eval_type,
    status: api.status,
    creator: api.creator,
    created_at: api.created_at,
    eval_duration: api.eval_duration ?? 0,
    reflow_duration: (api.reflow_duration ?? 0) as number,
    trigger_mode: (api.trigger_mode as 'auto' | 'manual') ?? 'manual',
    reflow_opinions: (api.reflow_opinions || []) as ReflowOpinion[],
    reflow_expect: (api.reflow_expect as EvalConclusion) ?? '',
    reflow_status: api.reflow_status,
    has_reflow: (api.has_reflow ?? 0) as number,
    metrics: buildMetricsFromApi(api.metrics),
    // 附加后端主键 id，供后续接口使用
    _id: api.id,
  } as EvalRow;
}

function avg(arr: number[]): number {
  if (!arr.length) return 0;
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

const evalSummary = computed<EvalSummary>(() => {
  const list = evalRows.value;
  const build = (l: EvalRow[]): EvalStageSummary => {
    if (!l.length) return { count: 0, avgCoverage: 0, coverageGain: 0, avgDuration: 0 };
    return {
      count: l.length,
      avgCoverage: avg(l.map(r => r.metrics.full.coverage)),
      coverageGain: avg(l.map(r => r.metrics.full.coverage - r.metrics.baseline.coverage)),
      avgDuration: avg(l.map(r => r.metrics.full.duration)),
    };
  };
  const stat = build(list);
  return { design: stat, develop: stat, test: stat };
});

// ============== 汇总区图表 ==============
const summaryMetric = ref<SummaryMetricKey>('coverage');

const SCENE_LABELS = ['无知识', '仅产品知识', '仅作业知识', '仅领域知识', '全量知识'];
const SCENE_KEYS: ('baseline' | 'init' | 'coreinsight' | 'corealm' | 'full')[] = ['baseline', 'coreinsight', 'init', 'corealm', 'full'];
const SCENE_COLORS = ['#b0b4bd', '#7c9ce8', '#7dcfb6', '#d4a3c4', '#7c9ce8'];

function avgMetricByScene(list: EvalRow[], kind: SummaryMetricKey, scene: 'baseline' | 'init' | 'coreinsight' | 'corealm' | 'full'): number {
  if (!list.length) return 0;
  return avg(list.map(r => r.metrics[scene][kind]));
}

function evalChartOption(stage: 'design' | 'develop' | 'test') {
  const list = evalRows.value;

  const kind = summaryMetric.value;
  const values = SCENE_KEYS.map(sc => avgMetricByScene(list, kind, sc));
  const baseline = values[0];

  const fmtValue = (v: number) => {
    if (kind === 'coverage') return (v * 100).toFixed(1) + '%';
    if (kind === 'token') return (v / 1000).toFixed(1) + 'K';
    const m = Math.floor(v / 60);
    const s = Math.round(v % 60);
    return `${m}m${s.toString().padStart(2, '0')}s`;
  };

  const fmtChange = (v: number, base: number) => {
    if (base === 0) return '';
    if (kind === 'coverage') {
      const diff = (v - base) * 100;
      const sign = diff > 0 ? '+' : '';
      return `${sign}${diff.toFixed(1)}pp`;
    }
    if (kind === 'token') {
      const diff = (v - base) / 1000;
      const sign = diff > 0 ? '+' : '';
      return `${sign}${diff.toFixed(1)}K`;
    }
    const diff = Math.round(v - base);
    const sign = diff > 0 ? '+' : '';
    return `${sign}${diff}s`;
  };

  const stageColor = stage === 'design' ? '#7c9ce8' : stage === 'develop' ? '#7dcfb6' : '#d4a3c4';

  return {
    grid: { left: 48, right: 16, top: 24, bottom: 28 },
    tooltip: {
      trigger: 'axis' as const,
      axisPointer: { type: 'shadow' as const },
      formatter: (params: any) => {
        const p = params[0];
        const i = p.dataIndex;
        if (p.value === 0) return `${p.name}<br/>无数据`;
        const base = values[0];
        if (i === 0) return `${p.name}<br/>${fmtValue(p.value)}`;
        const change = fmtChange(p.value, base);
        return `${p.name}<br/>${fmtValue(p.value)}${change ? '<br/>较无知识：' + change : ''}`;
      },
    },
    xAxis: {
      type: 'category' as const,
      data: SCENE_LABELS,
      axisLabel: { fontSize: 10, color: '#758095', interval: 0, rotate: 0 },
      axisLine: { lineStyle: { color: '#dfe4ed' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value' as const,
      axisLabel: {
        fontSize: 10,
        color: '#909399',
        formatter: (v: number) => {
          if (kind === 'coverage') return (v * 100).toFixed(0) + '%';
          if (kind === 'token') return (v / 1000).toFixed(0) + 'K';
          return Math.floor(v / 60) + 'm';
        },
      },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
    },
    series: [
      {
        type: 'bar' as const,
        data: values.map((v, i) => ({
          value: v,
          itemStyle: { color: v === 0 ? '#e8ebf0' : SCENE_COLORS[i], borderRadius: [4, 4, 0, 0] },
        })),
        barWidth: '52%',
        label: {
          show: true,
          position: 'top' as const,
          fontSize: 10,
          color: stageColor,
          formatter: (p: any) => {
            const i = p.dataIndex;
            if (p.value === 0) return '无数据';
            if (i === 0) return fmtValue(p.value);
            const change = fmtChange(p.value, baseline);
            return fmtValue(p.value) + (change ? '\n' + change : '');
          },
        },
      },
    ],
  };
}

function loadEvalData() {
  if (!scopeValid()) return;
  // 调用后端评测任务列表接口（按 scope 传 dept_name/product_id/pdu_name，含分页和筛选）
  kcService.getEvalTaskList({
    ...scopeFilterParams(),
    status: evalFilter.status || undefined,
    reflow_status: evalFilter.reflowStatus || undefined,
    keyword: evalFilter.reqTitle.trim() || undefined,
    creator: evalFilter.creator.trim() || undefined,
    page: evalPage.value,
    page_size: evalPageSize.value,
  }).then(res => {
    evalRows.value = (res.list || []).map(apiRowToLocal);
    evalTotal.value = res.total || 0;
    // 对 processing 状态的任务启动轮询
    startPollingProcessing();
  }).catch(err => {
    console.error('加载评测任务列表失败', err);
    evalRows.value = [];
    evalTotal.value = 0;
  });
}

// ============== processing 任务轮询 ==============
let pollTimer: ReturnType<typeof setInterval> | null = null;

function startPollingProcessing() {
  stopPollingProcessing();
  const hasProcessing = evalRows.value.some(r => r.status === 'processing');
  if (!hasProcessing) return;
  pollTimer = setInterval(() => {
    const processingRows = evalRows.value.filter(r => r.status === 'processing' && r._id);
    if (!processingRows.length) {
      stopPollingProcessing();
      return;
    }
    // 逐个查询详情，状态变更则更新
    processingRows.forEach(r => {
      if (!r._id) return;
      kcService.getEvalTaskDetail(r._id).then(detail => {
        if (detail.base_info.status !== 'processing') {
          const target = evalRows.value.find(e => e._id === r._id);
          if (target) {
            target.metrics = detail.metrics as EvalRow['metrics'];
            target.status = detail.base_info.status;
            target.eval_duration = detail.base_info.eval_duration ?? 0;
            target.reflow_duration = detail.base_info.reflow_duration ?? 0;
            target.trigger_mode = detail.base_info.trigger_mode;
          }
        }
      }).catch(() => { /* 忽略单条轮询失败 */ });
    });
  }, 5000);
}

function stopPollingProcessing() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

onBeforeUnmount(() => {
  skillDisposed = true; skillContext++; pickerSession++; pickerRequest++; skillAbort.abort();
  stopPollingProcessing(); stopPollingSkillResults();
});
watch(() => props.scope, () => {
  skillContext++; skillAbort.abort(); skillAbort = new AbortController(); stopPollingSkillResults();
  pickerSession++; pickerRequest++; selectingAllSkills.value = false; skillListLoading.value = false;
  evalModalVisible.value = false; skillForm.selected.clear(); evaluableSkills.value = []; skillListTotal.value = 0;
  closeSkillDrawer(); scopedSkillResults.value = []; skillResults.value = []; skillTotal.value = 0; skillResultsError.value = ''; skillResultsLoading.value = false;
  skillSubmission.value = null; skillObservationNotice.value = ''; Object.keys(pendingSkillObservations).forEach(id => delete pendingSkillObservations[id]);
  skillPage.value = 1; skillJumpPage.value = 1;
  if (scopeValid()) { evalPage.value = 1; evalJumpPage.value = 1; loadEvalData(); }
  else { stopPollingProcessing(); evalRows.value = []; evalTotal.value = 0; }
  if (evalTab.value === 'skill' && skillScopeValid()) { void loadSkillModes(); void loadSkillResults(); }
}, { immediate: true, deep: true });

// ============== 行点击打开侧边栏 ==============
const drawerVisible = ref(false);
const activeRow = ref<EvalRow | null>(null);
const reflowDetail = ref<EvalReflowDetail | null>(null);
type DrawerTab = 'detail' | 'reflow';
const drawerTab = ref<DrawerTab>('detail');
const drawerTabs: { key: DrawerTab; label: string }[] = [
  { key: 'detail', label: '知识评测' },
  { key: 'reflow', label: '知识回流' },
];

function openDrawer(r: EvalRow) {
  activeRow.value = r;
  drawerTab.value = 'detail';
  drawerVisible.value = true;
  reflowDetail.value = null;
  // 加载主表详情（补全 metrics）
  if (r._id) {
    kcService.getEvalTaskDetail(r._id).then(detail => {
      if (activeRow.value && activeRow.value._id === r._id) {
        // taskDetail 返回 {base_info, metrics}，直接映射到 activeRow
        const bi = detail.base_info;
        activeRow.value.metrics = detail.metrics as EvalRow['metrics'];
        activeRow.value.eval_duration = bi.eval_duration ?? 0;
        activeRow.value.reflow_duration = bi.reflow_duration ?? 0;
        activeRow.value.status = bi.status;
        activeRow.value.trigger_mode = bi.trigger_mode;
        // 同步回列表
        const target = evalRows.value.find(e => e._id === r._id);
        if (target) Object.assign(target, activeRow.value);
      }
    }).catch(err => console.error('加载评测详情失败', err));
    // 加载回流详情
    kcService.getEvalTaskReflow(r._id).then(detail => {
      reflowDetail.value = detail;
      // 回填 reflow_opinions 到 activeRow
      if (activeRow.value && activeRow.value._id === r._id) {
        activeRow.value.reflow_opinions = detail.reflow_opinions || [];
      }
    }).catch(err => console.error('加载回流详情失败', err));
  }
}
function closeDrawer() {
  drawerVisible.value = false;
  activeRow.value = null;
  reflowDetail.value = null;
}

// ---- GitHub 风格 diff 渲染 ----
type DiffRowType = 'context' | 'add' | 'del' | 'hunk' | 'meta';
interface DiffRow {
  leftNum: number | null;
  rightNum: number | null;
  type: DiffRowType;
  leftContent: string;
  rightContent: string;
}
interface DiffFile {
  oldName: string;
  newName: string;
  rows: DiffRow[];
}
function parseUnifiedDiff(diffText: string): DiffFile[] {
  const files: DiffFile[] = [];
  const lines = diffText.split('\n');
  let cur: DiffFile | null = null;
  let leftNum = 0;
  let rightNum = 0;
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    // 文件头
    if (line.startsWith('--- ')) {
      const newName = (lines[i + 1] || '').startsWith('+++ ') ? lines[i + 1].slice(4).trim() : '';
      cur = { oldName: line.slice(4).trim(), newName: newName.replace(/^b\//, ''), rows: [] };
      files.push(cur);
      i += 2;
      continue;
    }
    if (!cur) {
      // 没有 --- /+++ 头，把整段当作单文件
      cur = { oldName: '', newName: '', rows: [] };
      files.push(cur);
    }
    // hunk 头
    const hunkMatch = line.match(/^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
    if (hunkMatch) {
      leftNum = parseInt(hunkMatch[1], 10);
      rightNum = parseInt(hunkMatch[2], 10);
      cur.rows.push({ leftNum: null, rightNum: null, type: 'hunk', leftContent: line, rightContent: line });
      i++;
      continue;
    }
    if (line.startsWith('-')) {
      cur.rows.push({ leftNum: leftNum++, rightNum: null, type: 'del', leftContent: line.slice(1), rightContent: '' });
    } else if (line.startsWith('+')) {
      cur.rows.push({ leftNum: null, rightNum: rightNum++, type: 'add', leftContent: '', rightContent: line.slice(1) });
    } else if (line.startsWith(' ')) {
      cur.rows.push({ leftNum: leftNum++, rightNum: rightNum++, type: 'context', leftContent: line.slice(1), rightContent: line.slice(1) });
    } else {
      // 空行或其他
      cur.rows.push({ leftNum: leftNum++, rightNum: rightNum++, type: 'context', leftContent: line, rightContent: line });
    }
    i++;
  }
  return files;
}
function getDiffRows(diffText: string): DiffRow[] {
  const files = parseUnifiedDiff(diffText);
  const rows: DiffRow[] = [];
  files.forEach((f, fi) => {
    if (fi > 0) rows.push({ leftNum: null, rightNum: null, type: 'meta', leftContent: '', rightContent: '' });
    if (f.newName) {
      rows.push({ leftNum: null, rightNum: null, type: 'meta', leftContent: '', rightContent: f.newName });
    }
    rows.push(...f.rows);
  });
  return rows;
}

// 标记回流完成 / 拒绝回流：调用后端接口同步更新
function markReflowDone() {
  const r = activeRow.value;
  if (!r || !r._id || r.reflow_status === 'done' || r.reflow_status === 'ignored') return;
  kcService.markEvalReflowDone(r._id).then(() => {
    r.reflow_status = 'done';
    const target = evalRows.value.find(e => e._id === r._id);
    if (target) {
      target.reflow_status = 'done';
    }
  }).catch(err => {
    console.error('标记回流完成失败', err);
    alert('标记回流完成失败：' + (err?.message || err));
  });
}
function rejectReflow() {
  const r = activeRow.value;
  if (!r || !r._id || r.reflow_status === 'done' || r.reflow_status === 'ignored') return;
  kcService.rejectEvalReflow(r._id).then(() => {
    r.reflow_status = 'ignored';
    const target = evalRows.value.find(e => e._id === r._id);
    if (target) target.reflow_status = 'ignored';
  }).catch(err => {
    console.error('拒绝回流失败', err);
    alert('拒绝回流失败：' + (err?.message || err));
  });
}

// ---- 完整详情数据（基于 activeRow + 后端回流详情）----
interface DrawerDiffSuggestion {
  file_name: string;
  change_desc: string;
  diff: string;
  // 知识改进建议明细（report 表格形式）
  knowledge_id?: string;
  knowledge_name?: string;
  source?: string;
  suggestion?: string;
  uri?: string;
  problem_category?: string;  // 知识问题分类
  // 详情弹窗字段
  is_gap?: boolean;
  original_content?: string;
  improved_content?: string;
  content_summary?: string;
  reason?: string;
  remediation?: string;
  triage_reason?: string;
}

// 知识详情弹窗
const sugDetailVisible = ref(false);
const activeSugDetail = ref<DrawerDiffSuggestion | null>(null);
function openSugDetail(s: DrawerDiffSuggestion) {
  activeSugDetail.value = s;
  sugDetailVisible.value = true;
}
function closeSugDetail() {
  sugDetailVisible.value = false;
  activeSugDetail.value = null;
}

// 功能覆盖率详情弹窗
const coverageDetailVisible = ref(false);
const activeCoverageDetail = ref<{
  title: string;
  detail: CoverageDetail | null;
} | null>(null);
function openCoverageDetail(title: string, detail: CoverageDetail | null | undefined) {
  if (!detail) return;
  const hasFeatures = (detail.features && detail.features.length) || (detail.hunk_features && detail.hunk_features.length);
  if (!hasFeatures) return;
  activeCoverageDetail.value = { title, detail };
  coverageDetailVisible.value = true;
}

// 功能覆盖率计算：features得分总和/features总数*0.7 + hunk_features得分总和/hunk_features总数*0.3
function computeCoverage(detail: CoverageDetail | null | undefined): number {
  if (!detail) return 0;
  const f = detail.features || [];
  const h = detail.hunk_features || [];
  const fTotal = f.length;
  const hTotal = h.length;
  const fSum = f.reduce((s, it) => s + (Number(it.score) || 0), 0);
  const hSum = h.reduce((s, it) => s + (Number(it.score) || 0), 0);
  let val = 0;
  if (fTotal > 0) val += (fSum / fTotal) * 0.7;
  if (hTotal > 0) val += (hSum / hTotal) * 0.3;
  return val;
}
function coveragePercent(detail: CoverageDetail | null | undefined): string {
  return (computeCoverage(detail) * 100).toFixed(1) + '%';
}
// 得分等级：0 → red / 0.5 → yellow / 1 → green，其它值就近映射
function scoreLevel(score: number | string | undefined): 'red' | 'yellow' | 'green' {
  const s = Number(score);
  if (!Number.isFinite(s)) return 'red';
  if (s <= 0) return 'red';
  if (s < 1) return 'yellow';
  return 'green';
}
function scoreLabel(score: number | string | undefined): string {
  return Number(score || 0).toFixed(2);
}
// 覆盖率计算过程聚合数据
function coverageCalcParts(detail: CoverageDetail | null | undefined) {
  const f = detail?.features || [];
  const h = detail?.hunk_features || [];
  const fSum = f.reduce((s, it) => s + (Number(it.score) || 0), 0);
  const hSum = h.reduce((s, it) => s + (Number(it.score) || 0), 0);
  const fTotal = f.length;
  const hTotal = h.length;
  const fAvg = fTotal > 0 ? fSum / fTotal : 0;
  const hAvg = hTotal > 0 ? hSum / hTotal : 0;
  const fPart = fTotal > 0 ? fAvg * 0.7 : 0;
  const hPart = hTotal > 0 ? hAvg * 0.3 : 0;
  return { fSum, hSum, fTotal, hTotal, fAvg, hAvg, fPart, hPart };
}
function closeCoverageDetail() {
  coverageDetailVisible.value = false;
  activeCoverageDetail.value = null;
}

const drawerSuggestions = computed<DrawerDiffSuggestion[]>(() => {
  const r = activeRow.value;
  if (!r) return [];
  // 优先使用后端回流详情中的非代码仓建议
  const rd = reflowDetail.value;
  if (rd && rd.non_repo_reflow && rd.non_repo_reflow.suggestions && rd.non_repo_reflow.suggestions.length) {
    return rd.non_repo_reflow.suggestions.map(s => ({
      file_name: s.knowledge_name || s.knowledge_id || '-',
      knowledge_id: s.knowledge_id,
      knowledge_name: s.knowledge_name,
      source: s.source,
      suggestion: s.suggestion,
      uri: s.uri,
      problem_category: s.problem_category,
      is_gap: s.is_gap,
      original_content: s.original_content,
      improved_content: s.improved_content,
      content_summary: s.content_summary,
      reason: s.reason,
      remediation: s.remediation,
      triage_reason: s.triage_reason,
      change_desc: '',
      diff: '',
    }));
  }
  return [];
});

// 代码仓知识改进建议（diff 卡片形式）
const drawerRepoSuggestions = computed<DrawerDiffSuggestion[]>(() => {
  const r = activeRow.value;
  if (!r) return [];
  // 优先使用后端回流详情中的代码仓建议
  const rd = reflowDetail.value;
  if (rd && rd.repo_reflow && rd.repo_reflow.suggestions && rd.repo_reflow.suggestions.length) {
    return rd.repo_reflow.suggestions.map(s => ({
      file_name: s.file_name,
      change_desc: s.change_desc,
      diff: s.diff,
    }));
  }
  return [];
});


// 评测追溯链 - 知识回流MR
type ReflowMRStatus = 'merged' | 'open' | 'closed';
interface DrawerReflowMR {
  title: string;
  url: string;
  status: ReflowMRStatus;
  desc: string;
}
const drawerReflowMRs = computed<DrawerReflowMR[]>(() => {
  const r = activeRow.value;
  if (!r) return [];
  // 优先使用后端回流详情中的 reflow_mr
  const rd = reflowDetail.value;
  if (rd && rd.repo_reflow && rd.repo_reflow.reflow_mr) {
    return [{
      title: rd.repo_reflow.reflow_mr.title,
      url: rd.repo_reflow.reflow_mr.url,
      status: rd.repo_reflow.reflow_mr.status,
      desc: rd.repo_reflow.reflow_mr.desc,
    }];
  }
  return [];
});
function mrStatusLabel(s: ReflowMRStatus): string {
  return s === 'merged' ? '已合入' : s === 'open' ? '待合入' : '已关闭';
}

const drawerEffectMetrics = computed(() => {
  const r = activeRow.value;
  if (!r || !r.metrics) return [];
  const m = r.metrics;
  const pctFmt = (v: number) => (v * 100).toFixed(1) + '%';
  const tokFmt = (v: number) => Math.round(v) + '';
  const durFmt = (v: number) => v.toFixed(1) + 's';
  return [
    {
      key: 'coverage', label: '功能覆盖率', fmt: pctFmt,
      values: {
        baseline: m.baseline?.coverage ?? 0,
        init: m.init?.coverage ?? 0,
        coreinsight: m.coreinsight?.coverage ?? 0,
        corealm: m.corealm?.coverage ?? 0,
        full: m.full?.coverage ?? 0,
        improved: m.improved?.coverage ?? 0,
      },
    },
    {
      key: 'token', label: 'Token消耗', fmt: tokFmt,
      values: {
        baseline: m.baseline?.token ?? 0,
        init: m.init?.token ?? 0,
        coreinsight: m.coreinsight?.token ?? 0,
        corealm: m.corealm?.token ?? 0,
        full: m.full?.token ?? 0,
        improved: m.improved?.token ?? 0,
      },
    },
    {
      key: 'duration', label: '完成时长', fmt: durFmt,
      values: {
        baseline: m.baseline?.duration ?? 0,
        init: m.init?.duration ?? 0,
        coreinsight: m.coreinsight?.duration ?? 0,
        corealm: m.corealm?.duration ?? 0,
        full: m.full?.duration ?? 0,
        improved: m.improved?.duration ?? 0,
      },
    },
  ];
});

// 改进效果对比：知识改进前 = 全量知识(full)场景，知识改进后 = improved场景
// 复用 metrics.full / metrics.improved，无需独立 mock 数据
const drawerEffectCompare = computed(() => {
  const r = activeRow.value;
  if (!r) return [];
  // 优先使用后端回流详情中的 effect_compare
  const rd = reflowDetail.value;
  if (rd && rd.repo_reflow && rd.repo_reflow.effect_compare && rd.repo_reflow.effect_compare.length) {
    return rd.repo_reflow.effect_compare.map(item => {
      const key = item.metric_key as 'coverage' | 'token' | 'duration';
      let fmt: (v: number) => string;
      if (key === 'coverage') fmt = (v: number) => v.toFixed(2) + '%';
      else if (key === 'token') fmt = (v: number) => v.toLocaleString('en-US', { maximumFractionDigits: 0 });
      else fmt = (v: number) => v.toFixed(0) + 's';
      return {
        key,
        label: item.metric_label,
        before: item.before_val,
        after: item.after_val,
        fmt,
        before_coverage_detail: item.before_coverage_detail,
        after_coverage_detail: item.after_coverage_detail,
      };
    });
  }
  const before = r.metrics.full;
  const after = r.metrics.improved;
  if (!before || !after) return [];
  return [
    {
      key: 'coverage' as const,
      label: '功能覆盖率',
      before: Number((before.coverage * 100).toFixed(2)),
      after: Number((after.coverage * 100).toFixed(2)),
      fmt: (v: number) => v.toFixed(2) + '%',
      before_coverage_detail: before.coverage_detail || null,
      after_coverage_detail: after.coverage_detail || null,
    },
    {
      key: 'token' as const,
      label: 'Token消耗',
      before: before.token,
      after: after.token,
      fmt: (v: number) => v.toLocaleString('en-US', { maximumFractionDigits: 0 }),
      before_coverage_detail: null,
      after_coverage_detail: null,
    },
    {
      key: 'duration' as const,
      label: '完成时长',
      before: before.duration,
      after: after.duration,
      fmt: (v: number) => v.toFixed(0) + 's',
      before_coverage_detail: null,
      after_coverage_detail: null,
    },
  ];
});

// 改进效果对比柱状图：按指标拆成多张图，每张图一个指标（知识改进前/后）
// 每个指标量纲独立，单 y 轴标注真实单位
const EFFECT_CHART_META: { key: 'coverage' | 'token' | 'duration'; color: string; yName: string; yFmt: (v: number) => string }[] = [
  { key: 'coverage', color: '#7c9ce8', yName: '覆盖率', yFmt: (v: number) => v.toFixed(0) + '%' },
  { key: 'token', color: '#7dcfb6', yName: 'Token', yFmt: (v: number) => (v / 1000).toFixed(0) + 'K' },
  { key: 'duration', color: '#f0b97d', yName: '时长', yFmt: (v: number) => Math.floor(v / 60) + 'm' },
];
const drawerEffectCharts = computed(() => {
  const rows = drawerEffectCompare.value;
  const categories = ['知识改进前', '知识改进后'];
  return EFFECT_CHART_META.map(meta => {
    const row = rows.find(r => r.key === meta.key);
    return {
      key: meta.key,
      label: row?.label || meta.key,
      option: {
        title: { text: row?.label || meta.key, left: 'center', top: 0, textStyle: { fontSize: 12, fontWeight: 600, color: '#1b2334' } },
        tooltip: {
          trigger: 'axis' as const,
          axisPointer: { type: 'shadow' as const },
          formatter: (params: any[]) => {
            const idx = params[0].dataIndex;
            const val = row ? (idx === 0 ? row.before : row.after) : 0;
            return `${params[0].name}<br/>${params[0].marker}${row?.label || ''}: ${row ? row.fmt(val) : '—'}`;
          },
        },
        grid: { left: 48, right: 16, top: 30, bottom: 24 },
        xAxis: { type: 'category' as const, data: categories, axisLabel: { fontSize: 11 } },
        yAxis: {
          type: 'value' as const, name: meta.yName,
          nameTextStyle: { fontSize: 10, color: meta.color },
          axisLabel: { fontSize: 10, color: meta.color, formatter: meta.yFmt },
          splitLine: { lineStyle: { color: '#f0f2f5' } },
        },
        series: [
          {
            name: row?.label || meta.key, type: 'bar' as const, barWidth: '40%',
            data: row ? [row.before, row.after] : [0, 0],
            itemStyle: { color: meta.color, borderRadius: [3, 3, 0, 0] },
            label: {
              show: true, position: 'top' as const, fontSize: 10, color: '#5f6b80',
              formatter: (p: any) => row ? row.fmt(p.value) : '',
            },
          },
        ],
      },
    };
  });
});

const SCENE_LABELS_FULL: { key: 'baseline' | 'init' | 'coreinsight' | 'corealm' | 'full'; label: string }[] = [
  { key: 'baseline', label: '无知识' },
  { key: 'coreinsight', label: '仅产品知识' },
  { key: 'init', label: '仅作业知识' },
  { key: 'corealm', label: '仅领域知识' },
  { key: 'full', label: '全量知识' },
];
const drawerMetricRows = computed(() => {
  const r = activeRow.value;
  if (!r) return [];
  return SCENE_LABELS_FULL.map(s => ({
    key: s.key,
    label: s.label,
    metrics: r.metrics[s.key],
    done: isSceneDone(r, s.key),
  }));
});

// 评测指标柱状图：按指标拆成多张图，每张图一个指标（按场景分组）
// 每个指标量纲独立，单 y 轴标注真实单位；仅展示已评测的场景
const METRIC_CHART_META: { key: 'coverage' | 'token' | 'duration'; label: string; color: string; yName: string; yFmt: (v: number) => string; fmt: (v: number) => string }[] = [
  { key: 'coverage', label: '功能覆盖率', color: '#7c9ce8', yName: '覆盖率', yFmt: (v: number) => v.toFixed(0) + '%', fmt: (v: number) => (v * 100).toFixed(1) + '%' },
  { key: 'token', label: 'Token消耗', color: '#7dcfb6', yName: 'Token', yFmt: (v: number) => (v / 1000).toFixed(0) + 'K', fmt: (v: number) => v.toLocaleString('en-US', { maximumFractionDigits: 0 }) },
  { key: 'duration', label: '完成时长', color: '#f0b97d', yName: '时长', yFmt: (v: number) => Math.floor(v / 60) + 'm', fmt: (v: number) => { const m = Math.floor(v / 60), s = Math.round(v % 60); return `${m}m${s.toString().padStart(2, '0')}s`; } },
];
const drawerMetricCharts = computed(() => {
  const rows = drawerMetricRows.value.filter(s => s.done);
  const categories = rows.map(s => s.label);
  return METRIC_CHART_META.map(meta => ({
    key: meta.key,
    label: meta.label,
    option: {
      title: { text: meta.label, left: 'center', top: 0, textStyle: { fontSize: 12, fontWeight: 600, color: '#1b2334' } },
      tooltip: {
        trigger: 'axis' as const,
        axisPointer: { type: 'shadow' as const },
        formatter: (params: any[]) => {
          const r = rows[params[0].dataIndex];
          if (!r) return params[0].name;
          return `${params[0].name}<br/>${params[0].marker}${meta.label}: ${meta.fmt(r.metrics[meta.key])}`;
        },
      },
      grid: { left: 48, right: 16, top: 30, bottom: 24 },
      xAxis: { type: 'category' as const, data: categories, axisLabel: { fontSize: 10, interval: 0, rotate: 0 } },
      yAxis: {
        type: 'value' as const, name: meta.yName,
        nameTextStyle: { fontSize: 10, color: meta.color },
        axisLabel: { fontSize: 10, color: meta.color, formatter: meta.yFmt },
        splitLine: { lineStyle: { color: '#f0f2f5' } },
      },
      series: [
        {
          name: meta.label, type: 'bar' as const, barWidth: '40%',
          data: rows.map(s => meta.key === 'coverage' ? Number((s.metrics.coverage * 100).toFixed(2)) : s.metrics[meta.key]),
          itemStyle: { color: meta.color, borderRadius: [3, 3, 0, 0] },
          label: {
            show: true, position: 'top' as const, fontSize: 10, color: '#5f6b80',
            formatter: (p: any) => {
              const r = rows[p.dataIndex];
              return r ? meta.fmt(r.metrics[meta.key]) : '';
            },
          },
        },
      ],
    },
  }));
});

// ============== 评测主题标签 ===============
const evalThemeLabel: Record<EvalType, string> = {
  code_gen: '代码生成场景',
  test_gen: '测试生成场景',
  skill: 'Skill评测',
};
const reflowStatusLabel: Record<ReflowStatus, string> = {
  pending: '待回流',
  processing: '回流中',
  done: '已回流',
  ignored: '已忽略',
};

function clearEvalFilter() {
  evalFilter.reqTitle = '';
  evalFilter.status = '';
  evalFilter.reflowStatus = '';
  evalFilter.creator = '';
  evalPage.value = 1;
  evalJumpPage.value = 1;
  loadEvalData();
}
function goToPage(p: number | string) {
  const n = Number(p);
  if (!n || n < 1 || n > evalTotalPages.value || n === evalPage.value) return;
  evalPage.value = n;
  evalJumpPage.value = n;
  loadEvalData();
}
function onPageSizeChange() {
  evalPage.value = 1;
  evalJumpPage.value = 1;
  loadEvalData();
}
function onFilterChange() {
  evalPage.value = 1;
  evalJumpPage.value = 1;
  loadEvalData();
}

const filteredEvalRows = computed<EvalRow[]>(() => {
  return evalRows.value.slice();
});
</script>
