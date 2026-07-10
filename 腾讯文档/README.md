# 腾讯文档索引

本目录维护项目在线文档的 **file_id、链接与本地镜像** 对照，便于 Agent / 协作者同步。

## 文档清单

| 名称 | 类型 | 在线链接 | file_id | 本地镜像 | 最后同步 |
|------|------|----------|---------|----------|----------|
| CheatAgent 项目方案 | smartcanvas | [打开](https://docs.qq.com/aio/DZHZGSFVGYUJSQXdY) | `DZHZGSFVGYUJSQXdY` | `../CheatAgent.md` | 2026-07-10 20:45 |
| smoke_v1 评测报告 | smartcanvas | [打开](https://docs.qq.com/aio/DZEZ2YU9zQUdSREtY) | `DZEZ2YU9zQUdSREtY` | `../benchmark/reports/smoke_v1_eval.json` | — |
| beta_v1 评测报告 | smartcanvas | [打开](https://docs.qq.com/aio/DZHhoQVhNRVJSR1JM) | `DZHhoQVhNRVJSR1JM` | `../benchmark/reports/beta_v1_eval.json` | 2026-07-10 06:20 |
| **beta_v2 评测报告** | smartcanvas | [打开](https://docs.qq.com/aio/DZHVySmJVeHJvdm9I) | `DZHVySmJVeHJvdm9I` | `../benchmark/reports/beta_v2_eval.json` · `../benchmark/reports/RESULTS.md` | 2026-07-10 20:45 |
| 评测成果摘要 | 本地 | — | — | `../benchmark/reports/RESULTS.md` | 2026-07-10 19:17 |

## 同步规则

1. **SSoT 优先级**：`CheatAgent.md` 为本地主文档；在线 smartcanvas 为对外分享版，内容应保持一致。
2. **更新流程**：
   - 改本地 `CheatAgent.md` → 用 `smartcanvas_edit` 同步对应 block
   - 改在线文档 → 回写本地镜像并 git commit
3. **关键 block id**（CheatAgent 在线文档）：
   - 最后更新：`TaMg0RcYO5r9xad3AZ33Q1`
   - 进展摘要：`CUUtuPdIyQ0HUh0m5usQMd`
   - L2 世界态：`KkycSLgFgG6kA27CVe9xrs`

## MCP 工具速查

```bash
# 读取在线文档
smartcanvas_read(file_id="DZHZGSFVGYUJSQXdY")

# 搜索 block
smartcanvas_find(file_id="DZHZGSFVGYUJSQXdY", query="最后更新")

# 更新 block
smartcanvas_edit(file_id="...", action="UPDATE", id="...", content="<Paragraph>...</Paragraph>")
```

## 产物归档

测试截图、Playwright 快照等不入版本库，统一放在 `artifacts/`（见根目录 `.gitignore`）：
- UI 截图：`artifacts/mtcs/screenshots/`（含 `mta-python-*.png` 等 E2E 验收图）
- 页面快照：`artifacts/mtcs/snapshots/`
- Dashboard 截图：`artifacts/dashboard/`
