# Benchmark Reports

| 报告 | 路径 | 在线文档 |
|------|------|----------|
| smoke_v1 评测 | `smoke_v1_eval.json` | https://docs.qq.com/aio/DZEZ2YU9zQUdSREtY |
| beta_v1 评测（跑完后） | `beta_v1_eval.json` | — |

## 运行 Beta 全量 pipeline

```bash
# 实时日志 + 断点续跑
./scripts/run_beta_pipeline.sh beta_v1

# 或手动
PYTHONUNBUFFERED=1 POLARPRIVATE_URL=http://127.0.0.1:12790 \
  MTA_LLM_MODE=live MTA_LLM_MODEL=0001 MTA_NORMALIZE_MODEL=qwen3.7-plus \
  python scripts/run_benchmark_pipeline.py --preset beta_v1 --resume
```

规格：**30 用户 × 5 session × 20 轮 = 3000 轮对话**

日志：`benchmark/logs/beta_v1_pipeline.log`
