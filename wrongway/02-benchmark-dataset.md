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
