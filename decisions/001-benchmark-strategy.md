# ADR-001: Benchmark 策略 — Tier A + Tier B 两层

## 状态
accepted（Tier A 有效）；**Tier B 生成/评测流程 superseded by ADR-007**（2026-07-08）

## 背景

项目核心问题：多个用户就同一市场指标给出冲突回答，如何判断真伪并评估来源可信度。

**2026-07-08 修订**：旧 Tier B 规则模板实现废弃（见 `wrongway.md`）。Tier B 改为 **Agent 对抗生成 + Agent 评测 pipeline**。

Benchmark 必须满足：
1. 有**可验证的 ground truth**（程序 latent state，非 LLM 自评）
2. 覆盖双链路（交互采集 + 分析推断）
3. **生成与评测代码分离**，分析链路不读 GT

## 决定

```
Tier A  借用邻域数据集  →  组件级验证（Truth Discovery / ReCon / Claim 抽取）
Tier B  Agent 长对话 + 程序 GT  →  主端到端评测
```

---

### Tier A — 组件 Benchmark（不变）

验证**单个模块**，不声称代表铁矿石端到端效果。

| 模块 | 数据集 | 测什么 |
|------|--------|--------|
| Truth Discovery | FaitCrowd Game / SFV | 冲突聚合、来源 expertise |
| Truth Discovery 压力测试 | TruthFinder 合成 | 可控 conflict rate |
| Claim 验证方法论 | DialFact 子集 | verifiable claim 检测 |
| ReCon 推理 | BigTom + [Shenzhi-Wang/recon](https://github.com/Shenzhi-Wang/recon) | 一阶/二阶视角 |

---

### Tier B — Agent 驱动 Benchmark（ADR-007 取代旧流程）

#### 规模（分阶段）

| 阶段 | 规格 |
|------|------|
| 冒烟 | 3 用户 × 20 轮 × 1 session |
| Alpha | 10 用户 × 5 session × ≥20 轮 |
| **Beta** | **30 用户 × 5 session × ≥20 轮，横跨 5 个月** |

#### 生成（Agent）

1. 程序写入 persona + latent GT → `benchmark/datasets/{version}/`
2. **CustomerAgent (LLM)** ↔ **cheatAgent (LangGraph + Skills)** 生成 transcript
3. 每轮记录 `skill_id` 等 agent metadata

#### 评测（分离入口）

| 类别 | 指标 |
|------|------|
| **套话** | skill_kind_count, skill_invoke_count, skill_richness, skill_coverage |
| **分析** | Claim F1, EM vs MV, Pearson(r_u, honesty) — honesty **仅评测脚本** |

~~bias_triggered claim 比例~~ — 废弃（规则闭环无意义）

#### 价格

- 5 个月 `price_trajectory`，按 **session_date** 索引注入 Agent prompt 与分析 `external_consistency`

---

## 不做

- ~~规则模板对话冒充 LLM benchmark~~
- ~~Tier C 专家标注~~
- ~~ReCon 读取 persona.honesty~~

## 后果

- 旧 `benchmark/tier_b/scenarios/` 30 JSON 删除
- 新 dataset 路径：`benchmark/datasets/smoke_v1/` → `beta_v1/`
- 入口：`scripts/generate_dataset.py` / `scripts/evaluate_dataset.py`

## 参考

- ADR-007, ADR-008
- `wrongway.md`
