Created 3 todos
**当前项目与业务需求匹配度（高层结论）**
- **已有基础（+）**:  
  - Data flow: 前端 → 后端（`/api/search`）→ DDG 搜索 + fxtwitter 获取推文内容 → 过滤/排序。见 `backend/app/core/twitter_fetcher.py` and `frontend/src/components/SearchForm.jsx`.  
  - 支持时间窗口、最小点赞、作者 include/exclude、Playwright 回退与后台抓取缓存（`backend/app/core/x_search.py`, `backend/app/core/bg_worker.py`）。  
  - 快速可用、无须官方 API 的轻量方案，能抓到部分热门/可检索推文。
- **核心不足（—）**: 对于“meme 文化信号”的监控，当前系统偏重“检索 & 过滤已存在的推文”，但缺乏专门的信号检测、实时性、召回保证与多模态（图像/视频）分析，这些是判断 meme 热度与早期爆发的关键。

**与业务目标的关键差距（需要优先修复）**
1. **实时/near-real-time 数据摄取** — 当前依赖 DDG/Playwright 抓取页面属于搜索/回溯型，延迟高且不完整。要捕捉早期信号需引入流式/轮询或订阅式抓取（例如持续抓取热门账号、话题、或使用官方API/第三方stream）。  
2. **信号定义与检测能力不足** — “meme 文化的信号”不是单一关键词：需要组合信号（hashtags、图片/动图、特定用语、快速转发率上升、社区/钱包地址出现、低质量账号集中转发等）。当前只有点赞/文本长度/作者过滤。  
3. **多模态支持缺失** — Meme 很多是图片/GIF/视频与短文本；需抓取并分析媒体（图像哈希、OCR、图像相似度、视觉特征、模因模板识别）。  
4. **早期扩散检测/突发检测欠缺** — 需要时间序列与速率指标（mentions/min、retweet velocity、author-networks）来发现“快速扩散”的事件。  
5. **噪声/误报控制** — Meme 领域噪声高（模因语境、讽刺、复读），需要上下文理解（情感分析、讽刺/反语检测）来降低误报。  
6. **可扩展/可靠的数据平台** — Playwright 爬取消耗资源、容易被限流或遇到 CAPTCHAs。生产环境需缓存（已加）、队列、外部任务队列和可共享缓存（Redis）以扩大规模。  
7. **法律/合规风险与稳定性** — 大量页面抓取与绕过可能触及站点使用条款或触发防护，长期稳定性差；应评估使用官方 API 或经授权的第三方数据源优先级。

**具体改进建议（按优先级）**

- 优先级：P0（必须/高影响），P1（高收益中期），P2（增量优化）

P0 — 实时采集与索引
- 建立持续采集层（workers）：
  - 订阅或轮询高价值源（top influencers、相关 hashtags、已知社区账号列表）。实现方式：短轮询 Playwright profile 列表或使用 X API（若可获得）。文件/位置：扩展 `backend/app/core/bg_worker.py` 为 worker 调度 + 持久队列（RQ/Celery）。  
- 切换缓存为 Redis（跨进程、共享、TTL）：将 `x_search` 内存缓存替换为 Redis（key: query/timeline），并把后台 worker 写入 Redis，API 先返回 cached 结果再补齐。见 `backend/app/core/x_search.py`。  
- 增加数据湖 / 索引（轻量 ElasticSearch / Meili / RedisJSON）：将抓到的推文与时间序列写入索引以便快速检索和聚合。

P1 — 信号工程（核心能力）
- 定义“meme 信号”特征集合并实现检测器：
  - 文本特征：特定词表（meme 词典）、短文本比率、夸张标点、emoji 频率、重复词/拼写模式。  
  - 元数据：快速增加的 mention/retweet rate、作者账户类型（新/小粉/机器人迹象）、小时内点赞增长曲线。  
  - 社交图谱特征：密集转发群体、同一钱包/账号重复出现。  
- 实现规则 + ML 结合的分类器：先做规则引擎（regex + keyword + velocity thresholds），随后训练轻量模型（e.g., gradient-boosting 或小型 transformer）做二次筛选。  
- 多模态：抓取图片媒体并计算 perceptual hash，做相似度聚类；可用 CLIP 或视觉嵌入识别相同 meme 模板。

P1 — 早期报警与可视化
- 指标/报警：实现 mention velocity、retweet velocity、unique authors/min，定义阈值触发告警（Slack / Webhook / UI）。  
- 仪表盘：时间序列图、热度榜、作者网络视图、最近样例。

P2 — 可靠性与可运营性
- 改造 Playwright 到生产级：并发池、代理支持、浏览器轮换、截图与错误记录；或优先争取官方 API 权限/付费数据。  
- 监控与度量：抓取成功率、延迟、缓存命中率、报警误报率。  
- 自动化测试：端到端 smoke tests 覆盖常见查询与 author timelines。

**工程工作单（可直接执行的任务，带优先级与粗估）**
- T1 (P0, 3-5d): 引入 Redis，替换内存缓存，确保后台 worker 写入 Redis，API 先读 Redis（缓存）再触发 background fetch。  
- T2 (P0, 3-5d): 实现 scheduled crawlers：维护“关注账号/hashtags”列表并周期性抓取；store 到索引（Meili/ES）。  
- T3 (P1, 5-10d): 实现规则型 meme detector（关键词表 + velocity rules + emoji patterns）并把 detector 集成到 ingestion pipeline。  
- T4 (P1, 7-14d): 加入媒体处理（下载图片、生成 pHash/CLIP 嵌入、做聚类）与模因模板识别。  
- T5 (P1, 3-5d): 报警和仪表盘（简单 Web UI 或 Grafana）。  
- T6 (P2, 7-14d): 升级 worker 到 Celery/RQ + 添加代理管理/浏览器池/速率限制，或迁移到官方数据源。

**风险与权衡**
- Playwright 抓取：好处是覆盖面广、可抓取动态渲染内容；缺点是昂贵、容易被限流/封锁。长期应尽力获取官方 API 或付费数据源以减少运维负担。  
- 召回 vs 精度：提高召回（宽松规则、多源）会导致更多噪声，必须并行建立二次筛选/模型以控制误报。  
- 合规：必须评估抓取行为是否符合服务条款与法律义务。

**立刻可做的最小步骤（2–3 天）**
1. 将缓存改为 Redis（部署一个本地/容器 Redis），并把 `x_search` 的缓存读写改为 Redis（低风险，能立刻提高跨进程可用性）。  
2. 在 ingestion pipeline 加入一套简单的规则引擎（关键词 + emoji + velocity thresholds），把输出做为“meme_score”。  
3. 建立“监控账号/hashtag”列表并做短轮询（例如每 30s–2min）写入索引，确保早期数据被收集。



