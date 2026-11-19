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
            <span v-if="skillReportsLoading" class="skill-list-hint" role="status">正在加载当前页报告…</span>
          </div>
          <p v-if="!skillScopeValid()" class="skill-state">请先选择有效的部门、产品或 PDU。</p>
          <p v-if="skillObservationNotice" class="skill-report-notice">{{ skillObservationNotice }}</p>
          <div v-if="skillSubmission" class="skill-submission-notice" role="status">
            <strong>已确认提交 {{ skillSubmission.submitted_count }} / {{ skillSubmission.total_count }} 项</strong>
            <span v-if="skillSubmission.unconfirmed_count">，{{ skillSubmission.unconfirmed_count }} 项未确认。请先确认结果，再决定是否重试。</span>
            <span v-else>，结果会自动刷新。</span>
            <details v-if="submissionIssues.length"><summary>查看未确认项</summary><p v-for="item in submissionIssues" :key="item.key">{{ item.name }} · {{ skillModeLabel(item.mode) }}：{{ item.error }}</p></details>
            <p v-if="Object.keys(pendingSkillObservations).length">正在等待所选模式的新记录或报告；新记录出现前仍可能显示上次结果。</p>
            <button type="button" class="skill-text-button" @click="skillSubmission = null">收起提示</button>
          </div>
          <div v-if="skillResultsError" class="skill-state skill-state--error" role="alert">{{ skillResultsError }} <button class="skill-text-button" :disabled="skillResultsLoading" @click="loadSkillResults()">重试</button></div>
          <p v-if="skillResultsLoading && !skillResults.length" class="empty-text" role="status">正在加载 Skill…</p>
          <div v-if="skillResults.length" class="table-wrap" :aria-busy="skillResultsLoading">
            <table class="asset-table eval-table skill-results-table" v-col-resize data-col-resize-key="kg-skill-results-v5">
              <colgroup><col style="width:28%" /><col v-for="key in SKILL_MODE_KEYS" :key="key" style="width:24%" /></colgroup>
              <thead class="asset-table-head"><tr><th>Skill</th><th v-for="key in SKILL_MODE_KEYS" :key="key">{{ skillModeLabel(key) }}</th></tr></thead>
              <tbody><tr v-for="skill in skillResults" :key="skill.skill_id" class="hierarchy-row hierarchy-row-product clickable-row" :class="{ 'row-active': activeSkill?.skill_id === skill.skill_id }" @click="openSkillDrawer(skill)">
                <td><button class="skill-name-link" @click.stop="openSkillDrawer(skill)">{{ skill.skill_name || skill.name || '未命名 Skill' }}</button><p v-if="hasSkillMatchError(skill)" class="skill-match-error">{{ skill.match_error || '评测记录关联异常' }}</p></td>
                <td v-for="key in SKILL_MODE_KEYS" :key="key"><button type="button" class="skill-mode-cell" @click.stop="openSkillDrawer(skill, key)">
                  <span class="skill-mode-meta">
                    <span class="skill-mode-status" :class="skillModeResult(skill, key)?.status || 'not_evaluated'">{{ hasSkillMatchError(skill) ? '关联异常' : skillModeStatusLabel(skillModeResult(skill, key)?.status || 'not_evaluated') }}</span>
                    <span class="skill-mode-version">评测版本 {{ skillModeVersion(skill, key) }}</span>
                    <span v-if="isAwaitingSkillSource(skill.skill_id, key)" class="skill-observation-note">等待新记录</span>
                    <span v-if="!hasSkillMatchError(skill) && skillModeResult(skill, key)?.status === 'completed' && skillReportState(skillModeResult(skill, key))" class="skill-report-state" :class="{ 'has-error': skillModeResult(skill, key)?.report_status === 'error' }">{{ skillReportState(skillModeResult(skill, key)) }}</span>
                  </span>
                  <span v-for="entry in skillModeGlance(skill, key)" :key="entry.key" class="skill-cell-metric">{{ entry.label }} <b>{{ entry.value }}</b><small v-if="entry.detail">（{{ entry.detail }}）</small></span>
                </button></td>
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
              <header class="skill-drawer-header">
                <div class="skill-drawer-heading">
                  <p>Skill 评测结果</p>
                  <h3 id="skill-eval-title">{{ activeSkill?.skill_name || activeSkill?.name || '未命名 Skill' }}</h3>
                </div>
                <span v-if="activeSkill && !hasSkillMatchError(activeSkill)" class="status-pill" :class="activeSkill.status">{{ skillStatusLabel(activeSkill.status) }}</span>
                <button type="button" class="drawer-close" aria-label="关闭 Skill 评测结果" @click="closeSkillDrawer">×</button>
              </header>
              <template v-if="activeSkill && activeSkillResult">
                <div class="skill-mode-switcher" role="group" aria-label="选择评测模式">
                  <button v-for="mode in skillEvalModes" :key="mode.key" type="button" class="skill-mode-tab"
                          :class="skillModeClass(mode.key)" :aria-pressed="activeSkillMode === mode.key"
                          aria-controls="skill-mode-results" @click="selectSkillResultMode(mode.key)">
                    <span>{{ mode.label }}</span>
                    <span v-if="!hasSkillMatchError(activeSkill)" class="skill-mode-status" :class="skillModeResult(activeSkill, mode.key)?.status || 'not_evaluated'">
                      {{ skillModeStatusLabel(skillModeResult(activeSkill, mode.key)?.status || 'not_evaluated') }}
                    </span>
                  </button>
                </div>
                <div ref="skillDrawerBody" class="drawer-body skill-drawer-body" tabindex="0" aria-label="评测结果滚动区域" :aria-busy="skillResultsLoading">
                  <div v-if="skillResultsError" class="skill-state skill-state--error" role="alert">{{ skillResultsError }}</div>
                  <section id="skill-mode-results" class="skill-mode-panel" :class="skillModeClass(activeSkillMode)" :aria-label="skillModeLabel(activeSkillMode) + '结果'">
                    <p v-if="hasSkillMatchError(activeSkill)" class="skill-state skill-state--error" role="alert">{{ activeSkill.match_error || '评测记录关联异常，请检查 Skill 名称。' }}</p>
                    <template v-else>
                      <div v-if="activeSkillResult.result?.version || activeSkillResult.result?.created_at || activeSkillResult.reportVersion" class="skill-report-meta">
                        <div class="skill-task-meta">
                          <span v-if="activeSkillResult.result?.version">评测版本 <strong>{{ activeSkillResult.result.version }}</strong></span>
                          <span v-if="activeSkillResult.result?.created_at">开始时间 <strong>{{ activeSkillResult.result.created_at }}</strong></span>
                        </div>
                        <label v-if="activeSkillResult.reports.length > 1" class="skill-report-version-picker">
                          报告版本
                          <select :value="activeSkillResult.reportVersion" @change="selectSkillReportVersion(activeSkill.skill_id, ($event.target as HTMLSelectElement).value)">
                            <option v-for="report in activeSkillResult.reports" :key="report.version" :value="report.version">{{ report.version || '当前版本' }}</option>
                          </select>
                        </label>
                        <span v-else-if="activeSkillResult.reportVersion && activeSkillResult.reportVersion !== activeSkillResult.result?.version">
                          报告版本 <strong>{{ activeSkillResult.reportVersion }}</strong>
                        </span>
                      </div>
                      <p v-if="isAwaitingSkillSource(activeSkill.skill_id, activeSkillMode)" class="skill-report-notice" role="status">本次已提交，正在等待新记录。下方可能仍为上次评测结果。</p>
                      <div v-if="!activeSkillReport" class="skill-state skill-report-section" :class="{ 'skill-state--error': activeSkillResult.result?.status === 'failed' || activeSkillResult.result?.report_status === 'error' }" role="status">
                        {{ skillModeNotice(activeSkillResult.result) }}
                      </div>
                      <template v-else :key="activeSkillMode + ':' + activeSkillResult.reportVersion">
                        <section v-if="activeSkillReport.primaryMetrics.length || activeSkillReport.notes.length || activeSkillReport.triggerStats?.groups.length" class="skill-report-section">
                          <h4 class="skill-report-section-head">结果概览</h4>
                          <div class="skill-report-overview">
                            <dl v-if="activeSkillReport.primaryMetrics.length" class="skill-report-summary">
                              <div v-for="entry in activeSkillReport.primaryMetrics" :key="entry.key" class="skill-report-metric">
                                <dt>{{ entry.label }}</dt>
                                <dd><strong>{{ entry.value }}</strong><small v-if="entry.detail">（{{ entry.detail }}）</small></dd>
                              </div>
                            </dl>
                            <dl v-if="activeSkillReport.otherMetrics.length" class="skill-report-secondary">
                              <div v-for="entry in activeSkillReport.otherMetrics" :key="entry.key">
                                <dt>{{ entry.label }}</dt>
                                <dd>{{ entry.value }}<small v-if="entry.detail">（{{ entry.detail }}）</small></dd>
                              </div>
                            </dl>
                            <div v-if="activeSkillReport.triggerStats?.groups.length" class="skill-trigger-breakdown">
                              <span v-for="group in activeSkillReport.triggerStats.groups" :key="group.type">{{ group.label }} <strong>通过 {{ group.passed }} / {{ group.total }}</strong></span>
                            </div>
                            <p v-if="activeSkillReport.triggerStats?.unknown" class="skill-report-note">未判定用例不计入通过率。</p>
                            <dl v-if="activeSkillReport.notes.length" class="skill-report-fields">
                              <div v-for="entry in activeSkillReport.notes" :key="entry.key" class="skill-report-field"><dt>{{ entry.label }}</dt><dd>{{ entry.value }}</dd></div>
                            </dl>
                          </div>
                        </section>
                        <p v-if="activeSkillReport.triggerStats?.available === false" class="skill-report-notice">报告暂未提供可用于统计的用例数据。</p>

                        <section v-if="activeSkillReport.triggerCases.length" class="skill-report-section">
                          <h4 class="skill-report-section-head">触发用例 <span>{{ activeSkillReport.triggerCases.length }} 条</span></h4>
                          <div class="skill-case-row skill-case-trigger skill-case-columns" aria-hidden="true">
                            <span>测试任务</span><span>用例类型</span><span>预期触发</span><span>实际触发</span><span>判定</span>
                          </div>
                          <component v-for="item in activeSkillReport.triggerCases" :is="item.fields.length ? 'details' : 'div'" :key="item.index" class="skill-report-row">
                            <component :is="item.fields.length ? 'summary' : 'div'" class="skill-report-row-head skill-case-row skill-case-trigger">
                              <span class="skill-case-title">{{ item.title }}</span>
                              <span class="skill-case-cell skill-case-type"><span class="skill-visually-hidden">用例类型 </span>{{ item.type }}</span>
                              <span class="skill-case-cell skill-case-expected"><span class="skill-case-label">预期 </span>{{ item.expected }}</span>
                              <span class="skill-case-cell skill-case-actual"><span class="skill-case-label">实际 </span>{{ item.actual }}</span>
                              <span class="skill-case-verdict" :class="item.verdict"><span class="skill-visually-hidden">判定 </span>{{ item.verdictLabel }}</span>
                            </component>
                            <dl v-if="item.fields.length" class="skill-report-row-body skill-report-fields">
                              <div v-for="field in item.fields" :key="field.key" class="skill-report-field"><dt>{{ field.label }}</dt><dd>{{ field.value }}</dd></div>
                            </dl>
                          </component>
                        </section>

                        <section v-if="activeSkillReport.qualityCases.length" class="skill-report-section">
                          <h4 class="skill-report-section-head">质量用例 <span>{{ activeSkillReport.qualityCases.length }} 条</span></h4>
                          <div class="skill-case-row skill-case-columns" aria-hidden="true">
                            <span>测试任务</span><span>得分</span><span>判定</span><span>检查点通过</span>
                          </div>
                          <component v-for="item in activeSkillReport.qualityCases" :is="item.hasDetails ? 'details' : 'div'" :key="item.index" class="skill-report-row">
                            <component :is="item.hasDetails ? 'summary' : 'div'" class="skill-report-row-head skill-case-row">
                              <span class="skill-case-title">{{ item.title }}</span>
                              <span class="skill-case-cell skill-case-score"><span class="skill-case-label">得分 </span><strong>{{ item.score }}</strong></span>
                              <span class="skill-case-verdict" :class="item.verdict"><span class="skill-visually-hidden">判定 </span>{{ item.verdictLabel }}</span>
                              <span class="skill-case-cell skill-case-assertions"><span class="skill-case-label">检查点通过 </span>{{ item.assertionSummary }}</span>
                            </component>
                            <div v-if="item.hasDetails" class="skill-report-row-body">
                              <div v-if="item.caseId || item.duration" class="skill-task-meta">
                                <span v-if="item.caseId">用例 ID {{ item.caseId }}</span><span v-if="item.duration">耗时 {{ item.duration }}</span>
                              </div>
                              <dl v-if="item.fields.length" class="skill-report-fields">
                                <div v-for="field in item.fields" :key="field.key" class="skill-report-field"><dt>{{ field.label }}</dt><dd>{{ field.value }}</dd></div>
                              </dl>
                              <section v-if="item.assertions.length" class="skill-report-subsection">
                                <h5>检查点判定 <span>{{ item.assertions.length }} 条</span></h5>
                                <div class="skill-assertion-list">
                                  <article v-for="(assertion, index) in item.assertions" :key="index" class="skill-assertion">
                                    <div class="skill-assertion-heading">
                                      <span class="skill-case-verdict" :class="assertion.verdict">{{ assertion.verdictLabel }}</span>
                                      <span v-if="assertion.priority !== '—'" class="skill-report-note">{{ assertion.priority }}</span>
                                      <strong>{{ assertion.checkPoint }}</strong>
                                    </div>
                                    <p v-if="assertion.reason">{{ assertion.reason }}</p>
                                    <div v-if="assertion.confidence !== null || assertion.evidenceTurn !== null" class="skill-task-meta">
                                      <span v-if="assertion.confidence !== null">置信度 {{ assertion.confidence }}</span>
                                      <span v-if="assertion.evidenceTurn !== null">证据回合 {{ assertion.evidenceTurn }}</span>
                                    </div>
                                  </article>
                                </div>
                              </section>
                              <section v-else-if="item.expectItems.length" class="skill-report-subsection">
                                <h5>预期检查点</h5>
                                <ul class="skill-report-actions"><li v-for="(point, index) in item.expectItems" :key="index">{{ point }}</li></ul>
                              </section>
                            </div>
                          </component>
                        </section>

                        <section v-if="activeSkillReport.dimensions.length" class="skill-report-section">
                          <h4 class="skill-report-section-head">评分维度 <span>{{ activeSkillReport.dimensions.length }} 项</span></h4>
                          <component v-for="(dimension, index) in activeSkillReport.dimensions" :is="dimension.hasDetails ? 'details' : 'div'" :key="index" class="skill-report-row">
                            <component :is="dimension.hasDetails ? 'summary' : 'div'" class="skill-report-row-head skill-dimension-row">
                              <strong>{{ dimension.title }}</strong>
                              <span class="skill-dimension-score">得分 <strong>{{ dimension.score }}</strong></span>
                            </component>
                            <div v-if="dimension.hasDetails" class="skill-report-row-body">
                              <dl v-if="dimension.extra.length" class="skill-report-fields">
                                <div v-for="entry in dimension.extra" :key="entry.key" class="skill-report-field"><dt>{{ entry.label }}</dt><dd>{{ entry.value }}</dd></div>
                              </dl>
                              <section v-for="group in dimension.groups" :key="group.key" class="skill-report-subsection">
                                <h5>{{ group.label }} <span>{{ group.items.length }} 条</span></h5>
                                <article v-for="item in group.items" :key="item.index" class="skill-dimension-item">
                                  <strong>{{ item.title }}</strong>
                                  <dl v-if="item.fields.length" class="skill-report-fields">
                                    <div v-for="entry in item.fields" :key="entry.key" class="skill-report-field"><dt>{{ entry.label }}</dt><dd>{{ entry.value }}</dd></div>
                                  </dl>
                                </article>
                              </section>
                              <section v-if="dimension.actions.length" class="skill-report-subsection">
                                <h5>改进建议</h5>
                                <ul class="skill-report-actions"><li v-for="action in dimension.actions" :key="action">{{ action }}</li></ul>
                              </section>
                            </div>
                          </component>
                        </section>

                        <section v-for="group in activeSkillReport.groups" :key="group.key" class="skill-report-section">
                          <h4 class="skill-report-section-head">{{ group.label }} <span>{{ group.items.length }} 条</span></h4>
                          <component v-for="item in group.items" :is="item.fields.length ? 'details' : 'div'" :key="item.index" class="skill-report-row">
                            <component :is="item.fields.length ? 'summary' : 'div'" class="skill-report-row-head skill-finding-row">
                              <span>{{ item.title }}</span>
                            </component>
                            <dl v-if="item.fields.length" class="skill-report-row-body skill-report-fields">
                              <div v-for="entry in item.fields" :key="entry.key" class="skill-report-field"><dt>{{ entry.label }}</dt><dd>{{ entry.value }}</dd></div>
                            </dl>
                          </component>
                        </section>

                        <section v-if="activeSkillReport.actions.length" class="skill-report-section">
                          <h4 class="skill-report-section-head">改进建议</h4>
                          <ul class="skill-report-actions skill-report-actions--section">
                            <li v-for="action in activeSkillReport.actions" :key="action">{{ action }}</li>
                          </ul>
                        </section>

                        <details v-if="activeSkillReport.supplements.length" class="skill-report-section skill-report-appendix" :open="!activeSkillReport.hasMainContent">
                          <summary class="skill-report-section-head skill-report-row-head"><h4>补充信息</h4></summary>
                          <div class="skill-report-row-body">
                            <section v-for="section in activeSkillReport.supplements" :key="section.key" class="skill-report-subsection">
                              <h5>{{ section.label }}</h5>
                              <dl class="skill-report-fields">
                                <div v-for="entry in section.entries" :key="entry.key" class="skill-report-field"><dt>{{ entry.label }}</dt><dd>{{ entry.value }}</dd></div>
                              </dl>
                            </section>
                          </div>
                        </details>
                        <p v-else-if="!activeSkillReport.hasMainContent" class="skill-state skill-report-section">报告暂未提供指标或明细。</p>
                      </template>
                    </template>
                  </section>
                </div>
              </template>
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
      <div class="eval-modal" :class="{ 'eval-modal--skill': evalForm.taskType === 'skill' }">
        <div class="eval-modal-head">
          <div class="eval-modal-heading">
            <h3>{{ evalForm.taskType === 'skill' ? '发起 Skill 评测' : '新建评测任务' }}</h3>
          </div>
          <button type="button" class="eval-modal-close" aria-label="关闭" @click="closeEvalModal">&times;</button>
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
            <fieldset class="skill-modal-mode-field">
              <legend class="skill-modal-field-label">选择评测模式 <span class="skill-modal-field-hint">可多选</span></legend>
              <div class="skill-modal-mode-list">
                <label
                    v-for="mode in skillEvalModes"
                    :key="mode.key"
                    class="eval-mode-item"
                    :class="[skillModeClass(mode.key), { active: skillForm.modes.has(mode.key) }]"
                >
                  <input
                      type="checkbox"
                      :checked="skillForm.modes.has(mode.key)"
                      @change="toggleSkillMode(mode.key)"
                  />
                  <span class="eval-mode-label">{{ mode.label }}</span>
                </label>
              </div>
            </fieldset>

            <div>
              <div class="skill-modal-picker-heading">
                <span class="skill-modal-field-label">选择 Skill</span>
                <span class="skill-selected-count">已选 {{ skillForm.selected.size }} 个</span>
              </div>
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

