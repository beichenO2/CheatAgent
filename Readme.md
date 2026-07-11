## 展示启动提示词（复制给 Agent）

```
请严格按本仓库根目录的 Show.md 执行本地展示启动。不要跑评测 pipeline；不要改 CheatAgent 业务代码。

目标：把两个展示页拉起来并在浏览器打开——
1) 智能客服网站 http://127.0.0.1:3085
2) 评测报告 Dashboard http://127.0.0.1:8931/beta_v2/dashboard.html

按 Show.md 顺序执行。LLM Proxy 用 PolarPrivate_OpenSource（:12790，四位 QCSA 空壳，无预置真实 Key）：
- clone + privportal start + 前端 :12795；
- 指导用户在 UI 只填一把 API Key + 一条 Binding；
- 主动询问用户的供应商/Base URL/上游模型 ID（他们的模型通常不是作者预设）；
- 按 Show.md §1.3 在 PolarPrivate 的 model_routing.py 把本仓库会用的 `0001` 与 `1100`/`qwen3.7-plus` 都指到用户那条 Binding，使用户只维护一把 Key。
然后起 ./service/start.sh（:3945）、market-truth-cs docker（:3085/:3925）、python3 -m http.server 8931 托管 benchmark/reports，最后 open 两个 URL。
完成后回报：两个地址、登录方式（u001–u030 / admin 免密）、以及 Key/路由是否已按用户模型配好。
```

