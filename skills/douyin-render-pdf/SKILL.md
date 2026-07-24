---
name: douyin-render-pdf
description: Generate a professional, detailed, figure-rich LaTeX course note and final PDF from a Douyin long-form lecture, tutorial, or technical talk. Use when the user provides a Douyin long URL, short URL, share URL, or jingxuan modal URL and wants structured Chinese teaching notes with cover image, transcript, chapters, inspected key frames, and a rendered PDF.
---

# Douyin Render PDF

Use this skill to turn a Douyin long-form video into a complete, compileable `.tex` note and a rendered PDF.

This skill follows the same writing standard, figure strategy, LaTeX template, and final-delivery expectations as `youtube-render-pdf` and `bilibili-render-pdf`.
Its platform-specific work is concentrated in source acquisition: Douyin URL normalization, cookie-assisted extraction, page `RENDER_DATA` fallback, subtitle fallback, chapter handling, and platform UI cleanup.

## Douyin vs YouTube and Bilibili: Key Differences

| Aspect | Handling |
|--------|----------|
| **URL formats** | Support `douyin.com/video/<id>`, `douyin.com/jingxuan?modal_id=<id>`, `v.douyin.com/...`, and `iesdouyin.com/share/video/<id>/...` |
| **Cookie-sensitive extraction** | Try browser cookies with `yt-dlp --cookies-from-browser chrome` or `edge`; use cookies as normal logged-in access, not as a bypass mechanism |
| **`yt-dlp` instability** | If `yt-dlp` fails, parse the Douyin page `RENDER_DATA` and validate exposed video URLs before asking for a local file |
| **Subtitles** | Probe platform/page subtitles first; when no usable structured subtitle exists, treat Whisper transcription as the main path |
| **Chapters** | Use Douyin `chapterInfo` when present; otherwise rebuild the outline from ASR text, on-screen headings, pauses, and topic changes |
| **Series / multi-part videos** | Detect Douyin collection/series metadata from `mixInfo` and `seriesInfo`; ask which episode range to process when a full episode list or intended scope is unclear |
| **Layout** | Detect horizontal vs vertical layout; crop or ignore platform UI, bottom captions, side buttons, and decorative wrappers when they do not teach |
| **Platform noise** | Filter likes, follows, comments, live-room traffic, commerce calls, hashtags, and title hooks unless they are part of the lesson itself |

## Goal

Produce a professional Chinese lecture note from a Douyin long-form video.

The output must:

- use the video's actual teaching content rather than subtitle transcription alone
- place the video's original cover image on the front page of the `.tex` and rendered PDF whenever available
- include all necessary high-value key frames as figures, without adding redundant screenshots
- use Douyin `chapterInfo` or reconstructed chapters to build a coherent teaching outline
- end with a final synthesis section that includes the speaker's substantive closing discussion and your own distilled takeaways
- be structurally organized with `\section{...}` and `\subsection{...}`
- be a complete `.tex` document from `\documentclass` to `\end{document}`
- be compiled successfully to PDF as part of the final delivery

## Source Acquisition

### Safety and Cookie Rules

Use cookies only to access content available through the user's normal logged-in browser session.

- Prefer `--cookies-from-browser chrome`; if Chrome is unavailable, try `--cookies-from-browser edge`.
- If the user provides a Netscape-format cookie file, use `--cookies cookies.txt`.
- Never ask the user to paste raw cookie values into the chat.
- Do not include cookie files, browser profiles, downloaded cache files, or temporary credentials in final deliverables or commits.
- Do not attempt to bypass captcha, rate limits, account restrictions, or access controls.
- If link extraction fails after normal browser cookies and page parsing, ask the user for a local video file and continue from that file.

### URL Normalization

Normalize all supported URLs to an aweme/video ID before planning the download.

Supported input forms:

- `https://www.douyin.com/video/<aweme_id>`
- `https://www.douyin.com/jingxuan?modal_id=<aweme_id>`
- `https://v.douyin.com/<short_code>/`
- `https://www.iesdouyin.com/share/video/<aweme_id>/...`

For `v.douyin.com` links, follow redirects first and extract the ID from the resolved `iesdouyin.com/share/video/<id>` or Douyin page URL.
For `jingxuan` links, extract `modal_id`.
Keep the original URL and the normalized ID in local metadata notes so later figures, transcripts, and chapters can be traced back to the source.

### Metadata Inspection

