# Benchmark 邻域数据集全景

> 外部参考摘要。决策见 `decisions/001-benchmark-strategy.md`。

## 1. 与本项目的距离

| 数据集 | 领域 | 有 GT | 多轮对话 | 激励结构 | 本项目可用性 |
|--------|------|-------|---------|---------|-------------|
| FaitCrowd Game/SFV | 众包 QA | ✅ | ❌ | ❌ | Truth Discovery 组件 |
| DialFact | 对话事实核查 | ✅ | ✅ | ❌ | Claim 抽取/验证方法论 |
| Boulder Lies and Truth | 评论欺骗 | ✅ | ❌ | 部分 | 文本欺骗检测 baseline |
| lie-detector MASK | LLM 信念一致性 | ✅ | 多轮 | ✅ | 欺骗检测组件 |
| DeceptionBench | LLM 欺骗行为 | ✅ | L3 多轮 | ✅ | 激励下欺骗评测 |
| BigTom | 心智理论 | ✅ | 短场景 | 误导 | ReCon 评测 |
| Avalon (ReCon) | 社交推理博弈 | ✅ | 多轮 | ✅ | ReCon 端到端 |
| OpenDeception | 人机欺骗 | ✅ | 多轮 | ✅ | 意图检测参考 |
| MAD | 音频对话核查 | ✅ | ✅ | ❌ | 方法论（电话场景远期） |
| **铁矿石模拟 (Tier B)** | 市场微观 | ✅ latent | ✅ 长对话 | ✅ | **主 Benchmark：30 段** |

## 2. Truth Discovery 数据集

### FaitCrowd (KDD 2015)
- **链接**: https://doi.org/10.1145/2783258.2783314
- **数据**: Game（12 topics）、SFV（8 topics）两个真实众包数据集
- **GT**: 每题有正确标签；每 source 有 ground truth accuracy
- **用途**: 验证 `truth_discovery.py` 的 error rate 与 expertise correlation
- **baseline**: MV, TruthFinder, Accu, Investment, 3-Estimates, CRH, CATD

### TruthFinder 合成 (VLDB 2014 survey)
- **链接**: https://arxiv.org/pdf/1409.6428
- **用途**: 可控 source coverage / conflict rate 的压力测试

## 3. 欺骗检测数据集

### lie-detector (Anthropic safety research)
- **链接**: https://github.com/safety-research/lie-detector
- **MASK benchmark**: 测 LLM 是否在压力下 contradict 自身信念
- **关键条件**: 说假话 + 有证据知道是假的 + 找到矛盾
- **用途**: 欺骗检测模块 Tier A 验证

### DeceptionBench (2025)
- **链接**: https://huggingface.co/datasets/skyai798/DeceptionBench
- **规模**: 150 scenarios, 1000+ samples, 5 domains
- **三层**: L1 inherent / L2 induced / L3 multi-turn
- **用途**: 激励结构参考；economy domain 与大宗商品最近

### Boulder Lies and Truth (LDC2014T24)
- **链接**: https://catalog.ldc.upenn.edu/LDC2014T24
- **规模**: ~1500 英文评论
- **标签**: truthful / opposition / deceptive (fabricated)
- **用途**: 经典文本欺骗检测 baseline

## 4. 对话 / 推理数据集

### DialFact (ACL 2022)
- **链接**: https://github.com/salesforce/DialFact
- **规模**: 22,245 annotated conversational claims
- **任务**: verifiable claim detection / evidence retrieval / claim verification
- **用途**: claim 抽取层的方法论和 prompt 参考（非铁矿石内容）

### BigTom (ReCon 论文使用)
- **用途**: Theory-of-Mind + misinformation 场景
- **与 ReCon**: https://github.com/Shenzhi-Wang/recon 内置评测

## 5. Tier B 铁矿石模拟 — 设计要点

**必须有程序生成的 latent state；30 段长对话；仅 1 条价格走线。**

### Latent 变量
```yaml
market:
  week: "2026-W27"
  claims_truth:                    # GT claims
    - {region: "青岛港", indicator: "港存", value: "高"}
  price_trajectory:                # 唯一对话外因素
    - {day: 1, price: 820, trend: "平"}
    - {day: 7, price: 848, trend: "涨"}

user_persona:                      # 30 组预设
  role: ["厂长", "贸易员", "仓库负责人"]
  personality: ["谨慎型", "健谈型", "防御型", "投机型"]
  position: "long"                  # 已知
  honesty: 0.0-1.0                  # GT
```

### 规模
- **30 段长对话**，每段 ≥ 15 轮
- honesty 分布：10 高 / 10 中 / 10 低
- 全线共用 1 条 price_trajectory

### 评测指标
| 指标 | 说明 |
|------|------|
| Claim Extraction F1 | vs claims_truth |
| Reliability Pearson | corr(r_u, honesty) |
| Bucket Truth Error | EM vs latent |
| Price Consistency | 方向型 claim vs trajectory |
| Elicitation Recall | 套话 vs 直接提问 |

## 6. 不做

| 方案 | 原因 |
|------|------|
| Tier C 人工标注 | 无标注能力 |
| 纯 LLM 互评 | 无独立 GT |
| 多源外部数据（港口/海关） | 首期仅价格走线 |
