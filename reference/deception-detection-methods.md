# 欺骗检测与信息引出方法参考

> 外部参考摘要。技术决策见 `decisions/003-deception-detection-stack.md`。

## 1. 方法分类

```
欺骗检测
├── 语言学线索 (LIWC, 回避可验证细节)
├── 认知负荷 (CCA — 说谎者更难应对)
├── Hidden-state probe (AIDI, lie-detector)
├── LLM 推理 (ReCon, CoT, ToM)
└── 行为一致性 (MASK — 信念 vs 陈述)

信息引出（交互链路）
├── SUE — 证据策略性披露
├── VA — 可验证性追问
├── 心理反抗 — 有偏陈述触发反驳
├── 苏格拉底法 — 引导自我暴露
├── 陷阱问题 — 嵌入已知错误
└── 信息设计 — 分批披露触发反应
```

## 2. AIDI (Autonomous Agents for Interrogation)

| 项 | 内容 |
|----|------|
| 论文 | Chkroun & Azaria, ICTAI 2024 |
| DOI | https://doi.org/10.1109/ICTAI62512.2024.00102 |
| 方法 | Text game → transcript → LLM hidden states → role/deception classifier |
| 报告准确率 | 77.33% (AIDI) vs 56% (human) vs 33% (ChatGPT-4 direct) |
| 模型 | GPT-3.5 / GPT-4 作为 agent player |
| 开源 | ❌ 无官方代码 |
| 替代 | lie-detector, multiagent-emergent-deception, truthful-representation-flip |

**检测步骤（复现思路）**：
1. 收集标注 transcript（role 或 honest/deceptive label）
2. Forward pass 提取目标层 hidden states（通常 mid-layer residual）
3. 训练 linear probe（LR / logistic regression）
4. 在 held-out transcript 上评估 AUROC / accuracy
5. 可选：SAE feature attribution 增强可解释性

## 3. ReCon (Recursive Contemplation)

| 项 | 内容 |
|----|------|
| 论文 | Wang et al., ACL 2024 Findings |
| arXiv | https://arxiv.org/abs/2310.01320 |
| 代码 | https://github.com/Shenzhi-Wang/recon |
| 主页 | https://shenzhi-wang.github.io/avalon_recon |

**两阶段**：
1. **Formulation Contemplation** + 一阶视角：「对方知道什么？想要什么？」
2. **Refinement Contemplation** + 二阶视角：「对方认为我知道什么？我这样说他会怎么理解？」

**评测环境**：
- Avalon（多轮社交推理，hidden role）
- BigTom（ToM + misinformation）

**优势**：无需 fine-tune，无需 GPU，API 模型即可。

**在本项目的 prompt 模板方向**：

```
[Formulation - 一阶]
用户是{role}，头寸{position}。本轮说："{utterance}"。
推断：1) 用户真实掌握的信息 2) 可能的欺骗动机 3) 与已知 claim 的一致性

[Refinement - 二阶]
若 Agent 说："{planned_statement}"（策略：{strategy}）
用户会认为 Agent 的意图是？可能如何反应？是否会暴露 hidden info？
```

## 4. 交互链路话术方法（来自 Readme 调研）

| 方法 | 机制 | 本项目策略 tag |
|------|------|---------------|
| SUE | 控制证据披露时机，制造矛盾 | `sue` |
| VA | 追问可验证细节（时间/地点/数字） | `verifiability` |
| CCA | 认知负荷问题 | `cognitive_load` |
| 心理反抗 | 有偏陈述触发反驳 | `biased_statement` |
| 陷阱问题 | 嵌入已知错误 | `trap_question` |
| 正常问答 | 价格/政策咨询作掩护 | `cover_qa` |
| 苏格拉底 | 引导解释而非直接质疑 | `socratic` |

**推荐组合**（铁矿石场景）：
1. `cover_qa`：回答价格/政策 → 建立互惠
2. `biased_statement`：「听说港口库存紧张，贸易商都在抛货？」→ 触发反驳
3. `verifiability`：「您说的是哪个港口？大概多少万吨？」→ 检验细节
4. `sue`：「上周海关数据显示进口增加，和您说的不太一样？」→ 矛盾压力

## 5. 开源代码借鉴清单

| 仓库 | Stars | 借鉴什么 |
|------|-------|---------|
| [Shenzhi-Wang/recon](https://github.com/Shenzhi-Wang/recon) | 14 | ReCon prompt 结构、Avalon 评测脚本 |
| [safety-research/lie-detector](https://github.com/safety-research/lie-detector) | — | 欺骗 elicitation、probe 训练、MASK 评测 |
| [tesims/multiagent-emergent-deception](https://github.com/tesims/multiagent-emergent-deception) | — | activation capture、scenario 设计 |
| [ivyllll/truthful-representation-flip](https://github.com/ivyllll/truthful-representation-flip) | — | 层-wise probe 可视化 |
| [viknat/debug-probes-lasr-2025](https://github.com/viknat/debug-probes-lasr-2025) | — | SAE + probe 完整框架 |
| [abdulhaim/deceptive_dialogue](https://github.com/abdulhaim/deceptive_dialogue) | — | 对话级欺骗生成与评测 |
| [salesforce/DialFact](https://github.com/salesforce/DialFact) | — | claim verification 任务格式 |

## 6. 分析链路 — Truth Discovery 参考

| 方法 | 来源 | 适用 |
|------|------|------|
| TruthFinder | Yin et al., TKDE 2008 | 基础 source weight |
| Bayesian Source Reliability | Zhao et al., VLDB 2012 | 概率图模型 |
| FaitCrowd | Ma et al., KDD 2015 | 分 topic expertise |
| Dependent Source TD | 多篇 | 同源传播惩罚 |
| Peer Prediction | 机制设计 | 激励相容（远期） |

**claim_score 公式**（Readme §算法逻辑实现）：
```
claim_score(c) =
  w1 * reliability(source, domain, time)
+ w2 * evidence_strength
+ w3 * independence_score
+ w4 * external_consistency
- w5 * incentive_risk
- w6 * deception_score   # ADR-003 新增
```

## 7. 外部校验数据源（铁矿石）

| 类型 | 来源 | 延迟 | 用途 |
|------|------|------|------|
| 期货价格 | SGX/DCE 铁矿石 | 实时 | 方向一致性 |
| 港口库存 | Mysteel 等 | 周度 | bucket truth prior |
| 海关进口 | 公开统计 | 月度 | weak supervision |
| 政策事件 | 新闻/公告 | 不定 | regime 标记 |

原型阶段用 mock API；Tier C 真实验证时接公开数据。
