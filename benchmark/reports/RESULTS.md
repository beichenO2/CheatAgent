# MarketTruthAgent 评测成果摘要

> 最后更新：2026-07-10 19:17  
> **一句话**：抽槽和核心真值还原都很好；共享世界态下 TD 对 world_truth 全对；用户可信度与 honesty 已能测出正相关（beta_v1 几乎测不出）。

---

## beta_v2（Layer 3，跨用户 TD 真值还原）✅

**规格**：30 用户 × 5 session × 20 轮 · `world_truth_for(region, week)` 共享世界态 · PolarPrivate live · Normalize `qwen3.7-plus` · Fusion 主口径 `llm`

### 用户内（抽取 + 融合）

| 指标 | 值 |
|------|-----|
| slot recall / precision | **0.920** / **0.872** |
| slot F1（fusion=llm） | **0.888** |
| fusion 消融 F1 | llm **0.888** > voting 0.854 > last_wins 0.819 |
| bucket veracity（核心三槽 × world_truth） | **0.989** |
| claims | 3897 |
| escalation_rate | 0.354 |
| recon_honesty Pearson | r = −0.099 (n=150) |

### 跨用户 TD（主验收）

| 指标 | 值 | 含义 |
|------|-----|------|
| **td_world_truth_accuracy** | **1.0**（45 桶） | TD vs 共享 world_truth——**本次最关键验收** |
| reliability Pearson | **r = 0.258**（n=30） | TD 估可信度 vs honesty；方向正确（beta_v1 为 −0.097） |
| td_union_gt_alignment | 0.938（核心三槽 **1.0**） | TD vs 各 session GT 并集 |
| td_plurality_gt_accuracy | 0.854（核心三槽 **1.0**） | TD vs 桶内 GT 众数 |

**产物**：`beta_v2_eval.json` · `beta_v2/cross_user_td.json` · [dashboard.html](beta_v2/dashboard.html)  
**本地打开**：http://127.0.0.1:8931/beta_v2/dashboard.html

---

## beta_v1（Layer 1–2，抽取 + 用户内融合）✅

**规格**：30 用户 × 5 session × 20 轮 · PolarPrivate live · Normalize `qwen3.7-plus`

| 指标 | 值 |
|------|-----|
| slot F1（fusion=llm） | **0.822** |
| recall / precision | 0.862 / 0.800 |
| veracity（核心三槽） | 0.885 |
| fusion 消融 F1 | llm 0.822 > voting 0.806 > last_wins 0.773 |
| recon_honesty Pearson | r = −0.128 (n=150) |
| td_union_gt_alignment | 60.1% (n=654) |
| td_plurality_gt_accuracy | 74.7% (95 桶) |
| reliability Pearson（诊断） | r = −0.097 (n=30) |

**产物**：`beta_v1_eval.json` · `cross_user_td.json` · [dashboard.html](beta_v1/dashboard.html) · [在线报告](https://docs.qq.com/aio/DZHhoQVhNRVJSR1JM)

**限制**：世界态按 `user_id` 独立随机（`wrongway/02` §2.3）→ **禁止**用 beta_v1 报 `td_world_truth_accuracy`。

---

## beta_v1 → beta_v2 对比（为何要重生数据集）

| 项 | beta_v1 | beta_v2 |
|----|---------|---------|
| 世界态 | 每用户独立 latent | `(region, week)` 共享 `world_truth` |
| slot F1 (llm) | 0.822 | **0.888** |
| veracity | 0.885 | **0.989** |
| td_world_truth_accuracy | 不可验收 | **1.0** |
| reliability Pearson | −0.097（测不出） | **+0.258**（方向正确） |
