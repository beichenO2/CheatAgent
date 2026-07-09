# 05 LLM 与工程运维

## 5.1 Normalize 层误用 VL 模型（2026-07-08）

**做了什么**：`MTA_NORMALIZE_MODEL` 默认填了 `qwen3-vl-flash`（视觉-语言模型）跑纯文本转译。

**错在哪**：文本任务用 VL 模型——能力错配、费用浪费、延迟高。

**教训**：选型先查 PolarPrivate `/v1/models` 与模型说明；纯文本任务用纯文本模型（现 `qwen3.7-plus`）。

## 5.2 长任务静默运行（2026-07-08）

**做了什么**：`evaluate_dataset.py` 全程无输出，最后一次性 print JSON；外层还把 stderr 重定向进文件。

**错在哪**：跑 30+ 分钟无任何进度，无法区分「在跑」和「卡死」；用户只能杀进程重来。

**教训**：
- 长任务必须有 **流式进度日志**（`utils/progress.py`，stderr + flush）
- 启动命令必须 `tee` 到终端可见，禁止 `2>file` 静默
- 进度粒度到 user turn 级；LLM 单轮可能 60–90s，日志要让人能算 ETA

## 5.3 manifest 被单用户写入覆盖（2026-07-08 beta 生成）

**做了什么**：`write_dataset([单个 persona])` 按传入列表重建 manifest["users"]，把 30 人 manifest 覆盖成 1 人。

**错在哪**：8 小时生成完成后 gate 报 `expected >=30 users, got 1`；数据在盘上但索引丢了。

**教训**：manifest 更新必须**合并磁盘已有用户**（或从磁盘重建），绝不能用本次调用的子集覆盖全量索引。新增 `rebuild_manifest()` 从磁盘扫描重建。

## 5.4 checkpoint 写入携带不可序列化对象（2026-07-09 beta 评测）

**做了什么**：`evaluate_session` 返回值内嵌 `AnalysisResult` 对象，直接 `json.dumps` 写 checkpoint。

**错在哪**：U001 评完 44 分钟，落盘瞬间 `TypeError: not JSON serializable`，全部白跑；同一 bug 连崩两次（第一次修复不彻底，只 strip 了一处引用）。

**教训**：
- 评测函数返回值应**天生可序列化**（在源头去掉对象引用，而不是在每个调用点 strip）
- checkpoint 粒度要到 **session 级**，用户级落盘意味着一崩全丢
- 修 bug 后先用最小输入验证序列化路径，再上长任务

## 5.5 3000 次 LLM 调用无重试（2026-07-08 smoke 评测）

**做了什么**：评测链路直连 PolarPrivate，无任何重试；proxy 闪断一次，31 分钟的评测在 ablation 阶段崩掉。

**教训**：长链路每个 LLM 调用都要走 `utils/retry.py`（指数退避、可配 `MTA_RETRY_MAX`）；transient 错误（Connection refused / timeout / 5xx）自动重试，其余立刻抛。
