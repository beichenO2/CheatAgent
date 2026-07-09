# 04 分析链路（ReCon / Normalize / Claim / Truth Discovery）

## 4.1 正则覆盖 LLM Normalize 输出（2026-07-09，beta_v1 U001 定位）

**做了什么**：`normalize.py::_item_to_slot` 在 LLM 输出槽位后，用 `normalize_value(整句, indicator)` 做**全句关键词扫描**并覆盖 LLM 的值。

**错在哪**：
- 关键词命中与 indicator 无关联：「港存也就**中等**……采购积极性也**还行**」对 采购积极性 槽先命中「还行」→「中」，**覆盖 LLM 正确的「中性」**
- 覆盖后的「中」不在 {积极/消极/中性} → 校验失败 → **整槽丢弃**
- 「积极」二字是「采购积极性」指标名的子串，全句扫描天然误命中
- 结果：LLM 对了，正则把对的改错再扔掉——beta U001 slot_precision 0.325 的直接元凶

**教训**：
- LLM 结构化输出（enum 约束 + 严格校验 + 无效重试）**就是**归一层；后面不许再挂词典改写
- 关键词词典只允许在 **mock/fallback**（LLM 不可用）路径使用
- 校验失败应**丢弃该槽并记录**，绝不能改写后再校验

**处置**：删除 `_item_to_slot` 中的 `normalize_value` 覆盖调用（保留 `_rule_slots` fallback）。

## 4.2 last-wins 聚合 + 追问逻辑与数据处理错位（2026-07-09）

**做了什么**：评测 `predicted_slots` 对同一 (region, indicator) **按轮序覆盖，最后一轮赢**；Normalize 逐轮独立、仅 8 轮上下文、无累积槽状态。

**错在哪**：
- 第 1 轮说对（「港存中等、没暗降」≈GT），第 9 轮说模糊/被 4.1 搞歪 → 正确值被盖掉，recall 从 3/3 掉到 1/3
- 生成期 cheatAgent 有 `cognitive-conflict-probe`（发现矛盾会追问），但分析期对「改口」不做任何一致性处理——**问答逻辑和数据处理逻辑对不上**
- 多次抽取本身没错（能追踪表述演变），错在聚合**盲信最后一句**

**教训**：
- 聚合必须做 **claim 融合**：置信度加权投票 / 改口检测（rebuttal 提权、模糊降权），而非 last-wins
- 分析期设计要和生成期 Agent 行为对齐：Agent 会追问矛盾 → 分析层就应该把「追问后的澄清」权重调高

**处置**：聚合层重设计（见 claim 融合方案），`predicted_slots` last-wins 仅作 baseline 保留。

## 4.3 Session Fusion 三档落地（2026-07-09）

**做了什么**：新增 `analysis/fusion.py`，`evaluate_session` 默认用 `fusion_mode=llm`，并输出 `fusion_ablation`（llm / voting / last_wins）。

**分层**：
- 逐轮 Normalize：FC 严格 enum，**禁止**正则覆盖（4.1）
- 用户内 Session Fusion：LLM 语义合并（还行=中性）+ evidence_turns；voting / last_wins 作 ablation
- 跨用户 TD：投票权重 = reliability × external × (1−incentive) × (1−deception)

**验证**：`test/agents/test_fusion.py` + normalize 回归（采购「中」→「中性」、region drift guard）。

## 4.4 TD Beta 先验 + 单源不更新（2026-07-09）

**做了什么**：`TruthDiscoveryEngine` 用 Beta(α=2,β=2) 先验（均值 0.5）；桶内 `distinct(source_id) < 2` 时**不更新**该源 reliability。

**错在哪（旧启发式）**：单用户 session 评测时每个桶几乎只有一个 source → 「同意自己」被当成证据 → reliability 虚高到 ~0.91（honesty=0.2）。

**教训**：跨源一致性才是 reliability 证据；单源桶应保留先验，把判别力留给 multi-user TD / external。
