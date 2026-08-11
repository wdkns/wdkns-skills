---
name: bilibili-render-pdf
description: Generate a professional, detailed, figure-rich course note from a Bilibili lecture, tutorial, or technical talk. Supports two output formats: LaTeX→PDF (default) and Markdown. Use when the user provides a Bilibili URL (BV number) and wants structured Chinese teaching notes that combine the video's title, chapters, diagrams, formulas, code, subtitle explanations, the original video cover on the front page, and a final synthesis chapter, with key frames extracted from the highest usable video resolution and inserted as figures. Falls back to Whisper speech-to-text when no CC subtitles are available.
---

# Bilibili Render PDF

Use this skill to turn a Bilibili video into a complete, structured course note.

This skill extends the `youtube-render-pdf` workflow with Bilibili-specific adaptations for subtitle scarcity, login-gated high resolution, multi-part (分P) videos, and platform-specific non-teaching content.

## Output Format Selection

This skill supports two output formats. Choose based on user request or context:

- **LaTeX → PDF** (default): Use when the user wants a PDF, or does not specify a format. Produces a compileable `.tex` file and a rendered `.pdf`.
- **Markdown**: Use when the user explicitly asks for Markdown / MD notes, or when a LaTeX toolchain is unavailable. Produces a self-contained `.md` file with embedded images.

When the user does not specify, default to LaTeX → PDF.

## Bilibili vs YouTube: Key Differences

| Aspect | Handling |
|--------|----------|
| **Subtitle scarcity** | Try CC subtitles first → fall back to Whisper speech-to-text → visual-only mode |
| **Login-gated HD** | 1080P+ requires cookies; prompt the user to use `yt-dlp --cookies-from-browser chrome` |
| **Multi-part videos** | Detect 分P videos and ask the user which parts to process |
| **URL formats** | Support `bilibili.com/video/BVxxxxxxx` and `b23.tv` short links |
| **Danmaku** | Do not use danmaku as a teaching content source (too noisy); use only CC subtitles or Whisper output |

## Goal

Produce a professional Chinese lecture note from a Bilibili URL.

The output must:

- use the video's actual teaching content rather than subtitle transcription alone
- place the video's original cover image on the front page whenever available
- include all necessary high-value key frames as figures, without adding redundant screenshots
- end with a final synthesis section that includes the speaker's substantive closing discussion and your own distilled takeaways
- be structurally organized into clear sections and subsections

### LaTeX-specific requirements (when LaTeX mode is selected)

- be a complete `.tex` document from `\documentclass` to `\end{document}`
- use `\section{...}` and `\subsection{...}` for structure
- be compiled successfully to PDF as part of the final delivery

### Markdown-specific requirements (when Markdown mode is selected)

- be a complete, self-contained `.md` file
- use `##` for sections and `###` for subsections
- include a YAML frontmatter block with video metadata (title, author, date, channel, URL, cover path)
- use Markdown image syntax `![alt](path)` for all figures
- use `> **💡 核心概念**` blockquotes for importantbox-equivalent content
- use `> **📖 背景知识**` blockquotes for knowledgebox-equivalent content
- use `> **⚠️ 注意**` blockquotes for warningbox-equivalent content
- use `> **💬 原始对话（时间区间）**` blockquotes for dialoguebox-equivalent content
- use `$...$` for display math
- use fenced code blocks with language tags for code
- record figure time provenance as a caption line below each image, e.g. `*视频画面时间区间：00:12:31--00:12:46*`

## Pedagogical Standard

The notes must read like a strong human teacher is guiding the reader through the material.

- organize each major section so the reader first understands the motivation, then the main idea, then the mechanism, then the example or evidence, and finally the takeaway
- be patient and explicit about logical transitions; make it clear why the speaker introduces a concept, what problem it solves, and how the next idea follows
- aim for deep-but-accessible explanations: keep the technical depth, but introduce formalism only after giving intuition in plain language
- when a section is dense, break it into smaller subsections that progressively build understanding rather than compressing everything into one long derivation
- do not dump subtitle content in chronological order; rewrite it into a teaching sequence with clear intent, contrast, and buildup

