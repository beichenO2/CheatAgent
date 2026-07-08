# MarketTruthAgent — Dev

铁矿石智能客服：**Agent 套话采集** + Claim 真伪推断 + 用户信用评估。

> ⚠ **2026-07-08 重建中**：旧规则模板实现已删除，见 `wrongway.md`。

## 快速开始

```bash
pip install -e ".[dev,agent]"
pytest test/ -v
python scripts/generate_dataset.py    # 冒烟 3 用户 × 20 轮（含 smoke gate）
python scripts/evaluate_dataset.py    # 评测（GT 仅此处，未过 gate 则 exit 1)
```

### LLM 配置（M7）

| 变量 | 说明 |
|------|------|
| `MTA_LLM_MODE` | `mock`（默认，pytest/离线）或 `live` |
| `OPENAI_API_KEY` / `POLARPRIVATE_API_KEY` | live 模式密钥 |
| `OPENAI_BASE_URL` / `POLARPRIVATE_BASE_URL` | PolarPrivate 等兼容端点 |
| `MTA_LLM_MODEL` | 默认 `gpt-4o-mini` |

```bash
export MTA_LLM_MODE=live
export OPENAI_API_KEY=...
python scripts/generate_dataset.py
```

## 文档（SSoT）

| 文件 | 内容 |
|------|------|
| `PolarSoul.md` | 项目定位 |
| `polaris.json` | 当前状态 |
| `roadmap.md` | M6–M8 路线图 |
| `wrongway.md` | 已废弃路径与教训 |
| `decisions/007-008` | Agent 重建 + LangGraph 架构 |
| `skills/cheat-agent/` | 套话 Skills（M6 用户做） |

## 目录

```
src/market_truth_agent/
  agents/           cheatAgent + CustomerAgent + simulation
  analysis/         Truth Discovery, claim, ReCon 接入
  recon/            欺骗检测（无 GT 泄漏）
skills/cheat-agent/ 1+N 套话 Skills
benchmark/datasets/ Agent 生成 dataset
scripts/            generate / evaluate 分离
test/               单元 + Tier A + Agent 冒烟
```

## LangGraph 架构

详见 `decisions/008-cheat-agent-langgraph.md` — **待用户审阅修改**。
