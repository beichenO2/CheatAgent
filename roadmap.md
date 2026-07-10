# Roadmap — MarketTruthAgent

## 状态（2026-07-10 19:17）

**YOLO 阶段交付已废弃**（规则模板 + 硬编码 benchmark）。见 `wrongway.md`。

> **一句话**：抽槽和核心真值还原都很好；共享世界态下 TD 对 world_truth 全对；用户可信度与 honesty 已能测出正相关（beta_v1 几乎测不出）。详见 `benchmark/reports/RESULTS.md`。

| 阶段 | 状态 | 说明 |
|------|------|------|
| M0 SSoT + 调研 | ✅ | ADR-001~008 |
| M1 分析骨架 | ✅ | LLM ClaimExtractor + ReCon LLM + Truth Discovery EM |
| M2 旧 Tier B | ❌ 已删 | 规则 dialogue_simulator / 30 scenario |
| M3 旧交互链路 | ❌ 已删 | 7 模板 + FSM |
| M5 演示 UI | ✅ 完成 | ① Dashboard：论文风格 Overview + Session 回放（TC 书签）② 客服 Web UI：PolarChat 发行版 `market-truth-cs`（:3085/:3925，30 用户 × 150 对话 + 三层记忆 + 情景侧栏分组；JWT 链 + DEV/Release 双模式 + 数据清洗已回灌 `_template`） |
| **M6 套话 Skills** | **✅ 完成** | 1 路由 + 11 专项；15 篇论文；`套话skill/` + `skills/cheat-agent/` |
| **M7 cheatAgent 智能体** | **✅ 完成** | LangGraph + LLM route_skill + invoke_skill + CustomerAgent LangGraph |
| **M8 Dataset + 冒烟评测** | **✅ live** | PolarPrivate 3×20 + Claim F1/Pearson/EM 评测 |
| **M9 分层融合 + TD Beta + 扩 GT** | **✅ 完成** | ADR-010：Fusion(llm/voting/last_wins) · Beta(2,2) 先验 · session GT 扩标 30/30 |
| **M9.5 复查修复 L1–L4** | **✅ 代码完成** | ADR-010 修复记录：veracity 限核心三槽 · 传闻回声过滤 · `cross_user_td.py` · beta_v2 世界态 |
| **Beta 全量 eval** | **✅ 完成（Layer 1–2 only）** | 30/30 · F1=0.822；**禁止**用 beta_v1 报 TD 真值还原（见 `wrongway/02` §2.3） |
| **beta_v2 生成** | **✅ 完成** | 30/30；`world_truth_for(region,week)` |
| **beta_v2 eval + TD 标定** | **✅ 完成** | 30/30 · F1=0.888 · **td_world_truth_accuracy=1.0** · reliability r=+0.258 · Dashboard 已重建 |

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
| 路由 LLM 接入 | `router.py::route_skill` | ✅ |

**11 个 skill_id**：`clarification-probe` · `info-seeking-inference` · `bayesian-tom` · `implicit-user-modeling` · `reactance-biased-statement` · `socratic-probe` · `trap-question` · `info-design-disclosure` · `info-manipulation-bias` · `cognitive-conflict-probe` · `cover-qa`

**验收**：✅ router 输出合法 `skill_id`；✅ 每个专项有触发/禁用/模板；✅ LLM utterance 生成（M7，`invoke_skill`）。

---

## M7 — LangGraph cheatAgent ✅（2026-07-08 完成）

**架构文档**：`decisions/008-cheat-agent-langgraph.md`

```
cheatAgent (LangGraph)          CustomerAgent (LLM simulator)
  ├ load_context                  ├ load_persona + latent GT
  ├ update_user_model             └ compose_reply (honesty=strategy)
  ├ route_skill → SKILL-router (LLM)
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
- [x] Alpha live 部分生成（U001–U007 完成；U008–U010 mock，全量暂缓）
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

## Alpha — 10×5 dataset 🟡（7/10 live）

| 项 | 状态 |
|----|------|
| `ALPHA_PERSONAS` ×10 | ✅ `personas.py` |
| 多 session + 跨 session 记忆 | ✅ `runner.write_dataset` |
| 价格走线 7 周 | ✅ `price_data.PRICE_TRAJECTORY` |
| live 生成 | 🟡 U001–U007 ✅（各 5×20）；U008–U010 mock；全量暂缓 |

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

## M9 — 分层融合 + TD Beta 先验 + 扩 GT ✅（2026-07-09 完成，ADR-010）

| 项 | 实现 |
|----|------|
| 正则覆盖 bug 修复 | `normalize.py` 信任 LLM enum；仅软修「采购积极性 中→中性」（`wrongway/04`） |
| Session Fusion 层 | `analysis/fusion.py`：llm（主口径）/ voting / last_wins 消融三档 |
| TD Beta 先验 | `truth_discovery.py`：Beta(2,2)，单源桶不更新（防自我印证） |
| 扩 GT | `scripts/expand_latent_gt.py`：session 级挖断言 → `session.claims_truth`，30/30 用户 |
| 冒烟验证 | U001/U002/U003 S001 回放 F1 = 1.0 / 1.0 / 1.0（扩 GT + 手工补标后） |

## Beta — 30×5 全量 eval ✅（2026-07-10 完成）

- 命令：`run_benchmark_pipeline.py --preset beta_v1 --phase evaluate --resume`
- 日志：`benchmark/logs/beta_v1_eval_full.log`（35428s COMPLETE）
- 产物：`benchmark/reports/beta_v1_eval.json` · `cross_user_td.json` · `dashboard.html`
- **主指标（150 session, fusion=llm）**：recall **0.862** · precision **0.800** · F1 **0.822** · veracity **0.885**
- **消融**：llm > voting > last_wins（F1 0.822 > 0.806 > 0.773）
- L1–L4 全部已修（ADR-010 修复记录）；**beta_v1 世界态 P0 缺陷**见 `wrongway/02` §2.3——跨用户 TD 干净标定**仅** beta_v2
- **ReCon**：Pearson(deception, honesty) **r=-0.128** (n=150)，弱负相关

## Beta v2 — expand → eval 🟡（2026-07-10 启动）

- 生成：✅ 30/30（`world_truth_for(region,week)`，`memory_beta_v2/`）
- 命令链：
  ```bash
  python scripts/expand_latent_gt.py --dataset benchmark/datasets/beta_v2
  python scripts/run_benchmark_pipeline.py --preset beta_v2 --phase evaluate --resume
  python scripts/cross_user_td.py --preset beta_v2
  python scripts/build_dashboard.py --preset beta_v2
  ```
- 日志：`benchmark/logs/beta_v2_expand.log` · `benchmark/logs/beta_v2_eval.log`
- 验收：`td_world_truth_accuracy` + reliability Pearson（干净标定）

## 旧验收（已作废）

~~pytest 30 passed~~、~~run_tier_b.py Pearson 0.90~~ — 见 `wrongway.md`。
