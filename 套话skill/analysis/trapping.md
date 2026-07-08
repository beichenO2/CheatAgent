# 陷阱问题 / 有偏信息检测真实性 — 研究方向分析

> 研究来源：`crowdsourcing-trapping`（Jiménez, Fernández Gallardo & Möller, WWW 2018）  
> 应用场景：铁矿石电话客服套话（MarketTruthAgent 交互链路 — `trap-question`）

---

## 1. 核心机制

**基本命题**：在对话中嵌入**已知标准答案**的「控制性错误/有偏信息」，观察用户是否识别并纠正——纠正行为是**领域知识 + 认真参与**的可观测代理信号；沉默接受或附和则提示敷衍、外行或策略性配合。

### 1.1 众包质控 → 套话验证的映射

WWW 2018 论文研究两类众包可靠性机制：

| 机制 | 众包含义 | 套话 Agent 映射 |
|------|---------|----------------|
| **Trapping Questions（陷阱题）** | 插入有 gold answer 的控制题，筛掉不认真作答者 | 在业务陈述中嵌入**可核验的事实性错误**（与 `price_snapshot`、公开港存/指数矛盾） |
| **Outlier Detection（异常检测）** | 剔除统计上偏离群体的评分 | 跨轮检测用户 claim 与**外部锚点、自身前后陈述**的偏离 |
| **F-TQ-OD 组合** | 先过陷阱题，再对剩余数据做异常过滤 | **陷阱触发纠正** + **多轮一致性/对价证据交叉**联合判 reliability |

Readme 第 150–159 行的核心映射：

```
Agent 嵌入已知错误 P(wrong)
    │
    ├─ 用户纠正 → P(expertise | correction) ↑，可 elicit 更细 claim
    ├─ 用户不纠正 → P(perfunctory | silence) ↑ 或 P(bluff | agree)
    └─ 与 outlier 信号叠加 → 更新 UserModel.knowledge_depth / deception 权重
```

### 1.2 与「心理反抗有偏陈述」的机制差异

| 维度 | 陷阱问题（本方向） | 有偏陈述（reactance） |
|------|-------------------|----------------------|
| 错误性质 | **有 gold answer**，对错可客观判定 | 偏误程度连续，无唯一标准答案 |
| 检测目标 | 是否**识别基础事实错误** | 是否**主动提供专业细节** |
| 用户反应类型 | 二元：纠正 / 不纠正 / 错误附和 | 纠正、部分认同、回避、情绪反抗 |
| 信息产出 | 主要验证**真实性**；纠正时可附带细节 | 主要 elicit **领域细节** |

本方向是 Readme 所称策略的「**简化版质控**」：不靠长篇引导，而用一两个**硬锚点**快速分流「真内行 vs 可能不专业/在敷衍」。

### 1.3 为何必须「陷阱 + 异常」组合

论文实证结论（语音质量众包，ITU-T P.800/P.863）：

- **单独 F-TQ**：能去掉明显不认真者，但可能误伤「真 outlier 意见」；对整体与实验室金标准的相关性提升有限。
- **单独 OD**：可能删掉真实但少数派的判断；单独使用同样不足以提升准确性。
- **F-TQ-OD 组合**：先陷阱筛参与质量，再对剩余回答做统计异常过滤——**两者互补**，相关性最优。

套话含义：

```
trap 纠正信号 ──→ 筛「是否在认真对话、是否具备基础事实感」
       +
outlier 一致性 ──→ 筛「纠正了但仍与 price_snapshot / 前序 claim 矛盾」的伪装内行
       │
       └──→ UserModel.reliability_score
```

### 1.4 与系统模块的衔接

- **输入**：`session.price_snapshot`、公开港存/指数、`partial_claims`（来自信息寻求推断）
- **触发**：`SKILL-router` 原则 3 — 已有 partial truth 且需验证真伪 → `trap-question`
- **输出**：`knowledge_depth`、`deception_signals`、`reliability_score` 更新；纠正后接 `va-detail-chase` 锁定可验证参数
- **phase**：通常 `CHALLENGE` 或 `VERIFY`；高 resistance 时降级为轻量 trap 或暂缓

