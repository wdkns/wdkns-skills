# youtube-render-pdf

这个仓库现在只用于托管一个 Codex skill：`youtube-render-pdf`。

它的目标是把 YouTube 上的课程、讲座、技术分享视频，整理成结构化的中文 LaTeX 讲义，并最终产出可编译的 PDF。skill 本身强调以下几点：

- 以视频真实教学内容为主，而不是只依赖字幕转写
- 优先使用原始视频封面作为首页封面图
- 按教学价值提取关键画面、图表、公式和代码片段
- 生成带 `\section{}` / `\subsection{}` 结构的完整 `.tex`
- 最终必须落到可交付的 PDF

## 仓库结构

```text
.
├── LICENSE
├── README.md
└── skills/
    └── youtube-render-pdf/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── assets/
            └── notes-template.tex
```

## 包含内容

- `skills/youtube-render-pdf/SKILL.md`
  skill 的主说明文件，定义适用场景、工作流、写作规则、配图规则和最终交付要求。
- `skills/youtube-render-pdf/assets/notes-template.tex`
  默认 LaTeX 模板，包含首页封面位、盒子样式、代码块样式和正文占位结构。
- `skills/youtube-render-pdf/agents/openai.yaml`
  给 agent UI 使用的显示名称、简介和默认提示。

## 使用方式

如果你想在本地 Codex 环境中使用这个 skill，可以把 `skills/youtube-render-pdf/` 放到你的技能目录中，例如：

```bash
mkdir -p ~/.codex/skills
cp -R skills/youtube-render-pdf ~/.codex/skills/
```

然后在 Codex 中使用这个 skill 处理 YouTube 视频链接，请求生成讲义 `.tex` 和最终 PDF。

除了 coding agent 会自动安装匹配的 `yt-dlp`、`ffmpeg`、`xelatex`、`magick` 等工具，这个 skill 能否成功执行的另一个前提，是运行它的 coding agent 必须具备一定的读图能力。

一个典型任务会要求模型：

- 先读取视频标题、章节、时长、字幕、封面等元数据
- 选择可下载的最高可用视频源用于截图
- 基于字幕时间轴定位关键画面并筛选高价值配图
- 把讲解内容、公式、代码和图示组织成中文讲义
- 用模板生成 `.tex`，并产出最终 PDF

## 适用场景

- 技术课程笔记整理
- YouTube 教学视频转 LaTeX 讲义
- 需要封面图、关键帧和总结章节的高质量课程文档生成

## License

仓库保留了根目录下原有的 `LICENSE` 文件。使用、分发或二次修改时，请以该许可证为准。
