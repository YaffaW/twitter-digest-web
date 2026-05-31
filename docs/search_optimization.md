# Search Recall & Quality Optimization

这是关于提升搜索召回与结果质量的建议和操作步骤，供本地部署使用。

## 目标
- 在满足用户过滤条件同时，提高不被遗漏的推文召回（尤其是 `from:` 指定用户和近期推文）。

## 已实现改进
- 增加 Playwright 的 X 搜索抓取（`backend/app/core/x_search.py`）。
- 在 `twitter_fetcher` 中合并 DDG 与 X 搜索结果；对 `from:` 指定的作者抓取其时间线以补足漏检。
- 前端增加 `use_x_search` 开关，作为可选回退。
- 为 fxtwitter 请求加入重试与指数退避，减少临时超时导致的漏抓。

## 推荐的进一步优化（优先级排序）
1. 缓存与去重：对查询/作者结果做短期缓存（例如 5-15 分钟），减少重复抓取并提升响应速度。
2. 异步/后台抓取：对于耗时的 Playwright 抓取，在后台 worker 异步执行并把结果写入缓存；同步请求先返回DDG结果并标记为可能不完整。
3. 限速与退避：对 Playwright 抓取与外部 API（fxtwitter、ddgs）实现速率限制与全局退避策略，避免被对方限流或触发验证码。
4. 多源合并打分：引入融合评分函数（结合关键词匹配度、点赞/转发权重、时间衰减）来对来自不同来源的结果统一排序。
5. 周期性预抓：为高关注作者或常用查询预先抓取并索引（cron 或 worker），支持更快的查询响应。
6. 可观察性：增加抓取成功率/失败率、延迟、被限流次数和缓存命中率的监控指标。
7. 安全与合规：遵守目标站点的 robots/使用条款，确保不触发滥用检测。

## 快速操作命令
- 安装 Playwright 并下载浏览器（已执行过）：
```bash
pip install playwright
playwright install chromium
```
- 启动后端（在项目根目录）：
```bash
cd backend
.venv/bin/python run.py
```
- 启动前端开发服务器：
```bash
cd frontend
npm run dev
```

## 建议的代码改动（已部分实现）
- `backend/app/core/twitter_fetcher.py`:
  - 对 `fetch_tweet()` 增加重试与退避。
  - 在搜索合并阶段加入对 `from:` 的用户时间线抓取。
- `backend/app/core/x_search.py`:
  - 提供 `search_x()` 与 `search_user_timeline()` 两个抓取接口。

## 下一步（我可以代劳）
- 提交并推送当前改动到远程仓库（我可以执行）。
- 为 Playwright 抓取添加缓存层和异步 worker（需要决定缓存策略与存储）。
- 将 `use_x_search` 可视化为前端设置并储存在本地配置，便于默认策略控制。

如需，我可以现在提交并推送改动并启动前端开发服务器来演示。