# Benchmark Reports

> **成果摘要**：[RESULTS.md](RESULTS.md)（beta_v1 ✅ · **beta_v2 ✅**）

| 报告 | 路径 | 在线文档 |
|------|------|----------|
| smoke_v1 评测 | `smoke_v1_eval.json` | https://docs.qq.com/aio/DZEZ2YU9zQUdSREtY |
| **beta_v1 全量评测** | `beta_v1_eval.json` | https://docs.qq.com/aio/DZHhoQVhNRVJSR1JM |
| cross-user TD（诊断） | `beta_v1/cross_user_td.json` | — |
| Dashboard（beta_v1） | `beta_v1/dashboard.html` | 本地双击 / http://127.0.0.1:8931/beta_v1/dashboard.html |
| **beta_v2 全量评测** | `beta_v2_eval.json` | — |
| cross-user TD（验收） | `beta_v2/cross_user_td.json` | — |
| **Dashboard（beta_v2）** | `beta_v2/dashboard.html` | http://127.0.0.1:8931/beta_v2/dashboard.html |

## 一句话结论（2026-07-10）

抽槽和核心真值还原都很好；共享世界态下 TD 对 world_truth 全对；用户可信度与 honesty 已能测出正相关（beta_v1 几乎测不出）。

## beta_v2 验收摘要（2026-07-10 19:17）

- **规模**：30 用户 × 5 session × 20 轮 = 150 session，3897 claims
- **主口径 fusion=llm**：recall **0.920** · precision **0.872** · F1 **0.888** · veracity **0.989**
- **消融 F1**：llm 0.888 > voting 0.854 > last_wins 0.819
- **td_world_truth_accuracy**：**1.0**（45 桶）——Layer 3 主验收通过
- **reliability Pearson**：**r=+0.258**（n=30）
- **union / plurality**：alignment 0.938 · plurality 0.854（核心三槽均为 1.0）
- **重建 Dashboard**：`python scripts/build_dashboard.py --preset beta_v2`

## beta_v1 验收摘要（2026-07-10）

- **规模**：30 用户 × 5 session × 20 轮 = 150 session，4068 claims
- **主口径 fusion=llm**：recall **0.862** · precision **0.800** · F1 **0.822** · veracity **0.885**
- **消融 F1**：llm 0.822 > voting 0.806 > last_wins 0.773
- **cross-user TD**：Pearson(reliability, honesty) **r=-0.097** (n=30)，beta_v1 仅诊断
- **⚠️ beta_v1 世界态缺陷**：`wrongway/02-benchmark-dataset.md` §2.3 — 禁止用 beta_v1 报 `td_world_truth_accuracy`

## 运行 Beta 全量 pipeline

```bash
# 实时日志 + 断点续跑
./scripts/run_beta_pipeline.sh beta_v2

# 或手动
PYTHONUNBUFFERED=1 POLARPRIVATE_URL=http://127.0.0.1:12790 \
  MTA_LLM_MODE=live MTA_LLM_MODEL=0001 MTA_NORMALIZE_MODEL=qwen3.7-plus \
  python scripts/run_benchmark_pipeline.py --preset beta_v2 --phase evaluate --resume
python scripts/cross_user_td.py --preset beta_v2
python scripts/build_dashboard.py --preset beta_v2
```

规格：**30 用户 × 5 session × 20 轮 = 3000 轮对话**

日志：`benchmark/logs/beta_v2_eval.log` · `benchmark/logs/beta_v2_pipeline.log`
