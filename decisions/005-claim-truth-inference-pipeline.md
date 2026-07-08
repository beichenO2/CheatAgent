# ADR-005: 对话采集场景 — Claim 设计、Truth Inference 与欺骗识别

## 状态
accepted

## 背景

「对话采集场景」（`Readme.md` §算法逻辑实现）只考虑**分析用户回答**，不涉及如何提问。

需明确：
1. Claim 如何设计才能进统一 truth inference 框架
2. 多源冲突 claim 如何联合估真值
3. ReCon 欺骗识别在流程中的位置与作用

## Claim 设计

### 设计原则

1. **一个 claim = 一条可独立判真伪的市场判断**（非整句对话）
2. **canonical_key 是 truth inference 的 join key** — 口语差异先规范化，再进框架
3. **每条 claim 携带 provenance** — 可追溯至 turn，支持 elicitation 评测
4. **欺骗信号挂在 claim 上，不替代 claim** — deception 调制权重，不直接删 claim

### Schema（SSoT）

```json
{
  "claim_id": "uuid",
  "source_id": "user_id",
  "conversation_id": "uuid",
  "time": "ISO8601",

  "region": "青岛港",
  "market_object": "铁矿石",
  "indicator": "港存",
  "value": "高",
  "claim_type": "ordinal",

  "canonical_key": "2026-W27|青岛港|铁矿石|港存",
  "bucket_key": "2026-W27|青岛港|铁矿石|港存",

  "evidence_strength": 0.7,
  "stance_risk": 0.3,
  "incentive_risk": 0.4,

  "provenance": {
    "utterance": "港口那边货还是多的",
    "turn_index": 5,
    "elicitation_channel": "bias_triggered",
    "is_rebuttal": true
  },

  "extractor_confidence": 0.85,

  "deception": {
    "score": 0.35,
    "recon_reasoning": "...",
    "signals": ["vague_quantifier", "stance_aligned"]
  }
}
```

### 字段说明

| 字段 | 用途 |
|------|------|
| `canonical_key` | 本体规范化后的唯一键；合并「库存多」「港存偏高」 |
| `bucket_key` | truth inference 聚合单元 = `(week, region, object, indicator)` |
| `claim_type` | numeric / directional / ordinal / binary → 决定冲突判定方式 |
| `evidence_strength` | VA：有无数字、时间窗、地点、第一手主体 |
| `stance_risk` | 该 claim 对用户头寸是否有利 |
| `incentive_risk` | 与用户已知 position 的方向性偏差风险 |
| `elicitation_channel` | direct / bias_triggered / rebuttal / cover — Tier B 套话评测 |
| `deception.score` | ReCon 输出，汇入 claim_score |

### Claim 生命周期

```
utterance (raw)
    → [extract] draft claim
    → [canonicalize] canonical_key 赋值、value 映射到本体值域
    → [enrich] evidence_strength, stance_risk, incentive_risk
    → [deception] ReCon analyze → deception.score
    → [score] claim_score 计算
    → claim_store (持久化)
    → truth_inference (按 bucket 聚合)
```

### 本体层（canonicalization）

`Readme.md` 已有枚举，确认为 SSoT：

| 维度 | 值域 |
|------|------|
| region | 青岛港、日照港、唐山、… |
| indicator | 港存、到港量、疏港量、采购积极性、报价松动、利润、压港、发运 |
| ordinal value | 高/中/低、紧/平/松 |
| directional value | 上涨/平稳/下跌 |

冲突判定：
- 同 `bucket_key` + 不同 `value` → **conflict**
- 同 `bucket_key` + 同 `value` → **support**（提升 independence 判断）

---

## 统一 Truth Inference 框架

### 输入 / 输出

**输入**：`claim_store` 中所有 canonicalized claims  
**输出**：
- `bucket_truths[bucket_key]` → `{value, confidence, supporting_sources}`
- `user_reliability[source_id]` → `{r, domain_breakdown, trend}`
- `dependence_graph` → 高同源来源对

### 处理流程

```
Step 0  按 bucket_key 分桶
Step 1  桶内：计算每条 claim 的 claim_score
Step 2  桶内：加权投票 / EM 估计 latent truth z_b
Step 3  跨桶：用 z_b 与用户历史一致性更新 r_{u,d,t}
Step 4  跨来源：措辞/时间/引用链相似 → dependence penalty
Step 5  外部：price_trajectory → 方向型 claim 的 external_consistency
Step 6  迭代至收敛（或固定 5 轮 EM）
```

### claim_score 公式

