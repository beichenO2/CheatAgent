---
name: cheatagent-show
description: >-
  启动 CheatAgent 本地展示：LLM Proxy（PolarPrivate_OpenSource）、智能客服网站
  （market-truth-cs :3085）、评测报告 Dashboard（:8931），并在浏览器打开。
  Use when the user asks to demo / 展示 / 跑起来 / 打开网站 / show the project /
  start the UI / open dashboard.
---

# CheatAgent 展示启动

给**查看本仓库的 Agent**用：把展示所需服务拉起来，并在浏览器打开两个页面即可。
不要跑评测 pipeline；**不要改 CheatAgent 业务代码**。
例外：为让用户「只填一把 Key」跑通 LLM，允许按 §1.3 改 **PolarPrivate_OpenSource** 的路由表（`model_routing.py`），且须先问清用户的模型/供应商。

## 展示目标（两个页面）

| 页面 | URL | 作用 |
|------|-----|------|
| 智能客服（CheatAgent 网站） | http://127.0.0.1:3085 | 以客户身份登录，与情报客服对话 / 回放 150 段对话 |
| 评测报告 Dashboard | http://127.0.0.1:8931/beta_v2/dashboard.html | 论文风格指标报告（主看 beta_v2；对照可用 beta_v1） |

登录客服站：`u001`…`u030` 或 `admin`（免密直登）。

## 依赖路径（约定）

以本仓库根目录为 `$CHEAT`（即本 `Show.md` 所在目录）。

| 组件 | 默认路径 | 说明 |
|------|----------|------|
| 本仓库（报告 + Python 服务） | `$CHEAT` | GitHub: `beichenO2/CheatAgent` |
| 客服 Web UI | `~/Desktop/Web_related/market-truth-cs` | PolarChat 发行版；若缺失见下方「缺目录时」 |
| LLM Proxy | `~/Desktop/Web_related/PolarPrivate_OpenSource` 或任意克隆目录 | **必须先起**，默认 `http://127.0.0.1:12790` |

## 步骤（按顺序）

### 0. 先探活，已在跑就跳过

```bash
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:12790/v1/models   # LLM Proxy
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3085/             # 客服站
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8931/beta_v2/dashboard.html  # 报告
docker ps --format '{{.Names}} {{.Status}}' | grep -E 'mtcs-|market-truth' || true
```

已返回 2xx/3xx 的服务不要重复启动。

### 1. LLM Proxy：克隆并启动 PolarPrivate_OpenSource