---

## 2. 适用场景（铁矿石电话客服套话）

### 2.1 高适用

| 场景 | 触发条件 | 陷阱设计要点 | 预期信号 |
|------|---------|-------------|---------|
| **partial claim 待验** | 用户给出库存/成交价，尚未交叉验证 | 嵌入与 claim **方向一致但数值明显错误**的「复述」 | 纠正 → 可信；附和错误数 → 降权 |
| **身份/岗位存疑** | 自称贸易/库存岗，但首问极泛、答模板化 | 嵌入**一线必知**的错误（如混淆青岛/日照港、指数发布日） | 纠正 → 岗位可信 |
| **多轮后进入 VERIFY** | rapport 已建立，需分流真内行 | 单条可核验硬错误 + 观察是否展开细节 | 纠正 + 细节 → 高价值 claim |
| **与 reactance 互补** | 有偏陈述未引出反驳 | 换**更硬、更二元**的事实陷阱 | 区分「无反应」vs「无能力识别」 |
| **欺骗信号中等** | 前后口径略有不一致 | trap 测基础事实 + OD 测跨轮一致 | 组合判 reliability |

### 2.2 中适用

- **用户主动假设检验**（「是不是已经 1.5 亿吨了？」）：可轻度 trap——故意复述其数字并**故意错一位**，看是否敏感。  
- **cover-qa 之后**：正常答价 2–3 轮后再插 trap，避免初期暴露测试意图。  
- **研究员/对手盘**：可能故意不纠正以套信息——需 OD 与 deception 模块降权 trap 结论。

### 2.3 低适用 / 不宜单独依赖

- **RAPPORT 前 2 轮**：trap 易被感知为「不专业客服」，损 trust。  
- **用户已高 resistance**：trap 加剧心理反抗 → 转 RECOVER。  
- **无可靠 gold answer**（纯主观预期、传闻）→ 应用 `reactance-biased-statement`，非本方向。  
- **已有 price_snapshot 且 claim 明确矛盾** → 优先 `sue-price-confront`，而非再设 trap。  
- **用户明确拒答经营数据**：trap 不能替代 VA/SUE 的合法 elicitation 路径。

### 2.4 在 1+N Skill 架构中的位置

| 上游 | 本 skill | 下游 |
|------|---------|------|
| `info-seeking` 推断 gap | `trap-question` 验证 partial claim | 纠正 → `va-detail-chase` |
| `reactance-biased-statement` 未触发反驳 | 换硬 trap | 仍无反应 → `socratic-probe` 或降权 |
| `cover-qa` 建立互惠 | VERIFY 阶段插入 trap | OD 矛盾 → `sue-price-confront` |

---

## 3. 话术模板（至少 5 条 — 嵌入已知错误/有偏信息）

以下模板均含 **Agent 已知 gold**（来自 `price_snapshot` 或公开可核验事实）。执行时须**本地化替换**错误数值，且错误须「内行一眼可识、外行可能忽略」。

### 模板 1：指数点位张冠李戴（gold：当日实际指数）

**嵌入错误**  
「今天 62% 普氏指数大概在 **920 美元**左右吧，和上周差不多。您那边成交跟指数走得近吗？」

**已知 gold**  
`price_snapshot.platts_62` 实际为 ~850（示例；执行时读 session）。

**预期反应**  
- 纠正：「920 不对，今天八百多」→ `knowledge_depth ↑`  
- 不纠正/附和：「差不多吧」→ `reliability_score ↓`  
- 错误附和更高价：可能 bluff 或抬价意图

**提取目标**  
是否具备基础价格感知；纠正后追问实际成交区间。

---

### 模板 2：港口库存数量级错误（gold：公开港存统计）

