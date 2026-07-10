# 02 Benchmark 与数据集

## 2.1 规则模拟对话冒充 Tier B Benchmark（2026-07-08）

**做了什么**：`dialogue_simulator.py` 用 `HONEST_TEMPLATES` / `DECEPTIVE_TEMPLATES` 按 `honesty` 阈值拼句子；claim 用关键词规则抽取。

**错在哪**：
- ADR-001 写「LLM 生成长对话」，实现是硬编码模板——**文档与代码严重不符**
- 生成与评测同一套规则闭环，指标自洽但**零外部效度**
- `bias_triggered` 比例测的是模板触发 rebuttal 关键词，不是套话能力
- 宣称 F1=0.65、Pearson=0.90 等数字**没有评测意义**

**教训**：
- Dataset 构建 = **CustomerAgent（LLM）× cheatAgent（LLM）** 对抗生成
- GT（latent truth、honesty）只写入 dataset metadata，**分析/评测代码严禁读取**
- 生成 pipeline 与评测 pipeline **代码分离**

**处置**：删除 `dialogue_simulator.py`、`evaluator.py`、`multi_user_eval.py`、`scripts/run_tier_b.py`、旧 30 scenario JSON。

## 2.2 Dataset 规模严重不足（2026-07-08）

**做了什么**：30 用户 × 1 段对话 × 16 轮 × 单周 `2026-W27`。

**错在哪**：不满足业务要求（每用户 ≥100 轮、5 次会话、横跨 5 个月、价格按 session 介入）。

**教训**：分阶段交付——先 **冒烟 3 用户 × 20 轮**，再 Alpha 10×5，再 Beta 30×5×20。

## 2.3 beta_v1 世界态按 user_id 独立随机、未按 (region, week) 共享（P0，2026-07-08 引入 / 2026-07-09 发现 / 2026-07-10 归档）

**做了什么**：Beta 30×5 全量生成使用 `SimulationRunner(world_state=False)`（preset `beta_v1`）。
CustomerAgent 的 latent GT 来自 `latent_for_persona(persona)`：

```python
# runner.py — beta_v1 路径（错误）
variant = TRUTH_VARIANTS[hash(persona.user_id) % len(TRUTH_VARIANTS)]
```

每个用户按 **user_id 哈希** 固定分到 8 种市场盘之一；**同一用户 5 个 session 共用同一份 latent**（函数不接 `week`）；
**不同用户 latent 互相独立**，未约定「同 region、同 week 共享一份世界真值」。

**错在哪**（业务语义 + 评测语义双重错误）：

1. **违反真实场景**：同一周、同一港口，30 个厂长/贸易员/仓库负责人面对的是**同一个市场**，不是 30 个平行宇宙。诚实用户之间不应因「世界不同」而冲突。
2. **违反 TD 前提**：Truth Discovery 假设每个桶 `(week, region, indicator)` 有**唯一世界真值**，冲突来自来源撒谎或误差。beta_v1 下即使全员 honesty=1.0，同桶 GT 仍互相矛盾。
3. **实现上比「忘了对齐」更蠢**：`latent_for_persona` **根本不读 week**——5 次跨月 session 市场盘不变，与「横跨 5 个月、价格走线变化」的 Benchmark 叙事自相矛盾。
4. **规模化时未做跨用户一致性门禁**：冒烟 3 用户 × 1 session 看不出；扩到 30 用户后才暴露（ADR-010 L2 复查：青岛港 W09 港存 honest latent = 中/高/低 混杂）。

**实测证据**（`benchmark/datasets/beta_v1`，青岛港 · 2026-W09 · 港存）：

| 用户 | honesty | latent 港存 |
|------|---------|-------------|
| U001 | 0.20 | 中 |
| U002 | 0.23 | **高** |
| U005 | 0.30 | **低** |
| U007 | 0.36 | **高** |
| … | … | 15 用户：高 10 / 中 3 / 低 2 |

**影响**（什么废了、什么还能用）：

| 仍有效（beta_v1） | 无效或仅诊断（beta_v1） |
|-------------------|-------------------------|
| 用户内抽取 + LLM 融合（slot F1 ≈ 0.82） | `td_world_truth_accuracy`（无共享 world_truth） |
| 套话 skill 触发与对话质量 | reliability 与 honesty 的**干净** Pearson 标定 |
| ReCon 弱信号（方向性） | 「TD 能否还原市场真相」的结论 |
| `td_union_gt_alignment`（折中：GT 并集，见 ADR-010） | 把 beta_v1 cross-user 数字当最终验收 |

**根因（为什么会犯）**：

- 从 smoke/alpha 单用户路径直接放大，**只验证了「每人对话能生成」**，未验证「多人同桶世界一致」。
- `latent_for_persona` 是早期方便给每人不同盘面的快捷函数，扩 Beta 时**未替换**为 `world_truth_for(region, week)`。
- 文档写了「横跨 5 月、多源 truth discovery」，生成代码**未实现**共享世界态——文档与生成语义脱节。

**教训（防再犯检查清单）**：

生成新 preset 或扩数据集规模前，**必须**逐项确认：

- [ ] latent / `world_truth` 是否按 **`(region, week)`** 键共享，而非 `user_id` 独立？
- [ ] 同桶是否存在**跨用户一致性断言**（脚本门禁：同 region+week 的 `session.world_truth` 全库唯一）？
- [ ] 跨月 session 的 latent 是否**随 week 变**（若业务要求市场演化）？
- [ ] 指标分层：用户内（抽取/融合）与用户间（TD）是否用**不同数据集 preset** 验收？
- [ ] 规模从 3→30 时，是否跑**跨用户桶冲突率**冒烟（honesty=1 子集不应大量冲突）？

**处置**：

| 项 | 状态 |
|----|------|
| 归档本教训 | ✅ `wrongway/02` §2.3 |
| 修复实现 | ✅ `world_truth_for(region, week)` + `SimulationRunner(world_state=True)` → preset **`beta_v2`** |
| beta_v2 生成 30×5×20 | ✅ 2026-07-09（`memory_beta_v2/` 隔离，防继承 beta_v1 画像） |
| beta_v2 expand → eval → cross_user_td | ❌ **待跑**（`td_world_truth_accuracy` 在此验收） |
| beta_v1 定位 | **仅** Layer 1–2（抽取 + 用户内融合）；禁止再报「TD 还原市场真相」 |
| 代码注释 | `latent_for_persona` 保留供 smoke/alpha 历史兼容，**禁止**用于新 Beta preset |

**正确路径（beta_v2）**：

```python
# runner.py — beta_v2 路径（正确）
digest = hashlib.md5(f"{region}|{week}".encode()).hexdigest()
variant = TRUTH_VARIANTS[int(digest, 16) % len(TRUTH_VARIANTS)]
# 同 region+week 全用户共享；honesty 只决定报真报假
```

**交叉引用**：ADR-010 L2 · `decisions/010-fusion-td-beta-gt-expand.md` · `runner.py::world_truth_for`
