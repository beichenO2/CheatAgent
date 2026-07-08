# ADR-003: 欺骗检测 — 仅 ReCon，按论文复刻

## 状态
accepted（2026-07-07 修订：弃用 AIDI，ReCon 为唯一方案）

## 背景

分析链路需在单用户/单轮粒度检测欺骗与激励偏差，再汇入 Truth Discovery。

- **AIDI** (ICTAI 2024)：hidden-state probe，77.33% 准确率，**无开源代码** → **不采用**
- **ReCon** (ACL 2024 Findings)：[GitHub](https://github.com/Shenzhi-Wang/recon) 有官方实现 → **唯一方案**

## ReCon 算法摘要（待复刻）

论文：Wang et al., [arXiv:2310.01320](https://arxiv.org/abs/2310.01320)

两阶段 + 两阶视角：

| 阶段 | 视角 | 作用 |
|------|------|------|
| Formulation Contemplation | 一阶：推断他人心理 | 用户知道什么、想隐瞒什么 |
| Refinement Contemplation | 二阶：他人如何看自己 | 用户认为 Agent 意图是什么 |

**特点**：无需 fine-tune；官方代码基于 Avalon/BigTom 评测。

## 决定

### 一期：ReCon prompt 集成（快速可用）

- 借鉴 `Shenzhi-Wang/recon` 的 prompt 结构与思维链格式
- 中文铁矿石场景适配
- 输出结构化 `DeceptionSignal`

### 二期：按论文描述复刻算法（roadmap M3.5）

对照论文 Algorithm / Figure 1，逐步实现：

1. **Formulation**：生成初始 thought + 一阶 perspective transition
2. **Refinement**：polish thought/speech + 二阶 perspective transition
3. **History 累积**：\( H \leftarrow H \cup \{S'_k\} \)（论文 Eq.7）
4. **与 Avalon 解耦**：抽取 ReCon 核心循环，嵌入分析/交互链路

**验收**：在 Tier A BigTom 子集上复现论文趋势（ReCon > CoT baseline）；在 Tier B 上 `deception_score` 与 `persona.honesty` 负相关。

### 分析链路 — 欺骗检测模块

```python
def analyze_turn(turn, user_context, history) -> DeceptionSignal:
    # ReCon 两阶段（唯一路径）
    recon = recon_analyze(
        formulation={"first_order": "推断用户隐藏状态与动机"},
        refinement={"second_order": "用户如何解读 Agent 提问意图"},
        history=history,
    )
    incentive_risk = check_stance_risk(turn, user_context.position)
    evidence = score_verifiability(turn)  # VA 可验证性
    
    return DeceptionSignal(
        deception_score=recon.deception_score,
        reasoning=recon.thought_chain,
        incentive_risk=incentive_risk,
        evidence_strength=evidence,
    )
```

### 交互链路 — ReCon 话术优化

同一 ReCon 核心，prompt 目标不同：
- 分析侧：判断用户是否说谎
- 交互侧：二阶视角优化下一句话术

## 与 Truth Discovery 衔接

`deception_score` 是 **claim 的可选权重信号**，不直接判真伪：

```
claim_score(c) =
  w1 * reliability(source, domain, time)
+ w2 * evidence_strength
+ w3 * independence_score
+ w4 * external_consistency      # 仅 price_trajectory
- w5 * incentive_risk
- w6 * deception_score           # ReCon
```

## 不做

- ~~AIDI hidden-state probe~~ — 无代码、需 GPU、API 模型不可用
- ~~lie-detector probe 训练~~ — 仅 Tier A 可选 baseline 对比，非主路径

## 后果

- 分析/交互共用 `src/recon/` 模块，两套 prompt 模板
- roadmap 增加 **M3.5 ReCon 论文复刻** 里程碑

## 参考

- ReCon 代码：https://github.com/Shenzhi-Wang/recon
- 论文：https://doi.org/10.18653/v1/2024.findings-acl.591
- AIDI（仅文献参考，不实现）：https://doi.org/10.1109/ICTAI62512.2024.00102