<script lang="ts" setup>
import { ref, shallowRef, reactive, computed, watch, nextTick, onBeforeUnmount } from 'vue';
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
    if (hasReadySkillReport(result)) return '';
    if (result.report_status === 'unloaded') return '报告待加载';
    if (result.report_status === 'error') return '报告读取失败';
    return '报告生成中';
  }
  return skillModeStatusLabel(result.status);
}
function skillModeNotice(result: SkillEvalModeResult | null): string {
  if (result?.status === 'failed') return `执行失败：${skillErrorText(result.error || '评测服务未返回失败原因')}`;
  if (result?.report_status === 'error') return `报告读取失败：${result.report_error || '请稍后重新搜索'}`;
  if (result?.report_status === 'unloaded') return '正在加载报告，请稍候。';
  if (result?.status === 'completed' && !hasReadySkillReport(result)) return '执行已完成，报告生成中，结果会自动更新。';
  return `${skillModeStatusLabel(result?.status || 'not_evaluated')}，暂无可查看的报告。`;
}
function skillModeVersion(skill: SkillEvalSkillResult, mode: string): string { return skillModeResult(skill, mode)?.version || '—'; }
function skillTimestamp(value: string | null | undefined): number | null {
  if (!value?.trim()) return null;
  // 与后端一致：无时区的 ISO 时间按 UTC 比较，避免浏览器时区改变排序。
  let normalized = value.trim().replace(' ', 'T');
  if (!/(?:Z|[+-]\d{2}:?\d{2})$/i.test(normalized)) normalized += 'Z';
  const timestamp = Date.parse(normalized);
  return Number.isFinite(timestamp) ? timestamp : null;
}
function skillLatestTimestamp(skill: SkillEvalSkillResult): number | null {
  const timestamps = SKILL_MODE_KEYS.map(key => {
    const result = skillModeResult(skill, key);
    return skillTimestamp(result?.updated_at) ?? skillTimestamp(result?.created_at);
  }).filter((value): value is number => value !== null);
  return timestamps.length ? Math.max(...timestamps) : null;
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

const skillForm = reactive({ modes: new Set<string>(['STATIC']), selected: new Set<string>(), keyword: '' });
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

// 收齐轻量状态后筛选分页；只加载当前显示页、抽屉与待确认记录的报告。
const scopedSkillResults = shallowRef<SkillEvalSkillResult[]>([]);
const observedSkillResults = shallowRef<SkillEvalSkillResult[]>([]);
const skillReportLoadedAt = new Map<string, number>();
function shouldDisplaySkillResult(skill: SkillEvalSkillResult): boolean {
  if (skill.skill_status !== '已完成' || hasSkillMatchError(skill)) return false;
  return SKILL_MODE_KEYS.some(mode => {
    const result = skillModeResult(skill, mode);
    if (!result) return false;
    const status = normalizeSkillModeStatus(result.status);
    const evaluating = !isSkillModeTerminal(result);
    const generatingReport = status === 'completed' && ['pending', 'unloaded'].includes(result.report_status);
    const hasReport = hasReadySkillReport(result) && hasReportValue(result.report);
    return evaluating || generatingReport || hasReport;
  });
}
const displayedSkillResults = computed(() => scopedSkillResults.value
    .filter(shouldDisplaySkillResult)
    .map(skill => ({ skill, timestamp: skillLatestTimestamp(skill) ?? -Infinity }))
    .sort((left, right) => right.timestamp - left.timestamp || left.skill.skill_id.localeCompare(right.skill.skill_id))
    .map(item => item.skill));
const skillResults = shallowRef<SkillEvalSkillResult[]>([]), skillResultsLoading = ref(false), skillResultsError = ref('');
const skillReportsLoading = ref(false);
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
  const pageSize = 100, concurrency = 3;
  const fetchPage = (page: number) => kcService.getSkillEvalResults({ ...scope, keyword, page, page_size: pageSize, include_reports: false }, signal);
  const first = await fetchPage(1);
  const byId = new Map((first.items || []).map(skill => [skill.skill_id, skill]));
  let pages = Math.ceil(first.total / pageSize);
  for (let start = 2; start <= pages; start += concurrency) {
    const count = Math.min(concurrency, pages - start + 1);
    const results = await Promise.all(Array.from({ length: count }, (_, index) => fetchPage(start + index)));
    for (const result of results) {
      for (const skill of result.items || []) byId.set(skill.skill_id, skill);
      pages = Math.max(pages, Math.ceil(result.total / pageSize));
    }
  }
  return [...byId.values()];
}
const skillDrawerVisible = ref(false), skillDrawerPanel = ref<HTMLElement | null>(null);
const skillDrawerBody = ref<HTMLElement | null>(null);
const activeSkill = shallowRef<SkillEvalSkillResult | null>(null), activeSkillMode = ref('STATIC');
const selectedSkillReportVersions = ref<Record<string, string>>({});
let skillDrawerTrigger: HTMLElement | null = null;
const skillSubmission = ref<SkillEvalCreateResult | null>(null);
const submissionIssues = computed(() => (skillSubmission.value?.items || []).flatMap(skill => Object.entries(skill.modes || {})
    .filter(([, mode]) => mode.submission_status !== 'submitted').map(([key, mode]) => ({ key: `${skill.skill_id}:${key}`, name: skill.skill_name, mode: key, error: skillErrorText(mode.error || '未确认提交成功，请先确认结果') }))));
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
        skillObservationNotice.value = '部分所选模式尚未确认新结果，已停止等待。可重新搜索查看，请先确认结果再决定是否重试。';
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
      if (item.seen && isSkillModeTerminal(result) && !(result?.status === 'completed' && ['pending', 'unloaded'].includes(result.report_status))) delete entries[mode];
    });
    if (!Object.keys(entries).length) delete pendingSkillObservations[skill.skill_id];
  });
}
let skillPollTimer: ReturnType<typeof setTimeout> | null = null;
let skillContext = 0, skillDisposed = false, skillRefreshAgain = false;
let skillResultsRequest: Promise<void> | null = null;
let skillReportRequest: Promise<void> | null = null, skillReportAgain = false, skillReportRevision = 0;
let skillAbort = new AbortController();
function stopPollingSkillResults() { if (skillPollTimer) clearTimeout(skillPollTimer); skillPollTimer = null; }
function needsSkillRefresh(): boolean {
  return Object.keys(pendingSkillObservations).length > 0 || scopedSkillResults.value.some(skill => skill.skill_status === '已完成' && !hasSkillMatchError(skill) && SKILL_MODE_KEYS.some(key => {
    const result = skillModeResult(skill, key);
    return !isSkillModeTerminal(result);
  })) || [...skillResults.value, ...(activeSkill.value ? [activeSkill.value] : [])].some(skill => SKILL_MODE_KEYS.some(key => skillModeResult(skill, key)?.report_status === 'pending'));
}
function scheduleSkillRefresh() {
  stopPollingSkillResults();
  if (!skillSubmitting.value && !skillReportsLoading.value && !skillDisposed && evalTab.value === 'skill' && skillScopeValid() && needsSkillRefresh() && !skillResultsError.value) {
    skillPollTimer = setTimeout(() => void loadSkillResults(true), 10000);
  }
}
async function findScopedSkillResults(ids: Set<string>, scope: ReturnType<typeof skillScopeParams>, signal: AbortSignal): Promise<SkillEvalSkillResult[]> {
  const found: SkillEvalSkillResult[] = [];
  const requested = [...ids];
  for (let start = 0; start < requested.length; start += 100) {
    const res = await kcService.getSkillEvalResults({ ...scope, skill_ids: requested.slice(start, start + 100), page: 1, page_size: 100, include_reports: false }, signal);
    found.push(...(res.items || []));
  }
  return found;
}
function preserveLoadedSkillReports(items: SkillEvalSkillResult[]): SkillEvalSkillResult[] {
  const previous = new Map(scopedSkillResults.value.map(skill => [skill.skill_id, skill]));
  return items.map(skill => {
    const before = previous.get(skill.skill_id);
    SKILL_MODE_KEYS.forEach(mode => {
      const current = skillModeResult(skill, mode), old = before ? skillModeResult(before, mode) : null;
      // 只复用同一任务、更新时间和版本的已就绪报告；未就绪/失败的报告仍可重试。
      if (Date.now() - (skillReportLoadedAt.get(skill.skill_id) || 0) < 60000 && current?.report_status === 'unloaded' && hasReadySkillReport(old) && current.external_task_id === old?.external_task_id && current.updated_at === old?.updated_at && current.version === old?.version) {
        current.report = old!.report; current.report_status = 'ready'; current.report_error = null;
      }
    });
    return skill;
  });
}
function updateActiveSkillResult() {
  if (!activeSkill.value) return;
  const latest = displayedSkillResults.value.find(skill => skill.skill_id === activeSkill.value?.skill_id);
  if (latest) activeSkill.value = latest;
  else closeSkillDrawer();
}
function hydrateVisibleSkillReports(): Promise<void> {
  if (skillDisposed || !skillScopeValid() || evalTab.value !== 'skill') return Promise.resolve();
  if (skillReportRequest) { skillReportAgain = true; return skillReportRequest; }
  const context = skillContext, revision = skillReportRevision, scope = skillScopeParams(), signal = skillAbort.signal;
  skillReportsLoading.value = true;
  stopPollingSkillResults();
  const isCurrent = () => context === skillContext && revision === skillReportRevision && !skillDisposed && !signal.aborted && evalTab.value === 'skill';
  skillReportRequest = (async () => {
    while (isCurrent()) {
      const visible = new Set([...(activeSkill.value ? [activeSkill.value.skill_id] : []), ...skillResults.value.map(skill => skill.skill_id)]);
      const candidates = new Map([...observedSkillResults.value, ...scopedSkillResults.value].map(skill => [skill.skill_id, skill]));
      const needsReport = (id: string) => {
        const skill = candidates.get(id);
        return skill && SKILL_MODE_KEYS.some(mode => skillModeResult(skill, mode)?.report_status === 'unloaded');
      };
      const visibleIds = [...visible].filter(needsReport);
      const batchSize = 3;
      // 每批返回就更新当前页。等待确认的新任务在可见报告之后批量跟踪。
      const batches = (visibleIds.length
          ? [visibleIds.slice(0, batchSize), visibleIds.slice(batchSize, batchSize * 2)]
          : [Object.keys(pendingSkillObservations).filter(needsReport).slice(0, 100)])
          .filter(ids => ids.length);
      if (!batches.length) break;
      const results = await Promise.allSettled(batches.map(async ids => {
        const res = await kcService.getSkillEvalResults({ ...scope, skill_ids: ids, page: 1, page_size: 100, include_reports: true }, signal);
        if (!isCurrent()) return;
        const requested = new Set(ids), loaded = new Map((res.items || []).map(skill => [skill.skill_id, skill]));
        const merge = (items: SkillEvalSkillResult[]) => items.flatMap(skill => requested.has(skill.skill_id) ? (loaded.has(skill.skill_id) ? [loaded.get(skill.skill_id)!] : []) : [skill]);
        scopedSkillResults.value = merge(scopedSkillResults.value);
        observedSkillResults.value = merge(observedSkillResults.value).filter(skill => pendingSkillObservations[skill.skill_id]);
        loaded.forEach((_, id) => skillReportLoadedAt.set(id, Date.now()));
        observeSkillResults(res.items || []);
        applySkillResultPage();
        updateActiveSkillResult();
      }));
      for (const result of results) {
        if (result.status === 'rejected') throw result.reason;
      }
    }
  })().catch(error => {
    if (isCurrent()) skillResultsError.value = `当前页报告加载失败，已保留列表：${skillErrorText(error)}`;
  }).finally(() => {
    skillReportRequest = null;
    if (context === skillContext) skillReportsLoading.value = false;
    if (skillReportAgain && !skillDisposed) { skillReportAgain = false; void hydrateVisibleSkillReports(); }
    else scheduleSkillRefresh();
  });
  return skillReportRequest;
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
      skillReportRevision++;
      scopedSkillResults.value = preserveLoadedSkillReports(all);
      observedSkillResults.value = [];
      skillResultsError.value = '';
      observeSkillResults(all);
      applySkillResultPage();
      updateActiveSkillResult();
      skillResultsLoading.value = false;
      void hydrateVisibleSkillReports();
      const missing = new Set(Object.keys(pendingSkillObservations).filter(id => !all.some(skill => skill.skill_id === id)));
      if (missing.size) {
        const extra = await findScopedSkillResults(missing, scope, signal);
        if (context !== skillContext || skillDisposed) return;
        observeSkillResults(extra);
        // 搜索条件可能隐藏所选 Skill；仍跟踪它们的新任务与报告。
        observedSkillResults.value = extra.filter(skill => pendingSkillObservations[skill.skill_id]);
        void hydrateVisibleSkillReports();
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
function onSkillFilterChange() { skillReportRevision++; skillPage.value = 1; skillJumpPage.value = 1; closeSkillDrawer(); void loadSkillResults(); }
function clearSkillFilter() { skillFilter.keyword = ''; onSkillFilterChange(); }
function goToSkillPage(page: number | string) {
  const value = Number(page); if (!Number.isInteger(value) || value < 1 || value > skillTotalPages.value || value === skillPage.value) return;
  skillPage.value = value; skillJumpPage.value = value; closeSkillDrawer(); applySkillResultPage(); void hydrateVisibleSkillReports();
}
function onSkillPageSizeChange() { skillPage.value = 1; skillJumpPage.value = 1; closeSkillDrawer(); applySkillResultPage(); void hydrateVisibleSkillReports(); }
function skillResultKey(skillId: string): string { return JSON.stringify([activeSkillMode.value, skillId]); }
function selectSkillReportVersion(id: string, version: string) { selectedSkillReportVersions.value[skillResultKey(id)] = version; }
function selectSkillResultMode(mode: string) {
  activeSkillMode.value = normalizeSkillMode(mode);
  if (skillDrawerBody.value) skillDrawerBody.value.scrollTop = 0;
}
function openSkillDrawer(skill: SkillEvalSkillResult, mode = 'STATIC') {
  skillDrawerTrigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  activeSkill.value = skill; activeSkillMode.value = mode; skillDrawerVisible.value = true; selectedSkillReportVersions.value = {};
  void hydrateVisibleSkillReports();
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
const activeSkillResult = computed(() => {
  const skill = activeSkill.value;
  if (!skill) return null;
  const source = skillModeResult(skill, activeSkillMode.value);
  const reports = parsedSkillReports(skill, activeSkillMode.value);
  const selected = selectedSkillReportVersions.value[skillResultKey(skill.skill_id)];
  const preferred = source?.version?.replace(/^v/i, '');
  const current = reports.find(report => report.version === selected)
      || reports.find(report => report.version.replace(/^v/i, '') === preferred)
      || reports[0];
  return { reports, reportVersion: current?.version || '', result: source ? { ...source, report: current?.report || null } : null };
});

async function submitSkillEvaluation() {
  if (skillSubmitting.value || selectingAllSkills.value || !skillScopeValid()) return;
  if (!skillForm.modes.size) { skillSubmitError.value = '请至少选择一种评测模式。'; return; }
  const ids = [...skillForm.selected];
  if (!ids.length) { skillSubmitError.value = '请至少选择一个 Skill。'; return; }
  const context = skillContext, scope = skillScopeParams(), modes = [...skillForm.modes];
  const creator = props.currentUserId || undefined;
  skillSubmitting.value = true; skillSubmitError.value = ''; skillObservationNotice.value = '';
  const payload = { ...scope, skill_ids: ids, modes, creator };
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
    skillSubmitError.value = rejected ? `提交校验失败：${skillErrorText(error)}` : submitted ? `已收到提交结果，刷新失败：${skillErrorText(error)}` : `未能确认提交结果：${skillErrorText(error)}。若请求超时，请先确认结果再决定是否重试。`;
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
  // 详情页省略重复的 D10 通用评分说明。
  delete report.d10_low_confidence_note;
  return report;
}
// ---- Skill 报告渲染：每项内容归入对应区块，保留证据、零值与未知字段 ----
const REPORT_SUMMARY_LABELS: Record<string, string> = {
  grade: '等级', total: '总分', percent: '得分率',
  positive_trigger_rate: '正触发率', negative_false_trigger_rate: '负向误触发率',
  accuracy: '准确率', pass_rate: '通过率', total_cost_time: '总耗时',
  score: '得分', total_cases: '用例总数', passed_cases: '通过用例', failed_cases: '失败用例数',
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
  raw_score: '调整前得分',
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
    TRIGGER: ['passed_cases', 'pass_rate', 'total_cases', 'positive_trigger_rate', 'negative_false_trigger_rate', 'accuracy'],
    QUALITY: ['score', 'overall_score', 'total_score', 'total', 'average_score', 'avg_score', 'grade', 'percent', 'pass_rate'],
  };
  const caseStats = triggerCaseStats(report);
  const derived = mode === 'TRIGGER' && caseStats.available ? triggerStatsEntries(caseStats) : [];
  const scoreKeys = ['total', 'total_score', 'overall_score', 'score'];
  const maximum = [report.max_score, report.max].map(finiteScore).find(value => value !== null && value > 0) ?? null;
  const hasScoreFraction = maximum !== null && scoreKeys.some(key => finiteScore(report[key]) !== null);
  const entries = [...new Set([...(priority[mode] || []), ...Object.keys(REPORT_SUMMARY_LABELS)])]
      .filter(key => !(mode === 'QUALITY' && key === 'total_cost_time') && !(hasScoreFraction && ['max', 'max_score'].includes(key)) && report[key] !== undefined && report[key] !== null && typeof report[key] !== 'object' && !derived.some(entry => entry.key === key))
      .map(key => {
        const score = finiteScore(report[key]), totalCases = finiteScore(report.total_cases);
        const value = hasScoreFraction && scoreKeys.includes(key) && score !== null
            ? `${formatScore(score)} / ${formatScore(maximum!)}`
            : key === 'passed_cases' && score !== null && totalCases !== null
                ? `${formatScore(score)} / ${formatScore(totalCases)}` : formatReportValue(key, report[key]);
        return { key, label: REPORT_SUMMARY_LABELS[key], value };
      });
  if (mode === 'QUALITY') {
    const summary = qualitySummaryEntries(report);
    summary.forEach(entry => { const index = entries.findIndex(item => item.key === entry.key); if (index >= 0) entries.splice(index, 1); });
    entries.push(...summary);
    if (reportDimensions(report).length) entries.push({ key: 'dimension_count', label: '评分维度', value: String(reportDimensions(report).length) });
  }
  return [...derived, ...entries].filter(entry => mode !== 'TRIGGER' || entry.key !== 'failed_cases').map(entry => {
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
    { key: 'passed_cases', label: '通过用例', value: stats.available ? `${stats.passed} / ${stats.total}` : '—' },
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
    const expectItems = (Array.isArray(item.expect_items) ? item.expect_items : []).map((point: any) => formatCellValue(isReportObject(point) ? point.check_point : point));
    return { index, title: formatCellValue(item.task || item.case_name || item.title || item.name || item.case_id || '未命名测试任务'),
      score: score === null ? '—' : formatScore(score), verdict, verdictLabel: verdict === 'pass' ? '通过' : verdict === 'fail' ? '未通过' : '未判定',
      assertionSummary: assertions.length ? `${assertions.filter((assertion: { verdict: string }) => assertion.verdict === 'pass').length} / ${assertions.length}` : '—',
      assertions, fields, expectItems, caseId: item.case_id ? String(item.case_id) : '', duration: duration === null ? '' : `${formatScore(duration)} 秒`,
      hasDetails: Boolean(item.case_id || duration !== null || fields.length || assertions.length || expectItems.length) };
  });
}
const REPORT_GROUPS = [
  { key: 'critical_issues', label: '关键问题' },
  { key: 'findings', label: '问题发现' },
  { key: 'check_issues', label: '预检问题' },
  { key: 'results', label: '用例 / 结果明细' },
  { key: 'improvements', label: '改进建议' },
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
        const object = isReportObject(item);
        const entries = object ? reportObjectEntries(item) : [{ key: 'value', label: '内容', value: formatCellValue(item) }];
        const titleKey = object ? ['title', 'case_name', 'task', 'name', 'issue', 'description', 'suggestion', 'message', 'content'].find(key => hasReportValue(item[key])) : 'value';
        const title = object ? (titleKey ? item[titleKey] : undefined) : item;
        return { index, entries, titleKey, title: formatCellValue(title ?? `第 ${index + 1} 条`) };
      });
}
function reportGroups(report: Record<string, any> | null, mode = '') {
  return REPORT_GROUPS.filter(group => group.key !== 'improvements' && !(['QUALITY', 'TRIGGER'].includes(mode) && group.key === 'results'))
      .map(group => ({ ...group, items: reportCollectionItems(report, group.key).map(({ index, title, titleKey, entries }) => ({
        index, title, fields: entries.filter(entry => entry.key !== titleKey),
      })) })).filter(group => group.items.length);
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
const REPORT_PRIMARY_METRICS: Record<string, string[][]> = {
  STATIC: [['total', 'total_score', 'overall_score', 'score'], ['grade'], ['percent']],
  TRIGGER: [['passed_cases'], ['pass_rate', 'accuracy'], ['positive_trigger_rate'], ['negative_false_trigger_rate']],
  QUALITY: [['score', 'overall_score', 'total_score', 'total', 'average_score', 'avg_score', 'average_case_score'], ['passed_cases'], ['pass_rate'], ['assertions_passed']],
};
const REPORT_OVERVIEW_KEYS = new Set(['summary', 'conclusion', 'gate_blocked', 'content']);
const activeSkillReport = computed(() => {
  const report = activeSkillResult.value?.result?.report;
  if (!report) return null;
  const mode = activeSkillMode.value;
  const metrics = reportSummaryEntries(report, mode);
  const primary = (REPORT_PRIMARY_METRICS[mode] || []).flatMap(keys => {
    const metric = keys.map(key => metrics.find(entry => entry.key === key)).find(entry => entry !== undefined);
    return metric ? [metric] : [];
  });
  const primaryMetrics = primary.length ? primary : metrics.slice(0, 4);
  const otherMetrics = metrics.filter(entry => !primaryMetrics.includes(entry));
  const extra = reportExtraEntries(report);
  const notes = extra.filter(entry => REPORT_OVERVIEW_KEYS.has(entry.key));
  const triggerStats = mode === 'TRIGGER' ? triggerCaseStats(report) : null;
  const triggerCases = mode === 'TRIGGER' ? triggerResultRows(report) : [];
  const qualityCases = mode === 'QUALITY' ? qualityResultRows(report) : [];
  const dimensions = reportDimensions(report).map(dimension => {
    const groups = reportGroups(dimension.raw);
    const actions = reportImprovementActions(dimension.raw);
    const title = dimension.id && dimension.id !== dimension.name ? `${dimension.id} ${dimension.name}` : dimension.name;
    return { ...dimension, title, groups, actions, hasDetails: Boolean(dimension.extra.length || groups.length || actions.length) };
  });
  const groups = reportGroups(report, triggerCases.length || qualityCases.length ? mode : '');
  const actions = reportImprovementActions(report);
  const supplements = [
    { key: 'metadata', label: '报告信息', entries: extra.filter(entry => !REPORT_OVERVIEW_KEYS.has(entry.key)) },
    ...reportSupplementSections(report),
    { key: 'additional', label: '其他字段', entries: reportAdditionalEntries(report) },
  ].filter(section => section.entries.length);
  const hasMainContent = Boolean(metrics.length || notes.length || triggerCases.length || qualityCases.length || dimensions.length || groups.length || actions.length);
  return { primaryMetrics, otherMetrics, notes, triggerStats, triggerCases, qualityCases, dimensions, groups, actions, supplements, hasMainContent };
});

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
  skillListPage.value = 1; evaluableSkills.value = []; skillListTotal.value = 0; skillListLoading.value = false; skillListError.value = ''; skillSubmitError.value = '';
  evalModalVisible.value = true;
  if (evalTab.value === 'skill') { void loadSkillModes(); void loadEvaluableSkills(); }
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
  skillContext++; skillReportRevision++; skillAbort.abort(); skillAbort = new AbortController(); stopPollingSkillResults();
  pickerSession++; pickerRequest++; selectingAllSkills.value = false; skillListLoading.value = false;
  evalModalVisible.value = false; skillForm.selected.clear(); evaluableSkills.value = []; skillListTotal.value = 0;
  closeSkillDrawer(); scopedSkillResults.value = []; skillResults.value = []; skillTotal.value = 0; skillResultsError.value = ''; skillResultsLoading.value = false; skillReportsLoading.value = false;
  observedSkillResults.value = []; skillReportLoadedAt.clear();
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

<style scoped>
/* ---- root ---- */
.kg-eval { padding: 4px 0 0; }

/* ---- section ---- */
.section {
  margin-bottom: 20px; padding: 23px;
  border: 1px solid rgba(218,224,235,.92); border-radius: 11px;
  background: rgba(255,255,255,.92); box-shadow: 0 7px 24px rgba(44,59,92,.045);
}
.section-title { margin: 0 0 18px; color: #1b2334; font-size: 20px; font-weight: 700; }

/* ---- lifecycle placeholder ---- */
.lifecycle-placeholder { min-height: 240px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.empty-text { color: #7d879d; font-size: 15px; text-align: center; padding: 32px 0; }

/* ---- content section ---- */
.content-section { display: flex; flex-direction: column; min-height: 200px; max-height: 720px; }
.content-head { flex-shrink: 0; margin-bottom: 12px; display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.content-head h2 { margin: 0; color: #20283a; font-size: 20px; font-weight: 700; }

/* ---- 评测筛选 + 排序 ---- */
.eval-filters { display: flex; align-items: flex-end; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.eval-filter-field { display: flex; flex-direction: column; gap: 4px; font-size: 13px; color: #606266; }
.eval-filter-field input, .eval-filter-field select {
  width: 180px; padding: 6px 10px;
  border: 1px solid #dcdfe6; border-radius: 4px;
  font-size: 13px; outline: none; background: #fff; transition: border-color 0.2s;
}
.eval-filter-field input:focus, .eval-filter-field select:focus { border-color: #5269d4; }
.eval-filter-clear {
  padding: 6px 14px; border: 1px solid #dcdfe6; border-radius: 4px;
  background: #fff; color: #606266; font-size: 13px; cursor: pointer; transition: all 0.2s;
}
.eval-filter-clear:hover { color: #f56c6c; border-color: #f56c6c; }

/* ---- 分页 ---- */
.eval-pagination {
  display: flex; align-items: center; gap: 16px; margin-top: 14px; padding: 10px 4px;
  font-size: 13px; color: #606266; flex-wrap: wrap;
}
.eval-page-size select {
  margin: 0 6px; padding: 3px 8px; border: 1px solid #dcdfe6; border-radius: 4px;
  font-size: 13px; color: #303133; background: #fff; cursor: pointer;
}
.eval-page-info { color: #909399; }
.eval-page-nav { display: flex; align-items: center; gap: 4px; }
.eval-page-nav button {
  min-width: 30px; height: 30px; padding: 0 8px; border: 1px solid #dcdfe6; border-radius: 4px;
  background: #fff; color: #303133; font-size: 13px; cursor: pointer; transition: all 0.2s;
}
.eval-page-nav button:hover:not(:disabled) { color: #5269d4; border-color: #5269d4; }
.eval-page-nav button:disabled { color: #c0c4cc; cursor: not-allowed; background: #f4f4f5; }
.eval-page-nav button.active { color: #fff; background: #5269d4; border-color: #5269d4; font-weight: 600; }
.eval-page-ellipsis { padding: 0 4px; color: #909399; line-height: 30px; }
.eval-page-jump { display: flex; align-items: center; gap: 6px; margin-left: auto; }
.eval-page-jump input {
  width: 50px; height: 30px; padding: 0 6px; border: 1px solid #dcdfe6; border-radius: 4px;
  text-align: center; font-size: 13px; color: #303133;
}
.eval-page-jump input:focus { outline: none; border-color: #5269d4; }
.sort-btn { margin-left: 6px; border: none; background: none; cursor: pointer; font-size: 13px; color: #909399; padding: 0 4px; line-height: 1; vertical-align: middle; }
.sort-btn.asc { color: #5269d4; }
.sort-btn.desc { color: #f56c6c; }

/* ---- 汇总卡片 ---- */
.eval-summary-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.eval-summary-card {
  min-height: 280px; padding: 18px 20px;
  border: 1px solid #dce3ed; border-radius: 9px;
  background: rgba(250,252,255,.82);
  display: flex; flex-direction: column; gap: 12px;
}
.eval-summary-card.design { background: rgba(244,248,255,.86); border-color: #d8e2f3; }
.eval-summary-card.develop { background: rgba(243,250,248,.86); border-color: #d7e8e2; }
.eval-summary-card.test { background: rgba(251,246,251,.86); border-color: #eaddea; }
.es-head { display: flex; align-items: center; justify-content: space-between; }
.es-tag { padding: 4px 12px; border-radius: 6px; font-size: 14px; font-weight: 700; background: rgba(255,255,255,.7); }
.eval-summary-card.design .es-tag { color: #557bd4; }
.eval-summary-card.develop .es-tag { color: #39856f; }
.eval-summary-card.test .es-tag { color: #ad6682; }
.es-count { font-size: 13px; color: #8993a4; font-weight: 600; }
.es-chart-tabs { display: flex; gap: 4px; padding: 2px; background: rgba(255,255,255,.7); border-radius: 6px; }
.es-chart-tabs button { flex: 1; padding: 5px 8px; border: none; border-radius: 4px; background: transparent; color: #758095; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.es-chart-tabs button:hover { color: #5269d4; background: #f0f3ff; }
.es-chart-tabs button.active { color: #fff; background: #5269d4; box-shadow: 0 2px 6px rgba(82,105,212,.25); }
.es-chart { width: 100%; height: 168px; }

/* ---- 评测明细表 ---- */
.eval-detail-section { max-height: 1240px; }
.table-wrap { flex: 1; min-height: 0; overflow: auto; border: 1px solid #e1e5ed; border-radius: 8px; background: rgba(255,255,255,.9); }
.table-wrap::-webkit-scrollbar { width: 5px; height: 5px; }
.table-wrap::-webkit-scrollbar-track { background: transparent; }
.table-wrap::-webkit-scrollbar-thumb { background: #c8cfdb; border-radius: 4px; }
.table-wrap::-webkit-scrollbar-thumb:hover { background: #a8b2c2; }
table { width: 100%; border-collapse: collapse; border-radius: 0; }
th { padding: 13px 15px; color: #566277; background: #f6f7fb; border-bottom: 1px solid #e0e5ed; font-size: 16px; font-weight: 400; text-align: left; white-space: nowrap; }
td { padding: 15px; color: #4e5a70; border-bottom: 1px solid #e8ebf1; font-size: 15px; background: rgba(255,255,255,.88); }
tbody tr:last-child td { border-bottom: 0; }
tbody tr { transition: background .16s ease; }
tbody tr:hover td { background: #f8f9fd; }
.asset-table { min-width: 1040px; table-layout: fixed; }
.asset-table th, .asset-table td { vertical-align: middle; }
.asset-table td { padding: 10px 15px; text-align: left; }
.asset-table .asset-metric { text-align: center; }
.asset-table-head { background: #f6f7fb; }
.asset-table-head th { background: transparent; border-bottom: 0; }
/* 列宽拖拽手柄容器不裁切 */
.asset-table thead th { overflow: visible; }
.asset-table-head th[rowspan] { vertical-align: middle; }
.asset-table-head tr:first-child th { padding-bottom: 7px; border-bottom: 0; }
.asset-table-head .asset-group { text-align: center; color: #526078; font-weight: 700; }
.asset-table-head .asset-subhead th { padding-top: 8px; padding-bottom: 10px; border-top: 1px solid #e1e5ed; text-align: center; background: transparent; color: #718096; font-weight: 550; }
.hierarchy-row-pdu td { background: #f6f7fb; }
.hierarchy-row-dept td { background: #f8f9fd; }

.eval-table { min-width: 980px; table-layout: fixed; }
.eval-table .eval-col-req-title { width: 200px; }
.eval-table .eval-col-creator { width: 110px; }
.eval-table .eval-col-created-at { width: 150px; }
.eval-table .eval-col-duration { width: 80px; }
.eval-table .eval-col-gov-owner { width: 190px; }
.eval-table .eval-col-gov-expect { width: 90px; }
.eval-table .eval-col-gov-status { width: 90px; }
.eval-table .eval-col-status { width: 90px; text-align: left; }
.eval-table td.eval-req-title { color: #303133; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.eval-table .eval-obj-link { color: #2b5fd6; text-decoration: none; cursor: pointer; }
.eval-table .eval-obj-link:hover { color: #1d44a8; text-decoration: underline; }
.eval-table .eval-duration { font-size: 13px; color: #4e5a70; font-variant-numeric: tabular-nums; }
.eval-table .eval-creator { font-size: 13px; color: #303133; font-weight: 400; }
.eval-table .eval-created-at { font-size: 12px; color: #909399; }
.eval-table .conclusion-pill { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 12px; font-weight: 400; }
.eval-table .conclusion-pill.up { color: #2e8b57; background: #e6f5ef; }
.eval-table .conclusion-pill.down { color: #d04040; background: #fdeeee; }
.eval-table .gov-status-pill { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 12px; font-weight: 400; }
.eval-table .gov-status-pill.pending { color: #b8852a; background: #fdf3e0; }
.eval-table .gov-status-pill.processing { color: #4b66b1; background: #e8eeff; }
.eval-table .gov-status-pill.done { color: #2e8b57; background: #e6f5ef; }
.eval-table .gov-status-pill.ignored { color: #909399; background: #f0f2f5; }
.clickable-row { cursor: pointer; transition: background .15s; }
.clickable-row:hover td { background: #eef3fc !important; }
.clickable-row.row-active td { background: #e3ecff !important; }

/* ---- 评测任务明细侧边栏 ---- */
.drawer-mask {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(20, 28, 45, .42);
  display: flex; justify-content: flex-end;
}
.drawer-panel {
  width: 1280px; max-width: 96vw; height: 100%;
  background: #fff; display: flex; flex-direction: column;
  box-shadow: -8px 0 28px -10px rgba(38,51,85,.32);
}
.drawer-head {
  flex-shrink: 0; padding: 0; border-bottom: none;
}
.drawer-close {
  margin-left: auto; width: 32px; height: 32px; border: none; background: transparent;
  font-size: 24px; color: #909399; cursor: pointer; border-radius: 4px; line-height: 1;
  display: flex; align-items: center; justify-content: center;
}
.drawer-close:hover { background: #f0f2f5; color: #303133; }
.drawer-body {
  flex: 1; overflow-y: auto; padding: 16px 22px; display: flex; flex-direction: column; gap: 18px;
}
.drawer-section { display: flex; flex-direction: column; gap: 10px; }
.drawer-section-title {
  margin: 0; font-size: 13px; font-weight: 700; color: #4e5a70;
  padding-bottom: 6px; border-bottom: 1px solid #eef1f6;
}
.drawer-meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 16px; }
.drawer-meta-item { display: flex; flex-direction: column; gap: 4px; }
.drawer-meta-item .meta-label { font-size: 12px; color: #909399; }
.drawer-meta-item .meta-value { font-size: 13px; color: #303133; display: flex; align-items: center; gap: 6px; }
.drawer-meta-item .meta-time { font-size: 12px; color: #909399; }
.drawer-metric-table-wrap {
  width: 100%; overflow: auto; border: 1px solid #e3e8f0; border-radius: 8px;
  background: #fff; box-shadow: 0 1px 3px rgba(45, 70, 120, 0.04);
}
.drawer-metric-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.drawer-metric-table th, .drawer-metric-table td {
  padding: 10px 14px; text-align: left;
}
.drawer-metric-table thead th {
  background: linear-gradient(180deg, #f5f8fd 0%, #eef3fb 100%);
  color: #2f456c; font-weight: 600; font-size: 13px;
  border-bottom: 2px solid #d6e0ee;
}
.drawer-metric-table thead th:first-child { border-top-left-radius: 8px; }
.drawer-metric-table thead th:last-child { border-top-right-radius: 8px; }
.drawer-metric-table tbody tr {
  border-bottom: 1px solid #eef1f6; transition: background .15s;
}
.drawer-metric-table tbody tr:last-child { border-bottom: 0; }
.drawer-metric-table tbody tr:nth-child(even) { background: #fafbfd; }
.drawer-metric-table tbody tr:hover { background: #f0f5ff; }
.drawer-metric-table td { color: #4e5a70; font-variant-numeric: tabular-nums; }
.drawer-metric-table .dm-scene { font-weight: 600; color: #2f456c; }
.drawer-opinions { display: flex; flex-direction: column; gap: 10px; }
.drawer-opinion-item {
  padding: 10px 12px; background: #f7f9fc; border-left: 3px solid #5269d4; border-radius: 4px;
}
.drawer-opinion-item .opinion-file { font-size: 13px; font-weight: 600; color: #2f456c; margin-bottom: 4px; }
.drawer-opinion-item .opinion-text { font-size: 13px; color: #4e5a70; line-height: 1.6; }
.drawer-empty { margin: 0; font-size: 13px; color: #909399; padding: 12px 0; text-align: center; }
.drawer-foot {
  flex-shrink: 0; padding: 12px 22px; border-top: 1px solid #eaeef5;
  display: flex; gap: 10px; justify-content: flex-end;
}
.drawer-btn {
  padding: 7px 16px; border: 1px solid #dcdfe6; border-radius: 4px;
  background: #fff; color: #606266; font-size: 13px; cursor: pointer; transition: all .2s;
}
.drawer-btn:hover { border-color: #5269d4; color: #5269d4; }
.drawer-btn.primary { background: #5269d4; border-color: #5269d4; color: #fff; }
.drawer-btn.primary:hover { background: #4257c0; border-color: #4257c0; color: #fff; }

/* ---- 抽屉 tab 切换 ---- */
.drawer-tabs {
  flex-shrink: 0; display: flex; align-items: center; gap: 4px;
  margin: 0 -22px; padding: 0 22px;
  border-bottom: 1px solid #eaeef5; background: #fbfcfe;
}
.drawer-tab {
  position: relative; padding: 10px 14px; border: none; background: transparent;
  color: #606266; font-size: 21px; font-weight: 600; cursor: pointer;
  transition: color .18s; white-space: nowrap;
}
.drawer-tab:first-child { padding-left: 0; }
.drawer-tab:hover { color: #5269d4; }
.drawer-tab.active { color: #5269d4; }
.drawer-tab.active::after {
  content: ''; position: absolute; left: 0; right: 10px; bottom: -1px;
  height: 2px; background: #5269d4; border-radius: 2px;
}
.drawer-tab-pane { display: flex; flex-direction: column; gap: 14px; }
.drawer-tab-pane > .drawer-section { margin: 0; }

/* ---- 改进效果对比表 ---- */
.drawer-effect-table-wrap {
  width: 100%; overflow: auto; border: 1px solid #eaeef5; border-radius: 6px;
  background: #fff;
}
.drawer-effect-table {
  width: 100%; border-collapse: collapse; font-size: 13px; min-width: 760px;
}
.drawer-effect-table th, .drawer-effect-table td {
  padding: 6px 8px; border-bottom: 1px solid #eef1f6; text-align: left;
}
.drawer-effect-table th {
  background: #f7f9fc; color: #606266; font-weight: 600; white-space: nowrap;
}
.drawer-effect-table td { color: #4e5a70; font-variant-numeric: tabular-nums; }
.drawer-effect-table tbody tr:last-child td { border-bottom: 0; }
.drawer-effect-table .em-metric-name { font-weight: 600; color: #2f456c; }
.drawer-effect-table .em-improved {
  color: #2e8b57; font-weight: 700;
  background: #eaf7f0;
}
.drawer-effect-chart-block { display: flex; flex-direction: column; gap: 12px; }
.drawer-effect-compare { min-width: 880px; }
.drawer-effect-compare th, .drawer-effect-compare td { white-space: nowrap; }

/* ---- 基础信息：任务触发来源 ---- */
.drawer-meta-trigger { grid-column: 1 / -1; }
.meta-trigger-link {
  font-size: 13px; color: #2b5fd6; text-decoration: none; word-break: break-all;
}
.meta-trigger-link:hover { color: #1d44a8; text-decoration: underline; }

/* ---- 回流进度：知识回流MR ---- */
.drawer-reflow-mr {
  margin-top: 12px; padding: 10px 12px; background: #f7f9fc; border-radius: 6px;
  display: flex; flex-direction: column; gap: 6px;
}
.drawer-reflow-mr-label { font-size: 12px; color: #909399; }
.drawer-reflow-mr-link {
  font-size: 13px; color: #2b5fd6; text-decoration: none; word-break: break-all;
}
.drawer-reflow-mr-link:hover { text-decoration: underline; }
.drawer-reflow-mr-empty { font-size: 13px; color: #909399; }

/* ---- 评测详情 tab 标题 ---- */
.drawer-detail-title {
  margin: 22px 0 0; font-size: 21px; font-weight: 700; color: #2f456c;
  padding-bottom: 12px; border-bottom: 2px solid #d6e0ee;
  letter-spacing: 0.3px;
}
.drawer-detail-title:first-child { margin-top: 0; }

/* ---- 评测指标柱状图 ---- */
.drawer-metric-chart {
  width: 100%; padding: 8px 4px 0; background: #fff;
  border: 1px solid #e3e8f0; border-radius: 8px;
}
/* 按指标拆分的多张子图 */
.drawer-metric-charts {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
  width: 100%;
}
.drawer-metric-chart-item {
  min-width: 0; padding: 6px 4px 0; background: #fff;
  border: 1px solid #e3e8f0; border-radius: 8px;
}
@media (max-width: 960px) {
  .drawer-metric-charts { grid-template-columns: 1fr; }
}

/* ---- 回流操作按钮 ---- */
.drawer-reflow-actions {
  display: flex; gap: 10px; margin-top: 12px;
}
.reflow-btn {
  padding: 7px 18px; border: 1px solid #dcdfe6; border-radius: 4px;
  background: #fff; color: #606266; font-size: 13px; cursor: pointer;
  transition: all .2s; font-weight: 500;
}
.reflow-btn:hover:not(:disabled) { border-color: #5269d4; color: #5269d4; }
.reflow-btn:disabled { cursor: not-allowed; opacity: 0.6; }
.reflow-btn-done { color: #2e8b57; border-color: #abe0bf; background: #f0faf4; }
.reflow-btn-done:hover:not(:disabled) { background: #e3f5ec; border-color: #2e8b57; }
.reflow-btn-done:disabled { color: #2e8b57; background: #eaf7f0; border-color: #c6e6d3; }
.reflow-btn-reject { color: #d04040; border-color: #f0c4c4; background: #fdf3f3; }
.reflow-btn-reject:hover:not(:disabled) { background: #fbeaea; border-color: #d04040; }
.reflow-btn-reject:disabled { color: #909399; background: #f0f2f5; border-color: #dcdfe6; }

/* ---- 知识回流 tab 标题（段落加大、区分明显） ---- */
.drawer-reflow-title {
  margin: 22px 0 0; font-size: 21px; font-weight: 700; color: #2f456c;
  padding-bottom: 12px; border-bottom: 2px solid #d6e0ee;
  letter-spacing: 0.3px;
}
.drawer-reflow-title:first-child { margin-top: 0; }

/* ---- 知识回流子标题（h5，段落内分区） ---- */
.drawer-reflow-subtitle {
  margin: 14px 0 8px; font-size: 14px; font-weight: 600; color: #3a5a8c;
  padding-left: 8px; border-left: 3px solid #6b8cce;
}

/* ---- 知识回流MR 卡片 ---- */
.drawer-reflow-mr-list { display: flex; flex-direction: column; gap: 10px; }
.drawer-reflow-mr-card {
  padding: 12px 14px; background: #fff; border: 1px solid #e3e8f0;
  border-left: 3px solid #2e8b57; border-radius: 6px;
  display: flex; flex-direction: column; gap: 6px;
}
.drawer-reflow-mr-head {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
}
.drawer-reflow-mr-title {
  font-size: 13px; font-weight: 600; color: #2f456c;
}
.drawer-reflow-mr-status {
  flex-shrink: 0; padding: 2px 8px; border-radius: 10px;
  font-size: 11px; font-weight: 600;
}
.drawer-reflow-mr-status.merged { color: #2e8b57; background: #eaf7f0; }
.drawer-reflow-mr-status.open { color: #b8852a; background: #fdf3e0; }
.drawer-reflow-mr-status.closed { color: #909399; background: #f0f2f5; }
.drawer-reflow-mr-url {
  font-size: 12px; color: #2b5fd6; text-decoration: none; word-break: break-all;
}
.drawer-reflow-mr-url:hover { text-decoration: underline; }
.drawer-reflow-mr-desc { font-size: 12px; color: #606266; line-height: 1.6; }

/* ---- 改进概览文本 ---- */

/* ---- 改进建议明细 ---- */
.drawer-suggestion-list { display: flex; flex-direction: column; gap: 12px; }
.drawer-suggestion-card {
  padding: 12px 14px; background: #fff; border: 1px solid #eaeef5; border-radius: 6px;
  display: flex; flex-direction: column; gap: 8px;
}
.drawer-suggestion-file {
  font-size: 13px; font-weight: 600; color: #2f456c;
  display: flex; align-items: center; gap: 8px;
}
.drawer-suggestion-file .file-tag {
  font-size: 11px; padding: 1px 6px; border-radius: 3px;
  background: #e8eeff; color: #4b66b1; font-weight: 600;
}
.drawer-suggestion-desc { font-size: 12px; color: #606266; line-height: 1.6; }

/* ---- 改进建议明细表格 ---- */
.drawer-suggestion-table-wrap {
  overflow-x: auto; border: 1px solid #eaeef5; border-radius: 6px; background: #fff;
}
.drawer-suggestion-table {
  width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; color: #2d3748;
}
.drawer-suggestion-table th, .drawer-suggestion-table td {
  padding: 6px 8px; border-bottom: 1px solid #eef1f6; vertical-align: top; line-height: 1.5; white-space: normal; word-break: break-word;
}
.drawer-suggestion-table th:nth-child(1),
.drawer-suggestion-table td:nth-child(1) { width: 130px; } /* 知识名称列 */
.drawer-suggestion-table th:nth-child(2),
.drawer-suggestion-table td:nth-child(2) { width: 90px; } /* 来源列 */
.drawer-suggestion-table th:nth-child(3),
.drawer-suggestion-table td:nth-child(3) { width: 120px; } /* 知识问题分类列 */
.drawer-suggestion-table th:nth-child(4),
.drawer-suggestion-table td:nth-child(4) { width: auto; } /* 改进建议列（自适应占满剩余） */
.drawer-suggestion-table th:nth-child(5),
.drawer-suggestion-table td:nth-child(5) { width: 56px; text-align: center; white-space: nowrap; } /* 详情列 */
.drawer-suggestion-table th {
  background: #f7f9fc; font-weight: 600; color: #5a6678; text-align: left; position: sticky; top: 0; z-index: 1;
}
.drawer-suggestion-table tbody tr:hover { background: #fafbff; }
.drawer-suggestion-table td:first-child { font-size: 12px; color: #2d3748; }
.sug-name-link { color: #2563eb; text-decoration: none; word-break: break-all; }
.sug-name-link:hover { text-decoration: underline; }
.sug-badge {
  display: inline-block; padding: 1px 7px; border-radius: 3px; font-size: 11px; font-weight: 600; line-height: 1.6; white-space: nowrap;
}
.sug-badge-orange { background: #fff1e6; color: #d97706; }
.sug-badge-purple { background: #f3e8ff; color: #7c3aed; }
.sug-badge-blue   { background: #e6f0ff; color: #2563eb; }
.sug-badge-green  { background: #e6f9ef; color: #16a36b; }
.sug-badge-red    { background: #fde8e8; color: #dc2626; }
.sug-badge-gray   { background: #eef1f6; color: #5a6678; }
.sug-detail-btn {
  padding: 2px 12px; font-size: 12px; line-height: 1.6;
  border: 1px solid #d3d9e4; border-radius: 4px; background: #fff; color: #4b66b1; cursor: pointer; white-space: nowrap;
}
.sug-detail-btn:hover { background: #e8eeff; border-color: #4b66b1; }

/* ---- 知识改进建议详情弹窗 ---- */
.sug-detail-overlay {
  position: fixed; inset: 0; z-index: 3000;
  background: rgba(0,0,0,0.5); backdrop-filter: blur(2px);
  display: grid; place-items: center;
}
.sug-detail-modal {
  width: min(900px, 92vw); height: min(680px, 88vh);
  background: #fff; border-radius: 10px; box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  display: flex; flex-direction: column; overflow: hidden;
}
.sug-detail-header {
  padding: 14px 20px; border-bottom: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center; gap: 12px;
}
.sug-detail-title { font-size: 15px; font-weight: 600; color: #1a1a2e; margin: 0; word-break: break-all; }
.sug-detail-close { background: none; border: none; font-size: 24px; color: #999; cursor: pointer; padding: 0 4px; line-height: 1; }
.sug-detail-close:hover { color: #333; }
.sug-detail-body { padding: 16px 20px; overflow-y: auto; flex: 1; }
.sug-section-title {
  font-size: 14px; font-weight: 600; color: #1a1a2e;
  margin: 16px 0 8px 0; padding-bottom: 6px; border-bottom: 1px solid #eee;
}
.sug-section-title:first-child { margin-top: 0; }
.sug-pre {
  font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
  font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-break: break-word; color: #333; margin: 0;
}
.sug-text { font-size: 13px; line-height: 1.7; color: #333; padding: 4px 0; }
.sug-text-muted { color: #666; }
.sug-detail-fade-enter-active, .sug-detail-fade-leave-active { transition: opacity 0.2s ease; }
.sug-detail-fade-enter-from, .sug-detail-fade-leave-to { opacity: 0; }

/* ---- 功能覆盖率详情弹窗 ---- */
.coverage-link { color: #5269d4; cursor: pointer; text-decoration: underline; text-underline-offset: 2px; }
.coverage-link:hover { color: #3a51b8; }
.coverage-detail-modal { max-width: 760px; }

.coverage-summary {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
  padding: 14px 18px; margin-bottom: 16px;
  background: linear-gradient(135deg, #eef2ff 0%, #f5f7fb 100%);
  border: 1px solid #e3e8f5; border-radius: 8px;
}
.coverage-summary-main { display: flex; align-items: baseline; gap: 10px; }
.coverage-summary-label { font-size: 13px; color: #606266; }
.coverage-summary-value {
  font-size: 26px; font-weight: 800; color: #5269d4; letter-spacing: .5px;
}
.coverage-summary-legend { display: flex; flex-wrap: wrap; gap: 14px; }
.coverage-legend-item { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: #606266; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.legend-dot.green { background: #2e8b57; }
.legend-dot.yellow { background: #e6a700; }
.legend-dot.red { background: #d04040; }

.coverage-item-list { display: flex; flex-direction: column; gap: 8px; }
.coverage-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-radius: 8px;
  border: 1px solid #eef1f6; background: #fff; transition: box-shadow .15s, border-color .15s;
}
.coverage-item:hover { border-color: #d8dfeb; box-shadow: 0 2px 8px rgba(82,105,212,.08); }
.coverage-item-content { flex: 1; min-width: 0; }
.coverage-item-name {
  font-size: 14px; font-weight: 400; color: #1b2334; line-height: 1.5;
  word-break: break-word; overflow-wrap: anywhere;
}
.coverage-item-desc { font-size: 13px; color: #606266; margin-top: 4px; line-height: 1.5; }
.coverage-empty { font-size: 13px; color: #909399; padding: 8px 12px; }

/* 得分大按钮 */
.coverage-score-btn {
  flex: 0 0 auto; min-width: 64px; padding: 8px 14px;
  border: none; border-radius: 8px; cursor: default;
  font-size: 15px; font-weight: 800; color: #fff; text-align: center;
  box-shadow: 0 2px 6px rgba(0,0,0,.12); letter-spacing: .5px;
}
.coverage-score-btn.score-green { background: #2e8b57; box-shadow: 0 2px 8px rgba(46,139,87,.35); }
.coverage-score-btn.score-yellow { background: #e6a700; box-shadow: 0 2px 8px rgba(230,167,0,.35); }
.coverage-score-btn.score-red { background: #d04040; box-shadow: 0 2px 8px rgba(208,64,64,.35); }

/* 覆盖率计算过程 */
.coverage-calc {
  padding: 14px 16px; background: #f7f9fc; border: 1px solid #eef1f6; border-radius: 8px; margin-bottom: 16px;
  font-size: 13px; color: #555; line-height: 1.7;
}
.coverage-calc .sug-section-title { margin-bottom: 10px; }
.coverage-calc-formula {
  font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12.5px;
  background: #eef1f6; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px;
  color: #1b2334; line-height: 1.6;
}
.coverage-calc-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;
}
.coverage-calc-card {
  background: #fff; border: 1px solid #e7ecf3; border-radius: 8px; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 4px;
}
.coverage-calc-card-head {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;
}
.coverage-calc-card-tag {
  font-size: 12px; font-weight: 700; color: #5269d4;
}
.coverage-calc-card-weight {
  font-size: 11px; color: #909399; background: #f0f3fa; padding: 1px 6px; border-radius: 4px;
}
.coverage-calc-card-row {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  font-size: 12.5px; color: #555;
}
.coverage-calc-card-key { color: #606266; }
.coverage-calc-card-val { font-weight: 600; color: #1b2334; font-variant-numeric: tabular-nums; }
.coverage-calc-card-subtotal {
  margin-top: 4px; padding-top: 6px; border-top: 1px dashed #e7ecf3;
}
.coverage-calc-card-subtotal .coverage-calc-card-val { color: #5269d4; }
.coverage-calc-result {
  display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 8px;
  padding: 10px 12px; background: #fff; border: 1px solid #e7ecf3; border-radius: 8px;
  font-size: 13px;
}
.coverage-calc-result-eq { font-weight: 800; color: #1b2334; font-size: 15px; }
.coverage-calc-result-expr { font-family: ui-monospace, Menlo, Consolas, monospace; color: #606266; }
.coverage-calc-result-arrow { color: #909399; font-weight: 700; }
.coverage-calc-result-pct {
  font-size: 16px; font-weight: 800; color: #5269d4;
  padding: 2px 10px; background: #eef2ff; border-radius: 6px;
}
@media (max-width: 640px) {
  .coverage-calc-grid { grid-template-columns: 1fr; }
  .coverage-summary { flex-direction: column; align-items: flex-start; }
}
.drawer-diff-block {
  display: flex; flex-direction: column; gap: 8px;
  padding: 10px; background: #fafbfc; border-radius: 4px; border: 1px solid #eef1f6;
  overflow-x: auto;
}
.drawer-diff-content {
  margin: 0; white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere;
  font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 12px; line-height: 1.55;
  padding: 6px 8px; border-radius: 3px;
  background: #f5f7fa; color: #1b2334;
  border-left: 2px solid #5269d4;
}

/* ---- GitHub 风格 diff 渲染 ---- */
.gh-diff {
  border: 1px solid #d8dee4; border-radius: 6px; overflow: auto;
  background: #fff; margin-top: 8px;
  max-height: 320px; resize: vertical;
}
.gh-diff-table {
  border-collapse: collapse; width: max-content; min-width: 100%;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 13px !important; line-height: 1.4 !important;
  table-layout: fixed;
}
.gh-diff-table td {
  padding: 0 8px; vertical-align: top; border: none;
  white-space: pre;
  font-size: 13px !important; line-height: 1.4 !important;
}
.gh-diff-lineno {
  width: 42px; min-width: 42px;
  text-align: right; color: #8c959f; user-select: none;
  background: #f6f8fa; border-right: 1px solid #d8dee4;
  padding: 0 6px !important;
}
.gh-diff-left, .gh-diff-right {
  width: 50%; color: #24292f;
}
.gh-diff-row { background: #fff; }
.gh-diff-row.gh-diff-context { background: #fff; }
.gh-diff-row.gh-diff-del { background: #fff; }
.gh-diff-row.gh-diff-add { background: #fff; }
.gh-diff-row.gh-diff-hunk { background: #ddf4ff; }
.gh-diff-row.gh-diff-hunk td { color: #0969da; font-weight: 600; }
.gh-diff-cell-del { background: #ffebe9; }
.gh-diff-cell-add { background: #dafbe1; }
.gh-diff-sign {
  display: inline-block; width: 12px; margin-right: 4px;
  color: inherit; font-weight: 700;
}
.gh-diff-row.gh-diff-del .gh-diff-sign { color: #cf222e; }
.gh-diff-row.gh-diff-add .gh-diff-sign { color: #1a7f37; }
.gh-diff-meta-row td { padding: 6px 10px !important; background: #f6f8fa; }
.gh-diff-filename {
  font-weight: 700; color: #24292f;
  border-bottom: 1px solid #d8dee4 !important;
}
.gh-diff-left { border-right: 1px solid #d8dee4; }

/* ---- 抽屉过渡动画 ---- */
.drawer-slide-enter-active, .drawer-slide-leave-active { transition: opacity .25s; }
.drawer-slide-enter-active .drawer-panel, .drawer-slide-leave-active .drawer-panel { transition: transform .28s ease; }
.drawer-slide-enter-from, .drawer-slide-leave-to { opacity: 0; }
.drawer-slide-enter-from .drawer-panel, .drawer-slide-leave-to .drawer-panel { transform: translateX(100%); }

/* ---- type/status pill ---- */
.status-pill { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 12px; font-weight: 400; }
.status-pill.done { color: #2e8b57; background: #e6f5ef; }
.status-pill.processing { color: #b8852a; background: #fdf3e0; }
.status-pill.failed { color: #d04040; background: #fdeeee; }

/* ---- 新建评测任务按钮 + 弹窗 ---- */
.eval-new-btn {
  padding: 8px 20px; border: none; border-radius: 8px;
  color: #fff; background: #5269d4; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all .2s; box-shadow: 0 4px 12px rgba(82,105,212,.25);
}
.eval-new-btn:hover { background: #3a52c0; }
.eval-modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,.38);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.eval-modal { width: 560px; max-width: 92vw; max-height: 90vh; overflow-y: auto; border-radius: 12px; background: #fff; box-shadow: 0 20px 60px rgba(0,0,0,.2); }
.eval-modal-head { display: flex; align-items: center; justify-content: space-between; padding: 18px 24px; border-bottom: 1px solid #eef0f4; }
.eval-modal-head h3 { margin: 0; font-size: 18px; font-weight: 700; color: #1b2334; }
.eval-modal-close { border: none; background: transparent; font-size: 24px; color: #909399; cursor: pointer; line-height: 1; padding: 0; }
.eval-modal-close:hover { color: #303133; }
.eval-modal-body { padding: 24px; }
.eval-modal-field { margin-bottom: 24px; }
.eval-modal-field:last-child { margin-bottom: 0; }
.eval-modal-label { display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 4px; }
.eval-required { color: #f56c6c; }
.eval-modal-hint { margin: 0 0 10px; font-size: 12px; color: #909399; }
.eval-modal-error { margin: 6px 0 0; font-size: 12px; color: #f56c6c; }
.eval-task-name-input { width: 100%; }
.eval-mr-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 8px; }
.eval-mr-row { display: flex; align-items: center; gap: 8px; }
.eval-mr-input { flex: 1; width: 100%; box-sizing: border-box; padding: 8px 12px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 13px; outline: none; transition: border-color .2s; }
.eval-mr-input:focus { border-color: #5269d4; }
.eval-mr-remove { flex: 0 0 30px; width: 30px; height: 30px; border: 1px solid #fbc4c4; border-radius: 6px; background: #fef0f0; color: #f56c6c; font-size: 16px; font-weight: 700; cursor: pointer; display: grid; place-items: center; line-height: 1; }
.eval-mr-remove:hover { background: #fde2e2; }
.eval-mr-add { padding: 6px 14px; border: 1px dashed #c0c4cc; border-radius: 6px; background: transparent; color: #5269d4; font-size: 13px; font-weight: 600; cursor: pointer; transition: all .2s; }
.eval-mr-add:hover { border-color: #5269d4; background: #f0f3ff; }
.eval-mode-list { display: flex; flex-direction: column; gap: 10px; }
/* 任务类型选择 - 大按钮卡片 */
.eval-task-type-list { display: flex; flex-direction: column; gap: 12px; }
.eval-task-type-card { position: relative; display: flex; flex-direction: column; gap: 6px; padding: 16px 18px 16px 44px; border: 1.5px solid #e4e7ed; border-radius: 10px; cursor: pointer; transition: all .18s; background: #fafbfc; }
.eval-task-type-card:hover { border-color: #c0c4cc; background: #f7f8fa; }
.eval-task-type-card.active { border-color: #5269d4; background: #f0f3ff; box-shadow: 0 2px 8px rgba(82, 105, 212, 0.12); }
.eval-task-type-card input[type="radio"] { position: absolute; left: 16px; top: 18px; width: 18px; height: 18px; cursor: pointer; accent-color: #5269d4; }
.eval-task-type-card-title { font-size: 14px; font-weight: 600; color: #303133; line-height: 1.4; }
.eval-task-type-card.active .eval-task-type-card-title { color: #5269d4; }
.eval-task-type-card-desc { font-size: 12px; color: #909399; line-height: 1.6; }
.eval-task-type-card.disabled { opacity: .55; cursor: not-allowed; background: #f4f5f7; }
.eval-task-type-card.disabled:hover { border-color: #e4e7ed; background: #f4f5f7; }
.eval-task-type-card.disabled input[type="radio"] { cursor: not-allowed; }
.eval-task-type-card.disabled .eval-task-type-card-title { color: #a8abb2; }
.eval-task-type-card-tip {
  display: inline-block; margin-top: 2px; padding: 2px 8px;
  font-size: 11px; color: #d97706; background: #fef3e2; border-radius: 4px;
  align-self: flex-start;
}
.eval-mode-item { display: flex; align-items: center; gap: 8px; padding: 10px 14px; border: 1px solid #e4e7ed; border-radius: 8px; cursor: pointer; transition: all .15s; background: #fafbfc; }
.eval-mode-item:hover { border-color: #c0c4cc; }
.eval-mode-item.disabled { cursor: default; background: #f0f5ff; border-color: #d4e0ff; }
.eval-mode-item.disabled.reflow-disabled { opacity: 0.5; background: #f4f4f5; border-color: #dcdfe6; cursor: not-allowed; }
.eval-mode-item.disabled.reflow-disabled .eval-mode-label { color: #909399; }
.eval-mode-item.disabled.reflow-disabled .eval-mode-tag { color: #909399; background: #f0f2f5; }
.eval-mode-item input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; }
.eval-mode-item.disabled input[type="checkbox"] { cursor: default; }
.eval-mode-label { font-size: 14px; font-weight: 600; color: #303133; }
.eval-mode-tag { margin-left: auto; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; color: #5269d4; background: #e8efff; }
.eval-modal-foot { display: flex; justify-content: flex-end; gap: 12px; padding: 16px 24px; border-top: 1px solid #eef0f4; }
.eval-modal-btn { padding: 8px 22px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all .2s; border: 1px solid; }
.eval-modal-btn.cancel { color: #606266; background: #fff; border-color: #dcdfe6; }
.eval-modal-btn.cancel:hover { color: #f56c6c; border-color: #fbc4c4; }
.eval-modal-btn.confirm { color: #fff; background: #5269d4; border-color: #5269d4; }
.eval-modal-btn.confirm:hover { background: #3a52c0; }

/* ---- 类型列 ---- */
.eval-table .eval-col-eval-type { width: 110px; }
.eval-table .eval-col-task-type { width: 150px; }
.eval-type-pill { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.eval-type-pill.code_gen { color: #4b66b1; background: #f0f3ff; }
.eval-type-pill.test_gen { color: #4ea884; background: #eef7f1; }
.eval-type-pill.skill { color: #c4694a; background: #fdf0e8; }
.task-type-tag { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 12px; line-height: 18px; margin-right: 4px; border: 1px solid; }
.task-type-tag.tag-eval { color: #4b66b1; background: #f0f3ff; border-color: #c8d3f5; }
.task-type-tag.tag-reflow { color: #b8852a; background: #fdf3e0; border-color: #f0dba6; }
.drawer-reflow-empty-tip { padding: 40px 0; font-size: 14px; }

/* ---- 评测场景页签 ---- */
.eval-head-left { display: flex; align-items: center; gap: 18px; flex-wrap: wrap; }
.eval-scene-tabs { display: flex; gap: 4px; padding: 3px; background: #f2f4f9; border-radius: 8px; }
.eval-scene-tabs button {
  padding: 6px 16px; border: none; border-radius: 6px; background: transparent;
  color: #606b80; font-size: 13px; font-weight: 600; cursor: pointer; transition: all .18s;
}
.eval-scene-tabs button:hover { color: #5269d4; }
.eval-scene-tabs button.active { color: #fff; background: #5269d4; box-shadow: 0 2px 8px rgba(82,105,212,.22); }

/* ---- Skill 评测列表 ---- */
.eval-table .eval-col-modes { width: 220px; }
.eval-table .eval-col-progress { width: 140px; }
.skill-mode-pill {
  display: inline-block; margin-right: 6px; padding: 2px 8px; border-radius: 4px;
  font-size: 12px; color: #4b66b1; background: #f0f3ff; white-space: nowrap;
}
.skill-progress { font-size: 13px; color: #303133; font-variant-numeric: tabular-nums; }
.skill-progress-failed { color: #d04040; font-size: 12px; }

/* ---- 发起 Skill 评测 ---- */
.eval-modal--skill .eval-modal-head { align-items: flex-start; gap: 16px; }
.eval-modal--skill .eval-modal-close { flex-shrink: 0; }
.eval-modal-heading { min-width: 0; }
.eval-modal--skill .eval-modal-body { padding: 18px 24px; }
.skill-modal-fieldset, .skill-modal-mode-field { min-width: 0; margin: 0; padding: 0; border: 0; }
.skill-modal-fieldset { display: grid; gap: 18px; }
.skill-modal-field-label { padding: 0; color: #303133; font-size: 14px; font-weight: 600; line-height: 20px; }
.skill-modal-mode-field > legend { margin-bottom: 8px; }
.skill-modal-field-hint { margin-left: 4px; color: #647084; font-size: 12px; font-weight: 400; }
.skill-modal-mode-list { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.skill-modal-mode-list .eval-mode-item {
  min-height: 44px; box-sizing: border-box; justify-content: center; padding: 8px; background: #fff;
}
.skill-modal-mode-list .eval-mode-item input[type="checkbox"] { flex-shrink: 0; margin: 0; accent-color: var(--mode-color); }
.skill-modal-mode-list .eval-mode-label { font-size: 13px; overflow-wrap: anywhere; }
.skill-modal-mode-list .eval-mode-item.active { border-color: var(--mode-line); background: var(--mode-tint); }
.skill-modal-mode-list .eval-mode-item.active .eval-mode-label { color: var(--mode-color); }
.skill-modal-picker-heading { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; margin-bottom: 8px; }
.skill-selected-count { font-size: 12px; color: #5269d4; white-space: nowrap; }
.skill-modal-fieldset > .eval-modal-error { margin: 0; }
@media (max-width: 480px) {
  .eval-modal--skill .eval-modal-head, .eval-modal--skill .eval-modal-body, .eval-modal--skill .eval-modal-foot { padding-inline: 16px; }
  .skill-modal-mode-list { gap: 6px; }
  .skill-modal-mode-list .eval-mode-item { gap: 5px; padding-inline: 5px; }
}
@media (max-width: 360px) {
  .skill-modal-mode-list { grid-template-columns: 1fr; }
}

/* ---- Skill 选择器 ---- */
.skill-picker {
  border: 1px solid #e1e5ed; border-radius: 8px; background: #fafbfc; overflow: hidden;
}
.skill-picker-search { display: flex; gap: 8px; padding: 10px; border-bottom: 1px solid #eef0f4; }
.skill-picker-search-btn {
  flex: 0 0 auto; padding: 0 16px; border: 1px solid #5269d4; border-radius: 6px;
  background: #5269d4; color: #fff; font-size: 13px; font-weight: 600; cursor: pointer;
}
.skill-picker-search-btn:hover { background: #3a52c0; }
.skill-picker-toolbar {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 8px 12px; border-bottom: 1px solid #eef0f4; background: #f7f9fd;
}
.skill-picker-toolbar-left { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.skill-picker-select-all { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #4e5a70; cursor: pointer; }
.skill-picker-select-all-btn {
  border: none; background: none; padding: 0; color: #5269d4;
  font-size: 12px; font-weight: 600; cursor: pointer;
}
.skill-picker-select-all-btn:hover:not(:disabled) { color: #3a52c0; text-decoration: underline; }
.skill-picker-select-all-btn:disabled { color: #a8abb2; cursor: not-allowed; }
.skill-picker-select-all input[type="checkbox"] { accent-color: #5269d4; cursor: pointer; }
.skill-picker-clear { border: none; background: none; color: #909399; font-size: 12px; cursor: pointer; padding: 0; }
.skill-picker-clear:hover { color: #f56c6c; }
.skill-picker-list { max-height: 280px; overflow-y: auto; padding: 6px; }
.skill-picker-state { margin: 0; padding: 24px 0; text-align: center; font-size: 13px; color: #909399; }
.skill-picker-state.is-error { color: #d04040; }
.skill-picker-state button { margin-left: 8px; border: none; background: none; color: #5269d4; cursor: pointer; font-size: 13px; }
.skill-pick-item {
  display: flex; align-items: flex-start; gap: 10px; padding: 10px 12px;
  border-radius: 6px; cursor: pointer; transition: background .15s;
}
.skill-pick-item:hover { background: #f0f3ff; }
.skill-pick-item.active { background: #eaf0ff; }
.skill-pick-item input[type="checkbox"] { margin-top: 3px; accent-color: #5269d4; }
.skill-pick-main { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.skill-pick-name { font-size: 13px; font-weight: 600; color: #303133; }
.skill-pick-desc { font-size: 12px; color: #7d879d; line-height: 1.5; }
.skill-pick-meta { display: flex; gap: 10px; font-size: 11px; color: #a0a8b8; flex-wrap: wrap; }
.skill-picker-pager {
  display: flex; align-items: center; justify-content: center; gap: 12px;
  padding: 8px 10px; border-top: 1px solid #eef0f4; font-size: 12px; color: #606b80;
}
.skill-picker-pager button {
  padding: 4px 12px; border: 1px solid #dcdfe6; border-radius: 4px;
  background: #fff; color: #303133; font-size: 12px; cursor: pointer;
}
.skill-picker-pager button:disabled { color: #c0c4cc; cursor: not-allowed; background: #f4f4f5; }

/* ---- Skill 评测详情 ---- */
.drawer-panel--skill { width: 1040px; height: 100vh; height: 100dvh; min-height: 0; overflow: hidden; background: #f5f7fb; color: #24324a; }
.skill-drawer-header {
  display: flex; flex: 0 0 auto; align-items: center; gap: 14px;
  padding: 16px 26px; background: #fff;
}
.skill-drawer-heading { flex: 1; min-width: 0; }
.skill-drawer-heading p { margin: 0 0 4px; color: #65748a; font-size: 12px; }
.skill-drawer-heading h3 { margin: 0; font-size: 21px; line-height: 1.35; overflow-wrap: anywhere; }
.skill-drawer-header > .status-pill { flex: 0 0 auto; }
.skill-drawer-header > .status-pill:not(.done, .processing, .failed) { color: #53637a; background: #eef2f7; }
.skill-drawer-header > .drawer-close { flex: 0 0 32px; margin-left: 0; }
.skill-drawer-body {
  flex: 1 1 0; min-height: 0; min-width: 0; overflow-y: auto; overflow-x: hidden;
  scrollbar-gutter: stable; overscroll-behavior: contain; gap: 14px; padding: 18px 26px 32px;
}
.skill-drawer-body > * { flex: 0 0 auto; }
.skill-drawer-body:focus-visible { outline: 2px solid #3d6bcb; outline-offset: -2px; }
.skill-text-button { padding: 0; border: 0; background: none; color: #3668c9; font: inherit; cursor: pointer; }
.skill-text-button:disabled { opacity: .5; cursor: wait; }

.mode-static { --mode-color: #2f65c8; --mode-tint: #edf3ff; --mode-line: #bed0f4; }
.mode-trigger { --mode-color: #7652b7; --mode-tint: #f4effc; --mode-line: #d8c7ed; }
.mode-quality { --mode-color: #167c74; --mode-tint: #edf8f6; --mode-line: #b7dfd7; }
.mode-other { --mode-color: #52647e; --mode-tint: #f0f3f7; --mode-line: #ccd5e1; }
.skill-mode-switcher {
  display: grid; flex: 0 0 auto; grid-template-columns: repeat(3, minmax(0, 156px)); gap: 8px;
  padding: 0 26px; border-bottom: 1px solid #dfe6ef; background: #fff;
}
.skill-mode-tab {
  display: flex; align-items: center; justify-content: center; gap: 8px; min-width: 0; min-height: 45px;
  padding: 8px 10px; border: 0; border-bottom: 2px solid transparent; background: transparent; color: #516078;
  font: inherit; font-size: 13px; font-weight: 600; cursor: pointer; overflow-wrap: anywhere;
}
.skill-mode-tab:hover, .skill-mode-tab[aria-pressed="true"] { background: var(--mode-tint); color: var(--mode-color); }
.skill-mode-tab[aria-pressed="true"] { border-bottom-color: var(--mode-color); }
.skill-mode-status { display: inline-flex; align-items: center; padding: 3px 7px; font-size: 10px; line-height: 1.4; color: #7a879a; background: #f0f3f7; border-radius: 4px; }
.skill-mode-status.completed { color: #2e7a57; background: #edf7f1; }
.skill-mode-status.failed { color: #b4424a; background: #fceef0; }
.skill-mode-status.running, .skill-mode-status.queuing { color: #9a701c; background: #fcf5e6; }
.skill-mode-panel { display: grid; gap: 14px; min-width: 0; }

.skill-report-meta, .skill-task-meta {
  display: flex; align-items: center; flex-wrap: wrap; gap: 8px 18px;
  color: #627187; font-size: 12px; line-height: 1.5; overflow-wrap: anywhere;
}
.skill-report-meta { justify-content: space-between; }
.skill-report-meta strong { color: #3c4d65; font-weight: 600; }
.skill-report-version-picker { display: inline-flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.skill-report-version-picker select {
  max-width: 100%; padding: 4px 8px; border: 1px solid #dce3ed; border-radius: 5px;
  color: #3c4d65; background: #fff; font: inherit;
}
.skill-report-section { min-width: 0; overflow: hidden; border: 1px solid #dfe6ef; border-radius: 8px; background: #fff; }
.skill-report-section-head {
  display: flex; align-items: baseline; gap: 8px; margin: 0; padding: 13px 16px;
  color: #283951; font-size: 14px; font-weight: 650; line-height: 1.5;
}
.skill-report-section-head h4 { margin: 0; font: inherit; }
.skill-report-section-head > span, .skill-report-subsection h5 > span { color: #68778c; font-size: 12px; font-weight: 400; }
.skill-report-overview { display: grid; gap: 12px; padding: 0 16px 14px; }
.skill-report-summary {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(min(132px, 100%), 1fr));
  gap: 8px; margin: 0;
}
.skill-report-metric { min-width: 0; padding: 10px 12px; background: var(--mode-tint); border-radius: 6px; }
.skill-report-metric dt { color: #485a72; font-size: 12px; overflow-wrap: anywhere; }
.skill-report-metric dd {
  display: flex; align-items: baseline; flex-wrap: wrap; gap: 2px 4px; margin: 4px 0 0;
  color: var(--mode-color); line-height: 1.25; font-variant-numeric: tabular-nums; overflow-wrap: anywhere;
}
.skill-report-metric dd strong { min-width: 0; font-size: 24px; font-weight: 650; }
.skill-report-metric small, .skill-report-secondary small { color: #52637c; font-size: 12px; white-space: nowrap; }
.skill-report-secondary {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(min(148px, 100%), 1fr));
  gap: 7px 16px; margin: 0; color: #607087; font-size: 12px;
}
.skill-report-secondary > div { display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 8px; min-width: 0; }
.skill-report-secondary dd { margin: 0; color: #34465f; font-weight: 600; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
.skill-trigger-breakdown { display: flex; flex-wrap: wrap; gap: 6px 18px; color: #607087; font-size: 12px; }
.skill-trigger-breakdown strong { color: #34465f; font-weight: 600; }
.skill-report-note { margin: 0; color: #637187; font-size: 12px; line-height: 1.5; }

.skill-report-row { min-width: 0; border-top: 1px solid #edf0f5; }
.skill-report-row-head, .skill-case-row {
  display: grid; align-items: center; gap: 10px; padding: 9px 16px;
  box-sizing: border-box; min-width: 0; line-height: 1.55; overflow-wrap: anywhere;
}
.skill-report-row-head { min-height: 43px; color: #34445b; font-size: 13px; }
details > summary.skill-report-row-head { cursor: pointer; list-style: none; }
details > summary.skill-report-row-head::-webkit-details-marker { display: none; }
details > summary.skill-report-row-head::after {
  content: ''; width: 6px; height: 6px; justify-self: center;
  border-right: 1.5px solid #66768c; border-bottom: 1.5px solid #66768c;
  transform: rotate(-45deg);
}
details[open] > summary.skill-report-row-head::after { transform: rotate(45deg); }
details > summary.skill-report-row-head:hover, details[open] > summary.skill-report-row-head { background: #f1f5f9; }
.skill-report-row-body {
  display: grid; gap: 14px; padding: 12px 16px 14px; min-width: 0;
  border-top: 1px solid #e8edf4; background: #f8fafc;
}
.skill-dimension-row { grid-template-columns: minmax(0, 1fr) auto 12px; }
.skill-dimension-score { color: #607087; font-size: 12px; }
.skill-dimension-score strong { color: var(--mode-color); font-size: 14px; font-variant-numeric: tabular-nums; }
.skill-dimension-item { display: grid; gap: 5px; color: #34445b; font-size: 13px; white-space: pre-wrap; overflow-wrap: anywhere; }
.skill-dimension-item + .skill-dimension-item { padding-top: 8px; border-top: 1px solid #e8edf4; }
.skill-finding-row, .skill-report-appendix > summary { grid-template-columns: minmax(0, 1fr) 12px; }
.skill-finding-row > span { white-space: pre-wrap; }
.skill-report-appendix > summary { font-size: 14px; }

.skill-report-fields { display: grid; gap: 6px; margin: 0; }
.skill-report-field {
  display: grid; grid-template-columns: minmax(96px, 16%) minmax(0, 1fr); gap: 4px 14px;
  color: #495d76; font-size: 13px; line-height: 1.65; overflow-wrap: anywhere;
}
.skill-report-field dt { color: #617187; }
.skill-report-field dd { margin: 0; min-width: 0; white-space: pre-wrap; }
.skill-report-subsection { display: grid; gap: 8px; min-width: 0; }
.skill-report-subsection h5 { margin: 0; color: #34465f; font-size: 13px; }
.skill-report-subsection h5 > span { margin-left: 4px; }
.skill-report-actions { display: grid; gap: 7px; margin: 0; padding-left: 20px; color: #495d76; font-size: 13px; line-height: 1.65; }
.skill-report-actions li { white-space: pre-wrap; overflow-wrap: anywhere; }
.skill-report-actions--section { padding: 0 16px 14px 35px; }

.skill-case-row { grid-template-columns: minmax(0, 1fr) 70px 78px 105px 12px; }
.skill-case-trigger { grid-template-columns: minmax(0, 1fr) 85px 76px 76px 78px 12px; }
.skill-case-columns { padding-block: 6px; color: #586981; background: #f5f7fa; font-size: 12px; }
.skill-case-columns > span:not(:first-child), .skill-case-cell { text-align: center; }
.skill-case-title { color: #34445b; white-space: pre-wrap; }
.skill-case-cell { color: #53657e; font-size: 12px; font-variant-numeric: tabular-nums; }
.skill-case-score strong { color: var(--mode-color); font-size: 14px; }
.skill-case-label, .skill-visually-hidden {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip-path: inset(50%); white-space: nowrap;
}
.skill-case-verdict {
  justify-self: center; padding: 2px 7px; border-radius: 4px; color: #5d6c80;
  background: #eef1f5; font-size: 11px; white-space: nowrap;
}
.skill-case-verdict.pass { color: #276a4a; background: #e9f6ef; }
.skill-case-verdict.fail { color: #a83c44; background: #fceef0; }
.skill-assertion-list { display: grid; gap: 8px; }
.skill-assertion { display: grid; gap: 6px; padding: 9px 10px; border: 1px solid #e4eaf2; border-radius: 6px; background: #fff; }
.skill-assertion-heading { display: flex; align-items: baseline; flex-wrap: wrap; gap: 6px 8px; }
.skill-assertion-heading strong { flex: 1 1 160px; color: #34465f; font-size: 13px; font-weight: 600; overflow-wrap: anywhere; }
.skill-assertion > p { margin: 0; color: #495d76; font-size: 13px; line-height: 1.65; white-space: pre-wrap; overflow-wrap: anywhere; }

.skill-state { margin: 0; padding: 22px 16px; text-align: center; color: #65748a; font-size: 12px; line-height: 1.8; overflow-wrap: anywhere; }
.skill-state--error {
  display: flex; flex-direction: column; align-items: flex-start; gap: 6px; padding: 14px; text-align: left;
  color: #b64b54; background: #fff4f4; border: 1px solid #f1d6d9; border-radius: 7px; white-space: pre-wrap;
}
.skill-state--error p { margin: 0; }
.skill-report-notice { margin: 0; padding: 12px 14px; border-radius: 7px; color: #8d6c2f; background: #fff8e9; font-size: 12px; line-height: 1.8; }
.skill-mode-pill.mode-static, .skill-mode-pill.mode-trigger, .skill-mode-pill.mode-quality { color: var(--mode-color); background: var(--mode-tint); border: 1px solid var(--mode-line); }
.drawer-panel--skill button:focus-visible, .drawer-panel--skill summary:focus-visible, .drawer-panel--skill select:focus-visible { outline: 2px solid #3d6bcb; outline-offset: -2px; }

@media (max-width: 680px) {
  .drawer-panel--skill { max-width: 100vw; width: 100%; }
  .skill-drawer-header { padding: 12px 14px; gap: 8px; }
  .skill-drawer-heading h3 { font-size: 17px; }
  .skill-drawer-header > .status-pill { padding: 3px 6px; font-size: 11px; }
  .skill-mode-switcher { grid-template-columns: repeat(3, minmax(0, 1fr)); padding: 0 12px; gap: 4px; }
  .skill-mode-tab { flex-direction: column; gap: 4px; min-height: 52px; padding: 6px 3px; }
  .skill-drawer-body { padding: 12px 12px 24px; scrollbar-gutter: auto; }
  .skill-mode-panel { gap: 10px; }
  .skill-report-section-head, .skill-report-row-head, .skill-report-row-body { padding-inline: 11px; }
  .skill-report-overview { padding-inline: 11px; }
  .skill-report-metric { padding: 8px; }
  .skill-report-metric dd strong { font-size: 20px; }
  .skill-report-actions--section { padding-inline: 30px 11px; }
  .skill-case-columns { display: none; }
  .skill-case-row {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) auto 10px; gap: 5px 8px; padding: 8px 11px;
  }
  .skill-case-row .skill-case-title { grid-area: 1 / 1 / 2 / 3; }
  .skill-case-row .skill-case-verdict { grid-area: 1 / 3; justify-self: end; }
  .skill-case-row::after { grid-area: 1 / 4; }
  .skill-case-cell { grid-row: 2; text-align: left; }
  .skill-case-type, .skill-case-score { grid-column: 1; }
  .skill-case-expected { grid-column: 2; }
  .skill-case-actual { grid-column: 3 / 5; }
  .skill-case-assertions { grid-column: 2 / 5; }
  .skill-case-label { position: static; width: auto; height: auto; margin: 0; clip-path: none; }
}

@media (max-width: 460px) {
  .skill-report-field { grid-template-columns: minmax(0, 1fr); gap: 1px; }
  .skill-report-fields { gap: 8px; }
}

/* ---- responsive ---- */
@media (max-width: 900px) {
  .eval-summary-cards { grid-template-columns: 1fr; }
}
/* 按 Skill 展示的列表及结果状态 */
.skill-results-table { min-width: 1080px; table-layout: fixed; }
.skill-results-table td { vertical-align: top; white-space: normal; padding: 8px 14px; }
.skill-results-table td:first-child { vertical-align: middle; }
.skill-name-link { border: 0; background: none; padding: 0; text-align: left; color: #3f5fc3; font-size: 14px; font-weight: 600; cursor: pointer; overflow-wrap: anywhere; }
.skill-mode-cell { display: flex; flex-wrap: wrap; align-items: center; gap: 3px 10px; width: 100%; padding: 0; border: 0; background: transparent; color: inherit; font: inherit; line-height: 1.4; text-align: left; cursor: pointer; }
.skill-mode-meta { display: flex; flex: 0 0 100%; min-width: 0; flex-wrap: wrap; align-items: center; gap: 3px 8px; overflow-wrap: anywhere; }
.skill-mode-version, .skill-report-state { color: #7a8798; font-size: 12px; }
.skill-list-hint { color: #7a8798; font-size: 12px; margin-left: auto; }
.skill-cell-metric { color: #68768c; font-size: 12px; }
.skill-cell-metric b, .skill-cell-metric small { display: inline-block; white-space: nowrap; }
.skill-match-error, .has-error { color: #c74242; }
.skill-match-error { font-size: 12px; line-height: 1.6; margin: 4px 0 0; }
.skill-observation-note { display: block; font-size: 12px; color: #9a6a1a; line-height: 1.6; }
.skill-submission-notice { padding: 14px 16px; background: #f1f5ff; border: 1px solid #d9e3f9; border-radius: 8px; color: #425985; font-size: 13px; line-height: 1.7; margin-bottom: 14px; }
.skill-submission-notice p { margin: 6px 0; }
.skill-submission-notice details { margin-top: 8px; }
.skill-submission-notice summary { cursor: pointer; }
.skill-mode-status.not_evaluated, .skill-mode-status.cancelled, .skill-mode-status.canceled { color: #68768c; background: #eef1f5; }
.eval-modal-btn:disabled, button.eval-filter-clear:disabled { opacity: .55; cursor: not-allowed; }
.eval-modal-overlay { z-index: 4000; }

</style>