本项目 LLM **统一走** [PolarPrivate_OpenSource](https://github.com/beichenO2/PolarPrivate_OpenSource.git)
（OpenAI 兼容代理，默认 `:12790`）。**不要**把 API Key 写进 CheatAgent 仓库。

#### 1.0 兼容性（已核验，Agent 勿再猜）

| 项 | 结论 |
|----|------|
| 能力码 | **是四位 QCSA**（`0000`…`1111`）+ 视觉 `V****`；与本仓库一致 |
| 本仓库默认调用 | Agent/ReCon：`MTA_LLM_MODEL=0001`；Normalize：`MTA_NORMALIZE_MODEL=qwen3.7-plus`（对应 QCSA **`1100`**） |
| 仓库洁净度 | OpenSource 是**空壳**：无真实 Key、无提交的 sqlite/vault；仅有 demo placeholder（`demo-codingplan-api-key-placeholder`）与测试假 Key。用户本地 DB/日志在 `.gitignore` 外，不入库 |
| 预设上游 | 作者机预设（讯飞 glm51 / 阿里 codingplan / dashscope / MiniMax）——**访客机器通常没有这些**，必须按下方「一 Key + 改路由」适配 |

#### 1.1 克隆与启动

```bash
# 若本地还没有：
git clone https://github.com/beichenO2/PolarPrivate_OpenSource.git \
  ~/Desktop/Web_related/PolarPrivate_OpenSource

cd ~/Desktop/Web_related/PolarPrivate_OpenSource
cd backend && uv sync && privportal init-db && privportal start   # → :12790
# 另开终端：录入密钥用管理前端
cd ../frontend && npm install && npm run dev                     # → :12795
```

验收：`curl -s http://127.0.0.1:12790/health`（需 vault unlocked 才算 live）。

#### 1.2 告诉用户如何填 Key（只填一把）

Agent **必须停下来问用户**（不要假设他们有讯飞/阿里预设）：

1. 打开 http://127.0.0.1:12795
2. Onboarding：设 Master Password → 解锁保险库（之后每次重启都要 Unlock）
3. **Secrets** 页：新增（或改掉 demo placeholder）**一把** API Key  
   - 例：`secret.my.openai_compatible.api_key` = 用户的真实 Key  
   - Base URL = 用户供应商的 OpenAI 兼容端点（如 `https://api.openai.com/v1`、DashScope、自建网关等）
4. **Bindings** 页：建一条 Binding，例如 service 名 `llm.user.primary`，secret 指向上面那把 Key

明文 Key **只进 PolarPrivate Vault**，禁止写入本仓库任何文件 / commit / 聊天记录落盘。

#### 1.3 用户告知模型 → Agent 按规范改路由（一 Key 跑通）

本仓库调用的是 **能力码 / 固定模型名**，不是用户供应商的原始模型 ID。用户模型多半 ≠ 作者预设，因此：

1. **向用户索取**（缺一不可就再问）：
   - 供应商 / Base URL（若上一步已填可复用）
   - 他们要用的**上游模型 ID**（可只给一个；若对话与长文抽取要分开，可给两个）
2. Agent 在 **PolarPrivate 仓库**（不是 CheatAgent）改路由，使本仓库默认调用落到用户那一把 Key：

编辑 `backend/app/core/model_routing.py` 的 `CAPABILITY_CLOUD_MAP`（必要时同步 `MODEL_SERVICE_MAP` / `CAPABILITY_CODES.md`）：

| 本仓库会请求的 model 字段 | 应映射到 |
|---------------------------|----------|
| `0001`（Agent / ReCon / 客服） | `(用户对话模型 ID, llm.user.primary)` |
| `1100` 与/或字面量 `qwen3.7-plus`（Normalize） | `(用户抽取模型 ID 或同一模型, llm.user.primary)` |

原则：**用户只维护一把 Key + 一条 Binding**；其余 QCSA 码可一并指到同一 `service_name`，避免踩到作者预设的 `llm.glm51.enterprise` 等空 Binding。

改完后重启 `privportal start`，冒烟：

```bash
curl -s http://127.0.0.1:12790/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"0001","messages":[{"role":"user","content":"ping"}]}'
```

未配 Key / 用户暂不提供时：客服站可 `MTCS_MOCK_LLM=1` 做壳子演示（无真实对话）；报告 Dashboard 不依赖 LLM，仍可打开。

### 2. （推荐）启动本仓库 Python 客服后端 `:3945`

客服站默认模型 `mta-python` 依赖此服务：

```bash
cd "$CHEAT"
./service/start.sh
# health: curl -s http://127.0.0.1:3945/health
```

### 3. 启动 CheatAgent 网站（market-truth-cs）

```bash
cd ~/Desktop/Web_related/market-truth-cs
POLARPRIVATE_URL=http://host.docker.internal:12790 \
  docker compose -f docker-compose.polar.yml -f docker-compose.mtcs.yml \
  -p market-truth-cs up -d
```

验收：容器 `mtcs-librechat` / `mtcs-polar-api` Up；浏览器可开 http://127.0.0.1:3085 。

**缺目录时**：向用户说明 Web UI 发行版不在本 git 仓库内，默认路径为
`~/Desktop/Web_related/market-truth-cs`；若机器上没有，需先取得该发行版再执行本步。
详规见该目录 `README.md`（JWT 侧栏、DEV `:3090` / Release `:3085` 互斥）。

### 4. 启动评测报告站（静态 Dashboard）

报告已生成在仓库内，只需起一个静态 HTTP 服务（端口与文档一致用 **8931**）：

```bash
cd "$CHEAT/benchmark/reports"
python3 -m http.server 8931
```

主入口：http://127.0.0.1:8931/beta_v2/dashboard.html  
对照：http://127.0.0.1:8931/beta_v1/dashboard.html  

若 html 缺失或过旧，再重建（一般展示不需要）：

```bash
cd "$CHEAT"
python scripts/build_dashboard.py --preset beta_v2
```

### 5. 浏览器打开

```bash
open "http://127.0.0.1:3085"
open "http://127.0.0.1:8931/beta_v2/dashboard.html"
```

非 macOS 用 `xdg-open` 或把 URL 交给用户。

## 端口速查

| 端口 | 服务 |
|------|------|
| 12790 | PolarPrivate LLM Proxy |
| 12795 | PolarPrivate 管理前端（可选） |
| 3085 | 客服 Web UI（Release） |
| 3925 | Polar API（客服站后端） |
| 3945 | 本仓库 Python cheatAgent HTTP workflow |
| 8931 | 评测 Dashboard 静态站 |

## 完成标准

- [ ] `:12790` 可访问且 vault 已解锁（或已明确使用 `MTCS_MOCK_LLM=1`）
- [ ] 已指导用户填 **一把** Key；已询问并（如需要）按 §1.3 改好 PolarPrivate 路由，使 `0001` / `qwen3.7-plus` 可用
- [ ] `:3085` 打开为客服登录/聊天页
- [ ] `:8931/beta_v2/dashboard.html` 打开为指标报告（含图 3 可靠度标定等）
- [ ] 两个页面都已在浏览器中打开

向用户回报两个 URL + 登录方式 + Key/路由状态即可，无需额外长文。
