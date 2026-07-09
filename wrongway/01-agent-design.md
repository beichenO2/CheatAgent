# 01 架构与 Agent 设计

## 1.1 规则模板冒充「智能套话 Agent」（2026-07-08）

**做了什么**：7 个 Python f-string 模板（`cover_qa`、`biased_statement` 等）+ FSM 选 tactic。

**错在哪**：
- Readme §对话场景 引用了心理反抗、苏格拉底、信息设计、陷阱问题、Bayesian 说服等十余条研究线，最终只落成 7 句固定话术
- 无 persona 差异、无情境差异、无策略组合
- 用户一眼能看出是脚本，不是 Agent

**教训**：套话必须是 **1+N Skills + LangGraph Agent**，不能再用 `tactics/__init__.py` 模板。

**处置**：`src/market_truth_agent/interaction/` 整目录删除。

## 1.2 「炼化融合、不做 Skill」的 ADR-004 决策（2026-07-08）

**做了什么**：ADR-004 明确不建 Skill 目录，策略原语写死在 Python。

**错在哪**：与 Readme 心理学体系脱节；无法按「不同人、不同情况」扩展；用户无法独立迭代套话模块。

**教训**：套话单独立项——**1 个路由 Skill + N 个场景 Skill**（用户专门做）；cheatAgent 通过 LangGraph 调用 Skills。

**处置**：ADR-004 标记 superseded by ADR-007。
