---
name: trap-question
description: 陷阱问题套话——嵌入已知标准答案的事实性错误，用纠正行为验证专业度与真实性。来源 WWW 2018 Jiménez et al.
---

# trap-question — 陷阱问题

## 何时使用

- 有 `price_snapshot` / 公开锚点可构造 gold answer
- 需验证用户 claim 真实性（非仅 elicit 细节）
- 已有 partial claim，可信度待验
- **不用**：无 gold 配置；用户高 resistance

## 机制

```
嵌入 P(wrong) 且可客观核验
  ├─ 用户纠正 → expertise↑，追问细节
  ├─ 沉默/附和 → perfunctory↑ 或 bluff↑
  └─ 与多轮 outlier 检测组合（F-TQ-OD）
```

## 话术模板（嵌入可核验错误）

1. **指数点位错**：「普氏 62% 已经到 150 了？」（实际偏离 snapshot）
2. **港存量级错**：「青岛港都 2 亿吨了？」（夸大数量级）
3. **时间窗错**：「上周疏港创年内最高？」（与数据矛盾）
4. **南北对比错**：「北方比南方更松？」（与区域事实相反）
5. **品种混淆**：「卡粉和 PB 粉最近一个价？」（故意混淆）

## 提取目标

纠正内容中的真实数字、区域、时间；不纠正则降 reliability 权重。

## 禁忌

- gold answer 配置错误（误伤专业用户）
- 与 reactance 连续叠加 >2 次（操纵感）
- 把「不纠正」直接等同「撒谎」