## Source Acquisition

### Metadata Inspection

1. Inspect the video metadata first.
   Prefer title, chapters, duration, thumbnail availability, and subtitle availability before writing.

2. Detect multi-part (分P) videos.
   List all parts and ask the user which parts to process before downloading.

### Subtitle Acquisition (Three-Level Fallback)

**Priority 1: CC subtitles (platform-embedded)**

Use manual subtitles over auto-generated subtitles when both are available.
Prefer `zh-Hans`, `zh-CN`, `zh`, or `ai-zh` subtitle tracks.
Preserve the subtitle timestamps; do not flatten subtitles into plain text too early if figures still need to be located.

```
yt-dlp --write-subs --sub-langs "zh-Hans,zh-CN,zh,ai-zh" --convert-subs srt \
  --skip-download -o "%(title)s.%(ext)s" "<URL>"
```

**Priority 2: Whisper speech-to-text (when no CC subtitles are available)**

Extract audio first, then transcribe with Whisper to produce a timestamped SRT file.

If `whisper` is not on the system PATH, try the Box venv path:

```
# Try system PATH first
whisper audio.wav --model medium --language zh --output_format srt --output_dir .

# If not found, use the full path (Box venv on macOS)
"/Users/$USER/Library/Application Support/Box/boxenv/bin/whisper" \
  audio.wav --model medium --language zh --output_format srt --output_dir .
```

**Priority 3: Visual-only mode (when audio quality is too poor)**

Skip subtitles entirely and rely on dense frame sampling to extract teaching content from the video frames alone.

### Video and Cover Download

1. Acquire the video's original cover image before writing the `.tex`.
   Prefer the highest-resolution thumbnail exposed by the platform metadata.
   Save the selected cover locally and reference that local asset from the front page.

2. Prefer the best usable video source for figure extraction.
   Probe formats and choose the highest resolution that is actually downloadable in the current environment.
   Note that 1080P+ on Bilibili typically requires login cookies.

3. Keep all source artifacts local when practical.
   Typical working artifacts are metadata, the downloaded cover image, a timestamped subtitle file (CC or Whisper-generated), optional cleaned transcript text, a local video file, and extracted frames.

## Long Video Strategy

For longer videos, do not rely on a single monolithic pass.

- If the video is longer than 20 minutes, or the subtitle file contains more than 300 subtitle entries, split the work into smaller segments.
- Prefer chapter boundaries or 分P boundaries for splitting. If those are unavailable or too uneven, split by coherent time windows or subtitle ranges.
- When subagents are available, spawn multiple subagents in parallel for different segments so coverage stays high and detail is not lost.
- Give each subagent a concrete segment boundary and require it to return: the segment's teaching goal, the core claims, important formulas or code, required figures with time provenance, and any ambiguities that need integration-time resolution.
- Keep a small overlap between neighboring segments when the explanation crosses boundaries, then deduplicate during integration.
- The main agent must integrate the segment outputs into one unified outline and one coherent final narrative. The final PDF must read like a single lecture note, not a concatenation of chunk summaries.

## Teaching Content Rules

Build the notes from all of the following when available:

- video title and chapter structure
- the video's original cover image and key metadata
- on-screen diagrams, formulas, tables, plots, and architecture slides
- subtitle explanations, examples, and verbal emphasis
- short high-signal original dialogue segments in interview, panel, podcast, or conversation videos, when the exact wording adds presence, humor, intuition, or unusually compact information
- code snippets shown or described in the talk

Skip content that does not contribute to the actual lesson:

- greetings
- small talk
- routine back-and-forth that does not add information, tension, humor, intuition, or teaching value
- sponsorship
- channel logistics (一键三连, 关注投币, etc.)
- closing pleasantries

Keep the speaker's closing discussion when it carries actual teaching value, such as synthesis, limitations, future work, tradeoffs, advice, or open questions.

## Writing Rules

1. Write the notes in Chinese unless the user explicitly requests another language.

