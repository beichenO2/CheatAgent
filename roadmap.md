# Roadmap — MarketTruthAgent

## 状态（2026-07-08）

**YOLO 阶段交付已废弃**（规则模板 + 硬编码 benchmark）。见 `wrongway.md`。

| 阶段 | 状态 | 说明 |
|------|------|------|
| M0 SSoT + 调研 | ✅ | ADR-001~008 |
| M1 分析骨架 | 🟡 保留 | ontology、Truth Discovery EM、ReCon（已去 GT 泄漏） |
| M2 旧 Tier B | ❌ 已删 | 规则 dialogue_simulator / 30 scenario |
| M3 旧交互链路 | ❌ 已删 | 7 模板 + FSM |
| M5 演示 UI | 暂缓 | 用户确认先不做 |
| **M6 套话 Skills** | **✅ 完成** | 1 路由 + 11 专项；15 篇论文；`套话skill/` + `skills/cheat-agent/` |
| **M7 cheatAgent 智能体** | **✅ 完成** | LangGraph + route_skill + invoke_skill LLM + CustomerAgent LLM |
| **M8 Dataset + 冒烟评测** | **✅ live** | PolarPrivate 3×20 + Claim F1/Pearson/EM 评测 |

---

## M6 — 套话 Skills ✅（2026-07-08 完成）

**目标**：从 `Readme.md` §90–197 凝练 **1 路由 + N 专项** Skills。

| 交付物 | 路径 | 状态 |
|--------|------|------|
| 论文 PDF × 15 | `套话skill/reference/papers/` | ✅ |
| 论文 md × 15 | `套话skill/reference/markdown/` | ✅ |
| 10 方向分析 | `套话skill/analysis/*.md` | ✅ |
| 路由 Skill | `skills/cheat-agent/SKILL-router.md` | ✅ |
| 专项 Skills × 11 | `skills/cheat-agent/SKILL-*.md` | ✅ |
| 路由规则接入 | `graph.py::route_skill` | ✅ |

**11 个 skill_id**：`clarification-probe` · `info-seeking-inference` · `bayesian-tom` · `implicit-user-modeling` · `reactance-biased-statement` · `socratic-probe` · `trap-question` · `info-design-disclosure` · `info-manipulation-bias` · `cognitive-conflict-probe` · `cover-qa`

**验收**：✅ router 输出合法 `skill_id`；✅ 每个专项有触发/禁用/模板；✅ LLM utterance 生成（M7，`invoke_skill`）。

---

## M7 — LangGraph cheatAgent ✅（2026-07-08 完成）

**架构文档**：`decisions/008-cheat-agent-langgraph.md`

```
cheatAgent (LangGraph)          CustomerAgent (LLM simulator)
  ├ load_context                  ├ load_persona + latent GT
  ├ update_user_model             └ compose_reply (honesty=strategy)
  ├ route_skill → SKILL-router
  ├ invoke_skill → SKILL-*
  └ write_memory (L0–L3)
```

**代码**：

```
src/market_truth_agent/agents/
  cheat_agent/graph.py
  customer_agent/graph.py
  simulation/runner.py
```

**已完成**：
- [x] 接 LLM（PolarPrivate / OpenAI，`MTA_LLM_MODE=mock|live`）
- [x] Skills 文件加载 + prompt 组装（`llm/prompts.py`）
- [x] CustomerAgent 按 honesty/resistance 行为生成
- [x] 记忆分层持久化 L1–L3（`cheat_agent/memory.py`）

**待完成 / 待审阅**：
- [ ] live LLM 端到端验证（需 API 密钥）
- [ ] LLM 路由（`route_skill` 当前为规则引擎，非 LLM）
- [ ] 用户审阅修改 graph 节点划分（ADR-008）

**验收**：✅ `build_cheat_agent_graph()` 可编译；✅ 单轮 turn 可跑通（mock/live）。

---

## M8 — Dataset 生成 + 冒烟评测 ✅（2026-07-08 完成）

### 已完成

| 项 | 说明 |
|----|------|
| 冒烟 dataset | `benchmark/datasets/smoke_v1/` — 3 用户 × 20 轮 × 1 session |
| smoke gate | `agents/eval/smoke_runner.py` — transcript / skill metadata / GT 隔离 |
| 套话指标 | kind / invoke / richness / coverage（`tactic_metrics.py`） |
| 生成/评测分离 | `generate_dataset.py` ≠ `evaluate_dataset.py` |

### 规模路线

| 阶段 | 规格 |
|------|------|
| **冒烟（当前）** | 3 用户 × 20 轮 × 1 session |
| Alpha | 10 用户 × 5 session × ≥20 轮 |
| Beta | 30 用户 × 5 session × ≥20 轮，横跨 5 个月 |

### 入口

```bash
pip install -e ".[dev,agent]"
python scripts/generate_dataset.py --preset smoke_v1
python scripts/generate_dataset.py --preset alpha_v1   # 10×5×20
python scripts/evaluate_dataset.py --dataset-dir benchmark/datasets/smoke_v1
pytest test/agents/ -v
```

---

## Alpha — 10×5 dataset 🔧（管线就绪）

| 项 | 状态 |
|----|------|
| `ALPHA_PERSONAS` ×10 | ✅ `personas.py` |
| 多 session + 跨 session 记忆 | ✅ `runner.write_dataset` |
| 价格走线 7 周 | ✅ `price_data.PRICE_TRAJECTORY` |
| 全量 mock/live 生成 | 待跑 `benchmark/datasets/alpha_v1/` |

### 套话性能指标（ADR-007）

- `skill_kind_count` — 话术种类数
- `skill_invoke_count` — 触发次数
- `skill_richness` — 分布熵
- `skill_coverage` — 覆盖率

~~`bias_triggered` claim 比例~~ — 已废弃。

### 分析评测（离线，GT 隔离）✅

- Claim F1 vs latent — `evaluate_dataset.py` → `claim_metrics.claim_f1_vs_latent`
- EM vs MV bucket error — `claim_metrics.em_vs_mv_errors`
- Pearson(r_u, honesty) — `claim_metrics.pearson_reliability_honesty`（仅 evaluate 读 honesty GT）

---

## 旧验收（已作废）

~~pytest 30 passed~~、~~run_tier_b.py Pearson 0.90~~ — 见 `wrongway.md`。
