# Wrongway — 已废弃路径与教训（分类索引）

> 记录走偏的实现与踩过的坑，**禁止再沿用**。新坑必须当天归档到对应分类文件，不再堆回单文件。
> 原单文件 `wrongway.md` 已于 2026-07-09 拆分至此。

## 分类索引

| 文件 | 主题 | 收录教训 |
|------|------|----------|
| [01-agent-design.md](01-agent-design.md) | 架构与 Agent 设计 | 规则模板冒充智能 Agent；ADR-004「炼化融合」不建 Skill |
| [02-benchmark-dataset.md](02-benchmark-dataset.md) | Benchmark 与数据集 | 规则闭环冒充 Tier B；数据集规模不足；**beta_v1 世界态按 user_id 独立随机（P0）** |
| [03-gt-isolation-metrics.md](03-gt-isolation-metrics.md) | GT 隔离与指标 | ReCon 读 honesty GT 泄漏；bias_triggered 指标选错 |
| [04-analysis-pipeline.md](04-analysis-pipeline.md) | 分析链路 | **正则覆盖 LLM 输出**；last-wins 聚合与追问逻辑错位 |
| [05-llm-ops.md](05-llm-ops.md) | LLM 与工程运维 | VL 模型误用；静默长任务；manifest 覆盖；checkpoint 序列化崩溃；长链路无重试 |
| [06-external-data.md](06-external-data.md) | 外部数据 | 价格数据形同虚设 |
| [07-persona-prompt.md](07-persona-prompt.md) | 身份与 Prompt | 情报客服被写成贸易商口吻 |

## 使用规则

1. 动手前先扫本目录，确认不重犯
2. 新坑记录格式：**做了什么 / 错在哪 / 教训 / 处置（含修复 commit 或文件）**
3. 一个坑只归一个分类；跨类时主分类收录、次分类一行引用
