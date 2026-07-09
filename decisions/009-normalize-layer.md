# ADR-009: Normalize 层 — 多样化表达到标准 ontology

## 状态
accepted（2026-07-08）

## 背景

ClaimExtractor 直接从 raw utterance 抽槽位，F1 低且未体现 Readme 分析叙事。用户多样化表述（「还行」「偏高」「谁说的不对其实很高」）需结合 **上下文 + ReCon 欺骗信号** 转译为 canonical vocabulary，再形成 Claim 进入 Truth Discovery。

## 分析链路（新）

```
RAW user turn
  → ReCon（turn 级 DeceptionSignal）
  → Normalize（RAW + ReCon + 上下文 → canonical slots）
  → Claim 对象化
  → ClaimEnricher
  → Truth Discovery（EM + source reliability + external）
  → Escalation flags
```

## Normalize 层

| 项 | 说明 |
|----|------|
| 输入 | raw utterance, ReConThought, 近期对话, default_region, week |
| 输出 | `NormalizedSlot[]` → 程序化生成 `Claim` |
| 模型 | PolarPrivate **`qwen3.7-plus`**（纯文本，`MTA_NORMALIZE_MODEL`；QCSA `1100`） |
| 非一对一 | 一句可产出 0~N 槽位；无指标时 `normalized_slots: []` |
| 消融 | `enable_normalize=False` 回退旧 ClaimExtractor LLM 路径 |

## 转译规则（canonical vocabulary）

### regions
`青岛港` | `日照港` | `唐山`（未提及用 default_region 或 persona.region）

### indicators
`港存` | `到港量` | `疏港量` | `采购积极性` | `报价松动` | `利润` | `压港` | `发运`

别名映射：`库存/港口库存→港存`，`采购→采购积极性`，`报价/价格松动→报价松动`

### values（严格枚举）

| indicator 类 | allowed values |
|-------------|----------------|
| 港存/到港量/疏港量/利润/压港/发运 | 高 / 中 / 低 |
| 采购积极性 | 积极 / 消极 / 中性 |
| 报价松动 | 是 / 否 |
| 趋势 | 上涨 / 下跌 / 平稳 |

口语示例：`偏高/很多/货多→港存=高`；`还行/一般/按需→采购积极性=中性`；`紧张/不多→港存=低`；`没松动→报价松动=否`  
**禁止**用全句关键词覆盖 LLM 输出（见 wrongway/04 §4.1）。

### ReCon 调制

- `deception_score` 高 + `incentive_risk` 高 → 降低 confidence，reason 标注「策略性表述」
- `is_rebuttal` / `rebuttal_language` → 可提高 confidence（纠正性披露）
- 上下文前后矛盾 → 以 **本句 + 最近 agent 诱发句** 为准，reason 写明

## 评测指标（严谨 + 消融）

| 指标 | 层级 | 说明 |
|------|------|------|
| **slot_recall** | Normalize | TP/(TP+FN) vs latent slots |
| **slot_precision** | Normalize | TP/(TP+FP) 预测准确率 |
| **bucket_veracity_accuracy** | TD | 1 - em_error，bucket 推断 vs latent |
| **reliability_pearson** | TD | reliability_est vs honesty_gt |
| **recon_honesty_pearson** | ReCon | mean(deception) vs (1-honesty)，期望负相关 |
| **external_consistency_mean** | External | 外部价格走线一致性均值 |
| **escalation_rate** | Policy | 触发 escalation 的 claim 比例 |

### 消融实验

1. **ablate_normalize**：跳过 Normalize，用旧 ClaimExtractor
2. **ablate_turns**：截断对话轮数（如 6/12/20），观察 recall/precision 曲线

smoke 场景目标：**代码路径可跑、TD 可运行**；指标绝对值不作硬性 gate。

## 环境变量

| 变量 | 默认 | 用途 |
|------|------|------|
| `MTA_NORMALIZE_MODEL` | `qwen3.7-plus` | Normalize 层（纯文本 Qwen，勿用 VL） |
| `MTA_LLM_MODEL` | `0001` | Agent/ReCon 等 |

## 参考

- Readme.md §对话采集场景
- ADR-003 ReCon 栈
