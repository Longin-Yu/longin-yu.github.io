# 模板来源与本地定制

- 上游：[RayeRen/acad-homepage.github.io](https://github.com/RayeRen/acad-homepage.github.io)
- 导入版本：`2cc1577eeaf2f74dede6d016a70722dbd409ea2f`
- 导入日期：2026-09-27
- 导入方式：将模板文件迁入原站点仓库，保留原仓库历史与图片；不是重建 GitHub 仓库。
- 原许可：MIT，保留根目录 LICENSE。

保留模板的 Jekyll / Liquid / Sass 结构、作者侧栏、导航和 paper-box 论文排版。个人内容集中于 `_config.yml`、`_pages/about.md`、`_data/publications.json`。News 与实习资料分别位于 `_data/news.yml`、`_data/internships.yml`。自定义样式位于 `_sass/_custom.scss`，目前保留上游默认字号、栏目宽度、40%/60% 论文布局、图片阴影、蓝色角标和图标标题，仅增加窄屏与可访问性修正。

替换模板的占位个人信息和演示栏目；作者侧栏、导航、页面 head 和脚本入口做了简化。导航、论文正文及 BibTeX 展开无需 JavaScript。JS 增强剪贴板复制和 Scholar 引用数更新；未加载模板旧的 jQuery 插件包或 MathJax。修正嵌套 head 和默认全站新窗口链接，资源使用 Jekyll 的 URL 过滤器。

恢复上游以独立 google-scholar-stats 分支更新引用数的机制。抓取器增加 HTTP 超时、用户 ID 与字段校验、分页校验和失败时保留旧数据，工作流不强制覆盖分支历史。引用快照支持离线预览和无 JS 阅读。定时更新需发布后在 GitHub Actions 中验证，日常站点构建不需要 Python。

升级前先保存当前修改；对比这个上游版本之后的改动，按需移植模板修复。不要直接用上游 `_config.yml`、`_pages/about.md` 或导航覆盖本站文件。
