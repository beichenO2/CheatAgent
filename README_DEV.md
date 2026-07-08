# MarketTruthAgent — Dev

铁矿石智能客服：**Agent 套话采集** + Claim 真伪推断 + 用户信用评估。

> **2026-07-08**：M6–M8 已完成（Skills + LLM 链路 + 冒烟 benchmark）。旧规则模板已删除，见 `wrongway.md`。

## 快速开始

```bash
pip install -e ".[dev,agent]"
pytest test/ -v
python scripts/generate_dataset.py    # 冒烟 3 用户 × 20 轮（含 smoke gate）
python scripts/evaluate_dataset.py    # 评测（GT 仅此处，未过 gate 则 exit 1)
```

### LLM 配置（PolarPrivate 优先）

PolarPrivate 本地代理：`http://127.0.0.1:12790/v1`（vault 须 unlocked）。未设 `MTA_LLM_MODE` 且 health 正常时 **自动 live**。

| 变量 | 说明 |
|------|------|
| `MTA_LLM_MODE` | `mock`（CI）或 `live`；留空则探测 PolarPrivate |
| `POLARPRIVATE_URL` | 默认 `http://127.0.0.1:12790` |
| `MTA_LLM_MODEL` | PolarPrivate QCSA 码，默认 `0001`（Agent） |
| `OPENAI_API_KEY` | PolarPrivate 下可填 `local`（占位） |

```bash
# PolarPrivate 已运行时（推荐）
MTA_LLM_MODE=live MTA_LLM_MODEL=0001 python scripts/generate_dataset.py
python scripts/evaluate_dataset.py   # 输出 claim_f1 / pearson / em_error
```

## 文档（SSoT）

| 文件 | 内容 |
|------|------|
| `PolarSoul.md` | 项目定位 |
| `polaris.json` | 当前状态 |
| `roadmap.md` | M6–M8 路线图 + Alpha 待办 |
| `CheatAgent.md` | 方案/进度（对外汇报） |
| `wrongway.md` | 已废弃路径与教训 |
| `decisions/007-008` | Agent 重建 + LangGraph 架构 |
| `skills/cheat-agent/` | 运行时套话 Skills |
| `套话skill/` | 论文 + 分析 + Skills 源 |

## 目录

```
src/market_truth_agent/
  agents/           cheatAgent + CustomerAgent + simulation + eval
  llm/              mock/live LLM client + prompts
  analysis/         Truth Discovery, claim, ReCon 接入
  recon/            欺骗检测（无 GT 泄漏）
skills/cheat-agent/ 1+N 套话 Skills
benchmark/datasets/ Agent 生成 dataset（smoke_v1）
memory/             L1–L3 持久化（gitignore）
scripts/            generate / evaluate 分离
test/               单元 + Tier A + Agent 冒烟
```

## LangGraph 架构

详见 `decisions/008-cheat-agent-langgraph.md`。M6–M8 已实现；LangGraph 节点划分仍待用户审阅。
