# ADR-010: 分层融合 + TD Beta 先验 + 扩 GT（及 2026-07-09 方案复查）

## 状态

- 分层融合 / TD Beta 先验 / 扩 GT：**accepted（已实现，beta_v1 全量 eval 使用中）**
- Cross-user TD 阶段 / beta_v2 世界态一致数据集：**accepted（2026-07-09 用户拍板「全都修」，已实现，见文末修复记录）**

## 背景

beta U001 S001 心智审查（2026-07-09）定位三个抽取侧 bug：正则覆盖改错值、region 误归因、
last-wins 盖掉正确轮（`wrongway/04`）。用户拍板「分层双轨」（`Readme.md` §Claim 融合路线分歧）。
随后冒烟发现 precision 损失来自「对话谈及指标 ∉ latent GT」，用户拍板扩 GT。

## 决定 1：Session Fusion 层（用户内融合）

```
逐轮 Normalize（Function Calling 严格 enum，无正则覆盖）
  → session 级 LLM 语义融合：读全对话 + 逐轮 claims → 最终槽位 + evidence_turns
  → 消融：fusion = llm | voting | last_wins 三档并行（evaluate_session 默认全开）
```

- 代码：`analysis/fusion.py`、`llm/prompts.py::build_fusion_prompt`
- 主口径 `fusion_mode="llm"`；voting/last_wins 仅作消融对照
- 验收判例：TC-07（追问澄清）、TC-08（语义等价多表述），见 `CheatAgent.md` §五

## 决定 2：TD 可靠度 Beta 先验 + 单源桶不更新

- `TruthDiscoveryEngine` 每源维护 `Beta(2,2)` 后验（先验均值 0.5，温和怀疑）
- **单源桶不更新可靠度**——「与自己一致」不是证据；修复旧启发式把
  honesty=0.2 用户推到 reliability≈0.91 的自我印证 bug
- 代码：`analysis/truth_discovery.py::BetaPosterior`

## 决定 3：扩 GT（对话指标 = GT 指标，不多不少）

- `scripts/expand_latent_gt.py`：LLM 按 session 挖用户**明确断言**的槽 →
  写 `session.claims_truth`；核心三槽（港存/采购积极性/报价松动）值以原 latent 为准
- eval 优先读 `session.claims_truth`（`evaluate_dataset.py` / `run_benchmark_pipeline.py`）
- 生成侧 prompt 加硬约束：latent 未列指标 → 答「不清楚」（防以后再漂）
- 已应用 beta_v1 全部 30 用户 × 5 session（`gt_expand_summary.json`）

## 2026-07-09 复查发现的问题（按严重度）

### L1（P0）：用户间 TD 阶段缺失 → reliability_pearson 失效

单 session 单用户 = 全部桶单源 → 按决定 2 永不更新 → **所有用户 reliability_est ≡ 0.5**
（U001/U002 checkpoint 已证实）。`run_benchmark_pipeline` 结尾的
`pearson_reliability_honesty` 输入零方差，beta_v1「honesty 0.20–0.95 谱系做
reliability 标定」的核心目标当前测不出来。

**行动**：新增 cross-user TD 离线阶段——收集 30 用户 fused slots，按
`(week, region, indicator)` 全库分桶跑 TD → 得跨源 reliability 后验 → 再算 Pearson。
不必重跑逐 session eval，可从 checkpoints/fused_slots 后处理。

### L2（P0）：世界态跨用户不一致 → cross-user TD 无 GT 可评

同 region 同 week 不同用户的 latent 核心值互相矛盾（青岛港 W09 港存：
中/中/高/高/低/高/高/中/高/高）。TD 前提是每个桶一个世界真值、各源按 honesty 汇报；
当前即使全诚实用户也互相冲突，L1 的 cross-user TD 就算实现，其 veracity 与
reliability 标定也没有干净 GT。

**行动（beta_v2 提案，待拍板）**：世界态按 `(region, week)` 共享生成一份
`world_truth`；每用户 latent = world_truth ± honesty/头寸驱动的谎报偏移。
重生成对话（约一夜 LLM 量）。beta_v1 降级定位为「抽取 + 融合」基准（Layer 1–2），
TD 标定（Layer 3）放 beta_v2。

### L3（P1）：扩 GT 污染 veracity 口径

非核心指标的 session GT = 用户断言本身（生成时这些指标不受 honesty/latent 约束），
TD「相信用户」即得分 → `bucket_veracity_accuracy` 虚高。

**行动**：veracity 指标限定核心三槽（或给扩标槽加 provenance 标记并在
veracity 中排除）。slot F1 不受影响（它本来就测「说了什么抽没抽对」）。

### L4（P2）：扩 GT 挖出跨 region 传闻回声（18/150 session）

例 U005 S001 标出 `青岛港/港存=低`，实为用户复述 agent 植入的传闻
（「他们那边库存低，跟日照不是一回事」）。Normalize/Fusion 的 region 防漂移守卫
倾向不出非默认 region 槽 → 这些 GT 槽系统性 FN，压 recall。

**行动**：挖掘 prompt 加「转述/听说/比较句不算断言」；或后处理剔除
非 persona region 且证据含传闻词的槽。量级小（12%），可与 L3 一并修。

