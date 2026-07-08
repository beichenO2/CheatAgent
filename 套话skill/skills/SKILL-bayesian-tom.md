---
name: bayesian-tom
description: 贝叶斯心智理论套话——用 ideal observer 框架从行为序列更新对用户隐藏状态的后验，选择高ES elicitation。来源 Rothe 2018。
---

# bayesian-tom — 贝叶斯心智理论

## 何时使用

- 对话 ≥2 轮，有行为序列可累积 likelihood
- 需概率化选择话术（非硬规则）
- 需区分「真不懂 / 装懂 / 隐瞒」
- **不用**：冷启动首轮

## 状态更新

维护 `P(expertise)`, `P(position_direction)`, `P(inventory_level)`, `P(resistance)`。  
观测：纠正精度、术语深度、接受/忽略候选假设、沉默长度。

## 话术模板（候选假设抛球）

1. 「听说青岛港库存破 1.4 亿了，你们也是这个量级吗？」→ 更新 inventory 精度
2. 「要是下周再涨 5 美元，你们加快拿还是观望？」→ 更新 urgency
3. 「你们更看普氏还是港口现货？」→ 更新 expertise
4. 「疏港快还是到港快？我这边数据打架。」→ 更新 logistics
5. 「嗯，这块您方便多说一点吗？我想确认是否一致。」→ 更新 cooperation

## 执行要点

- 优先 **ES 型**（绑定决策）而非纯信息增益泛问
- 用户「评估/纠正」反应权重 > 自发叙述
- 先验（身份=多头）随轮次衰减，让行为主导后验

## 禁忌

- 后验未收敛连发 3 次 CHALLENGE
- 单次模糊回答当作高置信 claim
