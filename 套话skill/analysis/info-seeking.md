# 信息寻求推断 — 研究方向分析

> 研究来源：`children-info-search`（Nelson et al., 2014）、`do-people-ask-good-questions`（Rothe et al., 2018）  
> 应用场景：铁矿石电话客服套话（MarketTruthAgent 交互链路-1）

---

## 1. 核心机制

**基本命题**：一个人主动寻求什么信息，反映他**已知什么、缺什么、当前决策卡在哪**。在套话场景中，客户的问题不是噪声，而是对隐藏状态（latent state）的可观测信号。

### 1.1 信息寻求 = 在假设空间上做序贯搜索

两篇论文共用「二十问 / 主动学习」框架：

- 存在一组互斥的隐藏假设 \(H\)（例如：港存高/中/低、采购积极/消极、某区域报价是否松动）
- 提问者每次选一个 query \(x\)，得到答案 \(d\)，用贝叶斯更新后验 \(p(h \mid d, x)\)
- 「好问题」= 期望效用最大的 query：\(x^* = \arg\max_{x \in Q} \mathbb{E}[U(d; x)]\)

Nelson et al. 用**信息增益（Information Gain, IG）**量化：选能把剩余候选集一分为二、熵下降最大的约束性问题。Rothe et al. 进一步区分两种效用：

| 模型 | 含义 | 套话映射 |
|------|------|----------|
| **EIG**（期望信息增益） | 纯减不确定性，与后续行动无关 | 客户「好奇型」提问：想搞清全貌 |
| **ES**（期望节省） | 信息价值绑定具体决策成本 | 客户「交易型」提问：为下单/锁价/排产服务 |

Rothe et al. 发现：人**评估**问题时更接近 ES（知道什么信息能直接帮助决策），但**自发提问**时 rarely 问到最优题——瓶颈在**问题生成（query synthesis）**，不在**问题评估**。

### 1.2 从「客户问了什么」反推隐藏状态

套话 Agent 的角色是**倾听方 + 推断方**，逻辑与论文中「实验者观察被试提问」对称：

```
客户问题 x  ──→  推断：客户关心哪个 bucket、已有 partial claim、知识深度
                ──→  更新 UserModel.inferred_gaps / partial_claims
                ──→  选择下一话术（PROBE / CHALLENGE / cover-qa …）
```

推断依据三类信号（Nelson + Rothe 共识）：

1. **问题类型（constraint vs hypothesis-testing）**  
   - 约束性：「青岛港库存现在什么水平？」→ 区分假设子集，说明客户在**结构化排查**  
   - 假设检验性：「是不是已经 1.5 亿吨了？」→ 客户可能**已有具体数字**，在验证或钓鱼

2. **问题与环境的统计匹配度**  
   Nelson et al.：首问最 Informativeness；儿童在「代表现实分布」的环境中提问更高效。  
   套话含义：客户首问往往指向**其真实业务锚点**（库存岗问港存、贸易岗问报价/利润），首问权重应高于后续寒暄。

3. **上下文特异性（context sensitivity）**  
   Rothe et al.：同一问题模板换场景后 EIG 骤降——好问题是**情境绑定**的。  
   套话含义：不能静态映射「问库存 → 有库存」；需结合**已知身份**（区域、岗位）、**会话阶段**、**已披露 partial claim** 联合推断。

### 1.3 与现有代码的衔接

项目已在 `user_modeler.py` 实现最简版映射（关键词 → `inferred_gaps`）。本方向的价值是把该映射**理论化 + 分层**：

- 显式意图：客户字面在问什么  
- 隐式状态：客户为什么在这个时点问这个（缺信息 / 有信息要验证 / 抬价/压价前探路）  
- 潜在意图：其组织当前决策任务（补库、出货、对冲、观望）

---

## 2. 适用场景（铁矿石电话客服套话）

### 2.1 高适用

