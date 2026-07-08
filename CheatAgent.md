# CheatAgent

> **维护说明**：方案、进度、讨论记录放本文档；代码放 [GitHub — beichenO2/CheatAgent](https://github.com/beichenO2/CheatAgent.git)
>
> **在线文档（智能文档 / Markdown）**：[腾讯文档 — CheatAgent 项目方案](https://docs.qq.com/aio/DZExvSmVmZ0pnc0FP)
>
> **最后更新**：2026-07-08（M6–M8 完成，文档与 `polaris.json` / `roadmap.md` 对齐）

---

## 一、项目目标

构建一个能够通过多轮对话获取真实信息，并进行欺诈识别与真相还原的客服 Agent 系统。

**核心问题**：Agent 通过多轮对话、多方向询问等手段，从可能不诚实的对话方获取真实信息。

**场景约束**：铁矿石大宗商品电话客服，面向关键少数信息源（厂长、仓库负责人等）；用户明确知道对方是 Agent。

---

## 二、整体架构

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

## 三、功能模块

### 1. Agent（套话智能体）

| 维度 | 内容 |
|------|------|
| **目标** | 通过多轮对话从对话方获取真实市场信息 |
| **目前方案** | LangGraph cheatAgent + CustomerAgent 模拟器；1 路由 Skill（规则）+ 11 专项 Skills；分层记忆 L0–L3；`MTA_LLM_MODE=mock\|live` |
| **参考论文** | ProductAgent（澄清提问）、IntelliChain / AVERT / Zero-Shot Socratic（苏格拉底法）、Optimal Information Disclosure（信息设计）、Deceptively Dodging（信息操纵）等，见第八节 |
| **实现状态** | ✅ M6 Skills · ✅ M7 LLM utterance（mock 已验，live 待配密钥）· ✅ M8 冒烟 3×20 dataset + smoke gate |

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
| **局限** | 当前 dataset 为 mock LLM 生成；Claim F1 / Pearson 离线指标待补；话术能力需 skill 工程指标辅助 |

### 5. 展示页面

暂缓（M5）。详见第五节两个候选方案。

---

## 四、Benchmark 设计

### 现状（2026-07-08）

- 仍**没有**完全对应的公开数据集；欺诈研究多用游戏场景（Avalon、狼人杀等）
- **已落地**：Agent-Agent 冒烟 pipeline（`scripts/generate_dataset.py` / `evaluate_dataset.py`）
- **dataset 路径**：`benchmark/datasets/smoke_v1/`（manifest + 3 用户 meta.json）
- **套话指标**：`skill_kind_count` / `skill_invoke_count` / `skill_richness` / `skill_coverage`（ADR-007）
- **待补**：live LLM 重跑 dataset；Claim F1 vs latent；Pearson(r_u, honesty)

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

## 五、展示方案

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

## 六、当前存在问题（待学长讨论）

**Q1：Benchmark 是否有必要？**

LLM 生成 dataset 时，Agent 人设都是预先设定好的，而且 LLM 也不是人。心理学对 LLM 真的有用吗？效力可能不高。是我搭建 Benchmark 的思路有问题吗？

**Q2：展示方案如何设计？**

是对话页面吗？但对话页面并不能展示所谓的"抗欺诈性能"。可展示页面是否应该做成"类 PPT"数值看板？

**Q3：话术如何评价？**

套话话术要做 benchmark 吗？如何做？纯心理学 + Agent，没什么很好的量化思路。

> **2026-07-08 进展**：已用 cheatAgent 元数据指标（skill 种类/次数/熵/覆盖率）替代旧 `bias_triggered`；分析侧 Claim F1 / Pearson 仍待 `evaluate_dataset.py` 补全。

---

## 七、Roadmap

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

## 八、参考论文

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