> **SSoT 文档体系**（Agent 工作请优先读这些，本文件为初始调研笔记）：
> - 项目灵魂：`PolarSoul.md`
> - 当前状态：`polaris.json`
> - 规划：`roadmap.md`
> - 架构/Benchmark/Agent重建/LangGraph/测试策略：`decisions/001-011`
> - **已废弃教训**：`wrongway.md`
> - **套话 Skills（M6 ✅）· Agent LLM（M7 ✅）· Benchmark（M8/M9 ✅）**：`套话skill/` · `skills/cheat-agent/` · `benchmark/datasets/beta_v1/`
> - 外部参考摘要：`reference/`
> - **展示启动 skill**：`Show.md`（上方提示词可直接复制给 Agent）
>
> **展示（M5 ✅）**：
> - 评测成果摘要：`benchmark/reports/RESULTS.md`（**beta_v2 ✅** · F1=0.888 · td_world_truth_accuracy=1.0 · reliability r=+0.258）
> - 评测 Dashboard：`benchmark/reports/beta_v2/dashboard.html`（主）· `beta_v1/dashboard.html`（对照）；本地 http://127.0.0.1:8931/beta_v2/dashboard.html
> - 智能客服 Web UI：`~/Desktop/Web_related/market-truth-cs/`（PolarChat :3085 / API :3925，30 用户直登 + 150 段对话回放；侧栏按情景分组，JWT 鉴权链见 ADR-009；**DEV/Release 双模式 + 跨端口身份补全 + 数据清洗** 2026-07-10 已完成）；
>   **LLM API 统一走 LLM Proxy**——使用 [PolarPrivate_OpenSource](https://github.com/beichenO2/PolarPrivate_OpenSource.git)
>   提供 OpenAI 兼容服务（即生态内 PolarPrivate 的开源版，默认 `http://127.0.0.1:12790`）
> - UI 截图 / 快照：`artifacts/mtcs/screenshots/` · `artifacts/mtcs/snapshots/`

# 问题
考核内容：

我们之前有个小项目，探索：Agent 智能客服在服务客户问题的时候，也通过与用户交流、咨询等方式，从用户回答中提前个人或者市场的信息，这样就可以帮公司去收集信息了（比如，用户可以来咨询大宗商品相关的 Agent 智能客服，问今天铁矿石的价格，Agent可以回复用户价格，并且在与用户多轮问答过程中，去询问用户铁矿石的市场库存情况）。那么问题是，假设这个 Agent 能和很多个不同的用户进行交流，收集到很多用户的回答，我们如何判断这些回答的真假对错？比如，有人说库存还有很多，有人说库存不多了

 需要 1）去调研和思考这个领域和问题，看看这个问题有什么难度、现有方法有什么；2）形成你的一个解决方案；3）实现你的这个方案，最好有可展示的界面
# 问题定性
Agent 多轮对话获取真实信息：Agent 通过多轮对话、多方向询问等手段，从可能不诚实的对话方获取真实信息

# 条件拆分
## 对话情景
    作出假设 ：用户预先知道对方是Agent而不是人类，真实是在实际业务场景下多轮对话的前提，如果对方感觉到是一个Agent假扮人类，那么用户大概率根本不会继续交流。
进行推演：
    用户既然愿意和一个Agent聊天，必然是有功利性的目的
    在本场景中，**假设** 用户目的是获取准确的市场信息，为了方便建立benchmark，限定情景为：和铁矿石相关生产端对话。
得知了用户希望Agent说什么，我们可以进一步推演用户可能说什么：
    用户和Agent交流的目的是功利的，我们直接作出一个弱 **假设** ：用户想赚钱
    基于此，有两个可能：
        1、诚实的回答，希望能够持续的获取真实市场信息
        2、不诚实的回答，希望手里的头寸能更值钱（这里有一假设：我们知道用户在市场中是多方还是空方；在此假设下，我们简化模型，认为用户是多方，即希望价格上涨）
    最终，我们得到了两个可能的回答：
        1、认为自己能赚的更多的乐观回答，可能是真的也可能是假的。
        2、认为自己能赚的更少的悲观回答，大概率是真的，因为没必要散播这种假消息。

## 具体对话
在自然对话中收集市场微观信息，比如“港口库存怎么样”“钢厂采购积极性如何”“贸易商报价是否松动”
收集到的信息具有系统性差异，因为就算用户完全诚实，不同地区、不同时间窗口，都会有很大的差异：我们能收集到的信息是：
**某个来源，在某个时间，对某个市场对象、某个区域、某个指标，给出了某种数值型/方向型/等级型判断，并且附带一定证据强度。**
传统众包里的“多数投票”在这里很危险，因为市场谣言常常会快速复制（同源传播，看起来是一百个人说一个观点，但其实都是同一个人提出的，被扩散到了一百个人）。


## 场外信息
### 价格
人会骗人但价格不会， **假设** 与客户长期合作，那么期货价格变化是一个我们可以采集到的重要信息。
额外考虑市场资金巨大，有偏差也是完全正常的，所以实际价格变化和用户回答的差异，可以作为判断客户诚信度的辅助指标。
### 政策
政策对于市场的引导、规范作用不可忽视

# 算法逻辑
## 对话采集场景（只考虑分析用户的回答，不考虑如何提问）
问题定性：在对话式采集场景中，把自然语言回答经 **ReCon → Normalize → Claim → Truth Discovery** 联合估计 claim veracity、source reliability 与 escalation policy。

### 分析链路（ADR-009）
```
RAW user turn → ReCon（欺诈/策略性识别）→ Normalize（上下文转译到 canonical ontology）→ Claim → Truth Discovery
```

**Normalize 层**：PolarPrivate **`qwen3.7-plus`**（纯文本 Qwen，`MTA_NORMALIZE_MODEL`；勿用 `qwen3-vl-flash` 等 VL 模型）。

**评测指标**：slot_recall、slot_precision（预测准确率）、bucket_veracity_accuracy、reliability_pearson、recon_honesty_pearson、external_consistency、escalation_rate；支持消融（`--ablate-normalize`、`--max-turns`、`--ablation-report`）。

### Claim 融合路线分歧：算法加权 vs LLM 语义融合（2026-07-09，待定设计决策）

**背景（beta U001 S001 心智审查）**：honesty=0.2 的用户在 S001 全程说真话且高度一致——10 句 user turn 里 7 句重复「港存中等 / 采购还行·按需·中性 / 报价没松动」，第 13 轮原文出现「采购积极性看着中性」，与 GT（中/中性/否）完全一致。评测却只得 tp=1（recall 0.33）。逐轮核对结论：**槽位冲突不是用户改口造成的，而是逐轮抽取自己制造的噪声**——
1. 正则覆盖层把 LLM 的「中性」改成「中」再因非法丢弃（见 `wrongway/04`）；
2. Agent 上一句提到日照港时，Normalize 把槽位误归因到日照港（region 漂移 → FP）；
3. last-wins 聚合把噪声轮的值盖到正确轮之上。

**两条路线**：

| | 路线 X：算法加权投票 | 路线 Y：LLM 语义融合 |
|---|---|---|
| 做法 | 同槽多轮 claim 按 confidence/rebuttal/deception 加权投票 | session 结束后一次 LLM 调用：全部 user turns + 逐轮 ReCon → 直接输出最终槽位 + evidence turns |
| 强项 | 确定性、可审计、零额外 LLM 成本 | 语义理解「还行=按需=随行就市=中性」；真改口能读懂前因后果；deflect（打太极）不出槽 |
| 弱项 | 输入是逐轮噪声时 garbage-in-garbage-out；权重是拍脑袋魔数；关键词式改口检测脆弱 | 单点依赖 LLM；需强制 evidence citation 保可审计；成本 +1 次调用/session（但可省掉 10 次逐轮 Normalize） |
| 对应用户直觉 | 「多次抽取，聚合修正」 | 「多轮对话应该一次抽取」「用 LLM 直接处理语义」 |

**定论（2026-07-09 用户拍板，分层双轨）**：

```
轮内抽取     Function Calling 严格 enum（删正则覆盖）→ 逐轮 claim（溯源/ReCon 耦合）
用户内融合   LLM 语义融合直接出结果：session 级一次调用读全对话 → 最终槽位 + evidence_turns
用户间聚合   Truth Discovery 加权投票：每用户融合槽位 = 一票
             票权 = reliability 后验 × external 一致性 × (1−incentive_risk) × (1−deception)
消融验证     fusion=llm / voting / last-wins 三档并行，slot 准确率对比说话
```

**关键点（心智审查结论，必须记住）**：语义等价（「还行=按需=随行就市=中性」）必须读全局才能判，逐轮独立映射会把同义表述拆成分裂票——**这一点上投票永远做不好**；投票的正确位置在**用户间**（离散冲突裁决），不在**用户内**（语义理解）。

**用户说话的效力（票权）与什么有关**：
1. **reliability 后验**——跨源一致性 + 外部数据校验累积出的「预测诚实度」（Bayesian Beta 后验，替代现启发式；单人单桶无跨源证据时不更新）
2. **ReCon deception**——本次表述的策略性风格分（注意：测的是风格不是实锤谎言，见 CheatAgent.md §五「机理确认」）
3. **incentive_risk**——claim 方向与头寸利益的对齐度（long 用户报利多消息 → 风险高）
4. **external consistency**——与价格走线等场外数据的吻合度

**与生成期对齐**：cheatAgent 的 `cognitive-conflict-probe`（矛盾追问）产生的「追问后澄清」，在 LLM 融合中天然被读到（它看得见 agent 的追问句），不需要手写「rebuttal 提权」规则。

### 测试用例系列（benchmark 覆盖性判例）

> 完整版（含实录对话与逐条分析预期）见 `CheatAgent.md` §五「测试用例系列」。设计原则：**不强扭 latent 分配**——低 honesty × 中性盘 = 无谎可说本身是合理场景；覆盖性由用例组合保证。

| 用例 | 参数组合 | 场景 | 融合层验收点 |
|------|----------|------|--------------|
| TC-01 | 高诚实 × 中性真相 | 基线真话 | 三槽直取，无冲突 |
| TC-02 | 低诚实 × 中性真相 × 看空谣言（实录） | 否认谣言恰为真话 | deception 高 ≠ 丢弃真值 |
| TC-03 | 低诚实 × 看空真相 × long | 撒谎动机成立，三句全谎 | 单人不可证伪 → 靠跨源+外部数据压票权 |
| TC-04 | 高诚实 × 看空真相 | 真话但弱化词缓冲 | 语义映射「不低=高」 |
| TC-05 | 高抵抗 × trap-question（实录） | 打太极不接盘 | deflect 不出槽，宁缺勿滥 |
| TC-06 | 低抵抗 × reactance 有偏陈述（实录） | 被激出反驳泄露等级 | rebuttal 携带真值 |
| TC-07 | 追问后澄清（实录） | 还行 → 中性 精确化 | LLM 读因果采纳澄清；投票分裂票（消融判例） |
| TC-08 | 语义等价多表述（实录） | 还行/随行就市/正常/中性 | 读全局合并；逐轮映射必拆票 |

### Truth Discovery：多个来源对同一对象给出冲突信息时，如何同时估计：
- 哪个说法更可能是真的；
- 哪些来源更可靠；
- 某个来源在哪些任务上更可靠。

### Bayesian Source Reliability：维护每个用户的“可信度后验”
- 来源质量是解决冲突信息整合的关键，并可用概率图模型自动推断真值和来源质量。

### 众包真值推断
- 从多个 worker 的回答中推断正确答案，同时估计 worker 的 reliability。
- 对 Agent 场景的启发是：不要只存原始对话，要把回答抽取成 claim，并把 claim 放进统一的 truth inference 框架里。

### 外部数据与 Alternative Data 校验
- 整合价格、库存、生产、贸易、船运、港口、海关、新闻、供应链等多源数据。

### Human-in-the-Loop
- 合适的退出条件，什么时候模型失效，什么时候需要人工介入。

### 相关学术方向
- Automated / Autonomous Interviewing for Deception Detection	自动化虚拟 Agent 面试/审讯，检测人类欺骗	边境筛查、安全筛查
- Autonomous Scientifically Controlled Screening Systems (ASCSS)	自主科学控制筛查系统，检测人类故意隐藏的信息	安检、内部威胁检测
- Social Deduction with LLM Agents	LLM Agent 在社交推理博弈中识别欺骗	Avalon/狼人杀等博弈环境
- Automated Linguistic Deception Detection	自动化语言学线索分析检测欺骗	文本对话欺骗检测
- Information Elicitation Mechanisms	机制设计引出真实私有信息	众包、评估场景
### 相关成果
- 算力要求较高，检测欺骗效果好。利用LLM隐藏状态识别人类欺骗：Autonomous Agents for Interrogation （DOI：10.1109/ICTAI62512.2024.00102 ）
- 递归沉思： ReCon（Recursive Contemplation） 框架——结合一阶视角转换（推断他人心理状态）和二阶视角转换（理解他人如何看待自己的心理状态），通过递归沉思增强 LLM 识别欺骗性信息的能力。Avalon's Game of Thoughts: Battle Against Deception Through Recursive Contemplation (ReCon)（arXiv:2310.01320）

## 对话场景（怎么提问怎么回答）
用户说的话可能是假的，用Agent多轮对话的方式来完成套话获得真实信息。


### 相关学术方向&成果
#### 技术向
话术：
    Strategic Use of Evidence (SUE)	证据策略性使用	利用说谎者与诚实者不同的反审讯策略，通过控制证据披露时机制造矛盾	最成熟，检测准确率最高
    Verifiability Approach (VA)	可验证性方法	说谎者会回避可验证细节，诚实者会提供更多可核查信息	有效区分
    Cognitive Credibility Assessment (CCA)	认知可信度评估	施加认知负荷，说谎者比诚实者更难应对	多种子技术
    Reality Interviewing (RI)	现实面试法	通过特定提问模式引导真实记忆的提取	基于认知心理学
多轮对话：
    澄清Agent：产品特征摘要 → 查询生成 → 产品检索的完整策略链：ProductAgent: Benchmarking Conversational Product Search Agent with Asking Clarification Questions（DOI：10.1145/3770366.3770412）
#### 心理学
通过用户主动问的问题反向推断用户的隐藏状态/私有信息
    信息寻求行为分析	一个人寻求什么信息，反映他缺什么/有什么	⭐ 最直接——问库存说明有库存 Children’s sequential information search is sensitive to environmental probabilities
    贝叶斯心智理论	从可观测行为推断不可观测的心理状态	⭐ 核心方法论——从提问推断隐藏状态   Rothe, A., Lake, B.M. & Gureckis, T.M. Do People Ask Good Questions?. Comput Brain Behav 1, 69–89 (2018). https://doi.org/10.1007/s42113-018-0005-5
    隐式用户建模	从用户行为（而非显式输入）推断偏好/状态	⭐ 技术基础 
    显示偏好理论	经济学——选择行为揭示真实偏好	理论基础

Understanding user intent modeling for conversational recommender systems: a systematic literature review.：
    系统分析了近十年超过 13,000 篇论文，识别了 59 种模型和 74 个常用特征。 
    关键框架：用户意图建模的三层结构：

    显式意图——用户直接说了什么
    隐式意图——从行为推断的意图
    潜在意图——用户自己可能都没意识到的深层需求

    Farshidi, S., Rezaee, K., Mazaheri, S. et al. Understanding user intent modeling for conversational recommender systems: a systematic literature review. User Model User-Adap Inter 34, 1643–1706 (2024). https://doi.org/10.1007/s11257-024-09398-x

###### 陷阱问题
环节	相关研究方向	核心机制
给出有偏信息	信息设计 / Bayesian 说服	发送者策略性地选择披露什么信息
触发反驳	心理反抗理论	感知自由受威胁→产生反驳动机
提取真实信息	苏格拉底法 / 认知冲突	从用户的纠正/反驳中获取真实知识
📚 关键研究成果
一、心理反抗理论——为什么人爱反驳
Psychological Reactance Theory (PRT)

心理反抗理论由 Brehm (1966) 提出，核心观点是：当人感知到自己的自由受到威胁时，会产生反抗动机——倾向于做被禁止的事，或反驳被强加的观点。

关键机制：

自由威胁感知：当信息呈现方式让人觉得"被说服"或"被操控"时，用户感知到自由威胁
反驳动机：用户产生强烈的纠正/反驳欲望
反弹效应：不仅反驳，还可能走向更极端的立场
对你的启示：故意给出明显有偏的信息（如"听说铁矿石价格要大涨，现在库存多的都亏了"），用户如果真实情况是库存多且不亏，会产生强烈的反驳冲动——"谁说的？我库存多着呢，现在利润很好"——真实信息就这样被引出来了。

相关论文：

Freedom-prompting Reactance Mitigation Strategies（Communication Reports 2021）
Psychological Reactance Theory and Politeness Theory（Communication Monographs 2026）
二、苏格拉底法 + LLM——通过提问/引导激发用户纠正
1. AVERT: LLM-Based Procedure That Interactively Verifies Understanding

📎 论文链接
会议: ITHE 2024
核心方法：使用 LLM 驱动的聊天机器人，采用苏格拉底法动态生成问题，要求学生解释代码背后的逻辑。不是直接问"这是你写的吗"，而是通过引导学生解释和纠正来验证其真实理解程度。

与你的关联：AVERT 的思路是——不直接质疑，而是通过引导性的提问/陈述让学生自己暴露真实水平。你的策略是类似的——不直接问，而是给出有偏陈述让用户自己纠正。

2. IntelliChain: Enhanced Socratic Method Dialogue with LLMs and Knowledge Graphs

📎 论文链接
核心方法：结合知识图谱和 LLM，通过苏格拉底式对话引导用户思考和纠正认知偏差。

3. Socratic Mind: Scalable Oral Assessment Powered by AI

📎 论文链接
核心方法：AI 通过苏格拉底式提问进行口语评估——不直接告诉用户对错，而是通过引导性的陈述和问题让用户自己暴露真实水平。

三、众包中的"陷阱问题"——故意给错误信息来测试真实性
Outliers Detection vs. Control Questions to Ensure Reliable Results in Crowdsourcing

📎 论文链接
会议: WWW 2018 | 引用: 13
核心方法：在众包任务中插入陷阱问题（trapping questions）——这些问题有已知的正确答案，用来检测工作者是否在认真回答。

关键发现：单独使用陷阱问题或异常检测都不够有效，但两者结合效果最好。

与你的关联：这其实就是你策略的简化版——故意在信息中嵌入"已知错误"（有偏信息），看用户是否会纠正。如果用户纠正了，说明他对这个领域有真实了解；如果不纠正，说明他可能不专业或在敷衍。

四、信息设计 / Bayesian 说服——策略性信息披露
1. Optimal Information Disclosure: A Linear Programming Approach

📎 论文链接
期刊: Theoretical Economics
核心理论（Kamenica & Gentzkow 2011 的后续工作）：发送者可以策略性地设计信息披露方式，使得接收者在贝叶斯理性的前提下，做出对发送者有利的行动。

与你的关联：你的策略本质上是信息设计的"反向应用"——不是为了让用户做出某种行动，而是为了激发用户的纠正行为从而获取信息。你设计有偏信息 P(biased)，使得用户在真实状态 S 下大概率会反驳，而你从反驳中更新 P(S|rebuttal)。

2. Divide and Inform: Rationing Information to Facilitate Persuasion

📎 论文链接
期刊: The Accounting Review
核心发现：将信息分批、有选择地披露比分一次全披露更有效——因为每批信息都会触发接收者的不同反应。

五、信息操纵理论——如何策略性地"歪曲"信息
Deceptively Dodging Questions: A Theoretical Note on Issues of Perception and Detection

📎 论文链接
期刊: Discourse & Communication 2018 | 引用: 12
核心理论（信息操纵理论 Information Manipulation Theory, IMT）：

基于 Grice 的合作原则（量、质、关联、方式）
沟通者可以通过微妙地违反这些原则来操纵信息
例如：说出真实但有选择性的信息（违反"量"的准则），或说出看似合理但有偏的信息（违反"质"的准则）
与你的关联：你的策略正是信息操纵的一种形式——给出的信息不是完全虚假的（否则用户不会认真对待），而是真实但有选择性/有偏向性的，使得用户觉得"这个说法不对/不完整"，从而产生纠正冲动。

六、认知冲突 / 概念转变——从纠正中学习
苏格拉底法的核心是制造认知冲突（Cognitive Conflict）：

提出一个与用户现有认知部分冲突的陈述
用户感到"不对但说不清楚哪里不对"
在反驳过程中，用户暴露了自己的真实认知状态
相关 LLM 应用：

On the Helpfulness of a Zero-Shot Socratic Tutor（2024）
The Pedagogical Hard Problem of Generative AI: Socratic Countermeasures（2026）
The Socratic Dialogue As a Method for Virtue Ethics in AI（AIES 2025）


# 算法逻辑实现
## 对话采集场景
### 对话到 claim 的结构化抽取层
把原始多轮对话抽成统一 schema：
```
claim = {
  source_id,
  conversation_id,
  time,
  region,
  market_object,
  indicator,
  value,
  claim_type,           # numeric / directional / ordinal / binary
  evidence_strength,    # 是否提到具体数字、第一手观察、时间窗口、地点、主体
  stance_risk,          # 对其头寸是否有利
  provenance,           # 原句、轮次、是否转述、是否引用别人
  extractor_confidence
}
```
### claim canonicalization 与领域本体层
这一步要解决“港口库存很多”“库存偏高”“港口还有货”“块矿不紧”等表达不一致的问题。
先建一个轻量 ontology：区域（青岛港、日照港、唐山等）、对象（铁矿石、钢厂、贸易商、港口）、指标（港存、到港量、疏港量、采购积极性、报价松动、利润、压港、发运）和标准值域（高/中/低、紧/平/松、上涨/平稳/下跌）。
如果这一步做得好，后面 truth discovery 就不会把“口语差异”误当成“事实冲突”。
FactKG、COPAAL 和 KG-based fact verification 说明，结构化表示会显著提升后续验证和解释的稳定性。[arXiv:2305.06590 [cs.CL]](https://arxiv.org/abs/2305.06590)

### 时变、分领域、带来源依赖惩罚的真值推断层
分层贝叶斯 / EM 混合框架
对每个 claim bucket b = (week, region, object, indicator)
估计 latent truth z_b

对每个来源 u、领域 d、时间 t
估计 reliability r_{u,d,t}

对每对来源 u,v、时间 t
估计 dependence a_{u,v,t}

对每个 bucket
引入外部证据 x_b 作为 weak supervision / prior

```
claim_score(c) =
  w1 * reliability(source, domain, time)
+ w2 * evidence_strength
+ w3 * independence_score
+ w4 * external_consistency
- w5 * incentive_risk
```
然后按 bucket 做迭代更新：先由当前来源权重合成 bucket truth，再根据来源与该 truth 的长期一致性更新来源后验；同时，如果两个来源在措辞、时间、引用链上高度接近，就提升 dependence penalty，压低它们作为“独立证据”的贡献。这里的思想直接来自 dependent-source truth discovery、multi-truth Bayesian 模型和 domain-aware reliability。

### 外部数据校验层
在铁矿石场景里，价格、 import stats、港口库存、贸易流和行业调研可以作为延迟但有力的“对照系”。
- 价格与市场反应：SGX / DCE 铁矿石价格以及期限结构
- 第二类是库存 / 物流 / 贸易实体数据：海关统计、Mysteel 港口库存、行业协会统计、Kpler / BigMint 的贸易流与 cargo intelligence
- 事件与 regime 标记：重大政策、天气、港口拥堵、矿山事故等触发非平稳状态
### 激励与人工接管层
人都是有偏向的，他会“相信”某东西，比如他一致认为会涨，跌了对他来说就是回撤，说明快涨起来了。
- 错误不是随机噪声，而是有方向的
    - 建立 incentive_risk（激励风险）， 若错误高度集中在对用户有利方向，说明不是普通错误。
- Peer Prediction：“别人会怎么说？”


# Benchmark 建立

> **决策**：仅 Tier A + Tier B（无人工标注能力）。详见 `decisions/001-benchmark-strategy.md`。
>
> - **Tier A**（组件）：FaitCrowd / BigTom+ReCon 等邻域数据集
> - **Tier B**（主评测）：**30 段长对话**；预设 persona（身份/性格/头寸/诚实度）；程序 latent state 作 GT；**仅 1 条价格走线**作对话外因素
>
> **⚠️ beta_v1 世界态 P0 缺陷**（2026-07-10）：生成时按 `user_id` 独立随机 latent，未按 `(region, week)` 共享——跨用户 TD 无法验收。详见 `wrongway/02-benchmark-dataset.md` §2.3。修复数据集 **`beta_v2` 已全量验收**（td_world_truth_accuracy=1.0 · reliability r=+0.258）；beta_v1 仅作抽取+融合（Layer 1–2）对照。成果见 `benchmark/reports/RESULTS.md`。
>
> ~~Tier C~~ 取消。数据集全景见 `reference/benchmark-landscape.md`。

# 假设&约束
由于项目约束过于简单，为了方便，我们做出一些假设来简化，方便后续的实现和研究。

- 我们知道用户的头寸方向：因为我们有用户的手机号码、能打过去电话，就说明对用户有一定了解，那就应该大约知道用户是多头还是空头（如用户是厂长，那就是多头，身份决定了头寸方向）。
- 任务设计限定在铁矿石：大宗商品每一个品种的特性都不同，扩展更多种类没有很大的意义，我们这里限定在铁矿石，以便给以更详细的约束。
- 用户明确知道对方是Agent：被发现是Agent装人类会导致对话完全无法继续；所以在用户明确对方是Agent的情况下，用户问问题会远多于回答问题。
- 用户遵循基本的互惠共利原则，不论真假，问两个问题后至少要回答我们一个问题。
- 作为一个商业项目而非学术项目的约束：电话客服而不是普通网站问答：网站问答情景下，Agent反问用户问题，用户回答的概率太低，很可能直接忽视，而且我们要收集信息源是面向关键少数（比如厂长、仓库负责人），数量级不会特别大。
    - 电话客服约束：根据用户特点定制声线，这里忽略影响，因为对于我们的研究任务，文本信息的价值远高于语调等非文本信息。