| 场景 | 客户典型提问 | 可推断的隐藏状态 | 后续套话策略 |
|------|-------------|-----------------|-------------|
| 开场 3 轮内 | 「青岛港库存怎么样？」 | 掌握或关注 `港存`；可能为库存/贸易岗 | PROBE 同区域其他指标（疏港量、到港量） |
| 价格异动后 | 「现在还能不能拿货？」 | 关心 `采购积极性` + 决策窗口；可能有未说出的库存压力 | cover-qa 报价 + 轻量 CHALLENGE |
| 反驳前兆 | 「听说库存很高，是不是要跌？」 | 已有 directional 观点；可能在试探客服信息源 | reactance-biased-statement 或 trap-question |
| 多港对比 | 「日照和青岛哪个更紧？」 | 跨 region 的 partial claim；物流/调配决策 | 追问其自身所在港、船期 |
| 成交前 | 「你们那边利润还行吗？」 | 关心 `利润` / 走线；可能接近成交或议价 | va-detail-chase 要可验证细节 |

### 2.2 中适用

- **身份未明、问题极泛**（「最近市场怎么样？」）：信息增益低，需先用 cover-qa 收窄 region/指标，再二次推断。  
- **客户几乎不问问题、只答**：本方向退化为「无信号」；改走心理反抗 / 有偏陈述等主动 elicitation。

### 2.3 低适用 / 不宜单独依赖

- 客户问题与业务无关（投诉、流程）  
- 客户刻意误导性提问（反向套客服）——需与欺骗检测、陷阱问题联用  
- 纯复述公开资讯、无决策压力——问题反映的是「媒体关注点」而非私有状态

### 2.4 在 1+N Skill 架构中的位置

`SKILL-router` 已列「信息寻求行为 → 推断缺什么 → PROBE 相关指标」为第一路由原则。本方向应作为 **router 的输入特征**，而非独立话术 skill：推断结果决定调用 `socratic-probe`、`va-detail-chase` 还是 `cover-qa`。

---

## 3. 话术模板（至少 5 条）

以下模板分两类：**A. 基于客户提问的推断规则（Agent 内部）**；**B. 推断后的对外话术（可进 skill）**。

### 模板 A1 — 首问锚定（高信息增益首问）

**触发**：会话前 2 轮，客户首句含指标关键词。  
**推断**：`inferred_gaps += [detect_indicator(首问)]`；若含区域则锁定 region。  
**话术**：

> 「您刚问的是{region}{indicator}，这边最近变化确实挺快。您自己那边{indicator}感觉怎么样？」

**机制**：Nelson et al. 首问权重最高；用 mirror + 开放式回扣，把「客户寻求的信息」转成「客户可能持有的 partial claim」。

---

### 模板 A2 — 假设检验式提问（hypothesis-testing）

**触发**：客户问「是不是…」「有没有到…」「会不会…」且带具体数值/方向。  
**推断**：客户 likely 已有 `{indicator, value}` 候选；标记 `partial_claims`，confidence 上调。  
**话术**：

> 「您提到的{value}这个数，市场上说法挺多的。您是自己盘过还是听同行说的？哪个港的数据？」

**机制**：Rothe et al. 的 demonstration / shipsize 类 query 对应「客户带假设来验证」；追问来源与 scope 可 elicit 更细 claim。

---

### 模板 A3 — 决策绑定型提问（ES 型）

**触发**：「还能买吗」「要不要出货」「锁不锁价」等行动导向问句。  
**推断**：`intent_layers.implicit = "decision_bound"`；优先补 `采购积极性`、`报价松动`、`利润`。  
**话术**：

> 「您这边是打算{补库/出货/观望}？不同做法对{indicator}的敏感度不一样。您更关心价格还是可提量？」

**机制**：对齐 Rothe et al. ES 模型——客户问的不是「最大熵减」，而是「对决策最有用的那一维」。

---

### 模板 A4 — 跨指标串联（constraint question 链）

**触发**：客户已问 A 指标，对 B 指标未问但 A-B 在本体中常共现（如港存 → 疏港量）。  
**推断**：`inferred_gaps` 含 A，推断 B 为 latent gap。  
**话术**：

