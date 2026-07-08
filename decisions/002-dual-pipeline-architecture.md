# ADR-002: 双链路架构 — 分析链路与交互链路

## 状态
accepted

## 背景

问题天然分为两个子问题（`Readme.md`）：
1. **怎么问**才能套出真实信息（交互）
2. **怎么判**用户说的是否可信（分析）

两者数据流交织但职责分离：交互链路产出对话；分析链路消费对话产出 claim、真值、信用。

## 逻辑架构

### 分析链路（Analysis Pipeline）

```
用户输入（历史对话）
    │
    ▼
┌──────────────────┐
│ 1. 对话存储层     │  conversation + turn + timestamp + metadata
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 2. 单用户分析     │  欺骗检测 + 激励偏差 + 证据强度
│    + 建模         │  → per-user per-turn signals
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 3. Claim 抽取     │  NL → structured claim schema
│    + 本体规范化   │  canonicalize(region, indicator, value)
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 4. 多源真值推断   │  Truth Discovery: z_b, r_{u,d,t}, a_{u,v,t}
│    (跨用户)       │  + 来源依赖惩罚 + 外部 weak supervision
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 5. 用户信用评估   │  Bayesian reliability posterior
│    + 升级策略     │  escalation: 何时人工介入
└──────────────────┘
```

**输出**：
- `claims[]` — 结构化市场判断
- `bucket_truths{}` — 每个 (week, region, object, indicator) 的 latent truth 估计
- `user_reliability{}` — 用户可信度后验
- `escalation_flags[]` — 需人工复核的 bucket/user

### 交互链路（Interaction Pipeline）

```
用户输入
    │
    ▼
┌──────────────────┐
│ 1. 轻量用户建模   │  从提问/已有回答推断：意图、知识深度、可能的隐藏状态
│    (实时)         │  贝叶斯心智理论 / 信息寻求行为分析
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 2. 话术策略选择   │  SUE / 有偏陈述 / 可验证性 / 认知负荷 / 陷阱问题
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 3. 引导式信息提供 │  故意给出 partial/biased 信息 → 触发心理反抗
│    + 套话执行     │  从反驳/纠正中提取 hidden claim
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 4. 反馈收集       │  解析用户响应：纠正、补充细节、情绪信号
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 5. 掩护问答       │  正常业务问答（价格、政策）穿插，降低对抗感
└──────────────────┘
         │
         └──→ 写入对话存储层（供分析链路消费）
```

**输出**：
- 下一 Agent  utterance
- `strategy_log` — 本轮使用的策略类型与目标
- `elicited_claims[]` — 实时抽取的新 claim（轻量，完整分析走分析链路）

## 代码模块映射

```
src/
├── storage/
│   ├── conversation_store.py      # 分析链路-1
│   └── schema.py                  # turn / claim / user models
├── analysis/
│   ├── claim_extractor.py         # 分析链路-3
│   ├── ontology.py                # 铁矿石本体
│   ├── deception_detector.py      # 分析链路-2 (ReCon only, ADR-003)
│   ├── truth_discovery.py         # 分析链路-4
│   ├── external_validator.py      # 分析链路-4 外部校验
│   └── credit_scorer.py           # 分析链路-5
├── interaction/
│   ├── user_modeler.py            # 交互链路-1，心理学炼化（ADR-004）
│   ├── phase_fsm.py               # 阶段状态机（ADR-004）
│   ├── tactic_selector.py         # 原语选择
│   ├── tactics/                   # L1 策略原语模板
│   ├── recon_orchestrator.py      # L3 ReCon 包裹决策
│   └── elicitation_engine.py      # 对外入口
├── recon/                         # ReCon 核心（分析+交互共用，ADR-003）
├── benchmark/
│   ├── tier_a/                    # 组件评测
│   └── tier_b/                    # 30 段长对话模拟
└── api/ + ui/                     # 演示
```

## 两链路交互点

| 交互点 | 方向 | 数据 |
|--------|------|------|
| 对话存储 | 交互 → 分析 | `ConversationTurn[]` |
| 用户模型 | 分析 → 交互 | `user_reliability`, 已有 claims（只读摘要） |
| 实时 claim | 交互 → 分析 | 轻量 `claim` 候选，分析链路异步精炼 |
| 策略反馈 | 分析 → 交互 | `incentive_risk` 高 → 切换 SUE/有偏陈述 |

## 对话存储 Schema（分析链路基础）

```json
{
  "conversation_id": "uuid",
  "user_id": "string",
  "scenario": "iron_ore_market",
  "started_at": "ISO8601",
  "turns": [
    {
      "turn_index": 0,
      "speaker": "user|agent",
      "text": "...",
      "timestamp": "ISO8601",
      "strategy_tag": "cover_qa|biased_statement|sue|direct_ask|null",
      "metadata": {
        "elicitation_goal": "port_inventory",
        "agent_model": "gpt-4o",
        "latency_ms": 1200
      }
    }
  ]
}
```

## Claim Schema（`Readme.md` 已有，此处确认为 SSoT）

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
  "evidence_strength": 0.7,
  "stance_risk": 0.3,
  "provenance": {"utterance": "...", "turn_index": 3},
  "extractor_confidence": 0.85,
  "deception_score": 0.2,
  "canonical_key": "2026-W27|青岛港|铁矿石|港存"
}
```

## 后果

- 交互链路和分析链路可独立开发、独立 Benchmark
- 分析链路不依赖特定话术，可回放任意对话
- 交互链路可先用规则 + ReCon prompt，不阻塞 Truth Discovery 开发

## 参考

- `Readme.md` §算法逻辑、§算法逻辑实现
- ProductAgent 澄清链：[DOI 10.1145/3770366.3770412](https://doi.org/10.1145/3770366.3770412)
- 心理反抗 + 苏格拉底法：`Readme.md` §陷阱问题
