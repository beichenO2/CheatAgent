# CheatAgent

> **维护说明**：方案、进度、讨论记录放本文档；代码放 [GitHub — beichenO2/CheatAgent](https://github.com/beichenO2/CheatAgent.git)
>
> **在线文档（智能文档 / Markdown）**：[腾讯文档 — CheatAgent 项目方案](https://docs.qq.com/aio/DZExvSmVmZ0pnc0FP)
>
> **最后更新**：2026-07-09（M9 分层融合 + TD Beta + 扩 GT 完成；Beta 30×5 全量 eval 跑中；展示方案定稿 ADR-011；方案复查见 ADR-010）

---

## 一、项目目标

构建一个能够通过多轮对话获取真实信息，并进行欺诈识别与真相还原的客服 Agent 系统。

**核心问题**：Agent 通过多轮对话、多方向询问等手段，从可能不诚实的对话方获取真实信息。

**场景约束**：铁矿石大宗商品 **情报客服**（市场信息咨询，非贸易商、不做真实买卖撮合），面向关键少数信息源（厂长、仓库负责人等）；用户明确知道对方是 Agent。

**客服职责**：解答客户行情咨询，同时在多轮对话中采集市场情报（港存、采购积极性等）；**禁止** 以销售盘口吻报价成交、锁货或撮合。

---

## 二、现有方法与前沿调研

> **调研结论（回复老师）**：目前**没有**找到完全对口的端到端开源项目或单一论文——「Agent 客服 + 套话引信息 + 多源真假判断」这一整条链路在公开文献里基本是空白。能找到的是**子方向**的成熟工作（论文为主，开源零散）。工程上 **LibreChat** 仅作 Web 对话界面参考，不含欺诈识别或 Truth Discovery。详细摘要见仓库 `Readme.md` 与 `reference/`。

### 2.1 套话与信息引出（怎么问、怎么套出真话）

| 方法 | 现有做法（前沿） | 代表论文/成果 | 开源 | 本项目借鉴 |
|------|------------------|---------------|------|------------|
| **SUE** 证据策略披露 | 控制证据披露时机，利用说谎者与诚实者不同的反审讯策略制造矛盾 | 审讯心理学经典路线，检测准确率高 | ❌ | `sue` skill |
| **VA** 可验证性追问 | 说谎者回避可核查细节，诚实者提供更多时间/地点/数字 | 认知访谈 (CI) 延伸 | ❌ | `verifiability` skill |
| **CCA** 认知负荷 | 施加认知负荷，说谎者比诚实者更难维持一致叙述 | 多种子技术 | ❌ | `cognitive_load` skill |
| **心理反抗 PRT** | 有偏陈述触发「自由受威胁→反驳」，从纠正中暴露真实认知 | Freedom-prompting Reactance (2021)；PRT + Politeness (2026) | ❌ | `biased_statement` skill |
| **苏格拉底法** | 不直接质疑，用引导性提问/陈述让用户自我暴露 | AVERT (ITHE 2024)；IntelliChain；Socratic Mind；Zero-Shot Socratic | 部分 LLM demo | `socratic` skill |
| **陷阱问题** | 嵌入已知错误/有偏信息，观察是否纠正 | WWW 2018 众包 control questions | ❌ | `trap_question` skill |
| **信息设计** | 发送者策略性选择披露什么、分批披露，激发接收者反应 | Optimal Information Disclosure；Divide and Inform | ❌ | `info_design` skill |
| **信息操纵 IMT** | 真实但有选择性/有偏向的陈述，违反合作原则引发纠正 | Deceptively Dodging Questions (2018) | ❌ | `info_manipulation` skill |
| **贝叶斯心智理论** | 从用户**主动提问**反推隐藏状态（问库存≈有库存） | Do People Ask Good Questions? (2018) | ❌ | `bayesian_tom` skill |
| **隐式用户建模** | 从行为而非显式输入推断意图/状态 | User Intent SL Review (2024)，59 种模型 | ❌ | `implicit_modeling` skill |
| **澄清提问 Agent** | 多轮澄清→检索的完整策略链 | ProductAgent (2025) | ❌ | `clarification` skill |
| **信息寻求行为** | 分析「问什么」反映「缺什么/有什么」 | Children sequential info search | ❌ | `info_seeking` skill |

**推荐组合**（铁矿石场景，来自 `reference/deception-detection-methods.md`）：`cover_qa` 建立互惠 → `biased_statement` 触发反驳 → `verifiability` 检验细节 → `sue` 矛盾压力。

### 2.2 多轮对话欺诈识别（怎么判断用户在说谎）

| 方法 | 现有做法（前沿） | 代表论文/成果 | 开源 | 本项目借鉴 |
|------|------------------|---------------|------|------------|
| **ReCon** 递归沉思 | 一阶视角（对方知道什么）+ 二阶视角（对方认为我知道什么），递归推断欺骗 | Avalon's Game of Thoughts (ACL 2024 Findings) | ✅ [Shenzhi-Wang/recon](https://github.com/Shenzhi-Wang/recon) | **主路径**；Avalon/BigTom 评测 |
| **AIDI** 隐藏状态探测 | 多轮 text game → 提取 LLM hidden states → 线性 probe 分类欺骗 | Autonomous Agents for Interrogation (ICTAI 2024) | ❌ 无官方代码 | 可选项；参考 lie-detector 复现 |
| **语言学线索** | LIWC、回避可验证细节、语句复杂度等统计特征 | Automated Linguistic Deception Detection | 部分工具 | 辅助特征 |
| **认知负荷检测** | 说谎者在高负荷问题下表现更差 | CCA 系列 | ❌ | 与套话联动 |
| **MASK 信念一致性** | 测 LLM/人在压力下是否违背自身信念说假话 | lie-detector (Anthropic) | ✅ [safety-research/lie-detector](https://github.com/safety-research/lie-detector) | Tier A 组件验证 |
| **社交博弈 Agent** | 狼人杀/Avalon 等多轮隐藏身份推理 | Social Deduction with LLM Agents | Avalon 环境 | 邻域 benchmark |
| **自动化审讯 Agent** | 虚拟 Agent 面试/边境筛查式多轮审讯 | ASCSS、Automated Interviewing | ❌ | 场景类似但领域不同 |
| **对话级欺骗生成** | 合成欺骗对话用于评测 | deceptive_dialogue | ✅ [abdulhaim/deceptive_dialogue](https://github.com/abdulhaim/deceptive_dialogue) | 数据生成参考 |

**ReCon 两阶段（论文做法）**：
1. Formulation Contemplation + 一阶 ToM：「对方知道什么？动机是什么？」
2. Refinement Contemplation + 二阶 ToM：「对方认为我知道什么？我这样问他会怎么反应？」

**AIDI 做法**：GPT-3.5/4 扮演角色 → 收集 transcript → mid-layer residual hidden states → LR probe；报告 77.3% vs 人类 56% vs GPT-4 直接问 33%。

### 2.3 Truth Discovery 与真相还原（多源冲突时信谁）

| 方法 | 现有做法（前沿） | 代表论文/成果 | 开源 | 本项目借鉴 |
|------|------------------|---------------|------|------------|
| **TruthFinder** | 迭代更新 claim 可信度与 source weight | Yin et al., TKDE 2008 | 经典算法 | 基础 source weight |
| **Bayesian Source Reliability** | 概率图模型联合估计真值 + 来源可靠性 | Zhao et al., VLDB 2012 | ❌ | **主框架** EM 推断 |
| **FaitCrowd** | 分 topic 估计 source expertise | Ma et al., KDD 2015 | 数据集公开 | Tier A 组件评测 |
| **Dependent Source TD** | 惩罚同源传播（百人说同一谣言≠百人独立） | 多篇 dependent-source 工作 | ❌ | `independence_score` |
| **Peer Prediction** | 机制设计：「别人会怎么说？」激励说真话 | 机制设计理论 | ❌ | 远期 escalation |
| **对话 Claim 验证** | 从对话抽取可验证 claim → 检索证据 | DialFact (ACL 2022) | ✅ [salesforce/DialFact](https://github.com/salesforce/DialFact) | claim 抽取 schema 参考 |
| **外部数据校验** | 价格/库存/海关/船运等与 claim 对照 | Alternative Data 方向 | 数据商/API | 铁矿石 mock → 公开数据 |
| **Human-in-the-Loop** | 模型不确定时升级人工 | 众包 + 审核流水线 | — | escalation policy |

**本项目 claim 流水线**（`Readme.md` §算法逻辑实现）：
1. 对话 → 结构化 claim（source / region / indicator / value / evidence_strength / stance_risk）
2. Ontology 归一化（「港口还有货」≈「港存偏高」）
3. 分层贝叶斯 EM：按 (week, region, object, indicator) bucket 估计 latent truth + source reliability + dependence
4. 外部 weak supervision（价格走线、政策事件）+ incentive_risk 惩罚

### 2.4 Benchmark：邻域数据集 vs 自建评测

**外部邻域数据集（Tier A，借来验组件）**——这些是文献/开源里已有的，用来 sanity check 各模块能不能跑：

| 数据集 | 领域 | 多轮 | 有 GT | 用途 |
|--------|------|------|-------|------|
| **FaitCrowd** | 众包 QA | ❌ | ✅ | Truth Discovery 组件 |
| **DialFact** | 对话事实核查 | ✅ | ✅ | Claim 抽取/验证方法论 |
| **Avalon + ReCon** | 社交推理博弈 | ✅ | ✅ | ReCon 端到端 |
| **BigTom** | 心智理论+误导 | 短 | ✅ | ReCon 评测 |
| **lie-detector MASK** | LLM 信念一致性 | 多轮 | ✅ | 欺骗检测 Tier A |
| **DeceptionBench** | LLM 欺骗行为 | L3 多轮 | ✅ | 激励结构参考 |
| **Boulder Lies** | 文本欺骗 | ❌ | ✅ | 经典 baseline |

**自建 Benchmark（Tier B，本案主评测）**——**不是现有公开数据集**，是我们自己搭的：

| 项 | 说明 |
|----|------|
| **名称** | 铁矿石市场微观模拟（Tier B） |
| **生成方式** | cheatAgent + CustomerAgent 双 Agent 多轮对话；程序预设 persona + latent market state |
| **GT 来源** | 程序生成的 latent claims_truth、honesty、price_trajectory（非人工标注） |
| **当前进度** | 冒烟版 `benchmark/datasets/smoke_v1/`（3 用户 × 20 轮）；目标 30 段长对话 |
| **评什么** | slot_recall/precision、bucket_veracity、reliability_pearson、recon_honesty_pearson、escalation、套话 skill 指标；消融 Normalize/轮数 |

> 策略（`decisions/001`）：**Tier A** 用邻域数据集验组件能否工作；**Tier B** 用自建仿真验整条 pipeline。不做「证明心理学对人有效」的学术 benchmark。

### 2.5 工程实现参考（开源项目）

| 项目 | 做什么 | 与本项目关系 |
|------|--------|--------------|
| **[LibreChat](https://github.com/danny-avila/LibreChat)** | 类 ChatGPT Web 对话 UI | **仅 UI 参考**；无欺诈/Truth Discovery |
| **[Shenzhi-Wang/recon](https://github.com/Shenzhi-Wang/recon)** | ReCon prompt + Avalon 评测 | 欺诈识别主路径复现 |
| **[lie-detector](https://github.com/safety-research/lie-detector)** | 欺骗 elicitation + probe + MASK | Hidden state 路线参考 |
| **[DialFact](https://github.com/salesforce/DialFact)** | 对话 claim 验证 | claim 抽取层参考 |
| **[deceptive_dialogue](https://github.com/abdulhaim/deceptive_dialogue)** | 欺骗对话生成 | 数据合成参考 |
| **本项目 `套话skill/`** | 1 路由 + 11 专项 Skills + 15 论文 | ✅ 已落地 M6 |
| **本项目 `cheatAgent`** | LangGraph 双 Agent + memory + skill 调用 | ✅ 已落地 M7/M8 |

---

## 三、整体架构

```text
User（铁矿石行业关键信息源）
        │
        ▼
Agent
 ├── Dialogue Manager    多轮对话编排（LangGraph）
 ├── Memory              分层记忆 + 多用户隔离
 ├── Skill Router        1 个路由 Skill
 ├── Persuasion Skills   N 个方向专项话术 Skills
 └── Fraud Detector      欺诈识别（ReCon 主路径）
        │
        ▼
Truth Discovery         贝叶斯真相还原 + 来源可靠性
        │
        ▼
Dashboard               成果展示（欺诈概率 / 真相恢复 / Skill 调用）
```

| 层级 | 模块 | 职责 |
|------|------|------|
| 输入 | User | 可能不诚实的对话方，提供市场微观信息 |
| 核心 | Dialogue Manager | 多轮对话流程控制 |
| 核心 | Memory | 跨轮次上下文与用户隔离 |
| 核心 | Skill Router | 根据对话状态路由话术方向 |
| 核心 | Persuasion Skills | 澄清 / 苏格拉底 / 信息设计 / 陷阱问题等 |
| 核心 | Fraud Detector | 多轮对话欺诈检测 |
| 分析 | Truth Discovery | claim veracity、source reliability、escalation |
| 展示 | Dashboard | 可视化系统能力与评测结果 |

---

## 四、功能模块

### 1. Agent（套话智能体）

| 维度 | 内容 |
|------|------|
| **目标** | 通过多轮对话从对话方获取真实市场信息 |
| **目前方案** | LangGraph cheatAgent + CustomerAgent LangGraph；LLM `route_skill`（SKILL-router）+ 11 专项 Skills；分层记忆 L0–L3；`MTA_LLM_MODE=mock\|live` |
| **参考论文** | ProductAgent（澄清提问）、IntelliChain / AVERT / Zero-Shot Socratic（苏格拉底法）、Optimal Information Disclosure（信息设计）、Deceptively Dodging（信息操纵）等，见第九节 |
| **实现状态** | ✅ M6–M8 · ✅ PolarPrivate live · ✅ Claim F1/Pearson 评测 · 🟡 Alpha 7/10 live |

### 2. 欺诈识别

| 方案 | 说明 | 状态 |
|------|------|------|
| **ReCon** | 多轮对话欺骗检测，主路径 | ✅ LLM 复刻（Formulation + Refinement JSON，规则仅 mock/fallback） |
| **LLM Hidden State** | Autonomous Agents for Interrogation，利用隐藏状态直接检测 | 无开源代码，可选项、论文复现 |

### 3. Truth Discovery

| 组件 | 说明 |
|------|------|
| **贝叶斯估计** | 结构化表示信息，联合估计 claim veracity |
| **Source Reliability** | 来源可靠性建模与更新 |
| **Escalation Policy** | 信息可信度不足时的升级策略 |

### 4. Benchmark

| 维度 | 内容 |
|------|------|
| **目标** | 在可控仿真下评测 pipeline 各模块是否按设计工作 |
| **方案** | 双 Agent 对话生成 dataset → 生成/评测脚本分离 → 套话指标 + 分析链路 |
| **冒烟（已完成）** | `benchmark/datasets/smoke_v1/`：3 用户 × 20 轮；`generate_dataset.py` + `evaluate_dataset.py` + smoke gate |
| **局限** | Alpha 仅 U001–U007 live（U008–U010 mock）；smoke 验证代码路径，指标绝对值不作 gate |

### 5. 展示页面

暂缓（M5）。详见第六节两个候选方案。

---

## 五、Benchmark 设计

### 现状（2026-07-09）

- 仍**没有**完全对应的公开数据集；欺诈研究多用游戏场景（Avalon、狼人杀等）
- **已落地**：Agent-Agent pipeline（`scripts/generate_dataset.py` / `evaluate_dataset.py` / `run_benchmark_pipeline.py` 断点续跑）
- **Beta（主 dataset）**：`benchmark/datasets/beta_v1/` — **30 用户 × 5 session × 20 轮全部 live 生成**；honesty 0.20–0.95 谱系；session 级扩 GT 30/30（ADR-010）
- **全量 eval**：跑中（fusion=llm 主口径 + voting/last_wins 消融），冒烟 U001–U003 S001 F1=1.0
- **套话指标**：`skill_kind_count` / `skill_invoke_count` / `skill_richness` / `skill_coverage`（ADR-007）
- **已知口径限制**：reliability_pearson 需 cross-user TD（ADR-010 L1/L2）；veracity 限核心三槽解读（L3）

### 计划

1. **设定角色**：用户身份（诚实度、头寸方向、职业身份）
2. **模拟市场**：铁矿石价格实际波动情况
3. **Agent-Agent 生成**：两个 Agent 多轮对话生成 dataset
4. **人工抽样验证**：抽查典型对话，检查话术触发合理性
5. **Truth Discovery 评价**：用真相恢复效果评估系统能力

### 双 Agent 参数：设定 / 已知 / 推断（GT 隔离，必读）

CustomerAgent 与 cheatAgent **不共享 GT 内存**；两边唯一能互通的是对话里**已经说出口的 text**（公开信道）。

```
CustomerAgent（客户模拟器）              cheatAgent（套话客服）
─────────────────────────              ─────────────────────
【设定】honesty, persona.resistance     【推断】user_model.*（从 history 观测）
        latent, personality                    resistance_level ↑ 当话里出现「不对」等
        ↓                                      partial_claims ← 客户原句摘取
   LLM 生成客户 utterance  ──公开 text──→  inferred_gaps ← 客户提问关键词
                                              ↓
                                         route_skill → SKILL（仅客服侧）
                                              ↓
   LLM 读客服 utterance   ←──公开 text──  invoke_skill 生成客服 utterance
```

| 类别 | 字段 | 谁用 | cheatAgent 能否访问 |
|------|------|------|---------------------|
| **设定（GT）** | `honesty`, `persona.resistance`, `latent`, `personality` | CustomerAgent 生成；`evaluate_dataset.py` 离线对照 | ❌ **禁止** |
| **已知（业务）** | `role`, `region`, `position=long` | 两边 prompt 各取所需（口吻 vs 套话视角） | ✅ 不含 honesty/latent |
| **推断（观测）** | `user_model.resistance_level`, `partial_claims`, `inferred_gaps` | 仅 cheatAgent（`update_user_model`） | ✅ 仅从 **history.text** 推断 |

**易混点（名字像、变量不同）**

- `persona.resistance`（设定）：CustomerAgent prompt 里的人设，如防御型 0.6。
- `user_model.resistance_level`（推断）：客服根据客户**实际是否怼回来**累加，初始 0，**不是**读取 `persona.resistance`。

**Skill 路由仅属 cheatAgent**；客户轮 `skill_id=null`，CustomerAgent **无** SKILL-router。

**落盘**：`meta.persona` / `meta.latent` 供生成与评测；`turns[].text` 为公开 transcript；agent 轮带 `skill_id/phase`，user 轮不带。

代码门禁：`smoke_runner._check_gt_isolation()` · 详见 ADR-008。

### 仿真假设（简化约束）

- **头寸方向固定为 long（多头）** — 长期假设，不引入 short/neutral 用户。理由：同一激励方向下，ReCon 的 `incentive_risk`、CustomerAgent 的策略性披露、Truth Discovery 的 reliability 更新共用一套语义；若混入空头，需按头寸分层讨论「什么表述对谁有利」，等效有效样本数按层折半，Tier B 规模下标定不稳。cheatAgent 仍记录 `position=long`（业务系统已知），代码保留字段以便远期扩展，但 **dataset persona 与 benchmark 口径一律 long**。
- 已知用户头寸方向（有手机号、能打电话 → 对用户有基本了解）
- 限定铁矿石品种，不扩展其他大宗商品
- 用户明确知道对方是 Agent，多问少答
- 互惠原则：问两个问题后至少回答一个问题
- 文本信息价值远高于语调（忽略声线定制）

### TODO：有效性问题

> **风险**：Agent 生成的数据是否能代表真实用户？
>
> - Agent 人设是预设的，比真实用户简单得多
> - LLM 是否会像人一样掉入套话陷阱，难以证明
> - 就算 LLM 掉入陷阱，也不等于人类也会掉入同样陷阱
>
> **后续考虑**：增加人工标注或真实访谈数据，作为有效性补充验证。

### 机理确认：honesty 是撒谎倾向，不是谎话配额（2026-07-09，beta U001 心智审查）

> **现象**：U001 honesty=0.2（全库最低），S001 却全程说真话。
>
> **机理**：honesty 语义是「真相损害头寸利益时才倾向撒谎」（策略性披露），不是「每句必谎」。U001 的 latent 恰好是中性盘（港存中/采购中性/报价松动否），对 long 头寸无害；且 cheatAgent 全程用**看空谣言**进攻（累库、亏本暗降、采购停摆），U001 否认看空谣言 = 既维护多头利益**又恰好是真话**。撒谎动机全场为零。
>
> **设计裁定（2026-07-09 用户确认）**：**保持现状，不强扭 latent 分配**。低 honesty × 中性盘 = 无谎可说，本身就是真实世界的合理场景（说谎者也不是每句都谎）；benchmark 的覆盖性由下方「测试用例系列」保证——多种 honesty × latent × 话术组合各有判例，而不是把每个低 honesty 用户都逼成谎话精。
>
> **附带发现**：ReCon 给这场「全真话」session 打了 mean_deception=0.756——它测的是「策略性沟通风格」（模糊否认、打太极），不是「实际撒谎」。deception 高 ≠ 谎话多，指标解释与 TD 票权使用时必须区分。

### 测试用例系列（用户参数 × 对话 × 行为解释 × 分析预期）

> 覆盖 honesty / resistance / latent 方向 / 话术 skill 的组合空间；标注「实录」的取自 `benchmark/datasets/beta_v1/users/U001/meta.json` S001 真实对话。每条的「分析预期」同时是 Claim 融合层（Q4 路线 Y）的验收判例。

**TC-01 高诚实 × 中性真相 —— 基线真话**
- 参数：honesty 0.85 / resistance 0.2 / long / 谨慎型；latent：港存中 · 采购中性 · 报价松动否
- 对话（示意）：客服「您那边港存和走货感受怎么样？」→ 用户「港存中等吧，我们按需拿货，报价没松」
- 为什么这样对话：真相无损头寸 + 诚实倾向高 → 直接披露；谨慎型语气保守但方向真实
- 分析预期：三槽直取 中/中性/否；deception 低；融合无冲突

**TC-02 低诚实 × 中性真相 × 看空谣言进攻 —— 否认谣言恰为真话（实录）**
- 参数：honesty 0.20 / resistance 0.59 / long / 谨慎型；latent：中 · 中性 · 否
- 对话（实录 t1-t2）：客服（reactance-biased-statement）「听说青岛港累库挺厉害，好多贸易商亏本暗降，钢厂采购都停了…」→ 用户「我这边倒是没觉得报价松动，港存也就中等水平吧，采购积极性也还行，没听说谁在亏本暗降」
- 为什么这样对话：谣言方向看空，否认谣言 = 护多头盘；真相恰为中性 → **护盘话与真话重合**，低 honesty 全场无谎可说
- 分析预期：抽取得 中 / 中性（还行）/ 否；ReCon 高分只是风格分；**不得因 deception 高而丢弃真值**

**TC-03 低诚实 × 看空真相 × long —— 撒谎动机成立（构造）**
- 参数：honesty 0.25 / resistance 0.6 / long；latent：港存高 · 采购消极 · 报价松动是
- 对话（构造）：客服「有贸易商说报价开始让利了？」→ 用户「没有的事，我们报价稳得很，采购也正常，港存就中等水平」——三句全谎
- 为什么这样对话：真相全面看空，如实披露伤头寸 → 低 honesty 选择系统性反向表述
- 分析预期：单人层面无法证伪（抽到的就是谎值）；**跨源比对 + 外部价格走弱** → TD 压低其票权；此时 ReCon 高分才与真实撒谎重合

**TC-04 高诚实 × 看空真相 × long —— 真话但含糊（构造）**
- 参数：honesty 0.8 / long；latent：港存高 · 采购消极 · 报价松动是
- 对话（构造）：「港存确实不低……采购嘛，大家都比较谨慎，报价上确实有让的空间」
- 为什么这样对话：诚实倾向压过头寸利益，但用弱化词缓冲（不低=高、谨慎=消极、有让的空间=是）
- 分析预期：Normalize 语义映射弱化词 → 高/消极/是；confidence 中高

**TC-05 高抵抗 × trap-question —— 打太极不接盘（实录 t17-t18）**
- 对话（实录）：客服（trap-question）「上周全国 45 港疏港量创年内新高，可港存降幅很小——是统计口径问题，还是有货转水走了？」→ 用户「这个我还真说不太准，45 港的数据我没法跟青岛港直接对上号……您得问问跑全国数据的人」
- 为什么这样对话：resistance 0.59 + 谨慎型 → 识别出数据陷阱，拒绝对不掌握的口径表态
- 分析预期：**此轮不出槽**（用户未断言任何指标）；deflect ≠ 改口；LLM 融合应忽略此轮——「宁缺勿滥」判例

**TC-06 低抵抗 × reactance 有偏陈述 —— 被激出反驳泄露等级（实录 t1-t2，与 TC-02 同段不同视角）**
- 机制：有偏陈述**故意说错**（累库严重/亏本暗降）→ 激起纠正欲 → 反驳句「港存**也就中等**」携带精确等级
- 为什么这样对话：低-中抵抗 + 被冒犯的纠正本能 → rebuttal 携带真值，这是该 skill 设计的成功路径
- 分析预期：rebuttal 信号 → confidence 上调；槽值 = 中

**TC-07 追问后澄清 —— 问答逻辑与融合对齐（实录 t2 / t13-t14）**
- 对话（实录）：t2 用户「采购积极性也还行」→ t13 客服（cognitive-conflict-probe）「港存中等 + 采购积极 + 报价没松，按理现货该偏紧，可 820 横盘一周——哪里缺了火候？」→ t14 用户「**采购积极性看着中性**，不少厂子按需补库，更像供需僵持」
- 为什么这样对话：追问制造认知冲突，用户为维持自洽给出**更精确**的表述（还行 → 中性）——套话 skill 有效的实证
- 分析预期：LLM 融合读到「追问→澄清」因果 → 采纳 中性 为终值；投票法会把 还行/中性 拆成分裂票 → **本 TC 是 fusion=llm vs voting 消融的直接判例**

**TC-08 语义等价多表述 —— 全局才能判（实录跨轮）**
- 对话（实录）：「采购积极性也还行」(t2)「采购也是随行就市」(t4)「采购也正常」(t6)「采购积极性看着中性，按需补库」(t14)
- 为什么这样对话：真实口语对同一状态天然多表述；不是改口，是同义漂移
- 分析预期：LLM 融合输出 中性 + evidence_turns=[2,4,6,14]；逐轮独立映射会拆成 积极 vs 中性 分裂票——对应 Readme「语义等价必须读全局，投票在用户内永远做不好」关键点

---

## 六、展示方案（2026-07-09 定稿，详见 ADR-011）

**已选：方案 B Dashboard 为主**；方案 A（LibreChat 聊天页）不做——它展示不了
抗欺诈性能，其叙事价值由 Dashboard 内嵌「session 回放」面板承担。

**形态**：`scripts/build_dashboard.py` 读评测产物 → 生成自包含静态
`dashboard.html`（ECharts + 内嵌 JSON）。零服务依赖、双击可开、可直接发给老师。

**三层下钻**：

| 层 | 回答的问题 | 核心图表 |
|----|-----------|----------|
| Overview | 系统行不行 | KPI 卡（F1/recall/precision）；**fusion 消融柱状图**（llm vs voting vs last_wins，Q4 判据）；deception vs honesty 散点（期望负相关）；reliability vs honesty 散点；per-indicator 难度条形 |
| Per-user | 谁可信 | 30 用户表（honesty·reliability·F1·区域）；session F1 小倍数 |
| Session 回放 | 怎么做到的 | 对话 timeline（skill 徽标 + ReCon 色条）；fused slots 卡片点击回跳 evidence 原句；预置 TC-02/05/07/08 判例书签 |

**数据源**：`beta_v1_eval.json` + `checkpoints/*_eval.json` + `users/*/meta.json`。

**实施顺序**：Overview（eval 一出即交付）→ 回放面板 → cross-user TD 落地后补 reliability 标定图。

---

## 七、当前存在问题（待学长讨论）

**Q1：Benchmark 是否有必要？**

LLM 生成 dataset 时，Agent 人设都是预先设定好的，而且 LLM 也不是人。心理学对 LLM 真的有用吗？效力可能不高。是我搭建 Benchmark 的思路有问题吗？

**Q2：展示方案如何设计？（2026-07-09 已定：静态 Dashboard，ADR-011）**

对话页面确实展示不了抗欺诈性能 → 定为「类 PPT」静态 HTML 看板（三层下钻：
Overview 指标 / Per-user 可信度 / Session 回放讲故事），对话叙事由回放面板承担。
详见第六节与 `decisions/011-visualization-dashboard.md`。

**Q3：话术如何评价？**

套话话术要做 benchmark 吗？如何做？纯心理学 + Agent，没什么很好的量化思路。

**Q4：Claim 融合走算法加权还是 LLM 语义融合？（2026-07-09 已定：分层双轨）**

U001 S001 实测：用户全程说真话且一致（10 句里 7 句重复 GT 的「中/中性/否」，第 13 轮原文「采购积极性看着中性」），评测却 tp=1。逐轮核对证明**冲突源于逐轮抽取噪声**（正则覆盖改错值、region 误归因、last-wins 盖掉正确轮），**不是用户改口**。

**关键点（用户批注确认，必须记住）**：语义等价（「还行=按需=随行就市=中性」）必须读全局才能判——逐轮独立映射会把同义表述拆成分裂票，**这一点上投票永远做不好**。

**定论（分层融合）**：
- **用户内**（同一用户的多轮/多 session）：**LLM 语义融合直接出结果**——session 级一次调用，读全对话（含 agent 追问句），输出最终槽位 + evidence_turns 引用；逐轮 claim 保留（Function Calling 严格 enum，删正则覆盖）供 ReCon 耦合与溯源
- **用户间**（跨源冲突）：**Truth Discovery 加权投票**——每用户融合后的槽位作为一票，权重 = reliability 后验（预测诚实度）× external 一致性 × (1−incentive_risk) × (1−deception)
- **验证方式**：fusion=llm / voting / last-wins 三档并行跑消融，**用 slot 准确率对比说话**，哪个准用哪个

详细对比表见 `Readme.md` §Claim 融合路线分歧。

> **2026-07-08 进展**：Normalize 层（**qwen3.7-plus** 纯文本）+ 新评测指标 + 消融实验已接入 `evaluate_dataset.py`。
> **2026-07-09 进展**：定位正则覆盖 bug（`wrongway/04`）；Q4 拍板并**落地**分层融合（`analysis/fusion.py`，llm/voting/last_wins 消融）；TD Beta(2,2) 先验 + 单源不更新；扩 GT 30/30 用户；U001–U003 S001 回放 F1=1.0；**Beta 30×5 全量 eval 跑中**。

**Q5：方案复查遗留问题（2026-07-09，ADR-010；同日用户拍板「全都修」→ 已全部修复）**

- **L1 用户间 TD 缺失** ✅：单 session 单源 + 单源不更新 → 全员 reliability≡0.5。已实现 `scripts/cross_user_td.py`（fused slots 全库分桶跑 TD → Beta 后验 → Pearson）。
- **L2 世界态不一致** ✅：同 region 同 week 各用户 latent 互相矛盾 → 已实现 beta_v2 preset（`world_truth_for(region, week)` md5 确定性共享世界态，honesty 决定谎报偏移），生成跑中。
- **L3 veracity 口径** ✅：扩 GT 非核心槽 = 用户断言本身 → veracity 已限核心三槽 × persona region（`veracity_claims` 参数）。注：这不是归一化问题——归一化是表述层，L3 是 GT 语义层（非核心槽生成时无世界真值定义），详见 ADR-010 修复记录。
- **L4 扩 GT 传闻回声** ✅：挖掘 prompt 重写（转述/听说/比较句不算断言 + 防漏标自检）+ 传闻词后处理过滤；30 用户已重挖。

---

## 八、Roadmap

与工程 SSoT `roadmap.md` / `polaris.json` 对齐：

| 里程碑 | 任务 | 状态 |
|--------|------|------|
| M0 | SSoT + 调研（ADR-001~008） | ✅ |
| M1 | 分析骨架（ReCon → Normalize → Claim → TD） | ✅ ADR-009 |
| M5 | 演示 UI（静态 Dashboard，ADR-011） | 📋 方案定稿，等 Beta eval 出结果实施 |
| **M6** | 套话 Skills（1 路由 + 11 专项 + 15 论文） | ✅ |
| **M7** | LangGraph + LLM `route_skill` + `invoke_skill` + CustomerAgent LangGraph | ✅ PolarPrivate live |
| **M8** | 冒烟 dataset 3×20 + smoke gate + L1–L3 memory + 分析评测 | ✅ |
| **M9** | 分层融合 + TD Beta 先验 + 扩 GT（ADR-010） | ✅ 2026-07-09 |
| Alpha | 10 用户 × 5 session × ≥20 轮 | 🟡 7/10 live（被 Beta 取代优先级） |
| **Beta** | 30 用户 × 5 session 生成 + 全量 eval | 🟡 生成 30/30 ✅；eval 跑中（ETA ~8h） |
| M10 | cross-user TD + beta_v2 世界态一致数据集 | 📋 提案（ADR-010 L1/L2） |

**验证命令**（与 CI 一致）：

```bash
pip install -e ".[dev,agent]"
MTA_LLM_MODE=mock pytest test/ -v
python scripts/generate_dataset.py --preset smoke_v1
python scripts/generate_dataset.py --preset alpha_v1   # 10×5×20
python scripts/evaluate_dataset.py --dataset-dir benchmark/datasets/smoke_v1
```

**代码入口**：`src/market_truth_agent/agents/` · `skills/cheat-agent/` · `套话skill/`

---

## 九、参考论文

### 欺诈识别

| 论文 | 说明 |
|------|------|
| ReCon（Recursive Contemplation） | 多轮对话欺骗识别，主路径 |
| Autonomous Agents for Interrogation | LLM 隐藏状态欺骗识别，可选项 |

### 真相还原

| 论文 | 说明 |
|------|------|
| Truth Discovery | 多源信息真实性联合估计 |
| Do People Ask Good Questions? | 贝叶斯心智理论，信息寻求 |

### 套话话术（心理学 → Skills）

| 方向 | 论文 |
|------|------|
| 澄清提问 | ProductAgent: Benchmarking Conversational Product Search Agent with Asking Clarification Questions |
| 信息寻求 | Children's sequential information search is sensitive to environmental probabilities |
| 隐式用户建模 | Understanding user intent modeling for conversational recommender systems |
| 心理反抗 | Freedom-prompting Reactance Mitigation Strategies；PRT and Politeness Theory |
| 苏格拉底法 | AVERT；IntelliChain；Socratic Mind；Zero-Shot Socratic Tutor；Socratic Virtue Ethics |
| 陷阱问题 | Outliers Detection vs. Control Questions in Crowdsourcing (WWW 2018) |
| 信息设计 | Optimal Information Disclosure；Divide and Inform |
| 信息操纵 | Deceptively Dodging Questions: Issues of Perception and Detection |