> 「库存这块您了解了。最近{region}疏港{快/慢}，您码头那边提货车好排吗？」

**机制**：Nelson et al. 的序贯 constraint 搜索；第二问应切分剩余假设空间，而非重复第一问。

---

### 模板 A5 — 低信息增益泛问的处理

**触发**：「市场怎么样」「最近如何」等 EIG≈0 的泛问。  
**推断**：不可 over-fit；标记 `knowledge_depth = unknown`。  
**话术**：

> 「您主要做{贸易/钢厂配套/码头}哪块？我好按您关心的港和指标说，省得您听一堆用不上的。」

**机制**：Rothe et al. 指出泛问 rarely optimal；客服应先**缩小假设空间**再推断，等价于 split-half 首问。

---

### 模板 A6 — 问题 + 反驳复合信号

**触发**：问句后紧跟「不对吧」「谁说的」等（`resistance_level` 上升）。  
**推断**：`reactance_triggered` + 问题指向的 indicator 为其真实知识区。  
**话术**（RECOVER 后）：

> 「您刚说的{correction}我记下了。除了这点，{related_indicator}您那边有听说什么吗？」

**机制**：问题定 topic，反驳定 truth direction；二者组合比单信号更强（与 PRT / 分析链路 rebuttal channel 衔接）。

---

## 4. 风险与禁忌

### 4.1 推断风险

| 风险 | 说明 | 缓解 |
|------|------|------|
| **过度解读** | 「问库存 ≠ 一定有库存」；可能是对手盘、研究员、或纯八卦 | 结合 `known_identity`（role/region）；多轮交叉验证 |
| **首问偏置** | 首问可能为套话/试探，非真实缺口 | 观察后续是否 self-contradict；与 deception 信号交叉 |
| **环境先验污染** | Nelson：人会按**现实世界统计**而非当前对话统计提问 | 客服勿把「行业常识」当「该客户私有信息」 |
| **生成-评估不对称** | Rothe：人不会问最优题，但客户的问题质量也参差不齐 | 推断用「问题指向的维度」，不假设客户问得「对」 |

### 4.2 话术禁忌

1. **禁止直接点破推断**：「您这么问是不是库存很多？」——破坏掩护感，触发防备。  
2. **禁止首问就追问敏感数值**：在 rapport 不足时，从泛问跳到「具体多少吨」会降 ES 且升 resistance。  
3. **禁止忽视客户问题的 ES**：客户问「能不能拿货」时大谈宏观政策（高 EIG、低 ES）——答非所问，流失 trust。  
4. **禁止静态关键词表 alone**：「库存→港存」过于粗糙；需区分「港口库存」vs「厂内库存」vs「在途」。  
5. **禁止与欺骗检测结论冲突**：若 deception 信号高，对「信息寻求推断」降权，改 trap / verify。

### 4.3 合规与伦理

- 推断结果仅用于**话术路由与 claim 采集**，不得对外声称「我们知道您的库存」。  
- 客户明确拒答后，不得同一指标连环追问（违反心理反抗 PRT 的 freedom 感知）。

---

## 5. 与其他方向边界

| 方向 | 核心动作 | 与本方向关系 |
|------|----------|--------------|
| **澄清提问**（ProductAgent） | Agent **主动问**以消歧 | 互补：澄清是 Agent→User；本方向是 User→Agent 提问的**反向推断** |
| **贝叶斯心智理论**（同 Rothe 2018） | 从行为推断心理状态的形式化框架 | **包含关系**：本方向是其在一类可观测量（提问）上的实例化 |
| **隐式用户建模**（SLR） | 从行为序列建 user profile | 本方向提供**特征层**（question type, gap, ES/EIG 代理特征） |
| **心理反抗 / 有偏陈述** | Agent 主动给偏信息引反驳 | **下游消费者**：推断出 gap 后，决定是否用 biased statement 激反驳 |
| **苏格拉底法** | 引导用户自证 | 推断出 `knowledge_depth` 低 → 可转 socratic；高 → 直接 va/challenge |
| **陷阱问题** | 嵌入已知错误测真实性 | 需**已有 partial claim**；partial claim 常由本方向从提问中初筛 |
| **信息设计 / Bayesian 说服** | 发送者设计披露 | 本方向是**接收者侧**读码；信息设计是**发送者侧**编码 |
| **信息操纵** | 违反 Grice 准则的策略性表述 | 本方向推断的是**真实寻求**；操纵是 Agent 主动产出，勿混淆因果 |

