# ADR-006: QA 测试策略 — TDD 驱动全栈交付

## 状态
accepted（单元/集成/Tier A 仍有效）；**Tier B 门禁 superseded by ADR-007**（2026-07-08）

## 背景

旧 Tier B 门禁（F1=0.65, Pearson=0.90 等）基于规则模板闭环，**已作废**。见 `wrongway.md`。

## 测试金字塔（更新）

```
        ┌─────────────┐
        │  Agent E2E  │  test/agents/ — 冒烟 dataset 生成+评测
        ├─────────────┤
        │  Benchmark  │  test/benchmark/test_tier_a.py
        ├─────────────┤
        │ Integration │  test/integration/test_analysis_pipeline.py
        ├─────────────┤
        │    Unit     │  test/unit/ — ontology, recon, truth_discovery, tactic_metrics
        └─────────────┘
```

## GT 隔离测试（新增）

| ID | 用例 | 断言 |
|----|------|------|
| T-050 | ReCon 不读 honesty | `recon/core.py` 无 `persona.honesty` 引用 |
| T-051 | 分析 pipeline 不依赖 GT 泄漏 | deception 与 honesty 无单调绑定 |

## M8 冒烟门禁

| ID | 用例 | 断言 |
|----|------|------|
| T-060 | 生成 3 用户 dataset | manifest.json 存在，每用户 meta.json |
| T-061 | 每用户 ≥20 轮 | turn_count ≥ 20 |
| T-062 | agent metadata 有 skill_id | skill_invoke_count > 0 |
| T-063 | tactic_metrics 可算 | kind_count, richness 非 NaN |

## 套话性能（替代 T-034 bias_trigger）

| ID | 用例 | 断言 |
|----|------|------|
| T-070 | skill_kind_count | ≥ 1 per session |
| T-071 | skill_richness | 可计算 |

~~T-014 单用户 Pearson~~ — 仅多用户 eval 脚本 + 离线 GT 对照

## 依赖

- **必须 LLM**（Agent 阶段）：`pip install -e ".[agent]"`
- Tier A 组件测试仍可离线

## 参考

- ADR-007
- `wrongway.md`
