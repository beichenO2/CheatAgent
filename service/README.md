# cheatAgent HTTP Workflow 服务

把主项目 `market_truth_agent`（LangGraph cheatAgent）包成 polar 可插拔的 HTTP workflow。

## 契约

与 Web 发行版 `examples/http-workflow-demo/README.md` 一致：

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 + `llm_mode` |
| `POST` | `/run` | 单轮客服；body = polar `run()` 入参 |

**请求**（polar 原样转发）：

```json
{
  "userId": "u001",
  "scenarioId": "scn_xxx",
  "sessionId": "ses_xxx",
  "message": "最近青岛港疏港量怎么样？",
  "memoryPayload": {
    "user": { "role": "贸易员", "region": "青岛港" },
    "scenario": {},
    "session": { "keypoints": [] }
  },
  "config": {},
  "workflowId": "mta-python"
}
```

**响应**：

```json
{
  "ok": true,
  "reply": "客服口语回复…",
  "memory_delta": {
    "session": { "青岛港/港存": "中" }
  }
}
```

- 内部入口：`run_cheat_agent_turn()`（`src/market_truth_agent/agents/cheat_agent/graph.py`）
- `memoryPayload` → `extra_context` 注入 cheatAgent prompt「业务系统记忆背景」
- 对话历史按 `sessionId` 进程内 dict 维护（重启清空）
- `memory_delta.session`：对本轮用户话做规则槽位抽取，键名 `{region}/{indicator}`

## 启动

前置：PolarPrivate 已解锁（默认 `http://127.0.0.1:12790`）。

```bash
cd /Users/mac/Desktop/Temp/雷老师组测试任务
./service/start.sh
# 等价：
# MTA_LLM_MODE=live PYTHONPATH=src \
#   python -m uvicorn web_workflow_service:app --app-dir service --host 0.0.0.0 --port 3945
```

健康检查：

```bash
curl -s http://127.0.0.1:3945/health
```

自测一轮：

```bash
curl -s http://127.0.0.1:3945/run \
  -H 'Content-Type: application/json' \
  -d '{"userId":"u001","sessionId":"test-1","message":"最近青岛港疏港量怎么样？","memoryPayload":{"user":{"region":"青岛港"}},"workflowId":"mta-python"}'
```

## 注册到 Web（market-truth-cs）

1. `site.config.json` → `http_workflows[]`：

```json
{
  "id": "mta-python",
  "label": "Python 情报客服（主项目算法）",
  "url": "http://host.docker.internal:3945/run",
  "timeout_ms": 120000
}
```

2. `librechat.yaml` → `modelSpecs.list` 增加同 id 的 preset（`prioritize: true` 时必须，否则 UI 不下拉）。

3. `docker restart mtcs-polar-api mtcs-librechat`

4. 验证：`curl -s http://127.0.0.1:3925/v1/models | jq '.data[].id'` 应含 `mta-python`。

## 依赖

- 解释器：含 `langgraph` / `langchain-openai` / `fastapi` / `uvicorn` 的环境（本机常用 `/Users/mac/.agent-reach-venv/bin/python3`）
- LLM：`MTA_LLM_MODE=live` + PolarPrivate（与 benchmark 相同）

## 局限

- 会话 history 仅内存，进程重启丢失；多 worker 不共享
- 单轮含路由 + 生成，live LLM 延迟可达数十秒；`timeout_ms` 建议 ≥ 120000
- 槽位抽取默认规则模式（避免每轮再打一次 LLM）；用户未断言指标时 `memory_delta` 可能为空
- 若环境 `NO_PROXY`/`no_proxy` 含 IPv6 `::1`，httpx 会报 `Invalid port: ':1'`；`start.sh` 与服务启动时会自动剔除