```
claim_score(c) =
  w1 * reliability(c.source, domain, time)
+ w2 * evidence_strength(c)
+ w3 * independence_score(c.source, bucket)
+ w4 * external_consistency(c, price_trajectory)
- w5 * incentive_risk(c)
- w6 * deception.score(c)
```

| 信号 | 来源 | 首期 |
|------|------|------|
| reliability | EM 反推 | ✅ |
| evidence_strength | VA 规则 + LLM | ✅ |
| independence | 来源依赖图 | ✅ 简化：同 conversation 不惩罚 |
| external_consistency | **仅 price_trajectory** | ✅ |
| incentive_risk | position × claim 方向 | ✅ |
| deception.score | **ReCon** | ✅ |

### EM 简化版（首期）

参考 FaitCrowd / Readme 分层贝叶斯，首期实现：

```python
# 对每个 bucket b:
# E-step: P(z_b = v | claims) ∝ Π_i P(c_i | z_b=v, r_{u_i})
# M-step: r_u ← 用户 claims 与 z_b 的历史一致率
#        减去 incentive_risk 和 deception 高的 claim 权重
```

**多数投票 (MV) 作为 baseline** — Tier B 要求 EM < MV error rate。

### 来源依赖惩罚

首期简化：
- 同一用户多 conversation：不视为独立（weight × 0.5）
- 引用链相同（「我也是听 XX 说的」）：标记 dependence edge
- 措辞 embedding 相似度 > θ：dependence penalty

---

## 欺骗识别在流程中的位置

### 不是独立后置步骤

```
❌ 错误：extract → truth inference → 最后 ReCon 判欺骗
✅ 正确：extract → ReCon per-claim → claim_score → truth inference
         且 ReCon per-turn 信号影响 user_model → 交互链路
```

### 两层 ReCon

| 粒度 | 时机 | 输出 | 消费者 |
|------|------|------|--------|
| **Turn-level** | 每轮用户发言后 | deception_score, reasoning | user_modeler, phase_fsm |
| **Claim-level** | claim 抽取后 | 每条 claim 的 deception.score | claim_score, truth inference |

Turn-level 示例：
> 用户第 5 轮说「库存还行吧」— ReCon 一阶：多头+模糊措辞+回避数字 → deception_score=0.6

Claim-level 示例：
> 抽出 `{indicator:港存, value:中}` — ReCon 对照 latent 与措辞 → 调整 deception.score

### 欺骗 vs 真伪 vs 信用

| 概念 | 含义 | 谁产出 |
|------|------|--------|
| **deception** | 本轮/本条是否在策略性误导 | ReCon |
| **claim veracity** | 该 market 判断是否为真 | Truth Inference (z_b) |
| **user reliability** | 该用户长期可信程度 | EM 反推 r_u |

三者关系：
- 高 deception + claim 与 z_b 一致 → 可能「诚实但表达含糊」，降 deception 权重
- 低 deception + claim 与 z_b 冲突 → 可能「客观错误/信息不足」，升 incentive_risk 权重
- 长期高 deception 且错误方向一致 → r_u 显著下降

---

## 对话采集场景端到端数据流

```
[交互链路产出]
  conversation turns (timestamp, phase, tactic)
        │
        ▼
[1. Claim Extractor]  LLM + ontology
        │
        ▼
[2. ReCon Analyzer]    turn-level + claim-level deception
        │
        ▼
[3. Claim Enricher]    evidence, stance, incentive, claim_score
        │
        ▼
[4. claim_store]       持久化
        │
        ▼
[5. Truth Inference]   bucket z_b, r_u, dependence
        │              + price_trajectory external_consistency
        ▼
[6. Credit Scorer]     user_reliability posterior
        │
        └──→ 反馈交互链路 user_model（只读摘要）
```

---

## 与 Tier B Benchmark 的对齐

| GT 来源 | 评测对象 |
|---------|---------|
| `latent.claims_truth` | Claim F1, bucket error |
| `persona.honesty` | r_u correlation |
| `price_trajectory` | external_consistency |
| `persona` + `elicitation_channel` | 套话 recall |

---

## 后果

- `src/analysis/` 按 6 步拆分模块
- claim schema 以本 ADR 为准，覆盖 ADR-002 中的简版
- 外部校验首期仅 `price_trajectory`，不接港口库存 API

## 参考

- `Readme.md` §算法逻辑实现
- ADR-001 Tier B、ADR-003 ReCon、ADR-004 交互策略
- FaitCrowd: https://doi.org/10.1145/2783258.2783314
