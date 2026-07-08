# ADR-007: 推倒重来 — Agent 驱动的 Dataset 与评测

## 状态
accepted（2026-07-08，**supersedes ADR-004 交互实现、ADR-001 Tier B 生成流程、ADR-006 Tier B 门禁**）

## 背景

YOLO 阶段交付的规则模板 + 硬编码对话被确认**不可用**（详见 `wrongway.md`）：

- 无 LLM → 无法代表真实套话场景
- GT 泄漏（ReCon 读 honesty）→ 指标虚假
- Dataset 规模与多 session 时间结构不满足要求
- 套话性能指标（bias_triggered）无测评价值

## 决定

### 1. 删除机械化交互与 Tier B 实现

移除 `interaction/` 模板 FSM、规则 `dialogue_simulator`、旧 Tier B evaluator。分析链路骨架保留；M8 冒烟 dataset 已接入 Agent 产出。

### 2. Dataset = Agent 对抗生成

```
CustomerAgent (LLM)  ←→  cheatAgent (LangGraph + Skills)
         │                        │
         └──── transcript ────────┘
                    +
         program GT (latent, persona metadata)
                    ↓
         benchmark/datasets/{version}/
```

- **GT 写入 dataset JSON**，不参与 Agent prompt（CustomerAgent 读 latent 决定「真实世界」；cheatAgent **不读** honesty）
- **生成脚本**与**评测脚本**分目录、分入口

### 3. Persona 语义修正

| 字段 | 旧含义 | 新含义 |
|------|--------|--------|
| `honesty` | 说真话概率 | **信息披露策略参数**（0=完全按头寸利益操纵，1=倾向真实披露）；≠ 每句假话 |
| `resistance` | 无 | **对话术抵抗能力**（心理反抗阈值） |
| `position` | long | 不变，已知头寸 |

评测时 honesty 仅用于 **离线 Pearson 对照**，分析链路 **严禁读取**。

### 4. Dataset 规模（分阶段）

| 阶段 | 规格 | 用途 |
|------|------|------|
| **冒烟** | 3 用户 × 20 轮 × 1 session | 验证 Agent 链路可跑通 |
| **Alpha** | 10 用户 × 5 session × ≥20 轮 | 初步 ablation |
| **Beta** | 30 用户 × 5 session × ≥20 轮，横跨 5 个月 | 完整 Tier B |

每 session 绑定：`session_date`、`week`、`price_snapshot`（从 `price_trajectory` 按日期索引）。

### 5. 套话性能指标（替代 bias_triggered）

从 **cheatAgent 元数据**统计，不依赖 claim：

| 指标 | 定义 |
|------|------|
| `skill_kind_count` | 会话内调用的 distinct skill_id 数 |
| `skill_invoke_count` | 套话 skill 总触发次数 |
| `skill_richness` | `-Σ p_i log p_i` 或 `kind_count / available_skills` |
| `skill_coverage` | 使用的 skill 占已注册 skill 比例 |

### 6. 分析链路 GT 隔离

```
✅ 允许读 GT：eval/*.py（离线评测）
❌ 禁止读 GT：recon/*, analysis/pipeline.py, cheatAgent 运行时
```

ReCon deception 仅基于 utterance 可观测特征 + 对话历史。

### 7. 套话 Skills（M6 ✅ 2026-07-08 完成）

基于 `Readme.md` §90–197 心理学与对话策略研究，已凝练并接入：

```
skills/cheat-agent/
  SKILL-router.md          # 1：路由 — 规则决策树（非 LLM 路由）
  SKILL-*.md × 11         # N：11 专项 + cover-qa
```

材料与论文见 `套话skill/`。`route_skill` + `invoke_skill`（LLM）已接入 LangGraph（ADR-008）。

## 后果

- ADR-004 标记 superseded
- ADR-001 Tier B 生成/评测章节 superseded（Tier A 组件 benchmark 保留）
- 旧 Tier B 门禁数字作废
- 新增 LangGraph + LLM 依赖（`pyproject.toml` `[agent]` extra）

## 参考

- `wrongway.md`
- 用户决策：2026-07-08 会话
- `Readme.md` §心理学、§陷阱问题