Inspect metadata before writing.
Prefer title, author, description, hashtags, duration, cover image, dimensions, chapter availability, collection/series availability, subtitle availability, and video URL availability.

Recommended order:

1. Try page inspection without cookies, especially `https://www.douyin.com/jingxuan?modal_id=<aweme_id>`.
   Parse embedded `RENDER_DATA` when present.
2. Try `yt-dlp` metadata extraction without cookies.
3. Retry `yt-dlp` metadata extraction with browser cookies.
4. If `yt-dlp` still fails, use the parsed page data if it exposes valid video and cover URLs.

Use whichever command form works in the environment:

```bash
yt-dlp --skip-download --dump-single-json "<URL>"
python -m yt_dlp --skip-download --dump-single-json "<URL>"
```

Cookie-assisted variants:

```bash
yt-dlp --cookies-from-browser chrome --skip-download --dump-single-json "<URL>"
yt-dlp --cookies-from-browser edge --skip-download --dump-single-json "<URL>"
yt-dlp --cookies cookies.txt --skip-download --dump-single-json "<URL>"
```

### Video and Cover Download

Acquire the original cover image before writing the `.tex`.
Prefer `originCover` or the highest-resolution cover exposed by metadata or `RENDER_DATA`.
Save the selected cover locally and reference that local asset from the front page.

Prefer the best usable video source for figure extraction.
When `yt-dlp` works, choose the highest resolution that is actually downloadable in the current environment:

```bash
yt-dlp --cookies-from-browser chrome -f "bv*[ext=mp4]+ba/b[ext=mp4]/b" -o "source.%(ext)s" "<URL>"
```

When `yt-dlp` fails but page data exposes direct video URLs:

- validate the candidate URL with a `HEAD` request or a small byte-range request before downloading the whole file
- prefer H264 MP4 for compatibility unless H265 is the only reliable high-quality source
- download immediately after validation because signed URLs may expire
- keep the validated source URL only in local working notes if it is temporary or signed

If no URL path works, ask the user for a local video file.
Treat the local video as a first-class source, not as a degraded mode.

### Subtitle Acquisition

Use a three-level fallback.

**Priority 1: platform or page subtitles**

Probe `yt-dlp` subtitles and page metadata.
Use manual subtitles over auto-generated subtitles when both are available.
Prefer Chinese tracks such as `zh-Hans`, `zh-CN`, `zh`, or `ai-zh`.
Preserve timestamps; do not flatten subtitles into plain text too early if figures still need to be located.

```bash
yt-dlp --cookies-from-browser chrome --write-subs --sub-langs "zh-Hans,zh-CN,zh,ai-zh" --convert-subs srt \
  --skip-download -o "%(title)s.%(ext)s" "<URL>"
```

**Priority 2: Whisper speech-to-text**

If no usable structured subtitles are available, extract audio from the downloaded video or local file and transcribe it.

```bash
ffmpeg -i source.mp4 -vn -ac 1 -ar 16000 audio.wav
whisper audio.wav --model medium --language zh --output_format srt --output_dir .
```

For long videos, prefer the local Whisper CLI over a Python API call unless the user explicitly asks otherwise.
Probe GPU availability, but if CUDA is unavailable or unsupported, record that fact and continue with CPU rather than blocking.
Do not let one monolithic Whisper run become the only path: for videos longer than about 20 minutes, split audio into manageable chunks, transcribe each chunk, and merge SRT timestamps back to the global timeline.
Keep the chunk outputs until the merged SRT is verified, then deliver only the merged subtitle file unless the user asks for intermediate artifacts.

**Priority 3: visual-only mode**

Use this only when audio is too poor or unavailable.
Increase frame sampling density and rely on visible headings, diagrams, formulas, and scene transitions.

### Series and Multi-Part Handling

Douyin long-form videos can belong to a collection or series.
This is not identical to Bilibili's multi-part (`分P`) structure, but it can play the same role when the user wants a complete multi-episode lecture note.

When page metadata is available, inspect:

- `mixInfo.mixId`, `mixInfo.mixName`, `mixInfo.currentEpisode`, `mixInfo.totalEpisode`
- `seriesInfo.seriesId`, `seriesInfo.seriesName`, `seriesInfo.currentEpisode`, `seriesInfo.totalEpisode`
- `seriesInfo.stats.currentEpisode`, `seriesInfo.stats.totalEpisode`, `seriesInfo.stats.updatedToEpisode`