**嵌入错误**  
「听说 **青岛港铁矿石库存已经到 1.8 亿吨**了，压港挺厉害。您走的也是青岛吗？」

**已知 gold**  
青岛港铁矿石库存公开口径约 **1.3–1.5 亿吨**量级（非 1.8）。

**预期反应**  
- 纠正：「没那么多，大概 X」→ 验证库存岗/区域真实性  
- 不纠正：可能非本地、非库存线、或敷衍

**提取目标**  
港存量级、所在港口、是否自有货。

---

### 模板 3：时间窗口错位（gold：session_date 与近期行情）

**嵌入错误**  
「**上周**那波反弹基本结束了，这周都在回调。您最近出货顺吗？」

**已知 gold**  
`session_date` 对应周实际为**上涨/震荡**而非「已结束反弹」（依 snapshot 配置）。

**预期反应**  
- 纠正：「这周还在涨 / 上周没那么涨」→ 时间线敏感，一线参与度高  
- 不纠正：信息滞后或不在一线

**提取目标**  
近期成交节奏、合同执行时点。

---

### 模板 4：区域/流向张冠李戴（gold：known_identity.region）

**嵌入错误**  
「**北方**这边钢厂补库挺积极，**南方**港口反而偏松。您在北方还是南方做？」

**已知 gold**  
用户 `known_identity.region = 华东/青岛`，且公开数据为**北方松、南方紧**（或反之——须与 snapshot 一致）。

**预期反应**  
- 纠正：「我们华东这边其实挺紧 / 北方没那么积极」→ 区域认知真实  
- 盲目认同错误南北对比 → 区域身份可疑

**提取目标**  
真实经营区域、本地供需感知。

---

### 模板 5：长协/现货结构简化错误（gold：行业常识 + 当期市场）

**嵌入错误**  
「现在 **现货比长协普遍便宜 30 美元以上**，大家都要 spot。您长协占比高吗？」

**已知 gold**  
当期 spot-premium 实际为 **±10 美元或长协更优**（依市场；session 配置）。

**预期反应**  
- 纠正：「没差那么多 / 我们长协还有优势」→ 采购结构真实  
- 附和：可能非采购岗或随声附和

**提取目标**  
长协/现货配比、采购渠道、价格敏感度。

---

### 模板 6：疏港/到港指标混淆（bonus）

**嵌入错误**  
「**到港量**最近下来，所以 **疏港**特别快，库存一直在降。您码头那边提货车好排吗？」

**已知 gold**  
到港量与疏港量为不同指标；当前可能「到港增、疏港慢、库存累」（依 snapshot）。

**预期反应**  
- 纠正概念或数据 → 物流/港口线专业  
- 不区分指标 → 非码头/物流一线

**提取目标**  
疏港节奏、排队天数、可提量。

---

### 模板 7：品位/品种错误归类（bonus）

**嵌入错误**  
「**PB 粉**现在最好卖，**卡粉**反而滞销，高品位都不好出。您主要什么品种？」

**已知 gold**  
当期市场卡粉/高品位相对紧俏（依 snapshot 或公开价差）。

**预期反应**  
- 纠正品种结构 → 贸易品种认知真实  
- 附和错误品种偏好 → 可能外行

**提取目标**  
手头品种、客户需求结构。

---

### 执行要点

1. **一次一轮只设一个硬错误**：多错误叠加易暴露「考卷感」，触发 meta-reactance。  
2. **错误须可核验且适度**：太离谱（指数差 50%）→ 用户认为 agent 不专业而不纠正；太 subtle → 无法分流。  
3. **纠正后立即收网**：用 VA 追问数字来源，勿连续追加新 trap。  
4. **与 OD 联用**：同一用户若 trap 通过但与其他 claim / price_snapshot 矛盾，仍降 reliability。  
5. **礼貌包装**：「我这边看到的数据是…，您那边是不是不一样？」——降低对抗感。

---

## 4. 风险与禁忌

### 4.1 主要风险

