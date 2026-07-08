# Wrongway — 已废弃路径与教训

> 记录 YOLO 阶段走偏的实现，**禁止再沿用**。2026-07-08 推倒重来。

## 1. 规则模板冒充「智能套话 Agent」

**做了什么**：7 个 Python f-string 模板（`cover_qa`、`biased_statement` 等）+ FSM 选 tactic。

**错在哪**：
- Readme §对话场景 引用了心理反抗、苏格拉底、信息设计、陷阱问题、Bayesian 说服等十余条研究线，最终只落成 7 句固定话术
- 无 persona 差异、无情境差异、无策略组合
- 用户一眼能看出是脚本，不是 Agent

**教训**：套话必须是 **1+N Skills + LangGraph Agent**，不能再用 `tactics/__init__.py` 模板。

**处置**：`src/market_truth_agent/interaction/` 整目录删除。

---

## 2. 规则模拟对话冒充 Tier B Benchmark

**做了什么**：`dialogue_simulator.py` 用 `HONEST_TEMPLATES` / `DECEPTIVE_TEMPLATES` 按 `honesty` 阈值拼句子；claim 用关键词规则抽取。

**错在哪**：
- ADR-001 写「LLM 生成长对话」，实现是硬编码模板——**文档与代码严重不符**
- 生成与评测同一套规则闭环，指标自洽但**零外部效度**
- `bias_triggered` 比例测的是模板触发 rebuttal 关键词，不是套话能力
- 宣称 F1=0.65、Pearson=0.90 等数字**没有评测意义**

**教训**：
- Dataset 构建 = **CustomerAgent（LLM）× cheatAgent（LLM）** 对抗生成
- GT（latent truth、honesty）只写入 dataset metadata，**分析/评测代码严禁读取**
- 生成 pipeline 与评测 pipeline **代码分离**

**处置**：删除 `dialogue_simulator.py`、`evaluator.py`、`multi_user_eval.py`、`scripts/run_tier_b.py`、旧 30 scenario JSON。

---

## 3. ReCon 分析阶段读取 `persona.honesty`（GT 泄漏）

**做了什么**：`recon/core.py` 在 deception 计算里直接用 benchmark GT 的 honesty 字段。

**错在哪**：
- 生产环境没有 honesty GT
- 使 Pearson(reliability, honesty) 指标**虚假偏高**
- 典型的 train-test / builder-evaluator 污染

**教训**：ReCon 只能看 **utterance + 可观测行为 + 历史对话**；honesty 仅存在于 dataset JSON，供**离线对照**，不进 inference。

**处置**：已从 `recon/core.py` 移除；后续 ReCon 需接 LLM 按论文复刻。

---

## 4. Dataset 规模严重不足

**做了什么**：30 用户 × 1 段对话 × 16 轮 × 单周 `2026-W27`。

**错在哪**：不满足业务要求（每用户 ≥100 轮、5 次会话、横跨 5 个月、价格按 session 介入）。

**教训**：分阶段交付——先 **冒烟 3 用户 × 20 轮**，再扩到完整规模。

---

## 5. 套话性能指标选错

**做了什么**：用 `elicitation_channel=bias_triggered` 占比衡量套话效果。

**错在哪**：claim 也是规则生成的，channel 标签是规则打的，**测的是规则不是 Agent**。

**正确方向**（ADR-007）：
- 话术 **种类数**（distinct tactics/skills invoked）
- 话术 **触发次数**（per session / per user）
- 话术 **丰富度**（entropy 或 skill coverage ratio）
- 这些从 **Agent 元数据**（每轮记录的 `skill_id`）统计，不从 claim 反推

---

## 6. 「炼化融合、不做 Skill」的 ADR-004 决策

**做了什么**：ADR-004 明确不建 Skill 目录，策略原语写死在 Python。

**错在哪**：与 Readme 心理学体系脱节；无法按「不同人、不同情况」扩展；用户无法独立迭代套话模块。

**教训**：套话单独立项——**1 个路由 Skill + N 个场景 Skill**（用户专门做）；cheatAgent 通过 LangGraph 调用 Skills。

**处置**：ADR-004 标记 superseded by ADR-007。

---

## 7. 价格数据形同虚设

**做了什么**：同一条 7 天走线复制进每个 scenario；SUE 硬编码「820→848」；`external_consistency` 对港存/采购/报价永远返回 0.5。

**教训**：价格必须按 **session 时间戳** 索引；Agent prompt 注入该 session 价格；分析链路按 turn 时间查 trend。

---

## 保留什么（未废弃）

| 模块 | 原因 |
|------|------|
| `analysis/ontology.py` | 领域本体仍需要 |
| `analysis/truth_discovery.py` | EM 框架仍需要（待接 Agent 产出 claim） |
| `analysis/claim_extractor.py` | 待升级为 LLM 抽取，规则版可作 fallback |
| `storage/conversation_store.py` | 对话存储仍需要 |
| `benchmark/tier_a_data.py` | 组件级 benchmark 仍有效 |
| `models.py` | 扩展后继续使用 |

---

## 下一步（见 roadmap M6–M8）

1. **M6** 构建套话 Skills（1 路由 + N 专项）— 用户主导
2. **M7** LangGraph cheatAgent + CustomerAgent 架构
3. **M8** Agent dataset 生成 + 冒烟评测（3×20）