2. Organize the document with `\section{...}` and `\subsection{...}`.
   Reconstruct the teaching flow when needed; do not blindly mirror subtitle order.
   Each section should answer, in order when applicable: what problem is being solved, why simpler views are insufficient, what the core idea is, how it works, and what the reader should retain.

   Avoid overusing the "不是……而是……" sentence pattern.
   Use it only when the video itself establishes a real contrast and that contrast materially clarifies the mechanism.

   Do not use vague or overly abstract phrasing.
   Ground claims in concrete mechanisms, examples, variables, steps, observed phenomena, timestamps, figures, or speaker-provided evidence whenever possible.

3. Start from the appropriate template:
   - LaTeX mode: copy `assets/notes-template.tex`
   - Markdown mode: copy `assets/notes-template.md`
   Fill in the metadata block, including the local cover image path, and replace the body content block with the generated notes.

4. The front page must include the video's original cover image when available.
   Place it on the first page rather than burying it later in the document.
   Keep it visually distinct from in-body teaching figures.

5. Use figures whenever they materially improve explanation.
   Include as many figures as are necessary for teaching clarity, even if that means many figures across the document.
   Do not optimize for a small figure count; optimize for explanatory coverage and readability.
   Good figures are key formulas, diagrams, tables, plots, visual comparisons, pipeline schedules, architecture views, and stage-by-stage visual progressions.

6. Do not place images inside custom message boxes (LaTeX) or blockquote callouts (Markdown).

7. When a mathematical formula appears:
   first explain in plain Chinese what the formula is trying to express and why it appears
   show it in display math using `$...$`
   then immediately follow with a flat list that explains every symbol

8. When code examples appear:
   explain the role of the code before the listing and summarize the expected behavior after it when useful
   - LaTeX mode: wrap them in `lstlisting` with a descriptive `caption`
   - Markdown mode: use fenced code blocks with a language tag, preceded by a brief intro paragraph

9. Highlight teaching signals deliberately and repeatedly when the content justifies it:
   - LaTeX mode: use `importantbox`, `knowledgebox`, `warningbox`, `dialoguebox` custom boxes
   - Markdown mode: use blockquote callouts:
     - `> **💡 核心概念**` for importantbox-equivalent content
     - `> **📖 背景知识**` for knowledgebox-equivalent content
     - `> **⚠️ 注意**` for warningbox-equivalent content
     - `> **💬 原始对话（时间区间）**` for dialoguebox-equivalent content
   Use `importantbox` / 💡 for core concepts the reader must walk away with, including formal definitions, central claims, key mechanism summaries, theorem-like statements, critical algorithm steps, and compact restatements of the main idea after a dense explanation
   Use `knowledgebox` / 📖 for background and side knowledge that improves understanding without being the main thread, including prerequisite reminders, historical lineage, engineering context, design tradeoffs, terminology comparisons, and intuition-building analogies
   Use `warningbox` / ⚠️ for common misunderstandings and failure points, including notation overload, hidden assumptions, misleading heuristics, easy-to-make implementation mistakes, causal confusions, off-by-one style reasoning errors, and places where the speaker contrasts a wrong intuition with the correct one
   Use `dialoguebox` / 💬 only for conversation-heavy videos when a brief original dialogue segment is high-information, funny, vivid, or especially intuitive, and preserving the speaker's wording gives the reader a stronger sense of being present in the discussion
   a dialogue segment may contain either one exchange or several tightly connected turns, such as a question, follow-up, pushback, clarification, and answer sequence
   keep dialogue snippets short: preserve speaker labels and a concrete timestamp or interval, lightly clean obvious ASR errors only when confident, and follow the box with prose that explains why the dialogue segment matters
   do not use dialogue callouts for greetings, filler, long transcript dumps, or dialogue that would be clearer as ordinary summarized exposition
   there is no quota of one callout per section; add multiple callouts in a section when the material contains multiple distinct teaching signals
   each callout should carry a specific pedagogical payload rather than generic emphasis
   prefer placing a callout immediately after the paragraph, derivation, or example that motivates it
   routine exposition should stay in normal prose; callouts are for high-signal takeaways, not decoration
   figures must stay outside all callout boxes / blockquotes

