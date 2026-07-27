# wdkns-skills

## Skills 一览

- [`youtube-render-pdf`](skills/youtube-render-pdf/)：将 YouTube 讲座、教程或技术分享整理为结构化、配图丰富的中文 LaTeX 讲义，并编译交付最终 PDF。
  - [`bilibili-render-pdf`](skills/bilibili-render-pdf/)：面向 Bilibili 视频生成中文 LaTeX 讲义和最终 PDF，并针对字幕缺失、登录高清与分 P 视频提供专门处理流程。
- [`subtitle-refine`](skills/subtitle-refine/)：在保持时间轴同步和原意不变的前提下精修 ASR 生成的中文 SRT 字幕，并通过校验脚本产出可发布的完整字幕。
- [`tensor-formula-viz`](skills/tensor-formula-viz/)：把张量、矩阵或向量公式及其代码路径转换为形状对齐、语义清晰且适合演示的计算示意图。

## video-render-pdf skills

这个仓库托管两个 Codex skill，用于将视频讲座转换为结构化的中文 LaTeX 讲义和最终 PDF。

| Skill | 平台 | 说明 |
|-------|------|------|
| `youtube-render-pdf` | YouTube | 原始版本，利用 YouTube CC 字幕和章节结构 |
| `bilibili-render-pdf` | Bilibili (B站) | 适配 B 站的字幕缺失、登录高清、分P视频等特点 |

两个 skill 共享相同的写作规则、配图策略和 LaTeX 模板，但在素材获取阶段有平台特定的差异。

### Bilibili 版的核心差异

- **字幕三级回退**：CC 字幕 → Whisper 语音转写 → 纯视觉模式（B 站大量视频无 CC 字幕）
- **登录获取高清**：1080P+ 需要 cookies（`yt-dlp --cookies-from-browser chrome`）
- **分P视频处理**：自动检测多 P，询问用户处理范围
- **平台话术过滤**：额外排除"一键三连"、"关注投币"等非教学内容
- **额外依赖**：`whisper`（openai-whisper）用于语音转写

### 共同特点

- 以视频真实教学内容为主，而不是只依赖字幕转写
- 优先使用原始视频封面作为首页封面图
- 按教学价值提取关键画面、图表、公式和代码片段
- 生成带 `\section{}` / `\subsection{}` 结构的完整 `.tex`
- 最终必须落到可交付的 PDF

### 使用方式

如果你想在本地 Codex 环境中使用这些 skill，可以把对应目录放到你的技能目录中：

```bash
mkdir -p ~/.codex/skills

# YouTube 版
cp -R skills/youtube-render-pdf ~/.codex/skills/

# Bilibili 版
cp -R skills/bilibili-render-pdf ~/.codex/skills/
```

然后在 Codex 中使用对应 skill 处理视频链接，请求生成讲义 `.tex` 和最终 PDF。

### 外部依赖

| 工具 | 两个 skill 都需要 | 仅 Bilibili 版需要 |
|------|:-:|:-:|
| `yt-dlp` | ✓ | |
| `ffmpeg` | ✓ | |
| `xelatex` (TeX Live + CTeX) | ✓ | |
| `magick` (ImageMagick) | ✓ | |
| `whisper` (openai-whisper) | | ✓ |

此外，运行 skill 的 coding agent 必须具备一定的读图能力，否则很难选择关键帧，很难做到图文align（即至少是一个还不错的 vlm model，ps. MiniMax 2.7 只是一个纯文本模型）。


### subagents 的触发

- codex 中对于 `spwan_agent` 的触发，规定的比较死，"Only use spawn_agent if and only if the user explicitly asks for sub-agents, delegation, or parallel agent work."，即需要我们在 query 中显式地要求，才可以触发 subagents

```
$youtube-render-pdf   https://www.youtube.com/watch?v=vXb2QYOUzl4 请 spwan 多 sub agents 执行，隔离上下文，避免 master agent 的“上下文焦虑”， 形成一个完整全面的 pdf：
  - 1 个 outline agent：先定全局目录、术语、符号表、章节边界等
  - 5 个 writer agents：各自直接写成完整章节草稿，落盘成 section_*.tex
  - 1 个 figure agent：单独负责抽帧、筛图、crop、脚本生成新的示意图、图注和时间脚注等；
  - 1 个 consistency agent：检查重复定义、前后术语不一致、章节衔接断裂
```

### tips

- 强烈建议在 codex 基于这个 skill 给出第一版结果之后，增加一个follow up question：`spwan 一个独立的reviewer agent，基于原始字幕文件，check 是否有重要、细节及有趣等一切有意的信息的漏召回，仅反馈，不修改，不断交互，直至reviewer agent 觉得 tex 信息已完备。`
  - 以缓解 ai extraction/summary 的共性问题，就是召回不足；

### License

仓库保留了根目录下原有的 `LICENSE` 文件。使用、分发或二次修改时，请以该许可证为准。
