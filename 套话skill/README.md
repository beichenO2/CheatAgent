# 套话 Skill 体系（1 路由 + 10 专项）

凝练自项目 `Readme.md` §90–197，工作流五步法已完成。

## 目录结构

```
套话skill/
├── reference/
│   ├── papers/          # 原始 PDF / stub
│   ├── markdown/        # AutoOffice to-markdown 产出
│   └── papers-manifest.json
├── analysis/            # N=10 研究方向分析（subagent 产出）
├── skills/
│   ├── SKILL-router.md           # 1 路由
│   └── SKILL-*.md                # 10 专项
└── scripts/download_papers.sh
```

## 10 个研究方向 → 10 个专项 Skill

| # | 研究方向 | skill_id | 核心论文 |
|---|---------|----------|---------|
| 1 | 澄清提问 | `clarification-probe` | ProductAgent (EMNLP 2025) |
| 2 | 信息寻求推断 | `info-seeking-inference` | Nelson 2014, Rothe 2018 |
| 3 | 贝叶斯心智理论 | `bayesian-tom` | Rothe 2018 |
| 4 | 隐式用户建模 | `implicit-user-modeling` | Farshidi SLR 2024 |
| 5 | 心理反抗 | `reactance-biased-statement` | Brehm PRT, Richards 2021 |
| 6 | 苏格拉底法 | `socratic-probe` | AVERT, IntelliChain, Socratic Mind |
| 7 | 陷阱问题 | `trap-question` | Jiménez WWW 2018 |
| 8 | 信息设计 | `info-design-disclosure` | Kolotilin 2018, Divide and Inform |
| 9 | 信息操纵 | `info-manipulation-bias` | Clementson 2018, IMT2 |
| 10 | 认知冲突 | `cognitive-conflict-probe` | Safety Gap 2026, Zero-Shot Socratic |

## 论文下载状态

- **已下载 PDF（10 篇）**：productagent, children-info-search, do-people-ask-good-questions, user-intent-slreview, intellichain, optimal-info-disclosure, socratic-virtue-ethics, socratic-mind-impact, socratic-hard-problem, zero-shot-socratic（部分为 stub）
- **stub 替代（6 篇）**：freedom-prompting-reactance, prt-politeness, avert, socratic-mind, crowdsourcing-trapping, divide-and-inform, deceptively-dodging（出版商 paywall/403）

## 使用方式

1. `route_skill` 读 `skills/SKILL-router.md` → 输出 `skill_id` + `phase`
2. `invoke_skill` 读 `skills/SKILL-{skill_id}.md` → 生成 utterance
3. 详细机理与扩展模板见 `analysis/{direction}.md`

## 与 cheatAgent 集成

可将 `套话skill/skills/` 复制或软链到 `skills/cheat-agent/`，替换占位 `SKILL-router.md`。