10. End every major section with a `### 本章小结` (Markdown) or `\subsection{本章小结}` (LaTeX).
    Add `### 拓展阅读` (Markdown) or `\subsection{拓展阅读}` (LaTeX) when there are one or two worthwhile external links.

11. End the document with a final top-level section such as `## 总结与延伸` (Markdown) or `\section{总结与延伸}` (LaTeX).
    That final section must include:
    - the speaker's substantive closing discussion, excluding routine sign-off language
    - your own structured distillation of the core claims, mechanisms, and practical implications
    - your expanded synthesis, including conceptual compression, cross-links between sections, and any careful generalization that stays faithful to the video
    - concrete takeaways, open questions, or next steps when the material supports them

12. Do not emit `[cite]`-style placeholders anywhere in the document.

## Figure Handling

Select figures by necessity and teaching value, not by an arbitrary quota or a bias toward keeping the document visually sparse.

When locating candidate frames, bias strongly toward recall before precision.
It is better to inspect too many nearby candidates first than to miss the one frame where the slide, formula, table, or diagram is finally fully revealed and readable.

Frame understanding must come from direct visual inspection.

- Use the `view image` tool to inspect candidate frames and crops before deciding what they show, how they should be described, and whether they are complete enough to include.
- Do not use OCR tools such as `tesseract` as a substitute for visual understanding of a frame.
- Do not infer a frame's semantic content only from nearby subtitles, filenames, or timestamps without checking the image itself.
- Contact sheets, montages, and tiled strips are good for recall, but final keep-or-reject decisions and semantic naming must be based on actual image inspection with `view image`.

### Frame Selection Checklist

Before inserting any video frame, first inspect several nearby candidates from the same subtitle-aligned interval and apply this checklist. If any item fails, reject the frame and keep searching nearby rather than forcing an approximate match.

- Relevance: the frame must directly support the exact concept discussed in the surrounding paragraph or subsection, not just the same broad topic.
- Required content visible: every visual element referenced in the text must already be visible in the frame.
- Fully revealed state: when slides, whiteboards, animations, or dashboards build progressively, use the final fully populated readable state rather than an intermediate state.
- Best nearby candidate: compare multiple nearby frames and prefer the one that is both most complete and most readable.
- Readability: text, formulas, labels, and diagram structure must be legible enough to justify inclusion.

### Frame Naming

- Use neutral timestamp-based names for raw candidate frames. Do not assign semantic names before inspecting the actual frame content.
- Rename a frame semantically only after visually confirming what is fully visible in the image.
- The semantic filename must describe the frame's actual visible content, not a guess based on subtitles, nearby narration, or the intended paragraph topic.
- If the frame is partially revealed, transitional, or ambiguous, keep searching and do not lock in a semantic name yet.

- Use the timestamped subtitle file (CC or Whisper-generated SRT) as the primary locator for key-frame search.
- First identify the subtitle span that corresponds to the concept, example, formula, or visual explanation being discussed.
- Then search within that subtitle-aligned time interval, and slightly around its boundaries when needed, to find the best readable frame.
- Do not jump directly from one guessed timestamp to one extracted frame.
  First generate a dense candidate set across the relevant interval, then inspect and down-select.
- Prefer tools that help you inspect many nearby candidates at once, such as `magick montage`, contact sheets, tiled frame strips, or equivalent workflows.
  Use them to maximize recall and avoid missing the frame where the visual content is fully present.
- When the visual is a progressive PPT reveal, animation build, whiteboard accumulation, or dashboard state change, explicitly search for the final fully populated state.
  Do not stop at the first frame that seems approximately correct.
