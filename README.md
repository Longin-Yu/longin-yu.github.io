# Hao Yu · Academic Homepage

个人主页，基于 [RayeRen/acad-homepage.github.io](https://github.com/RayeRen/acad-homepage.github.io) 的 Jekyll 模板。线上地址为 https://longin-yu.github.io/ 。

## 日常修改

| 内容 | 文件 |
| --- | --- |
| 姓名、学校、邮箱、头像、主页链接 | `_config.yml` |
| 英文介绍、栏目顺序 | `_pages/about.md` |
| 论文与技术报告 | `_data/publications.json` |
| News | `_data/news.yml` |
| Internship | `_data/internships.yml` |
| Scholar 引用快照 | `_data/scholar.json` |
| 顶部导航 | `_data/navigation.yml` |
| 单篇论文的 HTML | `_includes/publication.html` |
| 个人样式调整 | `_sass/_custom.scss` |
| 图片 | `assets/images/` |

页面沿用模板原有侧栏、字号、论文大图和会议角标，栏目为 News、Publications、Technical Reports、Internship。论文数据的 `section` 分别为 `publications`、`reports`；`featured: true` 的论文在 Publications 前半部使用图文排版，其余论文和报告使用紧凑列表。各组内按 JSON 顺序展示。作者列表保留原始顺序，`Hao Yu` 自动加粗，`*` 显示为共同贡献标记。团队项目只展示标题、署名、发表信息和资源链接，不填写个人职责。

图文论文可包含 `image`、`imageAlt`、`imageWidth`、`imageHeight` 和 `description`。论文配图仅作预览，不提供图片跳转；GeoPerceive 直接使用原始流程图。`scholarId` 保留 Scholar 条目映射，页面仅显示总引用数。本地资源路径相对仓库根目录，如 `assets/images/comrope.png`。请让 `id` 唯一，已发布条目尽量保留原 ID，避免原有锚点失效。

BibTeX 的正文只维护 JSON 中的 `bibtex`。Jekyll 自动将它用于页面和 `assets/citations/*.bib` 下载。为新论文增加下载时，新建同名 `.bib` 文件，复制已有文件的模板，仅修改 front matter 的 `publication_id`，使其对应论文 ID。

## 本地预览

需要 Ruby、Ruby 开发头文件、编译工具和 Bundler。本项目锁定 GitHub Pages 使用的 Jekyll 3.10.0，以及本站实际用到的插件；版本依据见 [GitHub Pages 依赖表](https://pages.github.com/versions/)。

```bash
bundle install
bash run_server.sh
```

默认访问 http://127.0.0.1:4000/ 。通过 VS Code Remote SSH 使用时，将远端服务端口添加到 Ports 面板，访问面板给出的本地地址。若需要改变端口，运行 `PORT=5500 bash run_server.sh`，但先确认该端口没有被其他预览进程占用。

`jekyll serve` 会监听内容和样式变化并重新构建；修改 `_config.yml` 后需要重启。发布前执行：

```bash
bundle exec jekyll build --safe
git diff --check
```

生成的 `_site/` 不提交。VS Code Live Server 无法直接编译 Jekyll：如继续使用 Live Server，必须让它服务 `_site/`，并同时运行 `bundle exec jekyll build --watch`。不能直接打开源码中的 Liquid 模板来验收页面。

当前迁移预览在远端 5500 端口，兼容旧地址 `/projects/personal/longin-yu.github.io/index.html`。本机特有的 Ruby 安装路径和双栈端口转发操作记录在工作区 `scripts/tutorials/personal-homepage-jekyll-preview.md`。

## 分支与发布

- `main`：已发布版本。
- `migration/acad-homepage`：本次模板迁移和预览。
- `backup/custom-homepage`：迁移前的定制主页，另有标签 `custom-homepage-before-acad`。
- 后续修改从 `main` 创建短期分支，如 `content/add-paper` 或 `style/sidebar`，预览通过后合并。

本次迁移完成时只保存本地提交，不推送。确认预览后，再将迁移分支合并到 `main` 并推送。GitHub Pages 应从 `main` 的仓库根目录构建 Jekyll；若当前仓库设置不同，需要在发布时确认 Settings → Pages 的构建来源。不提交 `.nojekyll`。

## Google Scholar 引用统计

总引用徽章位于个人介绍第一段，不显示逐篇引用数。`_config.yml` 中的 `google_scholar_id` 为 `DnYC9yoAAAAJ`。首次成功获取的数据保存于 `_data/scholar.json`，构建时直接渲染，所以禁用 JavaScript 或统计服务不可用时仍有真实数据。日期标明快照的更新时间。引用徽章沿用上游的浅灰／浅蓝样式，避免首发时依赖尚未建立的远端统计分支。

`.github/workflows/google_scholar_crawler.yml` 准备了每日抓取（08:17 UTC）和手动运行；首次推送此工作流到 main 时也会触发。成功后只向独立的 `google-scholar-stats` 分支提交两份 JSON，不改 main。页面在正式域名下读取该分支的 CDN 数据，仅接纳同一 Scholar 用户且不早于本地快照的数据；本地 5500 预览读取本地快照。本次仅配置工作流，没有执行任何 push 或远端 Actions。

Google Scholar 可能限制自动访问。初始化快照来自 2026-09-27 首次成功返回的公开主页；后续本机请求出现 HTTP 403，因此定时抓取在 GitHub Actions 环境中的连通性仍需发布后验证。抓取、解析或校验失败会让任务失败并保留上一次数据，不把失败写成 0。不要手工编造引用数，也不要将其他数据库引用数标成 Google Scholar。

本地刷新需要 Python 3、curl、BeautifulSoup4 和 PyYAML：

```bash
python3 -m pip install -r google_scholar_crawler/requirements.txt
python3 google_scholar_crawler/main.py --snapshot _data/scholar.json
python3 -m unittest discover -s google_scholar_crawler -v
```

抓取结果也会写入被忽略的 `google_scholar_crawler/results/`。要刷新发布时自带的快照，成功抓取后提交 `_data/scholar.json`。公开 Scholar ID 不需要设置为 GitHub Secret；工作流仅使用仓库自带的 GITHUB_TOKEN，仓库或组织策略需允许 `contents: write`。Google Analytics 继续关闭。

## 模板更新

模板来源、版本及定制范围见 [docs/template.md](docs/template.md)。以后升级模板时对照上游差异，逐项移植需要的修复，保留本站数据和个人样式。

## 致谢与许可

模板使用 MIT License，保留原 [LICENSE](LICENSE)。感谢 [Acad Homepage](https://github.com/RayeRen/acad-homepage.github.io)、[Academic Pages](https://github.com/academicpages/academicpages.github.io) 与 [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes)。论文、头像及研究图片保留其各自权利归属。
