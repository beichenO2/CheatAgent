---
name: taohua-router
description: 套话策略路由——根据 user_model、对话阶段、resistance，从 11 个专项 skill 中选最合适策略（含 cover-qa）。铁矿石电话客服。
---

# SKILL-router — 套话策略路由

> 实现：`graph.py::route_skill` 规则引擎；LLM 路由待 M7 接入。

## 输入

- `user_model`: inferred_gaps, partial_claims, resistance_level, last_user_had_question
- `session`: turn_count, price_snapshot, consecutive_challenge_count
- `known_identity`: role, region, position_direction

## 输出 JSON

```json
{
  "skill_id": "reactance-biased-statement",
  "phase": "CHALLENGE",
  "rationale": "resistance 低且无港存量化 claim",
  "secondary_skills": ["socratic-probe"]
}
```

## 注册表（11 skills）

| skill_id | 来源 | 用途 |
|----------|------|------|
| `cover-qa` | 互惠掩护 | RECOVER / 问2答1 |
| `clarification-probe` | ProductAgent | 意图模糊澄清 |
| `info-seeking-inference` | Nelson+Rothe | 从用户提问反推缺口 |
| `bayesian-tom` | Rothe 2018 | 多轮行为后验 |
| `implicit-user-modeling` | Farshidi SLR | 显/隐/潜在意图 |
| `reactance-biased-statement` | PRT | 有偏陈述引反驳 |
| `socratic-probe` | AVERT/IntelliChain | 引导自证 |
| `trap-question` | WWW 2018 + Interspeech 2015 | gold 错误验真 |
| `info-design-disclosure` | Kolotilin 2018 | 分批披露 |
| `info-manipulation-bias` | IMT/Clementson | 片面真实陈述 |
| `cognitive-conflict-probe` | Safety Gap | 认知冲突深挖 |

## 决策优先级（高→低）

1. **resistance > 0.6** → `cover-qa` + phase `RECOVER`
2. **consecutive_challenge ≥ 3** → `cover-qa` + phase `RECOVER`（互惠降温）
3. **用户本轮有提问** → `info-seeking-inference` + phase `PROBE`
   - 含假设数字/「是不是」→ 叠加 `trap-question` 或 `reactance-biased-statement`
4. **turn_count ≤ 2 且 gaps 空** → `clarification-probe` + phase `RAPPORT`
5. **partial_claims 非空 + price_snapshot 可核验** → `trap-question` + phase `VERIFY`
6. **partial_claims 非空但笼统/无量化** → `reactance-biased-statement` 或 `info-manipulation-bias` + phase `CHALLENGE`
7. **turn_count ≥ 4 且仍缺关键 gap** → `bayesian-tom` 或 `implicit-user-modeling`
8. **默认** → `clarification-probe` + phase `PROBE`

## Phase 约束

| Phase | 允许 skill |
|-------|-----------|
| RAPPORT | clarification-probe, info-seeking-inference, cover-qa |
| PROBE | clarification-probe, info-seeking-inference, implicit-user-modeling, socratic-probe |
| CHALLENGE | reactance, info-manipulation, info-design, cognitive-conflict |
| VERIFY | trap-question, bayesian-tom |
| RECOVER | cover-qa, clarification-probe（轻） |

## 硬约束

- 问 2 答 1；RECOVER 禁用 trap/reactance/cognitive-conflict
- 话术锚定 `price_snapshot` 与 `known_identity.region`
- skill 文件：`skills/cheat-agent/SKILL-{skill_id}.md`