## 指标口径备忘

| 指标 | 层级 | 当前状态（修复后） |
|------|------|----------|
| slot F1/recall/precision（fusion=llm） | 抽取+融合 | ✅ 有效，主口径 |
| fusion_ablation（llm/voting/last_wins） | 融合消融 | ✅ 有效（Q4 判据） |
| recon_honesty_pearson | ReCon | ✅ 有效（跨用户，mean_deception vs honesty） |
| external_consistency / escalation | 外部/策略 | ✅ 有效 |
| bucket_veracity_accuracy | TD | ✅ 已限核心三槽 + persona region（L3 修复） |
| reliability_pearson | TD | 🟡 `cross_user_td.py` 已实现（L1）；干净标定等 beta_v2（L2） |

---

## 修复记录（2026-07-09，用户拍板「全都修 + 影响到的部分重新跑」）

### L3 修复：veracity 限核心三槽

- `analysis_metrics.py`：新增 `CORE_TRUTH_INDICATORS` + `core_truth_claims()`；
  `evaluate_session` 增加 `veracity_claims` 参数，默认取 session GT 中
  核心三槽 × persona region；veracity 输出带 `veracity_scope` 标记
- `run_benchmark_pipeline.py` / `evaluate_dataset.py`：显式传
  `veracity_claims = session.world_truth（beta_v2）or latent.core_claims_truth`
  ——世界真值独立于对话挖掘，未讨论的核心槽照常计入（与扩标前口径一致可比）

**答用户批注「这个是因为没有归一化好吧」**：不是归一化问题。归一化解决的是
**表述层**（口语「还行」→ 枚举「中性」），这层是好的；L3 出在 **GT 语义层**——
非核心指标在生成时没有世界真值定义（honesty/latent 只约束核心三槽），扩标时
只能拿「用户断言」当参照。拿断言评 veracity = 奖励「信用户」，归一化做得再好
也不改变「这个槽没有独立真值」的事实。所以修法是收窄 veracity 的评估域，
而不是改归一化。非核心槽仍参与 slot F1（它测的本来就是「说了什么抽没抽对」）。

### L4 修复：扩 GT 传闻回声

- `expand_latent_gt.py` 挖掘 prompt 重写：「什么算/不算断言」分节，明确
  转述（听说/据说/他们那边/比较他港带过句）不建槽；跨 region 建槽仅限第一手；
  新增防漏标自检（对照 8 指标全表逐一确认）
- 后处理保险丝：非默认 region 槽的 evidence 含传闻词
  （听说/据说/你说/他们/那边/不是一回事）→ 丢弃并记日志
- 已全量重挖 30 用户（`benchmark/logs/beta_v1_gt_expand_v2.log`）；
  日志可见 hearsay-echo 被正确拦截（如 U002 S005 青岛港/港存 echo）

### L1 修复：cross-user TD 阶段

- 新脚本 `scripts/cross_user_td.py`：读 eval checkpoints 的 per-session
  `fused_slots`（llm 模式）→ 池化为 Claim → 按 `(week, region, indicator)`
  全库分桶跑 `TruthDiscoveryEngine` → 多源桶更新 Beta 后验 →
  输出 reliability 表 + Pearson(honesty) + 桶明细
- 支持 `--fusion-mode llm|voting|last_wins`（消融）；beta_v2 数据集自带
  `world_truth` 时同时输出 `td_world_truth_accuracy`
- 运行时机：全量 eval 出 checkpoint 后（`--preset beta_v1 / beta_v2`）

### L2 修复：beta_v2 世界态一致数据集

- `runner.py`：`world_truth_for(region, week)` — md5 确定性选 variant
  （Python `hash()` 有进程盐，不可复现，故用 md5）；
  `SimulationRunner(world_state=True)` 时每 session latent = 该 (region, week)
  的世界真值，并写入 `session.world_truth` + `latent.world_truth_by_week`
- `personas.py`：新增 preset `beta_v2`（同 30 personas，world_state=True）
- 记忆隔离：`memory_beta_v2/`，防止 regen 继承 beta_v1 的 L2 用户画像
- 15 个 (region×week) 世界态分布已检查：三港五周 8/15 非重复组合，
  含看多/看空/中性盘，跨源冲突与 honesty 谱系可交叉
- eval / expand 脚本均已接 `session.world_truth` 优先

### 重新跑（2026-07-09 17:40 起）

| 任务 | 状态 |
|------|------|
| GT 全量重挖（L4 口径） | ✅ 完成后自动链入 eval |
| beta_v1 全量 eval（L3 口径 + 新 GT，旧 checkpoint 已清） | 🟡 跑中，ETA ~9h |
| beta_v2 30×5×20 live 生成（与 eval 并行） | 🟡 跑中，ETA 一夜 |
| cross-user TD（beta_v1 诊断 + beta_v2 标定） | 📋 等 checkpoint |

## 参考

- `Readme.md` §Claim 融合路线分歧（用户定论原文）
- `CheatAgent.md` §五 测试用例系列、§七 Q4/Q5
- `wrongway/04-analysis-pipeline.md`
- ADR-005（claim/TD 框架）、ADR-009（Normalize 层）、ADR-011（可视化）
