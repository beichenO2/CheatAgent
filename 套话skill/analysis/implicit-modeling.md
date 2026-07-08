# 隐式用户建模 / 用户意图建模

> 分析来源：Farshidi et al., *Understanding User Intent Modeling for Conversational Recommender Systems: A Systematic Literature Review*（SLR, 791 篇文献，59 种模型，74 项特征）

---

## 1. 核心机制（显式 / 隐式 / 潜在意图三层）

用户意图建模（User Intent Modeling）旨在从用户输入与交互中识别其请求背后的真实目的，以驱动个性化、精准的对话式推荐（CRS）。SLR 虽未直接使用「三层意图」术语，但其 74 项特征与案例研究可归纳为以下结构：

### 1.1 显式意图层（Explicit Intent）

**定义**：用户通过自然语言直接表达的目标、约束与偏好。

**信号来源**：
- 查询文本（Query-Based、Query Refinement、Query Scoping）
- 意图分类标签（Intent Classification / Intent Detection）
- 多轮对话中的直接陈述与反馈（User Interaction / Interactivity）
- 用户显式评分与偏好声明

**典型方法**：SVM、LR、BERT、CRF、Rule-Based Tagging、Template-Based 方法

**机制**：对词、短语、上下文做语义分析与意图分类，将 utterance 映射到预定义或开放意图空间。

### 1.2 隐式意图层（Implicit Intent）

**定义**：未明说、但可从可观测行为中推断的偏好与目标。

**信号来源**：
- 点击流（Click-Through Recommendations）
- 会话序列（Session-Based Recommendations）
- 历史交互（Historical Data-Driven Recommendations）
- 行为模式（Behavior-Based Recommendations）
- 协同过滤信号（Collaborative Filtering、Item Recommendation）

**典型方法**：CF、MF、GRU4Rec、LSTM、Markov Chain、PageRank

**机制**：从行为共现、时序依赖、邻域相似性中估计用户当前偏好；GRU4Rec 等模型通过序列建模捕获「用户做了什么」而非「用户说了什么」。

### 1.3 潜在意图层（Latent Intent）

**定义**：用户自身未必意识到的深层动机，无法从单次 utterance 或孤立行为直接读出。

**信号来源**：
- 跨会话行为模式（Pattern-Based）
- 主题分布（Topic Modeling / LDA）
- 语义空间中的隐含关联（LSA、PLSA、Representation Learning）
- 注意力加权的序列表示（Self-attention、Attentive）

**典型方法**：LDA、ASLI（Attentive Sequential model of Latent Intent）、TCN + Self-attention、Deep Belief Networks

**机制**：将观测行为投影到 latent space，学习「隐藏意图表示」，再用于排序、预测下一物品或生成回复。Case Study 2（ASLI）明确指出：用户意图往往是 latent 的，需从类别内行为序列中推导。

### 1.4 三层协同与决策流程

SLR 提出基于 MCDM 的五步决策模型，可作为三层融合的工程框架：

1. **模型调研**：了解 LDA、BERT、CF 等 59 种常用模型
2. **特征需求抽取**：明确场景需要 prediction / ranking / recommendation / semantic analysis 等
3. **可行解搜索**：Table 3 映射「特征 → 模型」（如 CF 同时支持 prediction、ranking、item recommendation）
4. **组合选型**：常见组合如 BERT + TF-IDF（检索式 CRS）、GRU + LDA + BERT（ASLI 基线）
5. **性能验证**：Precision、Recall、NDCG 等指标 + 领域数据集实测

**融合原则**：显式层提供锚点，隐式层提供动态更新，潜在层补全未说出的动机；多轮对话中三层应随新 utterance 与新行为持续重估。

---

## 2. 适用场景

| 场景 | 为何适用 | 主要依赖层 |
|------|----------|------------|
| 对话式推荐系统（CRS） | 用户目标在多轮中逐步显露，需同时理解语言与行为 | 三层并用 |
| 电商 / 产品搜索对话 | 点击、浏览、加购等行为丰富，意图常未完整表述 | 隐式 + 潜在 |
| 冷启动 / 新用户 | 行为稀疏，需更多依赖显式 query 与内容特征 | 显式为主 |
| 会话内推荐（Session-based） | 短序列、强时效，GRU/LSTM 捕获即时意图漂移 | 隐式为主 |
| 检索式 CRS（vs 生成式） | 需语义匹配 + 排序，BERT + TF-IDF 组合有效 | 显式 + 语义 |
| 跨域个性化（内容 / 协同 / 上下文混合） | Hybrid Recommendation、Context-Aware 特征覆盖多信号 | 三层融合 |
| 虚拟助手 / Chatbot | 理解 query 并提供情境化回复 | 显式 + 上下文 |
| 信息真伪 / 市场探询类对话 | 从话术与行为推断真实信息需求，而非仅表面提问 | 潜在 + 隐式 |