| 风险 | 表现 | 后果 |
|------|------|------|
| **误伤真 outlier** | 用户持少数派但正确的市场观点，被 OD 当异常 | 错杀真实信息；论文明确警告此 trade-off |
| **trap 过滥** | 每轮都有明显错误 | 用户识别测试意图，信任崩塌 |
| **gold 错误** | Agent 嵌入的「错误」本身与事实不符 | 专业用户纠正 agent → 反向暴露 agent 不可信 |
| **不纠正 ≠ 不专业** | 用户礼貌、忙、或策略性不纠错 | 假阴性；需多信号组合 |
| **纠正 ≠ 说真话** | 用户只纠正 trap，其余仍隐瞒 | 假阳性；需 VA/SUE 后续验证 |
| **激怒 / 面子威胁** | 陷阱像「考客户」 | resistance ↑，对话终止 |
| **合规** | 被理解为欺诈性诱导 | 业务与伦理风险 |

### 4.2 禁忌清单

1. **禁止**在 RAPPORT 初期连续使用 trap；至少 2–3 轮 cover-qa 后再 VERIFY。  
2. **禁止**使用无 gold answer 的主观偏述冒充 trap——那是 reactance，不是本方向。  
3. **禁止** trap 错误与 `price_snapshot` 不一致（agent 侧 gold 必须先校验）。  
4. **禁止**用户纠正后坚持错误立场（「但我这边还是 920」）——破坏 elicitation，转 RECOVER。  
5. **禁止**单独依据「未纠正」下定论；须结合 OD、deception、多轮行为。  
6. **禁止** trap 与 SUE 同轮叠加——信息过载，且暴露对质意图。  
7. **禁止**对已知高 resistance 用户硬 trap；先 RECOVER 或 cover-qa。  
8. **禁止**编造与用户 `known_identity` 明显冲突且无法留白的错误（如已知青岛用户却断言「您走的湛江港库存」且无澄清空间）。

### 4.3 降级 / 退出条件

- 用户纠正 trap → **成功**：转 VA，暂停 trap 至少 3 轮。  
- 用户「嗯嗯/差不多」→ **弱信号**：可换另一维度 trap 一次；仍无反应则降权 reliability，勿连环 trap。  
- 用户「你数据不对」但未展开 → 轻追问一次；仍无细节 → 放弃 trap，改 socratic。  
- 用户情绪升温 → 立即 RECOVER，清空 CHALLENGE 队列。

---

## 5. 与其他方向边界

| 对比方向 | 核心差异 | 何时选 trap | 何时选对方 |
|---------|---------|------------|-----------|
| **心理反抗 / 有偏陈述** | 偏述无唯一 gold；激发细节 | 需**二元事实真伪**验证 | 需 elicit 连续细节、传闻级偏误 |
| **苏格拉底 / socratic-probe** | 引导自证，不预设错误结论 | 已有可核验 hard fact | 用户防御型、需解释逻辑链 |
| **SUE 价格对质** | 用外部证据直接对质 | 尚无足够证据、不宜撕破脸 | 已有 price_snapshot 且 claim 矛盾 |
| **VA 可验证性追问** | 追缺失参数 | trap **先验**真实性 | claim 框架已有，只缺数字 |
| **信息寻求推断** | 从提问反推 gap | 已有 partial claim 需**验证** | 刚从提问推断 gap，尚未 claim |
| **澄清提问** | Agent 消歧需求 | 验证对方**专业度/认真度** | 缩小检索空间、礼貌澄清 |
| **认知负荷** | 拆分复杂问题 | 测**事实识别** | 测回答是否过度流畅模板化 |
| **欺骗检测** | 多信号融合 | trap 是 deception 子信号 | 已有强矛盾，走专门 verify 流 |

**一句话边界**：`trap-question` = **用「已知错误的硬锚点」测用户是否具备可核验的领域真实度**；不是软偏述（reactance），不是证据对质（SUE），不是纯提问（socratic）。

