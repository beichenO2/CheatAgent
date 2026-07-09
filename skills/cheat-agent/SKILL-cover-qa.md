---
name: cover-qa
description: 掩护性问答——维持业务互惠（问2答1），在 RECOVER/RAPPORT 阶段提供真实市场信息换取用户配合。非 elicitation 主攻方向。
---

# cover-qa — 掩护性问答

## 何时使用

- `resistance_level` > 0.6 → RECOVER
- 连续 CHALLENGE 后需降温
- 用户只问不答 → 先答 1 条真实信息再轻问
- 任何阶段维持「互惠公理」

## 输出

```json
{ "utterance": "...", "phase": "RAPPORT|RECOVER|PROBE", "give_before_ask": true }
```

## 话术模板

1. **行情先行**：「青岛港 62% 指数附近大概 {price}，您那边最近港存和走货感受怎么样？」
2. **数据换数据**：「疏港这周还可以，到港略增——您更关心哪块？」
3. **降温**：「刚才可能说得急了，先跟您对齐下港口情况…」
4. **轻问**：「您主要做贸易还是钢厂配矿？」

## 禁忌

- 纯索取不给予（违反问2答1）
- 在 RECOVER 阶段继续 trap/reactance