If these fields show that the current video is part of a collection or series:

1. Record the collection or series name, ID, current episode, and total episode count in local metadata.
2. Check whether the page or extractor also exposes a full episode list with per-episode URLs or aweme IDs.
3. If a reliable episode list is available, list the episodes and ask the user which episode range to process before downloading multiple videos.
4. If only current/total episode metadata is available, do not invent the missing episode URLs.
   Process the current video only unless the user provides the other links or explicitly asks you to search for them.
5. Do not merge multiple episodes into one note unless the requested scope is clear.

Use collection/series boundaries as higher-level organization when processing multiple videos.
Use `chapterInfo` inside each episode for local section boundaries.

### Chapter Handling

Use Douyin `chapterInfo` when it exists.
Treat platform chapters as useful initial boundaries, not as unquestionable structure.
Verify chapter names, timestamps, and thumbnails against the transcript and video frames before using them in the final outline.

If `chapterInfo` is absent or too coarse, reconstruct the outline from:

- ASR subtitle topic shifts
- on-screen titles and section cards
- pauses and transition language
- visual changes, diagram changes, and example boundaries
- the title, description, hashtags, and speaker framing

Do not assume Douyin long-form videos lack chapters.
Do not assume chapters are present either.

## Long Video Strategy

For longer videos, do not rely on a single monolithic pass.

- If the video is longer than 20 minutes, or the subtitle file contains more than 300 subtitle entries, split the work into smaller segments.
- If the video is part of a requested collection or series, process each selected episode as its own major unit before integrating the final note.
- Prefer verified `chapterInfo` boundaries when available.
- If chapters are unavailable or uneven, split by coherent time windows or subtitle ranges.
- When subagents are available and the user explicitly asked for parallel agent work, spawn multiple subagents for different segments so coverage stays high and detail is not lost.
- Give each subagent a concrete segment boundary and require it to return: the segment's teaching goal, core claims, important formulas or code, required figures with time provenance, and ambiguities that need integration-time resolution.
- Keep a small overlap between neighboring segments when the explanation crosses boundaries, then deduplicate during integration.
- The main agent must integrate segment outputs into one unified outline and one coherent final narrative.

## Teaching Content Rules

Build the notes from all of the following when available:

- video title, description, and verified chapter structure
- the video's original cover image and key metadata
- platform `chapterInfo` thumbnails as figure candidates, after visual inspection
- on-screen diagrams, formulas, tables, plots, code, and visual comparisons
- subtitle explanations, examples, and verbal emphasis
- short high-signal original dialogue segments in conversation-heavy videos, when exact wording adds presence, humor, intuition, or unusually compact information

Skip content that does not contribute to the actual lesson:

- greetings
- small talk
- routine engagement prompts
- sponsorship
- Douyin logistics such as likes, follows, comments, live-room traffic, group buying, shopping-window calls, and creator-growth slogans
- hashtags, captions, and title hooks when they are only packaging
- closing pleasantries

Keep platform references only when they are part of the teaching content, such as a video analyzing platform mechanics, marketing, e-commerce, recommendation systems, creator operations, or social behavior.
Do not scrape or use comment-section content as a teaching source unless the user explicitly asks for it.

Keep the speaker's closing discussion when it carries actual teaching value, such as synthesis, limitations, future work, tradeoffs, advice, or open questions.

## Writing Rules

1. Write the notes in Chinese unless the user explicitly requests another language.

2. Organize the document with `\section{...}` and `\subsection{...}`.
   Reconstruct the teaching flow when needed; do not blindly mirror subtitle order.
   Each section should answer, in order when applicable: what problem is being solved, why simpler views are insufficient, what the core idea is, how it works, and what the reader should retain.

   Avoid overusing the "不是...而是..." sentence pattern.
   Use it only when the video itself establishes a real contrast and that contrast materially clarifies the mechanism.

   Do not use vague or overly abstract phrasing.
   Ground claims in concrete mechanisms, examples, variables, steps, observed phenomena, timestamps, figures, or speaker-provided evidence whenever possible.

3. Start from `assets/notes-template.tex`.
   Fill in the metadata block, including the local cover image path, and replace the body content block with the generated notes.
   Do not create the final PDF from a separate renderer, notebook, script, report generator, or parallel document representation.
   The final PDF must be compiled from the same `.tex` file that is delivered.

