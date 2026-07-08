---
name: taohua-router
description: 套话策略路由——根据用户模型、对话阶段、抵抗程度，从10个专项话术skill中选择最合适策略。铁矿石电话客服场景。
---

# SKILL-router — 套话策略路由

> **1 路由 + 10 专项**：凝练自 Readme §90–197 研究线 + `套话skill/analysis/*`

## 输入

```json
{
  "user_model": {
    "inferred_gaps": ["port","inventory"],
    "partial_claims": [{"indicator":"港存","value":"偏高"}],
    "resistance_level": "low|medium|high",
    "intent_layers": {"explicit":"","implicit":"","latent":""},
    "expertise_estimate": 0.0,
    "user_questions": []
  },
  "session": { "turn_count": 3, "phase": "RAPPORT|PROBE|CHALLENGE|VERIFY|RECOVER", "price_snapshot": {} },
  "known_identity": { "role": "厂长", "region": "青岛", "position_direction": "long" }
}
```

## 输出

```json
{
  "skill_id": "<专项 skill>",
  "phase": "RAPPORT|PROBE|CHALLENGE|VERIFY|RECOVER",
  "rationale": "一句话",
  "secondary_skills": ["可选组合"]
}
```

## 专项 Skill 注册表（M=10）

| skill_id | 研究方向 | 一句话 |
|----------|---------|--------|
| `clarification-probe` | 澄清提问 | 意图模糊→迭代追问收敛 |
| `info-seeking-inference` | 信息寻求推断 | 用户问什么→推断缺什么 |
| `bayesian-tom` | 贝叶斯心智理论 | 行为序列→后验更新 |
| `implicit-user-modeling` | 隐式用户建模 | 显/隐/潜在意图融合 |
| `reactance-biased-statement` | 心理反抗 | 有偏陈述→激发反驳 |
| `socratic-probe` | 苏格拉底法 | 引导自证，不直接质疑 |
| `trap-question` | 陷阱问题 | 嵌入 gold 错误验真 |
| `info-design-disclosure` | 信息设计 | 分批/选择性披露 |
| `info-manipulation-bias` | 信息操纵(IMT) | 真实但片面诱发纠正 |
| `cognitive-conflict-probe` | 认知冲突 | 部分冲突陈述暴露认知 |

## 路由决策树

```
turn_count ≤ 2 且意图模糊?
  YES → clarification-probe

用户主动提问?
  YES → info-seeking-inference (+ 更新 user_model)
       → 若假设检验型问题 → trap-question 或 reactance-biased-statement

resistance_level = high?
  YES → phase=RECOVER; 禁用 reactance/trap/cognitive-conflict
       → implicit-user-modeling 或 clarification-probe

resistance low/medium 且 partial_claim 缺量化?
  → reactance-biased-statement 或 info-manipulation-bias

有 price_snapshot 且 claim 可客观核验?
  → trap-question (VERIFY)

回答笼统/专业度待验?
  → socratic-probe

socratic 浅层无效 + 需深层的因果/逻辑?
  → cognitive-conflict-probe

需控制披露节奏、引用户补全?
  → info-design-disclosure

多轮行为需概率化选 tactic?
  → bayesian-tom (meta，可与其他 skill 组合)

行为信号丰富但不宜直问?
  → implicit-user-modeling
```

## 阶段与 Skill 亲和

| Phase | 优先 Skill |
|-------|-----------|
| RAPPORT | clarification-probe, info-seeking-inference |
| PROBE | clarification-probe, implicit-user-modeling, socratic-probe |
| CHALLENGE | reactance-biased-statement, info-manipulation-bias, info-design-disclosure, cognitive-conflict-probe |
| VERIFY | trap-question, bayesian-tom |
| RECOVER | clarification-probe（轻）, cover-qa（互惠） |

## 组合策略（常见链）

1. **澄清→反抗**：`clarification-probe` → `reactance-biased-statement`
2. **推断→陷阱**：`info-seeking-inference` → `trap-question`
3. **反抗→苏格拉底**：`reactance-biased-statement` → `socratic-probe`（深化细节）
4. **操纵→信息设计**：`info-manipulation-bias` → `info-design-disclosure`（分批补全）
5. **全链路 meta**：`bayesian-tom` 每轮更新 posterior 后重路由

## 硬约束（项目假设）

- 用户知道对方是 Agent；多问少答 → 优先 info-seeking-inference
- 互惠：问 2 答 1；路由不得连续 3 轮纯 CHALLENGE
- 已知身份作先验，随轮次衰减（bayesian-tom）
- 铁矿石单品种；话术锚定 `price_snapshot`

## 加载路径

```
invoke_skill 加载: 套话skill/skills/SKILL-{skill_id}.md
```
