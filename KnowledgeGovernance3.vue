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

/* ---- Skill 选择器 ---- */
.skill-selected-count { margin-left: 8px; font-size: 12px; font-weight: 400; color: #5269d4; }
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
.eval-mode-list--inline { flex-direction: row; flex-wrap: wrap; gap: 16px; }

/* ---- Skill 评测结果：概览、模式与明细层级 ---- */
.drawer-panel--skill { width: 1120px; height: 100vh; height: 100dvh; min-height: 0; overflow: hidden; background: #f5f7fb; color: #24324a; }
.skill-drawer-header { flex: 0 0 auto; display: flex; align-items: center; gap: 16px; padding: 18px 28px; background: #fff; border-bottom: 1px solid #e2e7ef; }
.skill-drawer-header h3 { margin: 5px 0 0; font-size: 20px; font-weight: 700; letter-spacing: -.3px; }
.skill-eyebrow { font-size: 11px; font-weight: 600; color: #7a879b; letter-spacing: .5px; }
.skill-drawer-body { flex: 1 1 0; min-height: 0; min-width: 0; overflow-y: scroll; overflow-x: hidden; scrollbar-gutter: stable; overscroll-behavior: contain; scrollbar-width: auto; scrollbar-color: #a7b5ca #edf1f7; gap: 24px; padding: 24px 28px 40px; }
/* 正文中的面板保持自然高度，禁止 flex 压缩后被 overflow:hidden 裁掉。 */
.skill-drawer-body > * { flex: 0 0 auto; }
.skill-drawer-body::-webkit-scrollbar { display: block; width: 11px; height: 11px; }
.skill-drawer-body::-webkit-scrollbar-track { background: #edf1f7; }
.skill-drawer-body::-webkit-scrollbar-thumb { background: #a7b5ca; border: 3px solid #edf1f7; border-radius: 8px; }
.skill-drawer-body::-webkit-scrollbar-thumb:hover { background: #8194af; }
.skill-overview { background: #fff; border: 1px solid #e1e7f0; border-radius: 12px; padding: 22px 24px 16px; }
.skill-section-heading { display: flex; align-items: center; justify-content: space-between; gap: 14px; }
.skill-section-heading h4 { margin: 6px 0 0; font-size: 19px; line-height: 1.5; overflow-wrap: anywhere; }
.skill-section-heading--small { margin-bottom: 12px; }
.skill-section-heading--small h4 { margin: 0; font-size: 15px; }
.skill-section-heading--small > span { color: #7c899c; font-size: 12px; }
.skill-text-button { padding: 0; border: 0; background: none; color: #3668c9; font: inherit; cursor: pointer; }
.skill-text-button:disabled { opacity: .5; cursor: wait; }
.skill-overview-stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; margin: 23px 0 19px; }
.skill-overview-stats > div { display: flex; flex-direction: column; gap: 8px; border-left: 1px solid #e7ebf3; padding-left: 22px; }
.skill-overview-stats > div:first-child { border-left: 0; padding-left: 0; }
.skill-overview-stats span { color: #748198; font-size: 12px; }
.skill-overview-stats strong { font-size: 29px; font-weight: 650; line-height: 1.1; font-variant-numeric: tabular-nums; }
.skill-overview-stats small { font-size: 16px; font-weight: 400; color: #8c98aa; }
.has-error, .skill-overview-stats .has-error strong { color: #bf454c; }
.skill-progress-track { height: 5px; display: flex; overflow: hidden; border-radius: 5px; background: #edf0f5; }
.skill-progress-track .is-completed { background: #6789dc; }
.skill-progress-track .is-failed { background: #d96b70; }
.skill-overview-note { margin: 10px 0 0; color: #8390a2; font-size: 11px; line-height: 1.65; }
.mode-static { --mode-color: #2f65c8; --mode-tint: #edf3ff; --mode-line: #bed0f4; }
.mode-trigger { --mode-color: #7652b7; --mode-tint: #f4effc; --mode-line: #d8c7ed; }
.mode-quality { --mode-color: #167c74; --mode-tint: #edf8f6; --mode-line: #b7dfd7; }
.mode-other { --mode-color: #52647e; --mode-tint: #f0f3f7; --mode-line: #ccd5e1; }
.skill-mode-switcher { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.skill-mode-card { min-width: 0; display: flex; flex-direction: column; gap: 11px; padding: 16px; text-align: left; color: #506079; background: #fff; border: 1px solid #dfe5ee; border-top: 3px solid var(--mode-line); border-radius: 10px; cursor: pointer; font: inherit; transition: border-color .16s, background .16s, box-shadow .16s; }
.skill-mode-card:hover { border-color: var(--mode-color); }
.skill-mode-card.active { background: var(--mode-tint); border-color: var(--mode-color); box-shadow: 0 0 0 1px var(--mode-color); }
.skill-mode-card-top { display: flex; align-items: center; gap: 9px; }
.skill-mode-icon { width: 30px; height: 30px; display: inline-flex; flex: 0 0 auto; align-items: center; justify-content: center; color: var(--mode-color); background: var(--mode-tint); border: 1px solid var(--mode-line); border-radius: 8px; font-size: 13px; font-weight: 700; }
.skill-mode-card-top > strong { font-size: 14px; color: var(--mode-color); }
.skill-mode-selected { margin-left: auto; color: #8390a1; font-size: 10px; white-space: nowrap; }
.skill-mode-card.active .skill-mode-selected { color: var(--mode-color); font-weight: 600; }
.skill-mode-description { font-size: 11px; line-height: 1.5; color: #79869a; }
.skill-mode-card-count { font-size: 12px; margin-top: 3px; }
.skill-mode-card-count b { font-size: 24px; font-weight: 650; color: #28374f; }
.skill-mode-card-foot { display: flex; justify-content: space-between; gap: 8px; padding-top: 9px; border-top: 1px solid var(--mode-line); color: #7c899c; font-size: 11px; }
.skill-mode-panel { min-width: 0; background: #fff; border: 1px solid var(--mode-line); border-top: 3px solid var(--mode-color); border-radius: 12px; overflow: hidden; }
.skill-mode-panel-header { display: flex; justify-content: space-between; align-items: center; gap: 15px; background: var(--mode-tint); border-bottom: 1px solid var(--mode-line); padding: 18px 20px; }
.skill-mode-panel-title { display: flex; align-items: center; gap: 12px; min-width: 0; }
.skill-mode-panel-title h4 { font-size: 17px; color: var(--mode-color); margin: 0 0 4px; }
.skill-mode-panel-title p { margin: 0; font-size: 12px; line-height: 1.5; color: #7b879a; }
.skill-mode-panel-count { font-size: 12px; color: var(--mode-color); white-space: nowrap; }
.skill-mode-outcome-overview { padding: 18px 20px; border-bottom: 1px solid #e7ecf4; background: #fcfdff; }
.skill-mode-outcome-overview h5 { margin: 0 0 12px; font-size: 13px; color: var(--mode-color); }
.skill-report-version-picker { color: #748299; font-size: 12px; }
.skill-report-version-picker label { display: flex; align-items: center; gap: 10px; }
.skill-report-version-picker select { padding: 5px 10px; border: 1px solid #dfe5ee; border-radius: 5px; color: #506079; background: #fff; }
.skill-trigger-breakdown { display: flex; flex-wrap: wrap; gap: 8px 24px; color: #718199; font-size: 12px; }
.skill-results-toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin: 0 20px; padding: 15px 0; color: #7c899b; font-size: 12px; }
.skill-results-toolbar label { display: flex; align-items: center; gap: 9px; }
.skill-results-toolbar select { padding: 5px 25px 5px 9px; border: 1px solid #dfe5ee; border-radius: 5px; background: #fff; color: #506079; font: inherit; }
.skill-result-card { margin: 0 20px 12px; border: 1px solid #e1e6ef; border-radius: 8px; overflow: hidden; background: #fff; }
.skill-result-card:last-child { margin-bottom: 20px; }
.skill-result-card.is-open { border-color: var(--mode-line); }
.skill-result-toggle { display: flex; align-items: center; flex-wrap: wrap; gap: 12px 18px; width: 100%; padding: 16px; border: 0; text-align: left; color: #3e4d65; background: #fff; cursor: pointer; font: inherit; }
.skill-result-toggle:hover { background: #fafbfe; }
.skill-result-identity { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; flex: 1 1 100%; min-width: 0; }
.skill-result-identity > strong { font-size: 14px; overflow-wrap: anywhere; }
.skill-result-version { font-size: 11px; color: #8b97a8; }
.skill-mode-status { display: inline-flex; align-items: center; padding: 3px 7px; font-size: 10px; line-height: 1.4; color: #7a879a; background: #f0f3f7; border-radius: 4px; }
.skill-mode-status.completed { color: #2e7a57; background: #edf7f1; }
.skill-mode-status.failed { color: #b4424a; background: #fceef0; }
.skill-mode-status.running, .skill-mode-status.queuing { color: #9a701c; background: #fcf5e6; }
.skill-result-glance { display: flex; flex-wrap: wrap; gap: 8px 20px; color: #7a879a; font-size: 12px; }
.skill-result-glance b { margin-left: 4px; color: #354762; font-weight: 650; white-space: nowrap; }
.skill-result-metric-count { display: block; margin-top: 3px; color: #8390a4; font-size: 11px; white-space: nowrap; font-variant-numeric: tabular-nums; }
.skill-result-glance .skill-findings-count { color: #b17823; }
.skill-result-action { margin-left: auto; font-size: 12px; font-weight: 500; white-space: nowrap; color: var(--mode-color); }
.skill-result-action > span { margin-left: 6px; }
.skill-result-muted { font-size: 12px; color: #8793a5; line-height: 1.65; overflow-wrap: anywhere; }
.skill-result-detail { padding: 18px 16px; border-top: 1px solid #e7ecf3; background: #fcfdff; display: flex; flex-direction: column; gap: 16px; }
.skill-detail-breadcrumb { font-size: 11px; color: var(--mode-color); overflow-wrap: anywhere; }
.skill-detail-breadcrumb span { margin: 0 7px; color: #b2bccb; }
.skill-report-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; }
.skill-report-metric { display: flex; flex-direction: column; gap: 8px; padding: 14px; border: 1px solid #e7ebf2; border-radius: 7px; background: #fff; min-width: 0; }
.skill-report-metric > span { font-size: 11px; color: #7e8b9f; }
.skill-report-metric > strong { font-size: 21px; line-height: 1.3; color: #2c3f5c; white-space: nowrap; font-variant-numeric: tabular-nums; }
.skill-report-metric > small { margin-top: -3px; font-size: 12px; line-height: 1.4; color: #8390a4; white-space: nowrap; font-variant-numeric: tabular-nums; }
.skill-report-extras { display: flex; flex-direction: column; gap: 8px; padding: 14px; background: #f3f6fb; border-radius: 7px; }
.skill-report-block { display: flex; flex-direction: column; gap: 8px; min-width: 0; }
.skill-report-block h5 { margin: 0 0 3px; font-size: 12px; color: #586b85; }
.skill-report-block h5 > span { margin-left: 5px; color: #9aa6b7; font-weight: 400; }
.skill-report-disclosure, .skill-report-item-disclosure { min-width: 0; border: 1px solid #e3e8f1; border-radius: 7px; background: #fff; }
.skill-report-disclosure > summary, .skill-report-item-disclosure > summary { display: flex; align-items: center; gap: 10px; cursor: pointer; padding: 13px 14px; list-style: none; font-size: 12px; color: #4d607d; }
.skill-report-disclosure > summary::-webkit-details-marker, .skill-report-item-disclosure > summary::-webkit-details-marker { display: none; }
.skill-report-disclosure > summary::before, .skill-report-item-disclosure > summary::before { content: '›'; display: inline-block; color: #8696ae; font-size: 17px; transition: transform .15s; }
.skill-report-disclosure[open] > summary::before, .skill-report-item-disclosure[open] > summary::before { transform: rotate(90deg); }
.skill-report-disclosure[open] > summary { background: #f5f8fc; border-bottom: 1px solid #e7ecf4; }
.skill-report-disclosure > summary > strong { overflow-wrap: anywhere; }
.skill-dimension-score { font-size: 12px; font-weight: 600; color: var(--mode-color); margin-left: auto; white-space: nowrap; }
.skill-dimension-disclosure > summary { display: grid; grid-template-columns: 12px minmax(0, 1fr) 108px 72px; align-items: center; }
.skill-dimension-disclosure > summary > .skill-dimension-score { margin-left: 0; text-align: right; justify-self: stretch; font-variant-numeric: tabular-nums; }
.skill-dimension-disclosure > summary > .skill-disclosure-hint { margin-left: 0; text-align: right; }
.skill-disclosure-hint { margin-left: auto; flex-shrink: 0; font-size: 10px; color: #8c99ad; }
.skill-report-disclosure[open] > summary > .skill-disclosure-hint { visibility: hidden; }
.skill-section-count { padding: 2px 6px; border-radius: 4px; background: #f1f4f9; color: #7d8ba0; font-size: 10px; white-space: nowrap; }
.skill-disclosure-body { display: flex; flex-direction: column; gap: 12px; padding: 14px; min-width: 0; }
.skill-report-item { display: grid; grid-template-columns: 22px minmax(0, 1fr); gap: 10px; padding: 12px; border: 1px solid #e9edf4; border-radius: 6px; }
.skill-report-item > div { display: flex; flex-direction: column; gap: 7px; }
.skill-report-item-index { display: inline-flex; justify-content: center; align-items: center; align-self: flex-start; width: 21px; height: 21px; background: #f0f3f8; color: #8695ac; border-radius: 4px; font-size: 10px; flex-shrink: 0; }
.skill-report-item-title { min-width: 0; overflow-wrap: anywhere; white-space: pre-wrap; line-height: 1.6; }
.skill-item-fields { padding: 4px 14px 14px 44px; display: flex; flex-direction: column; gap: 10px; }
.skill-report-field { display: grid; grid-template-columns: 95px minmax(0, 1fr); gap: 12px; font-size: 12px; line-height: 1.75; }
.skill-report-field-label { color: #8390a4; overflow-wrap: anywhere; }
.skill-report-field-value { color: #4c5e79; overflow-wrap: anywhere; white-space: pre-wrap; min-width: 0; }
.skill-state { margin: 0; padding: 22px 16px; text-align: center; color: #8895a9; font-size: 12px; line-height: 1.8; overflow-wrap: anywhere; }
.skill-state--error { display: flex; flex-direction: column; align-items: flex-start; gap: 6px; padding: 14px; text-align: left; color: #b64b54; background: #fff4f4; border: 1px solid #f1d6d9; border-radius: 7px; white-space: pre-wrap; }
.skill-state--error p { margin: 0; }
.skill-task-info { color: #8c99ac; font-size: 11px; line-height: 1.8; overflow-wrap: anywhere; }
.skill-task-info > summary { cursor: pointer; }
.skill-task-info > div { margin: 6px 0 0 15px; }
.skill-improvements { padding: 16px; border: 1px solid #e4eaf2; border-radius: 8px; background: #fff; }
.skill-improvements ul { margin: 0; padding-left: 20px; display: flex; flex-direction: column; gap: 10px; }
.skill-improvements li { color: #4e617d; font-size: 13px; line-height: 1.8; white-space: pre-wrap; overflow-wrap: anywhere; }
.skill-report-notice { margin: 0; padding: 12px 14px; border-radius: 7px; color: #8d6c2f; background: #fff8e9; font-size: 12px; line-height: 1.8; }
.skill-quality-case-columns, .skill-quality-case > summary { display: grid; grid-template-columns: 12px minmax(0, 1fr) 64px 72px 88px; gap: 12px; align-items: center; padding: 12px 14px; }
.skill-quality-case-columns { padding-top: 4px; padding-bottom: 4px; color: #8b98ab; font-size: 11px; }
.skill-quality-case-columns > span:nth-child(n+3) { text-align: center; }
.skill-quality-case { min-width: 0; border: 1px solid #e1e7f0; border-radius: 8px; background: #fff; }
.skill-quality-case > summary { cursor: pointer; list-style: none; font-size: 12px; color: #4b5f7d; }
.skill-quality-case > summary::-webkit-details-marker { display: none; }
.skill-quality-case > summary::before { content: '›'; color: #8a99b0; font-size: 17px; }
.skill-quality-case[open] > summary::before { transform: rotate(90deg); }
.skill-quality-case[open] > summary { background: #f5f8fc; border-bottom: 1px solid #e7edf5; }
.skill-quality-case-title { line-height: 1.8; overflow-wrap: anywhere; }
.skill-trigger-case-columns, .skill-trigger-case > summary { grid-template-columns: 12px minmax(0, 1fr) 76px 76px 76px 72px; }
.skill-trigger-case-type, .skill-trigger-case-expect, .skill-trigger-case-actual { text-align: center; color: #60738f; font-size: 11px; }
.skill-trigger-mobile-label { display: none; }
.skill-quality-case-score { text-align: center; color: var(--mode-color); font-size: 17px; font-variant-numeric: tabular-nums; }
.skill-quality-assertion-count { text-align: center; color: #60738f; font-variant-numeric: tabular-nums; }
.skill-case-verdict { justify-self: center; padding: 3px 7px; border-radius: 4px; font-size: 11px; white-space: nowrap; color: #8794a7; background: #f0f3f7; }
.skill-case-verdict.pass { color: #2f7d59; background: #edf7f1; }
.skill-case-verdict.fail { color: #b44851; background: #fceef0; }
.skill-quality-case-meta { display: flex; flex-wrap: wrap; gap: 8px 18px; color: #92a0b3; font-size: 11px; line-height: 1.8; overflow-wrap: anywhere; }
.skill-quality-text h6 { margin: 0 0 7px; color: #7b8aa0; font-size: 11px; }
.skill-quality-text p { margin: 0; color: #4d607c; font-size: 12px; line-height: 1.85; white-space: pre-wrap; overflow-wrap: anywhere; }
.skill-assertion-card { padding: 13px; border: 1px solid #e6ebf2; border-radius: 7px; }
.skill-assertion-heading { display: flex; align-items: flex-start; flex-wrap: wrap; gap: 8px; }
.skill-assertion-heading strong { flex: 1 1 220px; font-size: 12px; line-height: 1.8; color: #526683; overflow-wrap: anywhere; }
.skill-assertion-priority { color: #8998ad; font-size: 11px; line-height: 1.8; }
.skill-assertion-card > p { margin: 10px 0; color: #77879e; font-size: 12px; line-height: 1.8; white-space: pre-wrap; overflow-wrap: anywhere; }
.skill-mode-pill.mode-static, .skill-mode-pill.mode-trigger, .skill-mode-pill.mode-quality { color: var(--mode-color); background: var(--mode-tint); border: 1px solid var(--mode-line); }
.drawer-panel--skill button:focus-visible, .drawer-panel--skill summary:focus-visible, .drawer-panel--skill select:focus-visible { outline: 2px solid #3d6bcb; outline-offset: 3px; }
@media (max-width: 760px) {
  .drawer-panel--skill { max-width: 100vw; width: 100%; }
  .skill-drawer-header { padding: 16px; }
  .skill-drawer-body { padding: 16px 12px 28px; gap: 18px; }
  .skill-overview { padding: 17px 15px 12px; }
  .skill-section-heading--small { flex-wrap: wrap; gap: 5px; }
  .skill-overview-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px 10px; }
  .skill-overview-stats > div { padding-left: 12px; }
  .skill-overview-stats > div:nth-child(odd) { padding-left: 0; border-left: 0; }
  .skill-mode-switcher { grid-template-columns: 1fr; gap: 8px; }
  .skill-mode-card { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 7px 12px; padding: 12px; }
  .skill-mode-card-top { grid-column: 1 / -1; }
  .skill-mode-card-count { grid-column: 2; grid-row: 2 / 4; align-self: center; white-space: nowrap; }
  .skill-mode-card-foot { grid-column: 1; padding-top: 5px; }
  .skill-mode-description { grid-column: 1; }
  .skill-mode-panel-header { padding: 14px; }
  .skill-results-toolbar { margin: 0 12px; }
  .skill-result-card { margin: 0 12px 10px; }
  .skill-result-toggle { padding: 13px; }
  .skill-result-glance { gap: 7px 12px; }
  .skill-report-field { grid-template-columns: 1fr; gap: 2px; }
  .skill-item-fields { padding-left: 14px; }
  .skill-disclosure-hint { display: none; }
  .skill-dimension-disclosure > summary { grid-template-columns: 12px minmax(0, 1fr) 88px; }
  .skill-quality-case-columns { display: none; }
  .skill-quality-case > summary { grid-template-columns: 12px minmax(0, 1fr) 72px; gap: 8px 10px; }
  .skill-quality-case > summary::before { grid-column: 1; grid-row: 1; }
  .skill-quality-case-title { grid-column: 2; grid-row: 1; }
  .skill-quality-case-score { grid-column: 3; grid-row: 1; }
  .skill-quality-case > summary > .skill-case-verdict { grid-column: 2; grid-row: 2; justify-self: start; }
  .skill-quality-assertion-count { grid-column: 3; grid-row: 2; font-size: 11px; }
  .skill-quality-case > summary { grid-template-columns: 12px minmax(0, 1fr) 58px; gap: 8px; }
  .skill-quality-case-title { grid-column: 2; }
  .skill-quality-case-score { grid-column: 3; }
  .skill-quality-case > summary > .skill-case-verdict { grid-column: 2; justify-self: start; }
  .skill-quality-assertion-count { grid-column: 3; }
  .skill-trigger-case > summary { grid-template-columns: 12px minmax(0, 1fr) 72px; }
  .skill-trigger-case > summary > .skill-case-verdict { grid-column: 3; grid-row: 1; justify-self: center; }
  .skill-trigger-case-type { grid-column: 2; grid-row: 2; text-align: left; }
  .skill-trigger-case-expect { grid-column: 2; grid-row: 3; text-align: left; }
  .skill-trigger-case-actual { grid-column: 2; grid-row: 4; text-align: left; }
  .skill-trigger-mobile-label { display: inline; }
  .skill-report-item-disclosure > summary { align-items: flex-start; }
}

/* ---- responsive ---- */
@media (max-width: 900px) {
  .eval-summary-cards { grid-template-columns: 1fr; }
}
/* 按 Skill 展示的列表及结果状态 */
.skill-results-table { min-width: 950px; table-layout: fixed; }
.skill-results-table td { vertical-align: top; white-space: normal; padding: 16px 14px; }
.skill-name-link { border: 0; background: none; padding: 0; text-align: left; color: #3f5fc3; font-size: 14px; font-weight: 600; cursor: pointer; overflow-wrap: anywhere; }
.skill-mode-cell { display: flex; flex-direction: column; align-items: flex-start; gap: 7px; width: 100%; padding: 0; border: 0; background: transparent; color: inherit; font: inherit; text-align: left; cursor: pointer; }
.skill-directory-meta { display: flex; flex-wrap: wrap; gap: 8px 16px; color: #7a8798; font-size: 12px; margin-top: 10px; }
.skill-mode-version, .skill-report-state { color: #7a8798; font-size: 12px; }
.skill-list-hint { color: #7a8798; font-size: 12px; margin-left: auto; }
.skill-cell-metric { color: #68768c; font-size: 12px; line-height: 1.6; }
.skill-cell-metric b, .skill-cell-metric small { display: inline-block; white-space: nowrap; }
.skill-row-actions { display: flex; flex-direction: column; gap: 14px; align-items: flex-start; font-size: 13px; }
.skill-match-error, .has-error { color: #c74242; }
.skill-match-error { font-size: 12px; line-height: 1.6; margin: 8px 0 0; }
.skill-observation-note { display: block; font-size: 12px; color: #9a6a1a; line-height: 1.6; }
.skill-submission-notice { padding: 14px 16px; background: #f1f5ff; border: 1px solid #d9e3f9; border-radius: 8px; color: #425985; font-size: 13px; line-height: 1.7; margin-bottom: 14px; }
.skill-submission-notice p { margin: 6px 0; }
.skill-submission-notice details { margin-top: 8px; }
.skill-submission-notice summary { cursor: pointer; }
.skill-mode-status.not_evaluated, .skill-mode-status.cancelled, .skill-mode-status.canceled { color: #68768c; background: #eef1f5; }
.skill-mode-card > .skill-mode-status { align-self: flex-start; }
.skill-result-detail { border-top: 0; }
.eval-modal-btn:disabled, button.eval-filter-clear:disabled { opacity: .55; cursor: not-allowed; }
.skill-modal-fieldset { border: 0; padding: 0; margin: 0; min-width: 0; }
.skill-modal-options { margin-top: 18px; color: #66758c; font-size: 13px; }
.skill-modal-options summary { cursor: pointer; margin-bottom: 14px; }
.skill-modal-options .eval-modal-field { margin-top: 12px; }
.eval-modal-overlay { z-index: 4000; }

</style>
