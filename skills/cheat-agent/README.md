# cheatAgent Skills（M6 — 用户主导）

基于 `Readme.md` §90–197 心理学与对话策略研究，凝练 **1 + N** Skills：

| 类型 | 文件 | 职责 |
|------|------|------|
| **1 路由** | `SKILL-router.md` | 根据 user model、对话阶段、抵抗程度，选择专项 skill |
| **N 专项** | `SKILL-*.md` | 针对不同 persona / 情境 / 策略（心理反抗、苏格拉底、陷阱问题、SUE、VA…） |

## 状态

- [ ] `SKILL-router.md` — 占位，待用户编写
- [ ] 专项 skills — 待从 Readme 研究线映射

## 调用约定

cheatAgent `route_skill` 节点读取 router skill → 输出 JSON：

```json
{
  "skill_id": "reactance-biased-statement",
  "phase": "CHALLENGE",
  "rationale": "用户 resistance 低且尚未披露港存"
}
```

`invoke_skill` 节点加载 `skills/cheat-agent/SKILL-{skill_id}.md` 生成 utterance。

## 参考

- `decisions/007-agent-rebuild.md`
- `decisions/008-cheat-agent-langgraph.md`
- `Readme.md` lines 90–197