**不适用或需谨慎的场景**：
- 行为数据极少且用户拒绝任何澄清 → 推断置信度低
- 强隐私敏感领域（医疗、金融）且未获行为采集授权
- 单轮、信息完整的 factual QA → 过度建模反而引入噪声

---

## 3. 话术模板（至少 5 条）

以下模板面向**对话式探询 / 推荐**场景，目标是在不直接审问的前提下，通过自然话术激活三层意图信号。`{变量}` 需由系统从上下文或行为日志填充。

### 模板 1：行为镜像（隐式层激活）

> 「我注意到您刚才关注了 `{品类/属性}` 相关的几个选项——是想重点比较 `{维度A}` 和 `{维度B}`，还是已经有更偏向的方向了？」

**机制**：引用可观测行为（点击、停留），邀请用户确认或修正系统推断，降低「读心」感。

### 模板 2：场景投射（潜在层激活）

> 「很多和您情况类似的用户，最终选 `{选项}` 往往是因为 `{动机}`。您这边是更在意 `{动机}`，还是有别的考虑？」

**机制**：用群体 latent pattern（LDA / 协同信号）引出未明说的约束，给用户否定或补充空间。

### 模板 3：约束二分（显式 + 隐式联合）

> 「为了帮您缩小范围：在 `{约束1}` 和 `{约束2}` 之间，您目前更倾向哪一边？如果两个都要，也可以说下优先级。」

**机制**：将模糊意图结构化为可分类的显式选择，同时保留优先级信息供排序模型使用。

### 模板 4：会话承接（跨轮意图追踪）

> 「上一轮您提到 `{显式需求}`，后来又看了 `{行为对象}`。我理解为您可能在 `{推断意图}` 上还有顾虑——是这样吗？」

**机制**：显式 utterance + 后续行为 diff，实现多轮 intent tracking，类似 session-based recommendation 的话术版。

### 模板 5：偏好排序邀请（ranking 信号采集）

> 「如果下面三个方向只能先深入一个，您会选哪个？① `{A}` ② `{B}` ③ `{C}`——选完我们可以再展开其他的。」

**机制**：主动采集 pairwise / listwise 偏好，等效于轻量 click-through 监督，服务 ranking 特征。

### 模板 6：不确定性显式化（避免过度推断）

> 「目前信息还不够确定您的优先级。您方便补充一下：最不能接受的是什么？最必须满足的是什么？」

**机制**：当 prediction uncertainty 高时，从隐式推断退回显式 elicitation，符合 SLR 对 quality / validity 的要求。

### 模板 7： latent 动机探针（非诱导性）

> 「除了 `{表面目标}` 之外，有没有什么是「搞定了您就满意」的关键点？有时候真正在意的和一开始问的不完全一样。」

**机制**：温和探测潜在意图，避免假设性断言；适用于 ASLI 类「hidden intent」场景。

---

## 4. 风险与禁忌

### 4.1 主要风险

| 风险 | 表现 | 文献依据 |
|------|------|----------|
| **过度推断** | 将稀疏行为误读为强偏好，推荐偏离 | Case Study 2：latent intent 不可直接观测，需验证 |
| **隐私与透明** | 用户未授权的行为追踪引发信任崩塌 | 49.81% 研究用私有数据集，数据治理复杂 |
| **冷启动失效** | 新用户无历史，隐式/潜在层无信号 | CF、GRU4Rec 依赖历史交互 |
| **可解释性缺失** | BERT/深度模型难解释「为何这么推断」 | SLR 讨论 interpretability vs performance 权衡 |
| **数据偏倚** | 训练集不具代表性，latent 模式迁移失败 | 68.37% 公开数据集仅被引用一次，复用不足 |
| **模型组合不透明** | 多模型 pipeline 难以复现 | 仅 8.59% 论文公开代码 |
| **评估指标错配** | 用 accuracy 衡量不平衡 intent 分类 | SLR：imbalanced 场景应优先 precision/recall/F1 |

### 4.2 话术与交互禁忌

1. **禁止**在未确认前断言用户意图（「您一定想要…」）——应使用模板 6 的确认式表述。
2. **禁止**暴露底层追踪细节（「系统检测到你点击了 7 次」）——改为自然的行为镜像（模板 1）。
3. **禁止**在单信号下做高置信推荐——至少需显式 + 隐式双源或用户确认。
4. **禁止**将 latent 推断当作事实陈述——使用「可能」「似乎」「很多类似用户」等 hedging。
5. **禁止**忽视用户纠正——一旦用户否定推断，应重置隐式权重，而非坚持模型输出。
6. **禁止**在对抗性 / 欺骗检测场景中用诱导性话术制造虚假 latent intent（与「陷阱问题」方向混淆）。
7. **禁止**忽略多意图共存——用户可能同时有多个并行目标，单一 intent label 会丢失信息。

---

## 5. 与其他方向边界

