# ADR-008: cheatAgent — LangGraph 双 Agent 架构

## 状态
accepted（2026-07-08；**M6–M8 已实现**；LangGraph 节点划分仍待用户审阅）

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

## 参数三层：设定 / 已知 / 推断（硬约束）

双 Agent **数据不互通**。除对话 `turns[].text` 与业务身份外，CustomerAgent 的 GT 不得进入 cheatAgent 状态或 prompt。

| 层 | 含义 | 典型字段 | 使用方 | cheatAgent |
|----|------|----------|--------|------------|
| **设定** | 生成前写入 dataset 的 GT / 人设 | `honesty`, `persona.resistance`, `latent`, `personality` | CustomerAgent LLM；离线 `evaluate_dataset.py` | ❌ 禁止读 |
| **已知** | 业务系统预先掌握（非推断） | `role`, `region`, `position`（长期固定 `long`） | 两边 prompt 各用 | ✅ 无 GT |
| **推断** | 从已发生对话观测 | `user_model.resistance_level`, `partial_claims`, `inferred_gaps` | 仅 cheatAgent（`update_user_model` → `route_skill`） | ✅ 仅来自 history |

### 公开信道（唯一跨 Agent 数据流）

```
设定(GT) → CustomerAgent → 客户 utterance (text)
                                    ↓
              cheatAgent ← history.text → update_user_model（推断）
                                    ↓
              route_skill / invoke_skill → 客服 utterance (text)
                                    ↓
              CustomerAgent ← 客服 utterance + history（仍不可见 honesty/latent）
```

### 同名不同源：`resistance`

| 变量 | 类型 | 来源 |
|------|------|------|
| `persona.resistance` | 设定 | `personas.py` 预设，仅 CustomerAgent prompt |
| `user_model.resistance_level` | 推断 | 客户话中出现反驳词（「不对」「谁说的」等）时 +0.2，**不拷贝** persona 值 |

高 `persona.resistance` 的客户更常说出反驳 → 客服侧 `resistance_level` 升高 → 可能路由到 `cover-qa/RECOVER`，这是**行为因果**，不是 GT 泄漏。

### Skill 归属

- **SKILL-router + 11 专项 Skills**：仅 cheatAgent（`router.py` → `invoke_skill`）。
- **CustomerAgent**：`load_persona → load_latent_truth → compose_reply`，**无 skill 路由**；落盘 user 轮 `skill_id: null`。

### 运行时校验

`smoke_runner._check_gt_isolation()` 静态检查：ReCon / cheat prompt / invoke_skill 源码中不得出现 `persona.honesty` 或 `honesty:` GT 字段。

## cheatAgent LangGraph 节点

```
START
  │
  ▼
[load_context] ── 注入：session_date, price_snapshot, user_id,
│                  已知身份(role/region/position)，历史 turns
│                  ⚠ 不注入 honesty
▼
[update_user_model] ── 轻量 UserModel（**推断**，无 GT）：
│                       inferred_gaps, resistance_level,
│                       partial_claims — 均来自 history.text
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
| **L2 User Model** | `memory/users/{user_id}.json` | 推断字段：inferred_gaps, resistance_level 轨迹, partial_claims | 跨 session 累积 |
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

## 代码位置（2026-07-08 实现）

```
src/market_truth_agent/
  agents/
    cheat_agent/
      graph.py              # LangGraph + route/invoke/write_memory
      state.py
      memory.py             # L1 session / L2 user / L3 episodic
      skills_registry.py
    customer_agent/
      graph.py              # run_customer_agent_turn (LLM)
      personas.py
    simulation/
      runner.py             # 双 Agent 对话循环
    eval/
      tactic_metrics.py
      smoke_runner.py       # M8 smoke gate
  llm/
    client.py               # MTA_LLM_MODE mock|live
    prompts.py

skills/cheat-agent/         # M6 ✅ — 1 router + 11 专项
benchmark/datasets/smoke_v1/  # M8 ✅ 冒烟 dataset
scripts/generate_dataset.py
scripts/evaluate_dataset.py
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

LLM 调用走 PolarPrivate / OpenAI 兼容端点，环境变量配置，密钥不入库。实现见 `llm/client.py`（`MTA_LLM_MODE=mock|live`）。

## 冒烟测试（M8 门禁）✅ 2026-07-08 通过

| 项 | 规格 | 状态 |
|----|------|------|
| 用户数 | 3（honest≈0.85, medium≈0.55, strategic≈0.25） | ✅ |
| 轮次 | 每人 20 轮（user+agent 合计） | ✅ |
| dataset 落盘 | `benchmark/datasets/smoke_v1/` | ✅ |
| transcript 非空 | turns ≥ 20 | ✅ |
| skill metadata | `agent_metadata[].skill_id` | ✅ |
| GT 隔离 | `smoke_runner._check_gt_isolation()` | ✅ |
| 分析 pipeline | `evaluate_dataset.py` 可跑 | ✅ |

验证：`MTA_LLM_MODE=mock pytest test/agents/ -v` · `python scripts/generate_dataset.py`

## 待用户审阅/修改

- [ ] LangGraph 节点划分是否足够细？
- [x] 记忆分层 L0–L3 是否符合预期？（已实现 `memory.py`）
- [x] Skill 调用协议（router 输出 schema — `route_skill` 返回 skill_id/phase）
- [x] LLM provider 选型（`MTA_LLM_MODE` + OpenAI/PolarPrivate 兼容）
- [x] CustomerAgent prompt 中 honesty/resistance 行为（`llm/prompts.py`）
- [ ] live LLM 端到端质量验证（需 API 密钥）

## 参考

- ADR-007
- `wrongway.md`
- LangGraph 文档：https://langchain-ai.github.io/langgraph/