- If several nearby candidates differ only by progressive reveal state, keep checking until you find the frame with the most complete readable information.
- When in doubt between a sparse early frame and a denser later frame from the same explanation window, prefer the later frame if it is materially more complete and still readable.
- Include every figure that is necessary to explain the content well.
- It is acceptable, and often desirable, to include several figures within one section or subsection when the video builds an idea in stages.
- Omit repetitive or low-information frames.
- Extract frames near chapter boundaries and explanation peaks when chapters exist, but still validate them against subtitle timing.
- Search nearby timestamps when the first extracted frame catches an animation transition.
- Crop, enlarge, or isolate the relevant region when the full frame is too loose.
- When a slide reveals content progressively, capture the final readable state and add intermediate frames only when they teach a genuinely different step.
- For dense visual sections, it is acceptable to over-sample first and discard later.
  Do not optimize candidate count so early that key visual states are never inspected.
- Prefer a sequence of necessary figures over one overloaded figure with unreadable labels.
- Preserve readability of formulas and labels.

## Figure Time Provenance

Whenever the `.tex` or PDF references a specific video frame, or a crop derived from a video frame, record its source time interval on the same page as a bottom footnote.

- The footnote must show the concrete time interval, for example `00:12:31--00:12:46`.
- The interval should come from the subtitle-aligned segment used to locate the figure, not from a vague chapter-level estimate.
- If the figure is a crop, the footnote still refers to the original video time interval of the source frame or subtitle span.
- If several nearby frames in one figure all come from the same subtitle interval, one clear footnote is enough.
- Keep the figure and its time footnote anchored to the same page; prefer layouts such as `[H]`, a non-floating block, or another stable placement when ordinary floats would separate them.

In Markdown mode, record the time interval as an italic caption line directly below the image:

```
![图示描述](path/to/figure.png)

*视频画面时间区间：00:12:31--00:12:46。若为裁剪图，时间区间仍对应原视频画面。*
```

## Visualization

For concepts that remain hard to explain with only screenshots and prose, add accurate visualizations.

Two acceptable routes:

- generate LaTeX-native visualizations with TikZ or PGFPlots (LaTeX mode only)
- generate figures ahead of time with scripts and include them as images (both modes)

For script-generated illustrations, prefer Python tools such as `matplotlib` and `seaborn` when they are the clearest way to produce an accurate teaching figure.

When a visualization is generated externally:

- LaTeX mode: export the figure as `pdf` so it can be inserted into the `.tex` without rasterization loss; prefer vector output
- Markdown mode: export as `png` or `svg`; `png` is more universally supported in Markdown viewers

When the source material contains relationships, results, or equations that would be clearer when redrawn than when shown as a screenshot, prefer rebuilding them with LaTeX-native tools (LaTeX mode) or with `matplotlib` / `seaborn` (both modes).

Use visualizations for:

- process flows, pipelines, and architecture overviews
- curves and charts such as scaling laws, training curves, benchmark results, and ablation comparisons
- distributions, correlations, heatmaps, and other plots that explain data relationships
- complex functions, surfaces, contour plots, and geometric intuition figures
- tables or comparisons that become clearer when redrawn as charts
- summary diagrams that compress a section's core mechanism or takeaway into one figure

Do not add decorative graphics that do not teach anything.

## Final Checklist

Before delivery, verify all of the following:

- no important teaching content has been dropped, and no concrete but critical detail has been lost during condensation, restructuring, or summarization
- the text and figures are aligned: each inserted frame supports the surrounding explanation, necessary crops have been applied, and the chosen frame shows the fullest relevant information rather than a transitional or incomplete state
- the document is visually rich enough for teaching: check whether more high-information key frames should be added, and whether additional LaTeX-native or Python-script-generated illustrations would improve clarity

## Delivery

Deliver all of the following:

- the Whisper-generated SRT subtitle file, if speech-to-text was used
- the downloaded cover image referenced on the front page
- any extracted or generated figure assets referenced by the document
- the final `.tex` file and the compiled `.pdf` file (LaTeX mode), or the final `.md` file (Markdown mode)
  - must use a reasonable Chinese filename, e.g., `[中文视频标题]_notes.tex` and `[中文视频标题]_notes.pdf`, or `[中文视频标题]_notes.md`

## Asset

- `assets/notes-template.tex`: default LaTeX template to copy and fill
- `assets/notes-template.md`: default Markdown template to copy and fill