| 对比方向 | 隐式用户建模 | 边界要点 |
|----------|--------------|----------|
| **澄清提问**（ProductAgent） | 主动生成澄清问句，显式缩小意图空间 | 澄清是**显式 elicitation**；隐式建模侧重**从已有信号推断**，二者可串联：推断置信度低 → 触发澄清 |
| **贝叶斯心智理论**（Do People Ask Good Questions?） | 形式化 belief update、optimal question | 贝叶斯 ToM 强调**理性问句选择**；隐式建模强调**ML 特征 → 模型 → 预测**，理论框架不同但可互补 |
| **信息寻求推断**（Children's Info Search） | 观察 sequential search 如何敏感于环境概率 | 偏**认知科学 / 发展心理学**实验范式；隐式建模偏**工程化 CRS 系统** |
| **苏格拉底法**（Socratic 系列） | 通过提问引导用户自行发现 | 苏格拉底是** pedagogical discovery**；隐式建模是** statistical inference**，前者不依赖 clickstream |
| **陷阱问题 / 有偏信息**（Crowdsourcing Trapping） | 设置 control questions 检测不可靠回答 | 陷阱是**质控 / 对抗**手段；隐式建模是**服务用户**的偏好估计，目的相反 |
| **心理反抗**（Freedom-prompting / PRT） | 当用户感到被操控时产生 reactance | 过度暴露「我读出了你的 latent intent」会触发反抗；话术需保留自主感 |
| **信息设计 / Bayesian 说服** | 最优信息披露以影响信念 | 信息设计是**策略性披露**；隐式建模是**理解用户**而非说服用户 |
| **信息操纵理论**（Deceptively Dodging） | 研究回避问句与欺骗感知 | 隐式建模应**提升理解**，不可用于包装回避或误导 |

**一句话边界**：隐式用户建模 = **从语言 + 行为 +  latent 表示中估计用户真正想要什么**；不是教用户想什么（苏格拉底），不是考用户是否诚实（陷阱），也不是设计怎么说服用户（信息设计）。

---

## 6. 关键论文要点

### 6.1 主文献：SLR（Farshidi et al., 2023/2024）

- **范围**：791 篇出版物 → 59 种模型（≥6 篇提及）、74 项特征（≥6 篇提及）
- **核心贡献**：MCDM 决策模型（五步）+ 模型-特征映射表 + 质量属性 / 评估指标 taxonomy
- **高频模型**：LDA（topic / pattern）、BERT（semantic / transformer）、CF（prediction / ranking）
- **高频特征**：Prediction、Ranking、Topic Modeling、Content-Based Recommendations、Filtering
- **Top 5 质量属性**：Performance、Effectiveness、Diversity、Usefulness、Stability
- **Top 5 评估指标**：Precision、Recall、F1-Score、Accuracy、NDCG
- **常用数据集**：MovieLens、ReDial、TREC、Yelp、AOL session
- **主要局限**：代码开放率低（8.59%）、模型 singleton 多（58.66%）、数据集复用不足

### 6.2 Case Study 1：检索式 CRS（CRB-CRS, Klagenfurt）

- **任务**：检索式对话推荐 vs 生成式
- **选型**：TF-IDF（term weighting）+ BERT（semantic / ranking / end-to-end）
- **特征需求**：Semantic Analysis、Term Weighting、Content-Based Recommendations、Ranking、Transformer-Based、End-to-End
- **数据集**：MovieLens、ReDial
- **启示**：显式语义 + 排序能力比纯生成更可控；适合需要可解释检索链路的 CRS

### 6.3 Case Study 2：ASLI（UCSD, Attentive Sequential model of Latent Intent）

- **核心问题**：用户意图 latent，不能直接从交互观测
- **架构**：Self-attention（item similarity）→ TCN（latent intent representation）→ Attentive prediction
- **特征需求**：Pattern-Based、Prediction、Historical Data-Driven、Click-Through、Item Recommendation、Transformer-Based、Network Architecture、Attentive
- **基线组合**：GRU + LDA + BERT；实践中 GRU 表现不足，改为 custom self-attentive
- **数据集**：Etsy、Alibaba（电商域）
- **启示**：潜在意图层需序列 + 注意力；行为 click 是关键隐式信号

### 6.4 模型组合经验（SLR §4.3）

- **高频共现**：LDA–TF-IDF、LDA–SVM、CF–MF、LSTM–CF
- **选型逻辑**：先满足 feature requirements（Table 3），再验证组合可行性（Figure 2），最后 performance analysis
- **趋势**：BERT 类 transformer 上升，LDA 等传统模型仍作 topic / pattern 基础模块

### 6.5 对「套话 skill」的落地启示

1. **话术 = 轻量 feature elicitation**：每轮对话应产出可写入 intent model 的结构化特征（偏好、约束、ranking）。
2. **三层并行更新**：utterance 更新显式层，行为更新隐式层，跨轮模式更新潜在层。
3. **置信度门控**：低置信时切换到澄清模板，高置信时用镜像 / 承接模板。
4. **评估对齐 SLR**：对话策略除 task success 外，应追踪 precision@k（推荐命中）、用户纠正率（intent misread proxy）、多轮收敛轮数。

---

*文档版本：基于 user-intent-slreview.md 分析生成*