**与 reactance 的分工链**：

```
partial claim → reactance-biased-statement（软偏，要细节）
                    │
                    └─ 无反驳 → trap-question（硬错，要真伪）
                                    │
                                    └─ 仍无反应 → socratic-probe / 降权
```

---

## 6. 关键论文要点

### 6.1 Jiménez, Fernández Gallardo & Möller (2018) — WWW Companion

- **标题**：*Outliers Detection vs. Control Questions to Ensure Reliable Results in Crowdsourcing: A Speech Quality Assessment Case Study*  
- **DOI**：10.1145/3184558.3191545  
- **任务域**：语音质量主观评分众包（ITU-T Rec. P.800），刺激来自 ITU-T Rec. P.863 database 501。  
- **对比方法**：  
  - **Trapping Questions (F-TQ)**：插入有标准答案的控制题，过滤未通过者；  
  - **Outlier Detection (OD)**：对评分做统计异常过滤；  
  - **F-TQ-OD**：组合流程。  
- **效标**：与实验室条件下采集的历史金标准评分之**相关性**。  
- **核心发现 1**：**单独**使用 trap 或 OD **均不足以**显著提升结果准确性。  
- **核心发现 2**：**F-TQ-OD 组合**效果最佳——先质控参与，再滤统计异常。  
- **核心发现 3（trade-off）**：  
  - Trap 会增加与主任务无关的刺激（task overload）；  
  - OD 可能丢弃「真实但少数派」的 worker 意见。  
- **设计启示**：可靠性机制应**组合**而非单点依赖；设计实验时需显式权衡「筛掉噪声」与「误伤真 outlier」。

### 6.2 先验工作 — Naderi et al. (2015, Interspeech)

- **题目**：*Effect of Trapping Questions on the Reliability of Speech Quality Judgments in a Crowdsourcing Paradigm*  
- **要点**：系统研究 trap 题对众包语音质量判断可靠性的影响；为 WWW 2018 的 F-TQ 管线提供基础。  
- **套话 takeaway**：trap 题在**主观评估类任务**中已被验证为有效质控手段；套话场景将「主观评估」映射为「对用户 claim 真实性的 agent 侧评估」。

### 6.3 Readme 第 150–159 行 — 项目策略对齐

- **核心方法**：众包任务中插入有 gold answer 的 trapping questions，检测工作者是否认真作答。  
- **关键发现**：trap 与 outlier detection **单独都不够**，**结合最好**。  
- **项目映射**：故意嵌入「已知错误」/有偏信息 → 用户纠正 = 真实了解；不纠正 = 可能不专业或敷衍。  
- **实现注意**：Readme 将 trap 与 reactance 并列为「有偏信息」家族，但本分析强调——**trap 必须有 gold**；「有偏但不二选一」归 reactance。

### 6.4 对系统设计的含义

```
partial_claims + price_snapshot
         │
         ▼
   [trap-question 模块] ──→ correction? ──→ knowledge_depth, claim 更新
         │                        │
         │                        └─ 无反应 → reliability ↓
         ▼
   [outlier 模块] ──→ 跨轮 / 对 snapshot 一致性
         │
         ▼
   UserModel.reliability_score ──→ SKILL-router
```

- **评测建议**：除「trap 纠正率」外，增加「纠正后 claim 与 snapshot 一致率」（F-TQ-OD 对齐）、「误伤率」（真内行被 OD 降权）。  
- **Tier B 标注**：保留 `trap_embedded_error`、`gold_answer`、`user_correction`、`reliability_label` 四元组，便于单独评 trap 链。  
- **配置依赖**：trap 模板必须绑定 `session.price_snapshot` 动态生成，**禁止静态写死错误数值**。

---

*文档版本：v1 | 基于 `crowdsourcing-trapping-stub` 与 Readme.md 第 150–159 行；论文全文 PDF 未开放获取，WWW 2018 摘要及公开元数据补充*
