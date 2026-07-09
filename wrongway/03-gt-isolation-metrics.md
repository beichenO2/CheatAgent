# 03 GT 隔离与指标设计

## 3.1 ReCon 分析阶段读取 `persona.honesty`（GT 泄漏，2026-07-08）

**做了什么**：`recon/core.py` 在 deception 计算里直接用 benchmark GT 的 honesty 字段。

**错在哪**：
- 生产环境没有 honesty GT
- 使 Pearson(reliability, honesty) 指标**虚假偏高**
- 典型的 train-test / builder-evaluator 污染

**教训**：ReCon 只能看 **utterance + 可观测行为 + 历史对话**；honesty 仅存在于 dataset JSON，供**离线对照**，不进 inference。

**处置**：已从 `recon/core.py` 移除；ReCon 已接 LLM 按论文复刻。

## 3.2 套话性能指标选错（2026-07-08）

**做了什么**：用 `elicitation_channel=bias_triggered` 占比衡量套话效果。

**错在哪**：claim 也是规则生成的，channel 标签是规则打的，**测的是规则不是 Agent**。

**正确方向**（ADR-007）：
- 话术 **种类数**（distinct skills invoked）
- 话术 **触发次数**（per session / per user）
- 话术 **丰富度**（entropy / skill coverage ratio）
- 这些从 **Agent 元数据**（每轮 `skill_id`）统计，不从 claim 反推
