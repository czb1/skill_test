<template>
  <div class="kg-eval">
    <template v-if="scopeValid()">
      <!-- 三阶段评测汇总（已隐藏）-->
      <section class="section" v-if="false">
        <h2 class="section-title">知识评测汇总</h2>
        <div class="eval-summary-cards">
          <div class="eval-summary-card design">
            <div class="es-head">
              <span class="es-tag">设计阶段</span>
              <span class="es-count">{{ evalSummary.design.count }} 次评测</span>
            </div>
            <div class="es-chart-tabs">
              <button :class="{ active: summaryMetric === 'coverage' }" @click="summaryMetric = 'coverage'">功能覆盖率</button>
              <button :class="{ active: summaryMetric === 'token' }" @click="summaryMetric = 'token'">Token消耗</button>
              <button :class="{ active: summaryMetric === 'duration' }" @click="summaryMetric = 'duration'">完成时长</button>
            </div>
            <v-chart class="es-chart" :option="evalChartOption('design')" autoresize />
          </div>
          <div class="eval-summary-card develop">
            <div class="es-head">
              <span class="es-tag">开发阶段</span>
              <span class="es-count">{{ evalSummary.develop.count }} 次评测</span>
            </div>
            <div class="es-chart-tabs">
              <button :class="{ active: summaryMetric === 'coverage' }" @click="summaryMetric = 'coverage'">功能覆盖率</button>
              <button :class="{ active: summaryMetric === 'token' }" @click="summaryMetric = 'token'">Token消耗</button>
              <button :class="{ active: summaryMetric === 'duration' }" @click="summaryMetric = 'duration'">完成时长</button>
            </div>
            <v-chart class="es-chart" :option="evalChartOption('develop')" autoresize />
          </div>
          <div class="eval-summary-card test">
            <div class="es-head">
              <span class="es-tag">测试阶段</span>
              <span class="es-count">{{ evalSummary.test.count }} 次评测</span>
            </div>
            <div class="es-chart-tabs">
              <button :class="{ active: summaryMetric === 'coverage' }" @click="summaryMetric = 'coverage'">功能覆盖率</button>
              <button :class="{ active: summaryMetric === 'token' }" @click="summaryMetric = 'token'">Token消耗</button>
              <button :class="{ active: summaryMetric === 'duration' }" @click="summaryMetric = 'duration'">完成时长</button>
            </div>
            <v-chart class="es-chart" :option="evalChartOption('test')" autoresize />
          </div>
        </div>
      </section>

      <!-- 评测明细表 -->
      <section class="section content-section eval-detail-section">
        <div class="content-head">
          <div class="eval-head-left">
            <h2>知识评测与回流</h2>
            <div class="eval-scene-tabs">
              <button :class="{ active: evalTab === 'knowledge' }" @click="switchEvalTab('knowledge')">知识增益评测</button>
              <button :class="{ active: evalTab === 'skill' }" @click="switchEvalTab('skill')">Skill 评测</button>
            </div>
          </div>
          <button class="eval-new-btn" :disabled="skillSubmitting" @click="openEvalModal">
            {{ evalTab === 'skill' ? '+ 发起 Skill 评测' : '+ 新建评测任务' }}
          </button>
        </div>

        <!-- ===== 知识增益评测 ===== -->
        <template v-if="evalTab === 'knowledge'">
          <!-- 筛选行 -->
          <div class="eval-filters">
            <div class="eval-filter-field">
              <span>评测任务</span>
              <input v-model="evalFilter.reqTitle" placeholder="筛选评测任务" @keyup.enter="onFilterChange" />
            </div>
            <div class="eval-filter-field">
              <span>任务状态</span>
              <select v-model="evalFilter.status" @change="onFilterChange">
                <option value="">全部</option>
                <option value="done">已完成</option>
                <option value="processing">进行中</option>
                <option value="failed">失败</option>
              </select>
            </div>
            <div class="eval-filter-field">
              <span>回流状态</span>
              <select v-model="evalFilter.reflowStatus" @change="onFilterChange">
                <option value="">全部</option>
                <option value="pending">待回流</option>
                <option value="processing">回流中</option>
                <option value="done">已回流</option>
                <option value="ignored">已忽略</option>
              </select>
            </div>
            <div class="eval-filter-field">
              <span>创建人</span>
              <input v-model="evalFilter.creator" placeholder="按创建人筛选" @keyup.enter="onFilterChange" />
            </div>
            <button v-if="evalFilter.reqTitle || evalFilter.status || evalFilter.reflowStatus || evalFilter.creator" class="eval-filter-clear" @click="clearEvalFilter">清除</button>
          </div>

          <div class="table-wrap" v-if="filteredEvalRows.length">
            <table class="asset-table eval-table" v-col-resize data-col-resize-key="kg-eval">
              <colgroup>
                <col class="eval-col-req-title" />
                <col class="eval-col-eval-type" />
                <col class="eval-col-task-type" />
                <col class="eval-col-status" />
                <col class="eval-col-duration" />
                <col class="eval-col-creator" />
                <col class="eval-col-created-at" />
                <col class="eval-col-gov-expect" />
                <col class="eval-col-gov-status" />
              </colgroup>
              <thead class="asset-table-head">
              <tr>
                <th class="th-filter">评测任务</th>
                <th class="th-filter">场景</th>
                <th class="th-filter">任务类型</th>
                <th class="th-filter">任务状态</th>
                <th class="th-filter">耗时</th>
                <th class="th-filter">创建人</th>
                <th class="th-filter">创建时间</th>
                <th class="th-filter">回流预期</th>
                <th class="th-filter">回流状态</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="(r, idx) in filteredEvalRows" :key="idx" class="hierarchy-row hierarchy-row-product clickable-row" :class="{ 'row-active': activeRow === r }" @click="openDrawer(r)">
                <td class="eval-req-title">
                  <a class="eval-obj-link" :href="r.task_source" target="_blank" rel="noopener" :title="r.task_source" @click.stop>{{ r.task_name }}</a>
                </td>
                <td>{{ evalThemeLabel[r.eval_type] }}</td>
                <td>
                  <span class="task-type-tag tag-eval">评测任务</span>
                  <span v-if="r.has_reflow" class="task-type-tag tag-reflow">回流任务</span>
                </td>
                <td><span class="status-pill" :class="r.status">{{ r.status === 'done' ? '已完成' : r.status === 'processing' ? '进行中' : '失败' }}</span></td>
                <td class="eval-duration">{{ r.status === 'done' ? fmtDur(r.eval_duration) : '—' }}</td>
                <td class="eval-creator">{{ r.creator }}</td>
                <td class="eval-created-at">{{ r.created_at }}</td>
                <td>
                  <span v-if="r.reflow_expect" class="conclusion-pill" :class="r.reflow_expect">{{ r.reflow_expect === 'up' ? '效果上升' : '效果下降' }}</span>
                  <span v-else>—</span>
                </td>
                <td><span class="gov-status-pill" :class="r.reflow_status">{{ reflowStatusLabel[r.reflow_status] }}</span></td>
              </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty-text">该部门暂无评测数据。</p>

          <!-- 分页 -->
          <div v-if="evalTotal > 0" class="eval-pagination">
            <div class="eval-page-size">
              每页
              <select v-model.number="evalPageSize" @change="onPageSizeChange">
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
              </select>
              条
            </div>
            <div class="eval-page-info">共 {{ evalTotal }} 条</div>
            <div class="eval-page-nav">
              <button :disabled="evalPage <= 1" @click="goToPage(evalPage - 1)">上一页</button>
              <template v-for="p in evalPageNumbers" :key="p">
                <span v-if="p === '...'" class="eval-page-ellipsis">…</span>
                <button v-else :class="{ active: p === evalPage }" @click="goToPage(p)">{{ p }}</button>
              </template>
              <button :disabled="evalPage >= evalTotalPages" @click="goToPage(evalPage + 1)">下一页</button>
            </div>
            <div class="eval-page-jump">
              跳至
              <input type="number" min="1" :max="evalTotalPages" v-model.number="evalJumpPage" @keyup.enter="goToPage(evalJumpPage)" />
              页
            </div>
          </div>
        </template>

        <!-- ===== Skill 评测：以 Skill 为单位 ===== -->
        <template v-else>
          <div class="eval-filters">
            <div class="eval-filter-field"><span>Skill 名称 / 描述</span><input v-model="skillFilter.keyword" placeholder="搜索当前范围的 Skill" @keyup.enter="onSkillFilterChange" /></div>
            <button class="eval-filter-clear" @click="onSkillFilterChange">搜索</button>
            <button v-if="skillFilter.keyword" class="eval-filter-clear" @click="clearSkillFilter">清除</button>
            <button class="eval-filter-clear" :disabled="skillResultsLoading" @click="loadSkillResults()">{{ skillResultsLoading ? '刷新中…' : '刷新结果' }}</button>
            <span class="skill-list-hint">仅展示评测中或已有报告的 Skill</span>
          </div>
          <p v-if="!skillScopeValid()" class="skill-state">请先选择有效的部门、产品或 PDU。</p>
          <p v-if="skillObservationNotice" class="skill-report-notice">{{ skillObservationNotice }}</p>
          <div v-if="skillSubmission" class="skill-submission-notice" role="status">
            <strong>已确认提交 {{ skillSubmission.submitted_count }} / {{ skillSubmission.total_count }} 项</strong>
            <span v-if="skillSubmission.unconfirmed_count">，{{ skillSubmission.unconfirmed_count }} 项未确认。请先刷新结果，再决定是否重试。</span>
            <span v-else>，结果会自动刷新。</span>
            <details v-if="submissionIssues.length"><summary>查看未确认项</summary><p v-for="item in submissionIssues" :key="item.key">{{ item.name }} · {{ skillModeLabel(item.mode) }}：{{ item.error }}</p></details>
            <p v-if="Object.keys(pendingSkillObservations).length">正在等待所选模式的新记录或报告；新记录出现前仍可能显示上次结果。</p>
            <button type="button" class="skill-text-button" @click="skillSubmission = null">收起提示</button>
          </div>
          <div v-if="skillResultsError" class="skill-state skill-state--error" role="alert">{{ skillResultsError }} <button class="skill-text-button" :disabled="skillResultsLoading" @click="loadSkillResults()">重试</button></div>
          <p v-if="skillResultsLoading && !skillResults.length" class="empty-text" role="status">正在加载 Skill…</p>
          <div v-if="skillResults.length" class="table-wrap" :aria-busy="skillResultsLoading">
            <table class="asset-table eval-table skill-results-table" v-col-resize data-col-resize-key="kg-skill-results-v2">
              <colgroup><col style="width:24%" /><col v-for="key in SKILL_MODE_KEYS" :key="key" style="width:21%" /><col style="width:13%" /></colgroup>
              <thead class="asset-table-head"><tr><th>Skill</th><th v-for="key in SKILL_MODE_KEYS" :key="key">{{ skillModeLabel(key) }}</th><th>操作</th></tr></thead>
              <tbody><tr v-for="skill in skillResults" :key="skill.skill_id" class="hierarchy-row hierarchy-row-product clickable-row" :class="{ 'row-active': activeSkill?.skill_id === skill.skill_id }" @click="openSkillDrawer(skill)">
                <td><button class="skill-name-link" @click.stop="openSkillDrawer(skill)">{{ skill.skill_name || skill.name || '未命名 Skill' }}</button><div class="skill-directory-meta"><span>目录版本 {{ skill.version || '—' }}</span><span>Skill 状态：{{ skill.skill_status || '—' }}</span></div><p v-if="hasSkillMatchError(skill)" class="skill-match-error">{{ skill.match_error || '评测记录关联异常' }}</p></td>
                <td v-for="key in SKILL_MODE_KEYS" :key="key"><button type="button" class="skill-mode-cell" @click.stop="openSkillDrawer(skill, key)">
                  <span class="skill-mode-status" :class="skillModeResult(skill, key)?.status || 'not_evaluated'">{{ hasSkillMatchError(skill) ? '关联异常' : skillModeStatusLabel(skillModeResult(skill, key)?.status || 'not_evaluated') }}</span>
                  <span v-if="isAwaitingSkillSource(skill.skill_id, key)" class="skill-observation-note">等待新记录</span>
                  <span v-if="!hasSkillMatchError(skill) && skillModeResult(skill, key)?.status === 'completed'" class="skill-report-state" :class="{ 'has-error': skillModeResult(skill, key)?.report_status === 'error' }">{{ skillReportState(skillModeResult(skill, key)) }}</span>
                  <span class="skill-mode-version">评测版本 {{ skillModeVersion(skill, key) }}</span>
                  <span v-for="entry in skillModeGlance(skill, key)" :key="entry.key" class="skill-cell-metric">{{ entry.label }} <b>{{ entry.value }}</b><small v-if="entry.detail">（{{ entry.detail }}）</small></span>
                </button></td>
                <td><div class="skill-row-actions"><button type="button" class="skill-text-button" @click.stop="openSkillDrawer(skill)">查看结果</button><button type="button" class="skill-text-button" :disabled="skill.skill_status !== '已完成' || skillSubmitting || hasSkillMatchError(skill)" @click.stop="openSkillEvaluationFor(skill)">发起评测</button></div></td>
              </tr></tbody>
            </table>
          </div>
          <p v-else-if="!skillResultsLoading && !skillResultsError && skillScopeValid()" class="empty-text">{{ skillFilter.keyword ? '没有匹配的评测中或已有结果的 Skill。' : '该范围暂无评测中或已有结果的 Skill。' }}</p>
          <div v-if="skillTotal > 0" class="eval-pagination">
            <div class="eval-page-size">每页 <select v-model.number="skillPageSize" @change="onSkillPageSizeChange"><option :value="10">10</option><option :value="20">20</option><option :value="50">50</option></select> 个 Skill</div>
            <div class="eval-page-info">共 {{ skillTotal }} 个 Skill</div>
            <div class="eval-page-nav"><button :disabled="skillPage <= 1" @click="goToSkillPage(skillPage - 1)">上一页</button><template v-for="(page, index) in skillPageNumbers" :key="index"><span v-if="page === '...'" class="eval-page-ellipsis">…</span><button v-else :class="{ active: page === skillPage }" @click="goToSkillPage(page)">{{ page }}</button></template><button :disabled="skillPage >= skillTotalPages" @click="goToSkillPage(skillPage + 1)">下一页</button></div>
            <div class="eval-page-jump">跳至 <input type="number" min="1" :max="skillTotalPages" v-model.number="skillJumpPage" @keyup.enter="goToSkillPage(skillJumpPage)" /> 页</div>
          </div>
        </template>
      </section>

      <!-- 评测任务明细侧边栏 -->
      <transition name="drawer-slide">
        <div v-if="drawerVisible" class="drawer-mask" @click.self="closeDrawer">
          <aside class="drawer-panel" role="dialog" aria-modal="true">

            <div v-if="activeRow" class="drawer-body">
              <!-- Tab 页签 -->
              <div class="drawer-tabs">
                <button v-for="t in drawerTabs" :key="t.key"
                        :class="['drawer-tab', { active: drawerTab === t.key }]"
                        @click="drawerTab = t.key">{{ t.label }}</button>
                <button class="drawer-close" @click="closeDrawer" aria-label="关闭">×</button>
              </div>

              <!-- 评测详情（基础信息 + 评测指标） -->
              <section v-show="drawerTab === 'detail'" class="drawer-section">
                <h4 class="drawer-detail-title">基础信息</h4>
                <div class="drawer-meta-grid">
                  <div class="drawer-meta-item">
                    <span class="meta-label">场景</span>
                    <span class="meta-value"><span class="eval-type-pill" :class="activeRow.eval_type">{{ evalThemeLabel[activeRow.eval_type] }}</span></span>
                  </div>
                  <div class="drawer-meta-item">
                    <span class="meta-label">任务类型</span>
                    <span class="meta-value">
                    <span class="task-type-tag tag-eval">评测任务</span>
                    <span v-if="activeRow.has_reflow" class="task-type-tag tag-reflow">回流任务</span>
                  </span>
                  </div>
                  <div class="drawer-meta-item">
                    <span class="meta-label">任务状态</span>
                    <span class="meta-value"><span class="status-pill" :class="activeRow.status">{{ activeRow.status === 'done' ? '已完成' : activeRow.status === 'processing' ? '进行中' : '失败' }}</span></span>
                  </div>
                  <div class="drawer-meta-item">
                    <span class="meta-label">耗时</span>
                    <span class="meta-value">{{ activeRow.status === 'done' ? fmtDur(activeRow.eval_duration) : '—' }}</span>
                  </div>
                  <div class="drawer-meta-item">
                    <span class="meta-label">触发方式</span>
                    <span class="meta-value">{{ activeRow.trigger_mode === 'auto' ? '自动' : '手动' }}</span>
                  </div>
                  <div class="drawer-meta-item">
                    <span class="meta-label">评测创建人</span>
                    <span class="meta-value">{{ activeRow.creator }}<span class="meta-time">{{ activeRow.created_at }}</span></span>
                  </div>
                  <div class="drawer-meta-item drawer-meta-trigger">
                    <span class="meta-label">任务触发来源</span>
                    <span class="meta-value">
                    <a class="meta-trigger-link" :href="activeRow.task_source" target="_blank" rel="noopener" :title="activeRow.task_source">{{ activeRow.task_source }}</a>
                  </span>
                  </div>
                </div>

                <h4 class="drawer-detail-title">评测指标</h4>
                <template v-if="activeRow.status === 'done'">
                  <div v-if="drawerMetricRows.some(s => s.done)" class="drawer-metric-charts">
                    <div v-for="c in drawerMetricCharts" :key="c.key" class="drawer-metric-chart-item">
                      <VChart :option="c.option" autoresize style="height: 220px;" />
                    </div>
                  </div>
                  <p v-else class="drawer-empty">暂无评测指标数据</p>
                  <div v-if="drawerMetricRows.some(s => s.done)" class="drawer-metric-table-wrap">
                    <table class="drawer-metric-table">
                      <thead>
                      <tr>
                        <th>场景</th>
                        <th>功能覆盖率</th>
                        <th>Token消耗</th>
                        <th>完成时长</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr v-for="(scene, i) in drawerMetricRows.filter(s => s.done)" :key="i">
                        <td class="dm-scene">{{ scene.label }}</td>
                        <td>
                          <span v-if="scene.metrics.coverage_detail" class="coverage-link" @click="openCoverageDetail(scene.label, scene.metrics.coverage_detail)" title="点击查看功能覆盖率详情">{{ pct(scene.metrics.coverage) }}</span>
                          <span v-else>{{ pct(scene.metrics.coverage) }}</span>
                        </td>
                        <td>{{ fmtToken(scene.metrics.token) }}</td>
                        <td>{{ fmtDur(scene.metrics.duration) }}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                  <p v-else class="drawer-empty">暂无评测指标数据</p>
                </template>
                <p v-else class="drawer-empty">评测未完成，暂无指标数据</p>
              </section>

              <!-- 知识回流（合并回流意见 / 回流进度 / 改进效果 / 改进建议） -->
              <section v-show="drawerTab === 'reflow'" class="drawer-section">
                <!-- 无回流阶段：仅提示 -->
                <p v-if="!activeRow.has_reflow" class="drawer-empty drawer-reflow-empty-tip">该任务无知识回流阶段</p>
                <template v-else>
                  <!-- 回流进度 -->
                  <h4 class="drawer-reflow-title">回流进度</h4>
                  <div class="drawer-meta-grid">
                    <div class="drawer-meta-item">
                      <span class="meta-label">回流预期</span>
                      <span class="meta-value">
                    <span v-if="activeRow.reflow_expect" class="conclusion-pill" :class="activeRow.reflow_expect">{{ activeRow.reflow_expect === 'up' ? '效果上升' : '效果下降' }}</span>
                    <span v-else>—</span>
                  </span>
                    </div>
                    <div class="drawer-meta-item">
                      <span class="meta-label">回流状态</span>
                      <span class="meta-value"><span class="gov-status-pill" :class="activeRow.reflow_status">{{ reflowStatusLabel[activeRow.reflow_status] }}</span></span>
                    </div>
                    <div class="drawer-meta-item">
                      <span class="meta-label">回流耗时</span>
                      <span class="meta-value">{{ activeRow.reflow_status === 'done' ? fmtDur(activeRow.reflow_duration) : '—' }}</span>
                    </div>
                  </div>
                  <div class="drawer-reflow-actions">
                    <button
                        class="reflow-btn reflow-btn-done"
                        :disabled="activeRow.reflow_status === 'done' || activeRow.reflow_status === 'ignored'"
                        @click="markReflowDone"
                    >{{ activeRow.reflow_status === 'done' ? '已完成回流' : '标记回流完成' }}</button>
                    <button
                        class="reflow-btn reflow-btn-reject"
                        :disabled="activeRow.reflow_status === 'done' || activeRow.reflow_status === 'ignored'"
                        @click="rejectReflow"
                    >{{ activeRow.reflow_status === 'ignored' ? '已拒绝回流' : '拒绝回流' }}</button>
                  </div>

                  <!-- 回流概览 -->
                  <h4 class="drawer-reflow-title">回流概览</h4>
                  <div v-if="activeRow.reflow_opinions.length" class="drawer-opinions">
                    <div v-for="(op, i) in activeRow.reflow_opinions" :key="i" class="drawer-opinion-item">
                      <div class="opinion-file">{{ op.file }}</div>
                      <div class="opinion-text">{{ op.opinion }}</div>
                    </div>
                  </div>
                  <p v-else class="drawer-empty">暂无回流意见</p>

                  <!-- 代码仓知识回流 -->
                  <h4 class="drawer-reflow-title">代码仓知识回流</h4>

                  <!-- 改进效果 -->
                  <h5 class="drawer-reflow-subtitle">改进效果</h5>
                  <div v-if="drawerEffectCompare.length" class="drawer-effect-chart-block">
                    <div class="drawer-metric-charts">
                      <div v-for="c in drawerEffectCharts" :key="c.key" class="drawer-metric-chart-item">
                        <VChart :option="c.option" autoresize style="height: 220px;" />
                      </div>
                    </div>
                    <div class="drawer-metric-table-wrap">
                      <table class="drawer-metric-table">
                        <thead>
                        <tr>
                          <th>模式</th>
                          <th>功能覆盖率</th>
                          <th>Token消耗</th>
                          <th>完成时长</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr>
                          <td class="dm-scene">知识改进前</td>
                          <td v-for="m in drawerEffectCompare" :key="m.key">
                            <span v-if="m.key === 'coverage' && m.before_coverage_detail" class="coverage-link" @click="openCoverageDetail('知识改进前 - 功能覆盖率', m.before_coverage_detail)" title="点击查看功能覆盖率详情">{{ m.fmt(m.before) }}</span>
                            <span v-else>{{ m.fmt(m.before) }}</span>
                          </td>
                        </tr>
                        <tr>
                          <td class="dm-scene">知识改进后</td>
                          <td v-for="m in drawerEffectCompare" :key="m.key" class="em-improved">
                            <span v-if="m.key === 'coverage' && m.after_coverage_detail" class="coverage-link" @click="openCoverageDetail('知识改进后 - 功能覆盖率', m.after_coverage_detail)" title="点击查看功能覆盖率详情">{{ m.fmt(m.after) }}</span>
                            <span v-else>{{ m.fmt(m.after) }}</span>
                          </td>
                        </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div v-else class="drawer-effect-table-wrap">
                    <table class="drawer-effect-table">
                      <thead>
                      <tr>
                        <th>指标</th>
                        <th>无知识</th>
                        <th>仅产品知识</th>
                        <th>仅作业知识</th>
                        <th>仅领域知识</th>
                        <th>全量知识</th>
                        <th>全量改进知识</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr v-for="m in drawerEffectMetrics" :key="m.key">
                        <td class="em-metric-name">{{ m.label }}</td>
                        <td>{{ m.fmt(m.values.baseline) }}</td>
                        <td>{{ m.fmt(m.values.init) }}</td>
                        <td>{{ m.fmt(m.values.coreinsight) }}</td>
                        <td>{{ m.fmt(m.values.corealm) }}</td>
                        <td>{{ m.fmt(m.values.full) }}</td>
                        <td class="em-improved">{{ m.fmt(m.values.improved) }}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>

                  <!-- 改进建议 -->
                  <h5 class="drawer-reflow-subtitle">改进建议</h5>
                  <div v-if="drawerRepoSuggestions.length" class="drawer-suggestion-list">
                    <template v-for="(s, idx) in drawerRepoSuggestions" :key="'r' + idx">
                      <div class="drawer-suggestion-card">
                        <div class="drawer-suggestion-file">{{ s.file_name }}</div>
                        <div class="drawer-suggestion-desc">{{ s.change_desc }}</div>
                        <div class="gh-diff" v-if="s.diff">
                          <table class="gh-diff-table">
                            <tbody>
                            <template v-for="(row, ri) in getDiffRows(s.diff)" :key="ri">
                              <tr v-if="row.type !== 'meta'" :class="'gh-diff-row gh-diff-' + row.type">
                                <td class="gh-diff-lineno">{{ row.leftNum ?? '' }}</td>
                                <td class="gh-diff-left" :class="{ 'gh-diff-cell-del': row.type === 'del' }">
                                  <span v-if="row.type === 'del'" class="gh-diff-sign">-</span>{{ row.leftContent }}
                                </td>
                                <td class="gh-diff-lineno">{{ row.rightNum ?? '' }}</td>
                                <td class="gh-diff-right" :class="{ 'gh-diff-cell-add': row.type === 'add' }">
                                  <span v-if="row.type === 'add'" class="gh-diff-sign">+</span>{{ row.rightContent }}
                                </td>
                              </tr>
                            </template>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </template>
                  </div>
                  <p v-else class="drawer-empty">暂无代码仓改进建议</p>

                  <!-- 改进链接 -->
                  <h5 class="drawer-reflow-subtitle">改进链接</h5>
                  <div class="drawer-reflow-mr">
                    <template v-if="drawerReflowMRs.length">
                      <a v-for="(mr, idx) in drawerReflowMRs" :key="idx" class="drawer-reflow-mr-link" :href="mr.url" target="_blank" rel="noopener" :title="mr.url">{{ mr.url }} ↗</a>
                    </template>
                    <span v-else class="drawer-reflow-mr-empty">暂无</span>
                  </div>

                  <!-- 非代码仓知识回流 -->
                  <h4 class="drawer-reflow-title">非代码仓知识回流</h4>

                  <!-- 改进建议 -->
                  <h5 class="drawer-reflow-subtitle">改进建议</h5>
                  <div v-if="drawerSuggestions.length" class="drawer-suggestion-list">
                    <!-- report 表格形式（含 knowledge_id 字段） -->
                    <div v-if="drawerSuggestions.some(s => s.knowledge_id)" class="drawer-suggestion-table-wrap">
                      <table class="drawer-suggestion-table">
                        <thead>
                        <tr>
                          <th>知识名称</th>
                          <th>来源</th>
                          <th>知识问题分类</th>
                          <th>改进建议</th>
                          <th>详情</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="(s, idx) in drawerSuggestions.filter(x => x.knowledge_id)" :key="idx">
                          <td>
                            <template v-if="s.source === '人工补充'"></template>
                            <a v-else-if="s.uri" :href="s.uri" target="_blank" rel="noopener" class="sug-name-link">{{ s.knowledge_name || s.knowledge_id }}</a>
                            <span v-else>{{ s.knowledge_name || s.knowledge_id }}</span>
                          </td>
                          <td>{{ s.source }}</td>
                          <td>{{ s.problem_category }}</td>
                          <td>{{ s.suggestion }}</td>
                          <td>
                            <button class="sug-detail-btn" @click="openSugDetail(s)">查看</button>
                          </td>
                        </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <p v-else class="drawer-empty">暂无改进建议</p>
                </template>
              </section>

            </div>
          </aside>
        </div>
      </transition>

      <!-- 知识改进建议详情弹窗 -->
      <transition name="sug-detail-fade">
        <div v-if="sugDetailVisible" class="sug-detail-overlay" @click.self="closeSugDetail">
          <div class="sug-detail-modal">
            <div class="sug-detail-header">
              <h3 class="sug-detail-title">
                {{ activeSugDetail?.source || '' }} | {{ activeSugDetail?.knowledge_id || '' }}
              </h3>
              <button class="sug-detail-close" @click="closeSugDetail">&times;</button>
            </div>
            <div class="sug-detail-body">
              <template v-if="activeSugDetail">
                <!-- 非 gap：保留类，展示原文/改进后/改进建议/分诊原因 -->
                <template v-if="!activeSugDetail.is_gap">
                  <div class="sug-section-title">知识原文</div>
                  <pre class="sug-pre">{{ activeSugDetail.original_content || '无内容' }}</pre>
                  <template v-if="activeSugDetail.improved_content && activeSugDetail.improved_content !== activeSugDetail.original_content">
                    <div class="sug-section-title">改进后内容</div>
                    <pre class="sug-pre">{{ activeSugDetail.improved_content }}</pre>
                  </template>
                  <div class="sug-section-title">改进建议</div>
                  <div class="sug-text">{{ activeSugDetail.suggestion }}</div>
                  <div class="sug-section-title" v-if="activeSugDetail.triage_reason">分诊原因</div>
                  <div class="sug-text sug-text-muted" v-if="activeSugDetail.triage_reason">{{ activeSugDetail.triage_reason }}</div>
                </template>
                <!-- gap：展示内容摘要/分析原因/补救建议 -->
                <template v-else>
                  <div class="sug-section-title" v-if="activeSugDetail.content_summary">内容摘要</div>
                  <div class="sug-text" v-if="activeSugDetail.content_summary">{{ activeSugDetail.content_summary }}</div>
                  <div class="sug-section-title" v-if="activeSugDetail.reason">分析原因</div>
                  <div class="sug-text" v-if="activeSugDetail.reason">{{ activeSugDetail.reason }}</div>
                  <div class="sug-section-title" v-if="activeSugDetail.remediation">补救建议</div>
                  <div class="sug-text" v-if="activeSugDetail.remediation">{{ activeSugDetail.remediation }}</div>
                  <div class="sug-section-title" v-if="activeSugDetail.suggestion">改进建议</div>
                  <div class="sug-text" v-if="activeSugDetail.suggestion">{{ activeSugDetail.suggestion }}</div>
                </template>
              </template>
            </div>
          </div>
        </div>
      </transition>

      <!-- 功能覆盖率详情弹窗 -->
      <transition name="sug-detail-fade">
        <div v-if="coverageDetailVisible" class="sug-detail-overlay" @click.self="closeCoverageDetail">
          <div class="sug-detail-modal coverage-detail-modal">
            <div class="sug-detail-header">
              <h3>{{ activeCoverageDetail?.title || '功能覆盖率详情' }}</h3>
              <button class="sug-detail-close" @click="closeCoverageDetail">&times;</button>
            </div>
            <div class="sug-detail-body">
              <template v-if="activeCoverageDetail?.detail">
                <!-- 覆盖率计算结果 -->
                <div class="coverage-summary">
                  <div class="coverage-summary-main">
                    <span class="coverage-summary-label">综合覆盖率</span>
                    <span class="coverage-summary-value">{{ coveragePercent(activeCoverageDetail.detail) }}</span>
                  </div>
                  <div class="coverage-summary-legend">
                    <span class="coverage-legend-item"><i class="legend-dot green"></i>1.00 完全覆盖</span>
                    <span class="coverage-legend-item"><i class="legend-dot yellow"></i>0.50 部分覆盖</span>
                    <span class="coverage-legend-item"><i class="legend-dot red"></i>0.00 未覆盖</span>
                  </div>
                </div>
                <!-- 计算过程 -->
                <div class="coverage-calc">
                  <div class="sug-section-title">覆盖率计算过程</div>
                  <div class="coverage-calc-formula">
                    覆盖率 = (Σ 大粒度特性得分 / 大粒度特性总数) × 0.7 + (Σ 小粒度特性得分 / 小粒度特性总数) × 0.3
                  </div>
                  <div class="coverage-calc-grid">
                    <div class="coverage-calc-card">
                      <div class="coverage-calc-card-head">
                        <span class="coverage-calc-card-tag">大粒度特性</span>
                        <span class="coverage-calc-card-weight">权重 0.7</span>
                      </div>
                      <div class="coverage-calc-card-row">
                        <span class="coverage-calc-card-key">得分总和</span>
                        <span class="coverage-calc-card-val">{{ coverageCalcParts(activeCoverageDetail.detail).fSum.toFixed(2) }}</span>
                      </div>
                      <div class="coverage-calc-card-row">
                        <span class="coverage-calc-card-key">特性总数</span>
                        <span class="coverage-calc-card-val">{{ coverageCalcParts(activeCoverageDetail.detail).fTotal }}</span>
                      </div>
                      <div class="coverage-calc-card-row">
                        <span class="coverage-calc-card-key">平均得分</span>
                        <span class="coverage-calc-card-val">{{ coverageCalcParts(activeCoverageDetail.detail).fAvg.toFixed(4) }}</span>
                      </div>
                      <div class="coverage-calc-card-row coverage-calc-card-subtotal">
                        <span class="coverage-calc-card-key">加权贡献</span>
                        <span class="coverage-calc-card-val">× 0.7 = {{ coverageCalcParts(activeCoverageDetail.detail).fPart.toFixed(4) }}</span>
                      </div>
                    </div>
                    <div class="coverage-calc-card">
                      <div class="coverage-calc-card-head">
                        <span class="coverage-calc-card-tag">小粒度特性</span>
                        <span class="coverage-calc-card-weight">权重 0.3</span>
                      </div>
                      <div class="coverage-calc-card-row">
                        <span class="coverage-calc-card-key">得分总和</span>
                        <span class="coverage-calc-card-val">{{ coverageCalcParts(activeCoverageDetail.detail).hSum.toFixed(2) }}</span>
                      </div>
                      <div class="coverage-calc-card-row">
                        <span class="coverage-calc-card-key">特性总数</span>
                        <span class="coverage-calc-card-val">{{ coverageCalcParts(activeCoverageDetail.detail).hTotal }}</span>
                      </div>
                      <div class="coverage-calc-card-row">
                        <span class="coverage-calc-card-key">平均得分</span>
                        <span class="coverage-calc-card-val">{{ coverageCalcParts(activeCoverageDetail.detail).hAvg.toFixed(4) }}</span>
                      </div>
                      <div class="coverage-calc-card-row coverage-calc-card-subtotal">
                        <span class="coverage-calc-card-key">加权贡献</span>
                        <span class="coverage-calc-card-val">× 0.3 = {{ coverageCalcParts(activeCoverageDetail.detail).hPart.toFixed(4) }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="coverage-calc-result">
                    <span class="coverage-calc-result-eq">=</span>
                    <span class="coverage-calc-result-expr">{{ coverageCalcParts(activeCoverageDetail.detail).fPart.toFixed(4) }} + {{ coverageCalcParts(activeCoverageDetail.detail).hPart.toFixed(4) }}</span>
                    <span class="coverage-calc-result-arrow">→</span>
                    <span class="coverage-calc-result-pct">{{ coveragePercent(activeCoverageDetail.detail) }}</span>
                  </div>
                </div>
                <!-- 大粒度特性 features -->
                <div class="sug-section-title">大粒度特性</div>
                <div class="coverage-item-list">
                  <div v-for="(item, idx) in (activeCoverageDetail.detail.features || [])" :key="'f' + idx" class="coverage-item">
                    <div class="coverage-item-content">
                      <div class="coverage-item-name">{{ item.description || '—' }}</div>
                    </div>
                    <button class="coverage-score-btn" :class="'score-' + scoreLevel(item.score)" :title="'得分 ' + scoreLabel(item.score)">
                      {{ scoreLabel(item.score) }}
                    </button>
                  </div>
                  <div v-if="!(activeCoverageDetail.detail.features && activeCoverageDetail.detail.features.length)" class="coverage-empty">暂无数据</div>
                </div>
                <!-- 小粒度特性 hunk_features -->
                <div class="sug-section-title">小粒度特性</div>
                <div class="coverage-item-list">
                  <div v-for="(item, idx) in (activeCoverageDetail.detail.hunk_features || [])" :key="'h' + idx" class="coverage-item">
                    <div class="coverage-item-content">
                      <div class="coverage-item-name">{{ item.description || '—' }}</div>
                    </div>
                    <button class="coverage-score-btn" :class="'score-' + scoreLevel(item.score)" :title="'得分 ' + scoreLabel(item.score)">
                      {{ scoreLabel(item.score) }}
                    </button>
                  </div>
                  <div v-if="!(activeCoverageDetail.detail.hunk_features && activeCoverageDetail.detail.hunk_features.length)" class="coverage-empty">暂无数据</div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </transition>

      <!-- 单个 Skill 的三个模式结果 -->
      <Teleport to="body">
        <transition name="drawer-slide">
          <div v-if="skillDrawerVisible" class="drawer-mask" @click.self="closeSkillDrawer">
            <aside ref="skillDrawerPanel" class="drawer-panel drawer-panel--skill" role="dialog" aria-modal="true" aria-labelledby="skill-eval-title" tabindex="-1" @keydown.esc.stop="closeSkillDrawer" @keydown.tab="trapSkillDrawerFocus">
              <header class="skill-drawer-header"><div><span class="skill-eyebrow">评测中心 / Skill 结果</span><h3 id="skill-eval-title">{{ activeSkill?.skill_name || activeSkill?.name || '未命名 Skill' }}</h3></div><button class="drawer-close" @click="closeSkillDrawer" aria-label="关闭 Skill 评测结果">×</button></header>
              <div v-if="activeSkill" class="drawer-body skill-drawer-body" tabindex="0" aria-label="评测结果滚动区域" :aria-busy="skillResultsLoading">
                <section class="skill-overview">
                  <div class="skill-section-heading"><h4>评测结果</h4><span class="status-pill" :class="activeSkill.status">{{ skillStatusLabel(activeSkill.status) }}</span></div>
                  <div class="skill-directory-meta"><span>目录版本 {{ activeSkill.version || '—' }}</span><span>目录状态 {{ activeSkill.skill_status || '—' }}</span><span>最近更新 {{ skillLatestUpdated(activeSkill) }}</span><button type="button" class="skill-text-button" :disabled="skillResultsLoading" @click="loadSkillResults()">{{ skillResultsLoading ? '刷新中…' : '刷新结果' }}</button><button type="button" class="skill-text-button" :disabled="activeSkill.skill_status !== '已完成' || skillSubmitting || hasSkillMatchError(activeSkill)" @click="openSkillEvaluationFor(activeSkill)">发起评测</button></div>
                  <p class="skill-overview-note">三种模式分别展示最新结果及其评测版本；执行完成后，评分和用例判定以报告为准。</p>
                  <p v-if="hasSkillMatchError(activeSkill)" class="skill-state skill-state--error">{{ activeSkill.match_error || '评测记录关联异常，请检查 Skill 名称。' }}</p>
                </section>
                <div v-if="skillResultsError" class="skill-state skill-state--error" role="alert">{{ skillResultsError }}</div>
                <div class="skill-mode-switcher" role="group" aria-label="选择评测模式">
                  <button v-for="mode in skillEvalModes" :key="mode.key" type="button" class="skill-mode-card" :class="[skillModeClass(mode.key), { active: activeSkillMode === mode.key }]" :aria-pressed="activeSkillMode === mode.key" aria-controls="skill-mode-results" @click="selectSkillResultMode(mode.key)">
                    <span class="skill-mode-card-top"><span class="skill-mode-icon">{{ skillModeIcon(mode.key) }}</span><strong>{{ mode.label }}</strong></span>
                    <span class="skill-mode-description">{{ skillModeDescription(mode.key) }}</span>
                    <span class="skill-mode-status" :class="skillModeResult(activeSkill, mode.key)?.status || 'not_evaluated'">{{ hasSkillMatchError(activeSkill) ? '关联异常' : skillModeStatusLabel(skillModeResult(activeSkill, mode.key)?.status || 'not_evaluated') }}</span>
                    <span class="skill-mode-card-foot"><span>{{ skillReportState(skillModeResult(activeSkill, mode.key)) }}</span><span>版本 {{ skillModeVersion(activeSkill, mode.key) }}</span></span>
                    <span v-if="isAwaitingSkillSource(activeSkill.skill_id, mode.key)" class="skill-observation-note">等待本次评测的新记录</span>
                  </button>
                </div>
                <section id="skill-mode-results" class="skill-mode-panel" :class="skillModeClass(activeSkillMode)" :aria-label="`${skillModeLabel(activeSkillMode)}结果`">
                  <header class="skill-mode-panel-header"><div class="skill-mode-panel-title"><span class="skill-mode-icon">{{ skillModeIcon(activeSkillMode) }}</span><div><h4>{{ skillModeLabel(activeSkillMode) }}</h4><p>{{ skillModeDescription(activeSkillMode) }}</p></div></div><span class="skill-mode-panel-count">评测版本 {{ skillModeVersion(activeSkill, activeSkillMode) }}</span></header>
                  <article v-for="row in skillModeRows" :key="`${activeSkillMode}:${row.skill.skill_id}`" class="skill-result-card is-open">
                    <div class="skill-result-detail">
                      <p v-if="isAwaitingSkillSource(row.skill.skill_id, activeSkillMode)" class="skill-report-notice">本次已提交，正在等待新记录。下方可能仍为上次评测结果。</p>
                      <template v-if="row.result?.report">
                        <div v-if="row.reports.some(report => report.version)" class="skill-report-version-picker">
                          <label v-if="row.reports.length > 1">报告版本 <select :value="row.reportVersion" @change="selectSkillReportVersion(row.skill.skill_id, ($event.target as HTMLSelectElement).value)"><option v-for="report in row.reports" :key="report.version" :value="report.version">{{ report.version || '当前版本' }}</option></select></label>
                          <span v-else>报告版本 {{ row.reportVersion }}</span>
                        </div>
                        <div v-if="reportSummaryEntries(row.result.report, activeSkillMode).length" class="skill-report-summary">
                          <div v-for="entry in reportSummaryEntries(row.result.report, activeSkillMode)" :key="entry.key" class="skill-report-metric"><span>{{ entry.label }}</span><strong>{{ entry.value }}</strong><small v-if="entry.detail">（{{ entry.detail }}）</small></div>
                        </div>
                        <p v-if="activeSkillMode === 'TRIGGER' && !triggerCaseStats(row.result.report).available" class="skill-report-notice">报告已返回，但尚未识别到当前模式的用例明细或通过数量，暂不显示统计值。请稍后刷新结果。</p>
                        <p v-else-if="row.result.status !== 'completed'" class="skill-overview-note">以下统计基于已返回的报告内容；任务当前状态：{{ skillModeStatusLabel(row.result.status) }}。</p>
                        <p v-if="activeSkillMode === 'TRIGGER' && triggerCaseStats(row.result.report).total" class="skill-overview-note">按 results 中的 passed 统计；未通过表示用例判定未通过，与执行失败分别统计。<template v-if="triggerCaseStats(row.result.report).unknown"> 未判定用例不计入通过率分母。</template></p>
                        <div v-if="activeSkillMode === 'TRIGGER' && triggerCaseStats(row.result.report).total" class="skill-trigger-breakdown">
                          <span v-for="group in triggerCaseStats(row.result.report).groups" :key="group.type">{{ group.label }}：通过 {{ group.passed }} / {{ group.total }}</span>
                        </div>
                        <div v-if="reportExtraEntries(row.result.report).length" class="skill-report-extras">
                          <div v-for="entry in reportExtraEntries(row.result.report)" :key="entry.key" class="skill-report-field"><span class="skill-report-field-label">{{ entry.label }}</span><span class="skill-report-field-value">{{ entry.value }}</span></div>
                        </div>

                        <div v-if="reportDimensions(row.result.report).length" class="skill-report-block">
                          <h5>评测维度 <span>{{ reportDimensions(row.result.report).length }}</span></h5>
                          <details v-for="(dimension, index) in reportDimensions(row.result.report)" :key="index" class="skill-report-disclosure skill-dimension-disclosure">
                            <summary><strong>{{ dimension.id }} {{ dimension.name }}</strong><span class="skill-dimension-score">得分 {{ dimension.score }}</span><span class="skill-disclosure-hint">展开细节</span></summary>
                            <div class="skill-disclosure-body">
                              <div v-for="entry in dimension.extra" :key="entry.key" class="skill-report-field"><span class="skill-report-field-label">{{ entry.label }}</span><span class="skill-report-field-value">{{ entry.value }}</span></div>
                              <section v-if="reportImprovementActions(dimension.raw).length" class="skill-report-block skill-improvements">
                                <h5>改进建议</h5><ul><li v-for="(action, actionIndex) in reportImprovementActions(dimension.raw)" :key="actionIndex">{{ action }}</li></ul>
                              </section>
                              <section v-for="group in reportGroups(dimension.raw)" :key="group.key" class="skill-report-block">
                                <h5>{{ group.label }} <span>{{ group.items.length }}</span></h5>
                                <div v-for="item in group.items" :key="item.index" class="skill-report-item">
                                  <span class="skill-report-item-index">{{ item.index + 1 }}</span>
                                  <div><div v-for="entry in item.entries" :key="entry.key" class="skill-report-field"><span class="skill-report-field-label">{{ entry.label }}</span><span class="skill-report-field-value">{{ entry.value }}</span></div></div>
                                </div>
                              </section>
                              <p v-if="!dimension.extra.length && !reportGroups(dimension.raw).length && !reportImprovementActions(dimension.raw).length" class="skill-result-muted">报告仅返回维度得分，暂无更多细节。</p>
                            </div>
                          </details>
                        </div>

                        <section v-if="reportImprovementActions(row.result.report).length" class="skill-report-block skill-improvements">
                          <h5>改进建议</h5><ul><li v-for="(action, actionIndex) in reportImprovementActions(row.result.report)" :key="actionIndex">{{ action }}</li></ul>
                        </section>

                        <section v-if="activeSkillMode === 'TRIGGER' && triggerResultRows(row.result.report).length" class="skill-report-block skill-trigger-cases">
                          <h5>触发用例结果 <span>{{ triggerResultRows(row.result.report).length }} 条</span></h5>
                          <div class="skill-quality-case-columns skill-trigger-case-columns" aria-hidden="true"><span></span><span>测试任务</span><span>用例类型</span><span>预期触发</span><span>实际触发</span><span>判定</span></div>
                          <details v-for="item in triggerResultRows(row.result.report)" :key="item.index" class="skill-quality-case skill-trigger-case">
                            <summary><span class="skill-quality-case-title">{{ item.title }}</span><span class="skill-trigger-case-type">{{ item.type }}</span><span class="skill-trigger-case-expect"><span class="skill-trigger-mobile-label">预期：</span>{{ item.expected }}</span><span class="skill-trigger-case-actual"><span class="skill-trigger-mobile-label">实际：</span>{{ item.actual }}</span><span class="skill-case-verdict" :class="item.verdict">{{ item.verdictLabel }}</span></summary>
                            <div class="skill-disclosure-body">
                              <div v-for="field in item.fields" :key="field.key" class="skill-report-field"><span class="skill-report-field-label">{{ field.label }}</span><span class="skill-report-field-value">{{ field.value }}</span></div>
                              <p v-if="!item.fields.length" class="skill-result-muted">暂无更多用例信息。</p>
                            </div>
                          </details>
                        </section>

                        <section v-if="activeSkillMode === 'QUALITY' && qualityResultRows(row.result.report).length" class="skill-report-block skill-quality-cases">
                          <h5>质量用例结果 <span>{{ qualityResultRows(row.result.report).length }} 条</span></h5>
                          <div class="skill-quality-case-columns" aria-hidden="true"><span></span><span>测试任务</span><span>得分</span><span>判定</span><span>检查点通过</span></div>
                          <details v-for="item in qualityResultRows(row.result.report)" :key="item.index" class="skill-quality-case">
                            <summary><span class="skill-quality-case-title">{{ item.title }}</span><strong class="skill-quality-case-score">{{ item.score }}</strong><span class="skill-case-verdict" :class="item.verdict">{{ item.verdictLabel }}</span><span class="skill-quality-assertion-count">{{ item.assertionSummary }}</span></summary>
                            <div class="skill-disclosure-body">
                              <div class="skill-quality-case-meta"><span v-if="item.caseId">用例 ID {{ item.caseId }}</span><span v-if="item.duration">耗时 {{ item.duration }}</span></div>
                              <div v-for="field in item.fields" :key="field.key" class="skill-quality-text"><h6>{{ field.label }}</h6><p>{{ field.value }}</p></div>
                              <section v-if="item.assertions.length" class="skill-report-block">
                                <h5>检查点判定 <span>{{ item.assertions.length }}</span></h5>
                                <article v-for="(assertion, assertionIndex) in item.assertions" :key="assertionIndex" class="skill-assertion-card">
                                  <div class="skill-assertion-heading"><span class="skill-case-verdict" :class="assertion.verdict">{{ assertion.verdictLabel }}</span><span class="skill-assertion-priority">{{ assertion.priority }}</span><strong>{{ assertion.checkPoint }}</strong></div>
                                  <p v-if="assertion.reason">{{ assertion.reason }}</p>
                                  <div class="skill-quality-case-meta"><span v-if="assertion.confidence !== null">置信度 {{ assertion.confidence }}</span><span v-if="assertion.evidenceTurn !== null">证据回合 {{ assertion.evidenceTurn }}</span></div>
                                </article>
                              </section>
                              <section v-else-if="item.expectItems.length" class="skill-report-block"><h5>预期检查点</h5><ul><li v-for="(point, pointIndex) in item.expectItems" :key="pointIndex">{{ point }}</li></ul></section>
                            </div>
                          </details>
                        </section>

                        <details v-for="group in reportGroups(row.result.report, activeSkillMode)" :key="group.key" class="skill-report-disclosure">
                          <summary><strong>{{ group.label }}</strong><span class="skill-section-count">{{ group.items.length }} 条</span><span class="skill-disclosure-hint">展开细节</span></summary>
                          <div class="skill-disclosure-body">
                            <details v-for="item in group.items" :key="item.index" class="skill-report-item-disclosure">
                              <summary><span class="skill-report-item-index">{{ item.index + 1 }}</span><span class="skill-report-item-title">{{ item.title }}</span><span class="skill-disclosure-hint">查看完整内容</span></summary>
                              <div class="skill-item-fields"><div v-for="entry in item.entries" :key="entry.key" class="skill-report-field"><span class="skill-report-field-label">{{ entry.label }}</span><span class="skill-report-field-value">{{ entry.value }}</span></div></div>
                            </details>
                          </div>
                        </details>
                        <details v-for="section in reportSupplementSections(row.result.report)" :key="section.key" class="skill-report-disclosure">
                          <summary><strong>{{ section.label }}</strong><span class="skill-disclosure-hint">展开查看</span></summary>
                          <div class="skill-disclosure-body"><div v-for="entry in section.entries" :key="entry.key" class="skill-report-field"><span class="skill-report-field-label">{{ entry.label }}</span><span class="skill-report-field-value">{{ entry.value }}</span></div></div>
                        </details>
                        <details v-if="reportAdditionalEntries(row.result.report).length" class="skill-report-disclosure">
                          <summary><strong>补充信息</strong><span class="skill-disclosure-hint">展开查看</span></summary>
                          <div class="skill-disclosure-body"><div v-for="entry in reportAdditionalEntries(row.result.report)" :key="entry.key" class="skill-report-field"><span class="skill-report-field-label">{{ entry.label }}</span><span class="skill-report-field-value">{{ entry.value }}</span></div></div>
                        </details>
                        <p v-if="!hasReportContent(row.result.report)" class="skill-result-muted">评测已完成，报告暂未提供指标或明细。</p>
                      </template>
                      <div v-else class="skill-state" :class="{ 'skill-state--error': row.result?.status === 'failed' || row.result?.report_status === 'error' }" role="status">
                        <p>{{ skillModeNotice(row.result) }}</p>
                        <button v-if="row.result?.report_status === 'error' || row.result?.status === 'completed'" class="skill-text-button" :disabled="skillResultsLoading" @click="loadSkillResults()">刷新结果</button>
                      </div>
                      <div class="skill-directory-meta"><span>评测版本 {{ row.result?.version || '—' }}</span><span>开始时间 {{ row.result?.created_at || '—' }}</span><span>更新时间 {{ row.result?.updated_at || '—' }}</span></div>
                    </div>
                  </article>
                </section>
              </div>
            </aside>
          </div>
        </transition>
      </Teleport>

    </template>

    <section v-else class="section lifecycle-placeholder">
      <p class="empty-text">请先在上方选择部门、产品或 PDU，查看评测信息。</p>
    </section>

    <!-- 新建评测任务弹窗 -->
    <div v-if="evalModalVisible" class="eval-modal-overlay" @click.self="closeEvalModal">
      <div class="eval-modal">
        <div class="eval-modal-head">
          <h3>{{ evalForm.taskType === 'skill' ? '发起 Skill 评测' : '新建评测任务' }}</h3>
          <button class="eval-modal-close" @click="closeEvalModal">&times;</button>
        </div>
        <div class="eval-modal-body">
          <!-- 知识增益评测仍保留任务名称 -->
          <div v-if="evalForm.taskType !== 'skill'" class="eval-modal-field">
            <label class="eval-modal-label">
              任务名称 <span class="eval-required">*</span>
            </label>
            <input
                v-model="evalForm.taskName"
                class="eval-mr-input eval-task-name-input"
                placeholder="请输入任务名称"
                maxlength="100"
            />
            <p v-if="evalTaskNameError" class="eval-modal-error">{{ evalTaskNameError }}</p>
          </div>

          <!-- 知识增益评测类型 -->
          <div v-if="evalForm.taskType !== 'skill'" class="eval-modal-field">
            <label class="eval-modal-label">
              任务类型 <span class="eval-required">*</span>
            </label>
            <div class="eval-task-type-list">
              <label
                  v-for="t in evalTaskTypes.filter(item => item.key !== 'skill')"
                  :key="t.key"
                  class="eval-task-type-card"
                  :class="{ active: evalForm.taskType === t.key, disabled: t.disabled }"
              >
                <input
                    type="radio"
                    name="eval-task-type"
                    :value="t.key"
                    v-model="evalForm.taskType"
                    :disabled="t.disabled"
                />
                <span class="eval-task-type-card-title">{{ t.label }}</span>
                <span class="eval-task-type-card-desc">{{ t.desc }}</span>
                <span v-if="t.disabled" class="eval-task-type-card-tip">{{ t.tip }}</span>
              </label>
            </div>
          </div>

          <!-- 代码生成场景 / 测试生成场景：MR链接 + 评测模式 -->
          <template v-if="evalForm.taskType === 'code_gen' || evalForm.taskType === 'test_gen'">
            <div class="eval-modal-field">
              <label class="eval-modal-label">
                MR链接 <span class="eval-required">*</span>
              </label>
              <input
                  v-model="evalForm.taskSource"
                  class="eval-mr-input"
                  placeholder="https://code.example.com/repo/feature-xxx/-/merge_requests/123"
              />
            </div>

            <div class="eval-modal-field">
              <label class="eval-modal-label">
                评测模式 <span class="eval-required">*</span>
              </label>
              <div class="eval-mode-list">
                <label
                    v-for="mode in evalModes"
                    :key="mode.key"
                    class="eval-mode-item"
                    :class="{ disabled: mode.disabled }"
                >
                  <input
                      type="checkbox"
                      :checked="isModeChecked(mode.key)"
                      :disabled="mode.disabled"
                      @change="toggleMode(mode.key)"
                  />
                  <span class="eval-mode-label">{{ mode.label }}</span>
                  <span v-if="mode.disabled" class="eval-mode-tag">默认必选</span>
                </label>
              </div>
            </div>
          </template>

          <!-- Skill评测：评测模式 + Skill 勾选 -->
          <fieldset v-if="evalForm.taskType === 'skill'" class="skill-modal-fieldset" :disabled="skillSubmitting">
            <p class="skill-overview-note">选择 Skill 和评测模式即可发起；结果在对应 Skill 下更新。</p>
            <div class="eval-modal-field">
              <label class="eval-modal-label">
                评测模式 <span class="eval-required">*</span>
              </label>
              <div class="eval-mode-list eval-mode-list--inline">
                <label v-for="mode in skillEvalModes" :key="mode.key" class="eval-mode-item" :class="skillModeClass(mode.key)">
                  <input
                      type="checkbox"
                      :checked="skillForm.modes.has(mode.key)"
                      @change="toggleSkillMode(mode.key)"
                  />
                  <span class="eval-mode-label">{{ mode.label }}</span>
                </label>
              </div>
            </div>

            <div class="eval-modal-field">
              <label class="eval-modal-label">
                选择 Skill <span class="eval-required">*</span>
                <span class="skill-selected-count">已选 {{ skillForm.selected.size }} 个</span>
              </label>
              <div class="skill-picker">
                <div class="skill-picker-search">
                  <input
                      v-model="skillForm.keyword"
                      class="eval-mr-input"
                      placeholder="按 Skill 名称 / 描述搜索"
                      @keyup.enter="searchEvaluableSkills"
                  />
                  <button type="button" class="skill-picker-search-btn" @click="searchEvaluableSkills">搜索</button>
                </div>
                <div v-if="evaluableSkills.length" class="skill-picker-toolbar">
                  <div class="skill-picker-toolbar-left">
                    <label class="skill-picker-select-all">
                      <input
                          type="checkbox"
                          :checked="allCurrentPageSelected"
                          :indeterminate.prop="someCurrentPageSelected && !allCurrentPageSelected"
                          @change="toggleSelectAllCurrentPage"
                      />
                      <span>全选当前页（{{ evaluableSkills.length }} 个）</span>
                    </label>
                    <button
                        type="button"
                        class="skill-picker-select-all-btn"
                        :disabled="selectingAllSkills"
                        @click="selectAllSkills"
                    >{{ selectingAllSkills ? '全选中…' : `全选所有（共 ${skillListTotal} 个）` }}</button>
                  </div>
                  <button
                      v-if="skillForm.selected.size"
                      type="button"
                      class="skill-picker-clear"
                      @click="clearSelectedSkills"
                  >清空已选</button>
                </div>
                <div class="skill-picker-list">
                  <p v-if="skillListLoading" class="skill-picker-state">正在加载可评测 Skill…</p>
                  <p v-else-if="skillListError" class="skill-picker-state is-error">
                    {{ skillListError }}
                    <button type="button" @click="loadEvaluableSkills">重试</button>
                  </p>
                  <p v-else-if="!evaluableSkills.length" class="skill-picker-state">当前范围暂无可评测 Skill</p>
                  <label
                      v-for="s in evaluableSkills"
                      :key="s.skill_id"
                      class="skill-pick-item"
                      :class="{ active: skillForm.selected.has(s.skill_id) }"
                  >
                    <input
                        type="checkbox"
                        :checked="skillForm.selected.has(s.skill_id)"
                        @change="toggleSkillSelect(s.skill_id)"
                    />
                    <span class="skill-pick-main">
                      <span class="skill-pick-name">{{ s.name || s.skill_name || '未命名 Skill' }}</span>
                      <span class="skill-pick-desc">{{ s.description || '—' }}</span>
                      <span class="skill-pick-meta">
                        <span v-if="s.level1 || s.level2">{{ [s.level1, s.level2].filter(Boolean).join(' / ') }}</span>
                        <span v-if="s.version">{{ s.version }}</span>
                        <span v-if="s.status">{{ s.status }}</span>
                      </span>
                    </span>
                  </label>
                </div>
                <div v-if="skillListTotal > 0" class="skill-picker-pager">
                  <button type="button" :disabled="skillListPage <= 1" @click="goSkillListPage(skillListPage - 1)">上一页</button>
                  <span>{{ skillListPage }} / {{ skillListTotalPages }}（共 {{ skillListTotal }} 个）</span>
                  <button type="button" :disabled="skillListPage >= skillListTotalPages" @click="goSkillListPage(skillListPage + 1)">下一页</button>
                </div>
              </div>
            </div>
            <details class="skill-modal-options"><summary>更多信息（选填）</summary>
              <div class="eval-modal-field"><label class="eval-modal-label">调用者工号</label><input v-model="skillForm.creator" class="eval-mr-input" placeholder="当前用户工号，留空使用默认值" /></div>
              <div class="eval-modal-field"><label class="eval-modal-label">评测说明</label><input v-model="skillForm.description" class="eval-mr-input" placeholder="补充本次评测说明" /></div>
            </details>
            <p v-if="skillSubmitError" class="eval-modal-error" role="alert">{{ skillSubmitError }}</p>
          </fieldset>

          <!-- 是否生成知识改进意见并回流（建设中，默认不勾选且不可用；仅在选择任务类型后显示） -->
          <div v-if="evalForm.taskType && evalForm.taskType !== 'skill'" class="eval-modal-field">
            <label class="eval-modal-label">是否生成知识改进意见并回流</label>
            <div class="eval-mode-list">
              <label class="eval-mode-item disabled reflow-disabled">
                <input
                    type="checkbox"
                    v-model="evalForm.hasReflow"
                    disabled
                />
                <span class="eval-mode-label">生成知识改进意见并回流</span>
                <span class="eval-mode-tag">建设中</span>
              </label>
            </div>
          </div>
        </div>
        <div class="eval-modal-foot">
          <button class="eval-modal-btn cancel" @click="closeEvalModal">取消</button>
          <button class="eval-modal-btn confirm" :disabled="skillSubmitting || selectingAllSkills" @click="submitEvalTask">{{ skillSubmitting ? '提交中…' : '开始评测' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>
