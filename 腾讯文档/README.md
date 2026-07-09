# 腾讯文档索引

本目录维护项目在线文档的 **file_id、链接与本地镜像** 对照，便于 Agent / 协作者同步。

## 文档清单

| 名称 | 类型 | 在线链接 | file_id | 本地镜像 | 最后同步 |
|------|------|----------|---------|----------|----------|
| CheatAgent 项目方案 | smartcanvas | [打开](https://docs.qq.com/aio/DZHZGSFVGYUJSQXdY) | `DZHZGSFVGYUJSQXdY` | `../CheatAgent.md` | 2026-07-09 23:20 |
| smoke_v1 评测报告 | smartcanvas | [打开](https://docs.qq.com/aio/DZEZ2YU9zQUdSREtY) | `DZEZ2YU9zQUdSREtY` | `../benchmark/reports/smoke_v1_eval.json` | — |
| beta_v1 评测报告 | smartcanvas | —（eval 完成后创建） | — | `../benchmark/reports/beta_v1_eval.json` | — |

## 同步规则

1. **SSoT 优先级**：`CheatAgent.md` 为本地主文档；在线 smartcanvas 为对外分享版，内容应保持一致。
2. **更新流程**：
   - 改本地 `CheatAgent.md` → 用 `smartcanvas_edit` 同步对应 block（见下方 block id）
   - 改在线文档 → 回写本地镜像并 git commit
3. **关键 block id**（CheatAgent 在线文档）：
   - 最后更新：`LEitU6GjCrhgM8RvJKRTPY`
   - 进展摘要：`DhLZS76BXE7Jw07NxBjl2n`
   - Beta roadmap 状态：`VKAc9ELcqjVKHWQy81vhyC`

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

测试截图、Playwright 快照等不入版本库，统一放在 `artifacts/`（见根目录 `.gitignore`）。
