# ADR-004: 对话策略组织 — 炼化融合 + 阶段状态机

> **⚠ SUPERSEDED by ADR-007 / ADR-008**（2026-07-08）  
> 原「Python 模板原语 + FSM」实现已删除。套话改为 **1+N Skills + LangGraph cheatAgent**。  
> 教训见 `wrongway.md`。

## 状态
superseded

## 背景

`Readme.md` §对话场景 汇总了十余种策略（SUE、VA、CCA、心理反抗、苏格拉底、陷阱问题、信息设计、cover_qa 等）。

需决定实现形态：
- **方案 A**：每种策略提取为独立 Skill，状态机按规则切换调用
- **方案 B**：全部融入一个 mega-prompt，让 LLM 自由发挥
- **方案 C**：炼化融合 — 策略原语 + 阶段状态机 + ReCon 元层 + 心理学入模

## 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| A 纯 Skill + 状态机 | 可测试、可追溯 | 策略常组合使用；纯规则切换僵硬；Skill 数量膨胀 |
| B 纯 LLM 融合 | 自然、灵活 | 不可控、难 benchmark、难解释用了哪种策略 |
| **C 炼化融合** | 可测 + 自然 + 策略可组合 | 实现稍复杂 |

## 决定（已废弃）

~~采用 **方案 C：炼化融合 + 轻量阶段状态机**~~ → 实际落成 7 个 f-string 模板，未达目标。见 `wrongway.md`。

**新方向（ADR-007/008）**：方案 A 的 Skill 体系 + LangGraph Agent 编排。

## 参考

- `decisions/007-agent-rebuild.md`
- `decisions/008-cheat-agent-langgraph.md`
- `skills/cheat-agent/`
