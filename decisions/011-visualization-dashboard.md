# ADR-011: 结果可视化 — 静态 Dashboard（M5 重启）

## 状态

accepted / 已实现（2026-07-09）：`scripts/build_dashboard.py` 交付 Overview
（论文风格：消融表 mean±std + bootstrap CI、散点 + Pearson、指标难度、F1 分布）
与 **Session 回放面板**（对话 timeline + skill 徽标 + fused slots 证据回跳 +
TC-02/05/07/08 判例书签，书签 turn 由 skill metadata 数据驱动）。
支持 eval 中途按 checkpoint 增量重建（页面标注「阶段性快照 N/30」）。
Playwright 已验证渲染与交互（5 图有 canvas、书签高亮、槽位点击回跳）。
剩余：reliability 标定图已随 `cross_user_td.json` 自动填充（beta_v1 诊断 r=-0.097）；beta_v2 干净标定待 eval 后更新。

## 背景

考核要求「实现方案，最好有可展示的界面」（`Readme.md` §问题）。
`CheatAgent.md` §六给出两候选：A 聊天页面（LibreChat 套壳）/ B Dashboard（类 PPT 数值看板）。
Q2「对话页面展示不了抗欺诈性能」——选 **B 为主**；A 的叙事价值由 Dashboard 内嵌
「session 回放」面板承担，不再套 LibreChat。

## 决定

**单文件静态 HTML Dashboard**：`scripts/build_dashboard.py` 读评测产物 →
生成自包含 `benchmark/reports/beta_v1/dashboard.html`（ECharts CDN + 内嵌 JSON）。

理由：零服务依赖、双击可开、可直接发给老师/学长；数据是一次性评测报告，
不需要 Streamlit 常驻服务；版本可归档对比（dashboard_v1.html / v2.html）。

## 数据源

| 产物 | 内容 |
|------|------|
| `benchmark/reports/beta_v1_eval.json` | 全量聚合 + per-user rows |
| `benchmark/reports/beta_v1/checkpoints/*_eval.json` | per-session 明细（fusion_ablation 各档指标） |
| `benchmark/datasets/beta_v1/users/*/meta.json` | transcript / skill_id / persona（回放面板） |
| `benchmark/datasets/beta_v1/gt_expand_summary.json` | GT 扩标审计 |
| cross-user TD 产物（ADR-010 L1 落地后） | reliability 后验 vs honesty |

## 呈现风格（2026-07-09 用户批注：按科研论文方式）

所有图表按论文级规范呈现，不做营销风数字大屏：

1. **消融表为一等公民**：fusion（llm/voting/last_wins）× 指标（F1/recall/precision）
   主表，报 **mean ± std**（150 session 分布），最优列加粗；normalize / max_turns
   消融沿用 `run_ablation_suite` 产物
2. **置信区间**：聚合指标给 bootstrap 95% CI（session 级重采样，n=1000）；
   柱状图带 error bar
3. **相关性图规范**：散点 + 最小二乘拟合线 + `Pearson r (n=..)` 标注；
   reliability 标定图注明数据集（beta_v1 诊断 / beta_v2 标定）
4. **TD 置信度**：bucket confidence 分布直方图 + 多源桶占比；
   reliability 后验以 Beta(α,β) 均值 ± 区间呈现
5. **指标定义表**：每个指标的公式/口径/GT 来源（引用 ADR-009/010 口径备忘），
   杜绝「看图猜义」
6. **判例引用**：session 回放面板的 TC 书签对应 `CheatAgent.md` §五编号，
   图注写明「实录/构造」

## 页面结构（三层下钻）

### 1. Overview（答「系统行不行」）

- KPI 卡：用户数 / session 数 / claim 总数 / slot F1(llm) / recall / precision
- **Fusion 消融分组柱状图**：llm vs voting vs last_wins 的 F1——Q4「哪个准用哪个」的直接判据
- recon 散点：mean_deception vs honesty_gt + Pearson r（期望负相关）
- reliability 散点：reliability_est vs honesty_gt（cross-user TD 前是 0.5 平线，
  修复后展示标定能力；平线本身可作「单源不更新」的诚实展示）
- 指标难度条形图：per indicator 的 recall/precision（哪个指标最难抽）

### 2. Per-user（答「谁可信」）

- 30 用户表：honesty_gt · reliability_est · F1 · claim 数 · 区域，可排序
- session F1 小倍数条形（5 session/用户），异常 session 一眼可见

### 3. Session 回放（答「怎么做到的」，讲故事面板）

- 对话 timeline：每 turn 文本 + agent 轮 skill_id 徽标 + user 轮 ReCon deception 色条
- 右侧 fused slots 卡片：终值 + confidence + evidence_turns，点击回跳高亮原句
- 预置书签：TC-02（否谣言恰真话）/ TC-05（打太极不出槽）/ TC-07（追问澄清）/
  TC-08（语义等价合并）——`CheatAgent.md` §五判例的可视化实证
- 套话指标：skill invoke 分布 / richness / coverage

## 实现顺序

1. `build_dashboard.py` 骨架 + Overview（eval 报告一出即可交付）
2. Per-user 表 + session 回放
3. cross-user TD 落地后补 reliability 标定图

## 不做

- ~~LibreChat 套壳实时聊天~~（研究原型不需要在线服务；回放面板已覆盖叙事）
- ~~Streamlit/后端服务~~（分享与归档成本高于价值）

## 参考

- `CheatAgent.md` §六 展示方案、§七 Q2
- ADR-010（指标口径备忘：哪些图可信、哪些要等修复）
