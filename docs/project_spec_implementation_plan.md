# Project Implementation Plan — Meme-token Twitter Monitor

目标：构建稳定、可扩展并高召回的推特（X）监控系统，用于检测符合 meme 文化的早期信号，支持告警与可视化，供代币购买决策参考。

说明：每一步包含目的、具体改动、相关文件/组件、验收标准、预估工时与当前状态。状态会在实现后更新。

## 步骤清单

1) T1 — Redis 缓存与回退（状态：完成）
   - 目的：跨进程共享缓存，减少重复抓取并提升响应速度。
   - 具体改动：在 `backend/app/core/x_search.py` 优先使用 Redis（key: `search_x:<query>:<max_results>` / `timeline:<username>:<max_results>`）存取缓存；不可用时回退到内存缓存。更新 `backend/requirements.txt` 加入 `redis`。
   - 相关文件：`x_search.py`, `requirements.txt`, `twitter_fetcher.py`（调用缓存时的行为）。
   - 验收标准：在本地启动 Redis 后，后台抓取结果被写入并从 Redis 读取；API 响应优先命中 Redis 缓存。
   - 预估工时：已完成。

2) T2 — 异步后台抓取与调度（状态：完成）
   - 目的：避免 Playwright 抓取阻塞 API，先返回现有结果并异步补齐缓存。
   - 具体改动：加入轻量线程队列 `backend/app/core/bg_worker.py`；在 `twitter_fetcher` 缓存未命中时，排入后台抓取任务。可选后续迁移到 Celery/RQ。
   - 相关文件：`bg_worker.py`, `twitter_fetcher.py`, `x_search.py`。
   - 验收标准：API 在缓存未命中时立即返回；后台线程完成后写入缓存并可被后续请求命中。
   - 预估工时：已完成。

3) T3 — 持续采集（scheduled crawlers）与索引（状态：not-started）
   - 目的：建立 near-real-time 数据层，定期抓取关注账号/hashtags 并写入索引，支持快速检索与时间序列分析。
   - 具体改动：
     - 添加 crawler module（`backend/app/core/crawler.py`），维护“关注账号/hashtags”列表（config 文件或 DB），周期性抓取用户时间线与搜索页。使用 `bg_worker` 或后续 worker 框架调度。
     - 将抓取到的推文写入轻量索引（推荐：Meilisearch 或 SQLite+FTS 或 Elastic）。创建 `backend/app/core/indexer.py` 负责写入与查询。
   - 相关文件：`crawler.py`, `indexer.py`, 配置文件（`config.yaml` 或 env）。
   - 验收标准：能持续（例如每 1-5 分钟）抓取并将结果写入索引；API 能基于索引返回快速结果。
   - 预估工时：3-5 天。

4) T4 — 规则型 Meme Detector（状态：not-started）
   - 目的：定义并实现“meme 信号”的初级检测器，给每条推文打分（meme_score）。
   - 具体改动：
     - 新模块 `backend/app/core/detector.py`，实现规则集合：关键词表（meme 词典）、emoji 频率、短文本阈值、重复模板、快速增长（velocity）规则等。
     - 在 ingestion pipeline（crawler/indexer 或 `search_and_fetch`）中调用 detector，为结果添加 `meme_score` 字段。
   - 相关文件：`detector.py`, `indexer.py`, ingestion pipeline 调用点。
   - 验收标准：对已知样例（手工列出）打分能区分明显 meme 与非 meme；能在 API 中返回 `meme_score`。
   - 预估工时：4-7 天。

5) T5 — 多模态支持（媒体抓取、图像相似度）（状态：not-started）
   - 目的：支持图片/GIF 的识别与聚类（meme 模板识别），提高召回与聚合能力。
   - 具体改动：
     - 在抓取时下载媒体（图片/GIF），生成 perceptual hash（pHash）并保存到索引；可选生成 CLIP/视觉嵌入用于相似度检索。
     - 新模块 `backend/app/core/media.py` 处理下载、hash、嵌入。
   - 相关文件：`media.py`, indexer 修改以存储媒体元数据。
   - 验收标准：能对同一 meme 图片归类为同一模板；API 支持按视觉聚类查询。
   - 预估工时：7-14 天（取决于嵌入方案）。

6) T6 — 早期扩散检测与告警（状态：not-started）
   - 目的：实现 velocity/热度指标并触发告警（Webhook/Slack/UI）。
   - 具体改动：
     - 新模块 `backend/app/core/alerts.py` 计算 mention/retweet velocity、unique authors/min、增长斜率等。
     - 添加告警规则配置与通知接收器（Slack webhook、邮件、UI）。
   - 相关文件：`alerts.py`, `indexer.py`, 前端/通知配置。
   - 验收标准：当某条 meme_score 高且 velocity 超阈值时，能在 UI/Webhook 中收到告警。
   - 预估工时：3-6 天。

7) T7 — 可扩展抓取基础设施（状态：not-started）
   - 包括：将后台 worker 升级为 Celery/RQ，使用 Redis 做队列/缓存，添加浏览器池、代理管理、错误重试与监控。此步为生产就绪要求。
   - 预估工时：7-14 天。

8) T8 — 监控、度量与运维（状态：not-started）
   - 指标：抓取成功率、请求延迟、缓存命中率、报警误报率、Playwright 错误统计。将指标导出到 Prometheus/Grafana 或外部监控。
   - 预估工时：2-4 天。

9) T9 — 合规审查与风险控制（状态：not-started）
   - 评估抓取行为是否违反服务条款，决定是否申请官方 API 或采购第三方数据源以降低长期风险。
   - 预估工时：1-3 天（含沟通与决策）。

## 文档与状态更新规范
- 每完成一项（或半项），在本文件中更新对应步骤的`状态`与变更点，并 commit。状态值：`not-started`、`in-progress`、`completed`、`blocked`。
- 对于每项，保留 `验收标准` 的测试脚本或说明（放在 `tests/` 或 `scripts/` 里），以便自动验证。

---

当前：T1/T2 已实现并提交；后续步骤按优先级执行，请确认选择下一步开始项（建议先 T3 持续采集并索引）。
