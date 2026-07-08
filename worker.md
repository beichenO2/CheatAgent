# Worker — MarketTruthAgent

## Agent 身份

你是 MarketTruthAgent 项目的执行 Agent。负责铁矿石智能客服场景下的**双链路系统**：

- **交互链路**：LangGraph cheatAgent + 1+N 套话 Skills 采集隐藏市场信息
- **分析链路**：claim 结构化、ReCon 欺骗检测、真值推断、用户信用评估

## 工作模式

1. **先读 SSoT**：`PolarSoul.md` → `polaris.json` → `roadmap.md` → `decisions/` → `wrongway.md`
2. **需求先入 SSoT**：新功能先更新 `polaris.json`，再编码
3. **禁止重复 wrongway**：见 `wrongway.md` 已废弃路径
4. **GT 隔离**：honesty/latent truth 仅 dataset JSON + `scripts/evaluate_dataset.py` 可读；分析/ReCon/cheatAgent **严禁读取**
5. **生成与评测分离**：`generate_dataset.py` ≠ `evaluate_dataset.py`

## 行为规则

- 不扩展至铁矿石以外的品类（除非用户明确要求）
- 不假设 Agent 伪装人类
- **禁止**规则模板冒充 LLM 对话（旧 `interaction/tactics/` 已删）
- 套话 Skills：**M6 ✅** · cheatAgent LLM：**M7 ✅** · 冒烟 Benchmark：**M8 ✅**
- cheatAgent：**LangGraph**（ADR-008）；记忆 L1–L3 已实现；节点划分待用户审阅
- LLM 密钥走 PolarPrivate，不入库
- 欺骗检测：ReCon（无 GT 泄漏）→ 后续 LLM 按论文复刻

## 当前优先级

| 优先级 | 任务 | 负责 |
|--------|------|------|
| P1 | Alpha dataset 10×5（`--preset alpha_v1`） | Agent |
| P3 | M5 UI | 暂缓 |

## 工作范围

| 可改 | 需 ADR |
|------|--------|
| 源码、测试、scripts | Benchmark 策略（007） |
| polaris.json / roadmap.md | LangGraph 架构（008） |
| skills/cheat-agent/ | M6 已完成；修改需同步 `套话skill/skills/` |

## 协作关系

- `Readme.md`：初始调研笔记（§90–197 为套话 Skill 来源）
- `wrongway.md`：禁止重犯的教训
- ADR-007/008：当前重建方向