4. The front page must include the video's original cover image when available.
   Place it on the first page rather than burying it later in the document.
   Keep it visually distinct from in-body teaching figures.

5. Use figures whenever they materially improve explanation.
   Include as many figures as are necessary for teaching clarity, even if that means many figures across the document.
   Do not optimize for a small figure count; optimize for explanatory coverage and readability.
   Good figures are key formulas, diagrams, tables, plots, visual comparisons, pipeline schedules, architecture views, and stage-by-stage visual progressions.

6. Do not place images inside custom message boxes.

7. When a mathematical formula appears:
   first explain in plain Chinese what the formula is trying to express and why it appears
   show it in display math using `$$...$$`
   then immediately follow with a flat list that explains every symbol

8. When code examples appear:
   explain the role of the code before the listing and summarize the expected behavior after it when useful
   wrap them in `lstlisting`
   include a descriptive `caption`

9. Highlight teaching signals deliberately and repeatedly when the content justifies it:
   use `importantbox` for core concepts the reader must walk away with, including formal definitions, central claims, key mechanism summaries, theorem-like statements, critical algorithm steps, and compact restatements of the main idea after a dense explanation
   use `knowledgebox` for background and side knowledge that improves understanding without being the main thread, including prerequisite reminders, historical lineage, engineering context, design tradeoffs, terminology comparisons, and intuition-building analogies
   use `warningbox` for common misunderstandings and failure points, including notation overload, hidden assumptions, misleading heuristics, easy-to-make implementation mistakes, causal confusions, off-by-one style reasoning errors, and places where the speaker contrasts a wrong intuition with the correct one
   use `dialoguebox` only for conversation-heavy videos when a brief original dialogue segment is high-information, funny, vivid, or especially intuitive, and preserving the speaker's wording gives the reader a stronger sense of being present in the discussion
   keep `dialoguebox` snippets short: preserve speaker labels and a concrete timestamp or interval, lightly clean obvious ASR errors only when confident, and follow the box with prose that explains why the dialogue segment matters
   do not use `dialoguebox` for greetings, filler, long transcript dumps, or dialogue that would be clearer as ordinary summarized exposition
   there is no quota of one box per section; add multiple boxes in a section when the material contains multiple distinct teaching signals
   each box should carry a specific pedagogical payload rather than generic emphasis
   prefer placing a box immediately after the paragraph, derivation, or example that motivates it
   routine exposition should stay in normal prose; boxes are for high-signal takeaways, not decoration
   figures must stay outside `importantbox`, `knowledgebox`, `warningbox`, and `dialoguebox`

10. End every major section with `\subsection{本章小结}`.
    Add `\subsection{拓展阅读}` when there are one or two worthwhile external links.

11. End the document with a final top-level section such as `\section{总结与延伸}`.
    That final section must include:
    - the speaker's substantive closing discussion, excluding routine sign-off language
    - your own structured distillation of the core claims, mechanisms, and practical implications
    - your expanded synthesis, including conceptual compression, cross-links between sections, and any careful generalization that stays faithful to the video
    - concrete takeaways, open questions, or next steps when the material supports them

12. Do not emit `[cite]`-style placeholders anywhere in the LaTeX.

### Encoding and File Integrity

Before compiling, verify that the generated `.tex`, metadata notes, and test plan still contain readable Chinese text.
On Windows, do not trust terminal display alone: read the file as UTF-8 and check the actual file contents, because console code pages can either display valid text as mojibake or silently turn generated Chinese into `?`.
If any core Chinese field or body paragraph has become mojibake or question marks, regenerate or rewrite the affected file before compiling.
Do not use the PDF as proof of success until the source `.tex` has passed this text-integrity check.

## Figure Handling

Select figures by necessity and teaching value, not by an arbitrary quota or a bias toward keeping the document visually sparse.

Frame understanding must come from direct visual inspection.

- Use the `view image` tool to inspect candidate frames and crops before deciding what they show, how they should be described, and whether they are complete enough to include.
- Do not use OCR tools such as `tesseract` as a substitute for visual understanding of a frame.
- Do not infer a frame's semantic content only from nearby subtitles, filenames, chapter names, or timestamps without checking the image itself.
- Contact sheets, montages, and tiled strips are good for recall, but final keep-or-reject decisions and semantic naming must be based on actual image inspection with `view image`.

### Douyin Layout Checks

Before inserting a frame, inspect the full frame and decide whether cropping is needed.

