# cheatAgent Skills（M6 ✅）

**1 路由 + 11 专项**（10 研究线 + `cover-qa`），来源 Readme §90–197 + `套话skill/analysis/*`。

完整材料与论文清单见 [`套话skill/README.md`](../../套话skill/README.md)。

| 类型 | 文件 | 状态 |
|------|------|------|
| 路由 | `SKILL-router.md` | ✅ 规则引擎已接入 `graph.py::route_skill` |
| 专项 | `SKILL-*.md` × 11 | ✅ |

## 调用链

```
load_context → update_user_model → route_skill → invoke_skill → write_memory
```

| 节点 | 状态 | 说明 |
|------|------|------|
| `load_context` | ✅ | 注入 session / identity / history |
| `update_user_model` | 🟡 | 规则版 gap/resistance/claims 推断 |
| `route_skill` | ✅ | 读 SKILL-router 决策树，输出 `selected_skill_id` + `phase` |
| `invoke_skill` | ✅ M7 | 加载 `SKILL-{id}.md`，LLM 生成 utterance（mock/live） |
| `write_memory` | 🟡 | 脚手架已有，L1–L3 持久化待完善 |

## 论文材料

15 篇 PDF → `套话skill/reference/papers/`（2026-07-08 已整理，含 AVERT）
