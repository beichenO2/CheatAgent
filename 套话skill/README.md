# 套话 Skill 体系（1 路由 + 11 专项）

凝练自项目 `Readme.md` §90–197。

## 当前状态（2026-07-08）

| 阶段 | 状态 | 说明 |
|------|------|------|
| ① 论文采集 | ✅ | 15 篇 PDF，`reference/papers/` 已整理（无 stub） |
| ② AutoOffice 转 md | ✅ | 15 篇 → `reference/markdown/` |
| ③ 10 方向分析 | ✅ | `analysis/*.md` |
| ④ 11 专项 Skills | ✅ | 10 研究线 + `cover-qa` → `skills/SKILL-*.md` |
| ⑤ 路由 Skill | ✅ | `skills/SKILL-router.md` |
| ⑥ cheatAgent 集成 | ✅ | `route_skill` 规则路由 + `invoke_skill` LLM（M7） |
| ⑦ 同步到 cheat-agent | ✅ | `skills/cheat-agent/` 已同步全部 12 个 SKILL 文件 |

**下一步（Alpha）**：live LLM 扩至 10 用户 × 5 session；claim F1 / Pearson 离线对照。

## 目录结构

```
套话skill/
├── reference/
│   ├── papers/          # 15 篇 PDF
│   ├── markdown/        # AutoOffice to-markdown 产出（15 篇）
│   └── papers-manifest.json
├── analysis/            # 10 研究方向分析
├── skills/
│   ├── SKILL-router.md           # 1 路由
│   └── SKILL-*.md                # 11 专项
└── scripts/
    ├── download_papers.sh
    └── download_via_safari.sh
```

## 10 个研究方向 → 11 个专项 Skill

| # | 研究方向 | skill_id | 核心论文 |
|---|---------|----------|---------|
| 1 | 澄清提问 | `clarification-probe` | ProductAgent |
| 2 | 信息寻求推断 | `info-seeking-inference` | Nelson 2014, Rothe 2018 |
| 3 | 贝叶斯心智理论 | `bayesian-tom` | Rothe 2018 |
| 4 | 隐式用户建模 | `implicit-user-modeling` | Farshidi SLR 2024 |
| 5 | 心理反抗 | `reactance-biased-statement` | PRT + prt-politeness-arxiv |
| 6 | 苏格拉底法 | `socratic-probe` | AVERT, IntelliChain, Socratic Mind |
| 7 | 陷阱问题 | `trap-question` | WWW 2018, Interspeech 2015 |
| 8 | 信息设计 | `info-design-disclosure` | Kolotilin 2018 |
| 9 | 信息操纵 | `info-manipulation-bias` | IMT2 框架（分析文档） |
| 10 | 认知冲突 | `cognitive-conflict-probe` | Safety Gap 2026, Zero-Shot Socratic |
| — | 高抵抗恢复 | `cover-qa` | 正常问答掩护 reciprocity |

## 论文清单（15 篇）

| 文件 | 来源 | 覆盖方向 |
|------|------|---------|
| productagent.pdf | ACL Anthology | 澄清提问 |
| children-info-search.pdf | 作者页 | 信息寻求 |
| do-people-ask-good-questions.pdf | Princeton | 贝叶斯 ToM |
| user-intent-slreview.pdf | arXiv | 隐式建模 |
| prt-politeness-arxiv.pdf | arXiv | 心理反抗 |
| avert.pdf | IEEE（手动） | 苏格拉底 |
| intellichain.pdf | arXiv | 苏格拉底 |
| socratic-mind.pdf | arXiv | 苏格拉底 |
| socratic-mind-impact.pdf | arXiv | 苏格拉底 |
| zero-shot-socratic.pdf | 作者页 | 苏格拉底 / 认知冲突 |
| socratic-hard-problem.pdf | Frontiers | 认知冲突 |
| socratic-virtue-ethics.pdf | AAAI OJS | 苏格拉底 |
| crowdsourcing-trapping.pdf | DTG | 陷阱问题 |
| trapping-interspeech-2015.pdf | ISCA | 陷阱问题 |
| optimal-info-disclosure.pdf | 作者页 | 信息设计 |

**刻意未收录**（付费墙，已有替代或分析文档覆盖）：Freedom-prompting、Divide and Inform、Deceptively Dodging。

重新转 md：

```bash
cd /Users/mac/Polarisor/AutoOffice
node dist/cli.js to-markdown -i 套话skill/reference/papers -o 套话skill/reference/markdown
```

## 使用方式

1. `route_skill` 读 `SKILL-router.md` → 输出 `skill_id` + `phase`
2. `invoke_skill` 读 `SKILL-{skill_id}.md` → 生成 utterance（M7）
3. 详细机理与扩展模板见 `analysis/{direction}.md`

## 与 cheatAgent 集成

- 运行时路径：`skills/cheat-agent/`（与 `套话skill/skills/` 内容同步）
- `graph.py::route_skill` — ✅ 规则决策树
- `graph.py::invoke_skill` — ⏳ 占位，待 M7 接 LLM
