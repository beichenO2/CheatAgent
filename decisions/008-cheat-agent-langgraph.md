# ADR-008: cheatAgent — LangGraph 双 Agent 架构

## 状态
accepted（2026-07-08，架构草案，待用户审阅修改）

## 目标

用 LangGraph 搭建 **cheatAgent（客服套话）** 与 **CustomerAgent（模拟客户）** 对抗生成 dataset；评测同样走 Agent pipeline。

## 总览

```
                    ┌─────────────────────────────────────┐
                    │         SimulationRunner            │
                    │  (dataset 生成 / 冒烟评测入口)        │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
   ┌──────────────────────┐               ┌──────────────────────┐
   │    CustomerAgent     │◄── turns ───►│     cheatAgent       │
   │  (客户，持 latent GT)  │               │  (客服，套话采集)     │
   └──────────────────────┘               └──────────┬───────────┘
              │                                       │
              │ persona + latent                      │ Skills router
              │ (含 honesty, resistance)              │ + memory layers
              ▼                                       ▼
         不暴露 GT 给 cheatAgent                  不读 honesty GT
```

## cheatAgent LangGraph 节点

```
START
  │
  ▼
[load_context] ── 注入：session_date, price_snapshot, user_id,
│                  已知身份(role/region/position)，历史 turns
│                  ⚠ 不注入 honesty
▼
[update_user_model] ── 轻量 UserModel：inferred_gaps, resistance,
│                       intent_layers, partial_claims
▼
[route_skill] ── 调用 SKILL-router → 选出 skill_id
│
▼
[invoke_skill] ── 加载对应 SKILL-*.md → 生成 agent utterance
│                 记录 metadata: {skill_id, phase, recon_hint}
▼
[write_memory] ── 分层写入记忆（见下）
│
▼
END → agent utterance + metadata
```

## 记忆分层（每 user_id 独立）

| 层 | 存储 | 内容 | 生命周期 |
|----|------|------|----------|
| **L0 Working** | Graph state | 当前 session turns | 单 session |
| **L1 Session** | `memory/sessions/{user}/{session_id}.json` | 本次摘要、用过的 skills、tactic 计数 | 单 session 持久 |
| **L2 User Model** | `memory/users/{user_id}.json` | inferred_gaps, resistance 轨迹, partial_claims | 跨 session 累积 |
| **L3 Episodic** | `memory/episodes/{user_id}.jsonl` | 关键 turn 摘要（不含 GT） | 追加式 |

cheatAgent **预先知道** user_id 对应 role/region/position（业务系统已有），**不需要问用户身份**。

## CustomerAgent

```
START → [load_persona] → [load_latent_truth] → [compose_reply] → END
```

| 输入 | 说明 |
|------|------|
| `persona` | role, region, position, honesty, resistance, personality |
| `latent.claims_truth` | 该用户真实市场状态（GT） |
| `price_snapshot` | 当前 session 价格 |
| `cheat_agent_utterance` | 上轮客服话术 |
| `conversation_history` | 历史 |

**honesty 语义**：不是「每句撒谎」，而是信息披露策略——低 honesty = 优先按头寸利益组织表述，可真假混合、选择性披露。

**resistance**：对 biased_statement / trap_question 等产生心理反抗的概率与强度。

CustomerAgent **可读 GT**（它是 simulator）；cheatAgent **不可读**。

## Dataset 插入点

```yaml
# benchmark/datasets/smoke_v1/users/U001/meta.json
persona:
  user_id: U001
  role: 厂长
  region: 青岛港
  position: long
  honesty: 0.85          # GT，仅 eval 用
  resistance: 0.2
  personality: 谨慎型

latent:
  claims_truth: [...]
  price_trajectory: [...]   # 5 个月完整走线（冒烟期可截短）

sessions:
  - session_id: S001
    session_date: "2026-03-01"
    week: "2026-W09"
    price_snapshot: {price: 820, trend: "平"}
    turns: []                 # 生成后填充
    agent_metadata:           # 每轮 skill_id 等
      skill_invoke_count: 0
      skill_kinds: []
```

## 评测流程（Agent pipeline）

```
1. 加载已生成 dataset（或现场 re-run simulation）
2. AnalysisPipeline（LLM claim 抽取 + ReCon + EM）— 不读 honesty
3. Evaluator（离线）：
   - 分析：claim F1, EM vs MV, Pearson(r_u, honesty)  ← honesty 仅此处
   - 套话：skill_kind_count, skill_invoke_count, skill_richness
```

生成与评测 **不同 script 入口**：
- `scripts/generate_dataset.py`
- `scripts/evaluate_dataset.py`

## 代码位置（脚手架）

```
src/market_truth_agent/agents/
  cheat_agent/
    graph.py          # LangGraph 定义
    state.py          # CheatAgentState
    nodes/            # load_context, route_skill, invoke_skill, write_memory
  customer_agent/
    graph.py
    state.py
    personas.py
  simulation/
    runner.py         # 双 Agent 对话循环
    dataset_builder.py
  eval/
    tactic_metrics.py
    smoke_runner.py

skills/cheat-agent/   # M6 用户填充
  SKILL-router.md     # 占位
  README.md
```

## 依赖

```toml
[project.optional-dependencies]
agent = [
  "langgraph>=0.2",
  "langchain-core>=0.3",
  "langchain-openai>=0.2",  # 或 PolarPrivate 封装
]
```

LLM 调用走 PolarPrivate / 环境变量，密钥不入库。

## 冒烟测试（M8 门禁）

| 项 | 规格 |
|----|------|
| 用户数 | 3（honest≈0.85, medium≈0.55, strategic≈0.25） |
| 轮次 | 每人 20 轮（user+agent 合计） |
| 通过条件 | dataset 落盘；transcript 非空；skill metadata 有记录；分析 pipeline 可跑；无 GT 泄漏静态检查 |

## 待用户审阅/修改

- [ ] LangGraph 节点划分是否足够细？
- [ ] 记忆分层 L0–L3 是否符合预期？
- [ ] Skill 调用协议（router 输出 schema）
- [ ] LLM provider 选型（OpenAI / 内部 PolarPrivate）
- [ ] CustomerAgent prompt 中 honesty/resistance 的具体行为定义

## 参考

- ADR-007
- `wrongway.md`
- LangGraph 文档：https://langchain-ai.github.io/langgraph/
