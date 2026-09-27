# 模板来源与本地定制

- 上游：[RayeRen/acad-homepage.github.io](https://github.com/RayeRen/acad-homepage.github.io)
- 导入版本：`2cc1577eeaf2f74dede6d016a70722dbd409ea2f`
- 导入日期：2026-09-27
- 导入方式：将模板文件迁入原站点仓库，保留原仓库历史与图片；不是重建 GitHub 仓库。
- 原许可：MIT，保留根目录 LICENSE。

保留模板的 Jekyll / Liquid / Sass 结构、作者侧栏、导航和 paper-box 论文排版。个人内容集中于 `_config.yml`、`_pages/about.md`、`_data/publications.json`。自定义样式位于 `_sass/_custom.scss`。

替换模板的占位个人信息和演示栏目；作者侧栏、导航、页面 head 和脚本入口做了简化。导航、论文正文及 BibTeX 展开无需 JavaScript。JS 仅增强剪贴板复制；未加载模板旧的 jQuery 插件包、MathJax 或外部统计脚本。修正嵌套 head 和默认全站新窗口链接，资源使用 Jekyll 的 URL 过滤器。

引用统计抓取脚本作为可选参考保留，但未导入上游自动推送统计分支的 GitHub Actions 工作流。日常站点构建不需要 Python。

升级前先保存当前修改；对比这个上游版本之后的改动，按需移植模板修复。不要直接用上游 `_config.yml`、`_pages/about.md` 或导航覆盖本站文件。
