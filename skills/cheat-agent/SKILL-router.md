# SKILL-router — 套话策略路由（占位）

> **状态**：M6 待用户编写。本文件仅为 cheatAgent 脚手架占位。

## 职责

根据当前 UserModel、对话历史、session 上下文，选择最合适的专项套话 skill。

## 输入

- `user_model`: inferred_gaps, resistance_level, intent_layers, partial_claims
- `session`: session_date, price_snapshot, turn_count
- `known_identity`: role, region, position（预先已知，不问用户）
- `available_skills`: 已注册的专项 skill 列表

## 输出（JSON）

```json
{
  "skill_id": "<专项 skill 名>",
  "phase": "RAPPORT|PROBE|CHALLENGE|VERIFY|RECOVER",
  "rationale": "<一句话理由>"
}
```

## 路由原则（来自 Readme 研究线，待细化）

1. **信息寻求行为** — 用户问什么 → 推断缺什么 → 优先 PROBE 相关指标
2. **心理反抗** — resistance 高 → RECOVER / cover_qa；低 → 可 CHALLENGE
3. **陷阱问题 / 有偏陈述** — 已有 partial claim → trap / biased
4. **苏格拉底** — 需让用户自证 → socratic
5. **SUE** — 有价格证据且 claim 与价格矛盾 → sue
6. **VA** — claim 缺可验证细节 → va
7. **认知负荷** — 回答过于流畅模板化 → cognitive_load

## 专项 Skills（N — 待创建）

| skill_id | 研究来源 | 目标 persona/情境 |
|----------|---------|------------------|
| `cover-qa` | 正常问答掩护 | 全程维持业务互惠 |
| `reactance-biased-statement` | 心理反抗 PRT | 低 resistance、需引反驳 |
| `trap-question` | WWW 2018 陷阱问题 | 已有 partial truth |
| `socratic-probe` | AVERT / IntelliChain | 防御型、需自证 |
| `sue-price-confront` | Strategic Use of Evidence | 价格走线矛盾 |
| `va-detail-chase` | Verifiability Approach | claim 缺细节 |
| `cognitive-load-split` | CCA | 回答过于流畅 |
| … | … | 用户补充 |