- Detect whether the source is horizontal, vertical, or a horizontal lecture embedded inside vertical packaging.
- Crop out Douyin side buttons, bottom captions, black bars, duplicated wrappers, or creator UI when they reduce teaching clarity.
- Preserve the main teaching region, slide text, formulas, diagrams, whiteboard strokes, and speaker gestures when they help interpretation.
- Do not crop away visible context that the prose later references.
- Treat `chapterInfo` thumbnails as candidate recall aids only; still inspect video frames or full-resolution thumbnails before final inclusion.

### Frame Selection Checklist

Before inserting any video frame, first inspect several nearby candidates from the same subtitle-aligned interval and apply this checklist.
If any item fails, reject the frame and keep searching nearby rather than forcing an approximate match.

- Relevance: the frame must directly support the exact concept discussed in the surrounding paragraph or subsection.
- Required content visible: every visual element referenced in the text must already be visible in the frame.
- Fully revealed state: when slides, whiteboards, animations, or dashboards build progressively, use the final fully populated readable state.
- Best nearby candidate: compare multiple nearby frames and prefer the one that is both most complete and most readable.
- Readability: text, formulas, labels, and diagram structure must be legible enough to justify inclusion.

### Frame Naming

- Use neutral timestamp-based names for raw candidate frames.
- Do not assign semantic names before inspecting the actual frame content.
- Rename a frame semantically only after visually confirming what is fully visible in the image.
- The semantic filename must describe the frame's actual visible content, not a guess based on subtitles, nearby narration, or the intended paragraph topic.
- If the frame is partially revealed, transitional, or ambiguous, keep searching and do not lock in a semantic name yet.

### Time Provenance

Whenever the `.tex` or PDF references a specific video frame, or a crop derived from a video frame, record its source time interval on the same page as a bottom footnote.

- The footnote must show the concrete time interval, for example `00:12:31--00:12:46`.
- The interval should come from the subtitle-aligned segment or verified chapter segment used to locate the figure.
- If the figure is a crop, the footnote still refers to the original video time interval of the source frame or subtitle span.
- Keep the figure and its time footnote anchored to the same page.

## Visualization

For concepts that remain hard to explain with only screenshots and prose, add accurate visualizations.

Two acceptable routes:

- generate LaTeX-native visualizations with TikZ or PGFPlots
- generate figures ahead of time with scripts and include them as images

For script-generated illustrations, prefer Python tools such as `matplotlib` and `seaborn` when they are the clearest way to produce an accurate teaching figure.
Export plots and schematics as PDF when vector output improves readability.
Do not add decorative graphics that do not teach anything.

## Final Checklist

Before delivery, verify all of the following:

- supported URL forms were normalized and the final source ID was recorded
- cookie-assisted extraction was attempted when ordinary extraction failed, without storing credentials in deliverables
- page `RENDER_DATA` was checked when `yt-dlp` failed
- the subtitle source is clear: platform subtitle, Whisper SRT, or visual-only mode
- no important teaching content has been dropped, and no concrete but critical detail has been lost during condensation, restructuring, or summarization
- the text and figures are aligned: each inserted frame supports the surrounding explanation, necessary crops have been applied, and the chosen frame shows the fullest relevant information rather than a transitional or incomplete state
- the document is visually rich enough for teaching: check whether more high-information key frames should be added, and whether additional LaTeX-native or Python-script-generated illustrations would improve clarity
- the `.tex` compiles successfully to the final PDF
- the final PDF is compiled from the final `.tex` that starts from `assets/notes-template.tex`; do not generate a separate PDF from a parallel renderer or alternate document representation
- the final `.tex`, metadata, and test plan have readable UTF-8 Chinese content, not mojibake and not replacement `?` text
- the PDF has been opened or parsed after compilation: verify page count, encryption status, and render at least the cover, table of contents, one figure-heavy page, and the final page for visual inspection
- LaTeX auxiliary files, preview images, smoke-test transcripts, raw downloads, signed video URLs, and temporary chunk files are not included in final deliverables unless the user explicitly asks for them

## Delivery

Deliver all of the following:

- the final `.tex` file
- the downloaded cover image referenced on the front page
- any extracted or generated figure assets referenced by the document
- the compiled PDF
- the Whisper-generated SRT subtitle file, if speech-to-text was used

## Asset

- `assets/notes-template.tex`: default LaTeX template to copy and fill
