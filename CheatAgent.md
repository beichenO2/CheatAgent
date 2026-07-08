# CheatAgent

> **维护说明**：方案、进度、讨论记录放本文档；代码放 [GitHub — beichenO2/CheatAgent](https://github.com/beichenO2/CheatAgent.git)
>
> **在线文档（智能文档 / Markdown）**：[腾讯文档 — CheatAgent 项目方案](https://docs.qq.com/aio/DZFF3bWhYdWV3bktq)
>
> **最后更新**：2026-07-08（补充现有方法调研；M6–M8 完成）

---

## 一、项目目标

构建一个能够通过多轮对话获取真实信息，并进行欺诈识别与真相还原的客服 Agent 系统。

**核心问题**：Agent 通过多轮对话、多方向询问等手段，从可能不诚实的对话方获取真实信息。

**场景约束**：铁矿石大宗商品电话客服，面向关键少数信息源（厂长、仓库负责人等）；用户明确知道对方是 Agent。

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
| **评什么** | Claim F1、Pearson(r_u, honesty)、套话 skill 指标、Truth Discovery 恢复效果 |

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
| **目前方案** | LangGraph cheatAgent + CustomerAgent 模拟器；1 路由 Skill（规则）+ 11 专项 Skills；分层记忆 L0–L3；`MTA_LLM_MODE=mock\|live` |
| **参考论文** | ProductAgent（澄清提问）、IntelliChain / AVERT / Zero-Shot Socratic（苏格拉底法）、Optimal Information Disclosure（信息设计）、Deceptively Dodging（信息操纵）等，见第九节 |
| **实现状态** | ✅ M6 Skills · ✅ M7 LLM（PolarPrivate live 已验）· ✅ M8 冒烟 + Claim F1/Pearson 评测 |

### 2. 欺诈识别

| 方案 | 说明 | 状态 |
|------|------|------|
| **ReCon** | 多轮对话欺骗检测，主路径 | 🟡 规则版保留（已去 honesty GT 泄漏），待 LLM 按论文复刻 |
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
| **局限** | 规则 claim 抽取；ReCon 未 LLM 化；Alpha 规模待扩 |

### 5. 展示页面

暂缓（M5）。详见第六节两个候选方案。

---

## 五、Benchmark 设计

### 现状（2026-07-08）

- 仍**没有**完全对应的公开数据集；欺诈研究多用游戏场景（Avalon、狼人杀等）
- **已落地**：Agent-Agent 冒烟 pipeline（`scripts/generate_dataset.py` / `evaluate_dataset.py`）
- **dataset 路径**：`benchmark/datasets/smoke_v1/`（manifest + 3 用户 meta.json）
- **套话指标**：`skill_kind_count` / `skill_invoke_count` / `skill_richness` / `skill_coverage`（ADR-007）
- **待补**：Alpha 10×5 session；Claim LLM 抽取；ReCon LLM 复刻

### 计划

1. **设定角色**：用户身份（诚实度、头寸方向、职业身份）
2. **模拟市场**：铁矿石价格实际波动情况
3. **Agent-Agent 生成**：两个 Agent 多轮对话生成 dataset
4. **人工抽样验证**：抽查典型对话，检查话术触发合理性
5. **Truth Discovery 评价**：用真相恢复效果评估系统能力

### 仿真假设（简化约束）

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

---

## 六、展示方案

### 方案 A：聊天页面（LibreChat）

- 类似 ChatGPT 的对话界面，套壳 LibreChat
- **优点**：直观展示多轮对话交互流程
- **缺点**：难以直接展示抗欺诈性能与真相还原数值

### 方案 B：Dashboard（推荐）

- 类 PPT / 数据看板，可视化系统成果
- **展示内容**：
  - 欺诈概率曲线
  - 真相恢复结果（claim veracity、source reliability）
  - 信息来源追踪
  - Memory 状态
  - Skill 调用分布与覆盖率
- **优点**：比单聊天页面更容易展示成果，适合向学长汇报

---

## 七、当前存在问题（待学长讨论）

**Q1：Benchmark 是否有必要？**

LLM 生成 dataset 时，Agent 人设都是预先设定好的，而且 LLM 也不是人。心理学对 LLM 真的有用吗？效力可能不高。是我搭建 Benchmark 的思路有问题吗？

**Q2：展示方案如何设计？**

是对话页面吗？但对话页面并不能展示所谓的"抗欺诈性能"。可展示页面是否应该做成"类 PPT"数值看板？

**Q3：话术如何评价？**

套话话术要做 benchmark 吗？如何做？纯心理学 + Agent，没什么很好的量化思路。

> **2026-07-08 进展**：已用 cheatAgent 元数据指标（skill 种类/次数/熵/覆盖率）替代旧 `bias_triggered`；分析侧 Claim F1 / Pearson 仍待 `evaluate_dataset.py` 补全。

---

## 八、Roadmap

与工程 SSoT `roadmap.md` / `polaris.json` 对齐：

| 里程碑 | 任务 | 状态 |
|--------|------|------|
| M0 | SSoT + 调研（ADR-001~008） | ✅ |
| M1 | 分析骨架（ontology、EM、ReCon 无 GT 泄漏） | 🟡 保留，ReCon/claim 待 LLM 升级 |
| M5 | 演示 UI（Dashboard / LibreChat） | ⏸ 暂缓 |
| **M6** | 套话 Skills（1 路由 + 11 专项 + 15 论文） | ✅ |
| **M7** | LangGraph + `route_skill` + `invoke_skill` LLM + CustomerAgent LLM | ✅（mock 已验；live 待密钥） |
| **M8** | 冒烟 dataset 3×20 + smoke gate + L1–L3 memory | ✅ |
| Alpha | 10 用户 × 5 session × ≥20 轮 | 📋 下一步 |
| Beta | 30 用户 × 5 session × 5 月 | 📋 远期 |

**验证命令**（与 CI 一致）：

```bash
pip install -e ".[dev,agent]"
MTA_LLM_MODE=mock pytest test/ -v
MTA_LLM_MODE=mock python scripts/generate_dataset.py
MTA_LLM_MODE=mock python scripts/evaluate_dataset.py
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