**一句话边界**：信息寻求推断回答「**他从提问暴露了什么**」；澄清提问回答「**我该问什么**」；心理反抗/陷阱回答「**我怎么激他说**」。

---

## 6. 关键论文要点

### 6.1 Nelson et al. (2014) — *Children's sequential information search is sensitive to environmental probabilities*

- **任务**：Guess Who 式 Person Game（18 张脸、20 个 yes/no 特征）；对比 Representative vs Nonrepresentative 环境。  
- **发现 1**：四年级儿童提问的 scaled IG 显著优于随机（M≈0.87），但低于最优。  
- **发现 2**：**首问**最能反映对环境统计的适应；Representative 环境中 Gender 首问 55%，Nonrepresentative 中 Beard 首问 25%——与最优树一致。  
- **发现 3**：儿童会受**现实世界先验**影响（Nonrepresentative 中仍过度问 Gender）。  
- **发现 4**：先玩 Number Game 再玩 Person Game 有**正迁移**（d=0.69）——信息搜索策略可跨域泛化。  
- **方法要点**：split-half heuristic 在 Person Game 中等价于 max IG；序贯 greedy 不保证全局最优。  
- **套话 takeaway**：**首问 + 约束性问题的维度** = 高价值推断信号；环境统计（行业 vs 该客户）要分开建模。

### 6.2 Rothe, Lake & Gureckis (2018) — *Do People Ask Good Questions?*

- **任务**：Battleship 6×6，160 万假设空间；Exp1 自由生成自然语言问题，Exp2/3 排序/选择给定问题。  
- **发现 1（Exp1）**：605 条有效问题，87% 为 rich query（非单格点击）；**高度 context-specific**（置换 context 后 EIG 显著下降）。  
- **发现 2（Exp1）**：问题质量呈**单峰在中等 EIG**，最优题很少被自发问到；frequency 与 EIG 相关仅 r≈0.16。  
- **发现 3（Exp2/3）**：提供选项后，human rank 与 EIG r≈0.89、与 ES r≈0.78–0.86——**评估能力 >> 生成能力**。  
- **发现 4**：ES 略优于 EIG 解释 human judgment（80% 被试 log-likelihood 更高）——人更关心**对任务的直接帮助**。  
- **问题类型 catalog**：location / region / ship size / orientation / adjacency / demonstration——可类比为铁矿石本体的 region / indicator / value / relation 查询类。  
- **套话 takeaway**：  
  1. 客户提问是 rich、情境化的，应用函数式语义（非关键词）建模；  
  2. Agent 内部应用 ES 对齐客户决策任务；  
  3. 不要期望客户会问「最优 elicitation 问题」——客服须主动设计后续 probe。

### 6.3 两文合读对系统设计的含义

```
客户提问 ──→ [信息寻求推断模块] ──→ UserModel 更新
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
              inferred_gaps    partial_claims    decision_bound
                    │                 │                 │
                    └────────→ SKILL-router ──→ 专项套话 skill
```

- **评测建议**（对齐 ADR-007/008）：除 `inferred_gaps` 命中率外，增加「首问 bucket 推断准确率」「推断后所选 skill 的 ES 代理分」。  
- **与 Tier B benchmark**：在 dialogue 标注中保留 `user_question_type`、`inferred_latent_gap`、`ground_truth_gap` 三元组，便于单独评「推断链」而非端到端套话成功率。

---

*文档版本：v1 | 仅基于 `children-info-search` 与 `do-people-ask-good-questions` 两篇参考文献*
