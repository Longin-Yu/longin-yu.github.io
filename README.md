# Hao Yu · Academic Homepage

个人主页，基于 [RayeRen/acad-homepage.github.io](https://github.com/RayeRen/acad-homepage.github.io) 的 Jekyll 模板。线上地址为 https://longin-yu.github.io/ 。

## 日常修改

| 内容 | 文件 |
| --- | --- |
| 姓名、学校、邮箱、头像、主页链接 | `_config.yml` |
| 英文介绍、栏目顺序 | `_pages/about.md` |
| 论文与团队项目 | `_data/publications.json` |
| 顶部导航 | `_data/navigation.yml` |
| 单篇论文的 HTML | `_includes/publication.html` |
| 个人样式调整 | `_sass/_custom.scss` |
| 图片 | `assets/images/` |

论文数据的 `section` 分别为 `selected`、`publications`、`projects`；同一栏内按照 JSON 顺序展示。作者列表保留原始顺序，`Hao Yu` 自动加粗，`*` 显示为共同贡献标记。团队项目只展示标题、署名、发表信息和资源链接，不填写个人职责。

代表作可包含 `image`、`imageFull`、`imageAlt`、`imageWidth`、`imageHeight`、`imageCaption`、`topic` 和 `description`。本地资源路径相对仓库根目录，如 `assets/images/comrope.png`。请让 `id` 唯一，已发布条目尽量保留原 ID，避免原有锚点失效。

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

## 可选功能与模板更新

Google Analytics 和 Scholar 引用统计默认关闭。没有自动抓取或写入远端分支的工作流。保留 `google_scholar_crawler/` 作为上游可选功能的参考；配置统计功能时需先生成并发布统计 JSON，再设置 `google_scholar_stats_enabled: true`、添加相应展示节点。只打开开关不会自动生成统计数据。

模板来源、版本及定制范围见 [docs/template.md](docs/template.md)。以后升级模板时对照上游差异，逐项移植需要的修复，保留本站数据和个人样式。

## 致谢与许可

模板使用 MIT License，保留原 [LICENSE](LICENSE)。感谢 [Acad Homepage](https://github.com/RayeRen/acad-homepage.github.io)、[Academic Pages](https://github.com/academicpages/academicpages.github.io) 与 [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes)。论文、头像及研究图片保留其各自权利归属。
