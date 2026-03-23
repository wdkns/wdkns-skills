---
name: youtube-render-pdf
description: Generate a professional, detailed, figure-rich LaTeX course note and final PDF from a YouTube lecture, tutorial, or technical talk. Use when the user provides a YouTube URL and wants structured Chinese teaching notes that combine the video's title, chapters, diagrams, formulas, code, subtitle explanations, the original video cover on the front page, and a final synthesis chapter, with key frames extracted from the highest usable video resolution and inserted as figures, and where the final deliverable must include a rendered PDF.
---

# YouTube Render PDF

Use this skill to turn a YouTube video into a complete, compileable `.tex` note and a rendered PDF.

## Goal

Produce a professional Chinese lecture note from a YouTube URL.

The output must:

- use the video's actual teaching content rather than subtitle transcription alone
- place the video's original cover image on the front page of the `.tex` and rendered PDF whenever available
- include all necessary high-value key frames as figures, without adding redundant screenshots
- end with a final synthesis section that includes the speaker's substantive closing discussion and your own distilled takeaways
- be structurally organized with `\section{...}` and `\subsection{...}`
- be a complete `.tex` document from `\documentclass` to `\end{document}`
- be compiled successfully to PDF as part of the final delivery

## Source Acquisition

1. Inspect the video metadata first.
   Prefer title, chapters, duration, thumbnail availability, and subtitle availability before writing.

2. Prefer the best usable video source for figure extraction.
   Probe formats and choose the highest resolution that is actually downloadable in the current environment.

3. Acquire the video's original cover image before writing the `.tex`.
   Prefer the highest-resolution thumbnail exposed by the platform metadata.
   Save the selected cover locally and reference that local asset from the front page.
   Do not substitute a random video frame when an official cover image is available.

4. Prefer the best matching subtitle track.
   Use manual subtitles over auto-generated subtitles when both are available.
   Prefer the default language that best matches the video or the user's requested language.
   Fall back to the closest available subtitle track only when needed.
   Preserve the subtitle timestamps; do not flatten subtitles into plain text too early if figures still need to be located.

5. Keep all source artifacts local when practical.
   Typical working artifacts are metadata, the downloaded cover image, a timestamped subtitle file, optional cleaned transcript text, a local video file, and extracted frames.

## Teaching Content Rules

Build the notes from all of the following when available:

- video title and chapter structure
- the video's original cover image and key metadata
- on-screen diagrams, formulas, tables, plots, and architecture slides
- subtitle explanations, examples, and verbal emphasis
- code snippets shown or described in the talk

Skip content that does not contribute to the actual lesson:

- greetings
- small talk
- sponsorship
- channel logistics
- closing pleasantries

Keep the speaker's closing discussion when it carries actual teaching value, such as synthesis, limitations, future work, tradeoffs, advice, or open questions.

## Writing Rules

1. Write the notes in Chinese unless the user explicitly requests another language.

2. Organize the document with `\section{...}` and `\subsection{...}`.
   Reconstruct the teaching flow when needed; do not blindly mirror subtitle order.

3. Start from `assets/notes-template.tex`.
   Fill in the metadata block, including the local cover image path, and replace the body content block with the generated notes.

4. The front page must include the video's original cover image when available.
   Place it on the first page rather than burying it later in the document.
   Keep it visually distinct from in-body teaching figures.

5. Use figures whenever they materially improve explanation.
   Include as many figures as are necessary for teaching clarity, even if that means many figures across the document.
   Do not optimize for a small figure count; optimize for explanatory coverage and readability.
   Good figures are key formulas, diagrams, tables, plots, visual comparisons, pipeline schedules, architecture views, and stage-by-stage visual progressions.

6. Do not place images inside custom message boxes.

7. When a mathematical formula appears:
   show it in display math using `$$...$$`
   then immediately follow with a flat list that explains every symbol

8. When code examples appear:
   wrap them in `lstlisting`
   include a descriptive `caption`

9. Highlight teaching signals deliberately and repeatedly when the content justifies it:
   use `importantbox` for core concepts the reader must walk away with, including formal definitions, central claims, key mechanism summaries, theorem-like statements, critical algorithm steps, and compact restatements of the main idea after a dense explanation
   use `knowledgebox` for background and side knowledge that improves understanding without being the main thread, including prerequisite reminders, historical lineage, engineering context, design tradeoffs, terminology comparisons, and intuition-building analogies
   use `warningbox` for common misunderstandings and failure points, including notation overload, hidden assumptions, misleading heuristics, easy-to-make implementation mistakes, causal confusions, off-by-one style reasoning errors, and places where the speaker contrasts a wrong intuition with the correct one
   there is no quota of one box per section; add multiple boxes in a section when the material contains multiple distinct teaching signals
   each box should carry a specific pedagogical payload rather than generic emphasis
   prefer placing a box immediately after the paragraph, derivation, or example that motivates it
   routine exposition should stay in normal prose; boxes are for high-signal takeaways, not decoration
   figures must stay outside `importantbox`, `knowledgebox`, and `warningbox`

10. End every major section with `\subsection{本章小结}`.
   Add `\subsection{拓展阅读}` when there are one or two worthwhile external links.

11. End the document with a final top-level section such as `\section{总结与延伸}`.
   That final section must include:
   - the speaker's substantive closing discussion, excluding routine sign-off language
   - your own structured distillation of the core claims, mechanisms, and practical implications
   - your expanded synthesis, including conceptual compression, cross-links between sections, and any careful generalization that stays faithful to the video
   - concrete takeaways, open questions, or next steps when the material supports them

12. Do not emit `[cite]`-style placeholders anywhere in the LaTeX.

## Figure Handling

Select figures by necessity and teaching value, not by an arbitrary quota or a bias toward keeping the document visually sparse.

When locating candidate frames, bias strongly toward recall before precision.
It is better to inspect too many nearby candidates first than to miss the one frame where the slide, formula, table, or diagram is finally fully revealed and readable.

- Use the timestamped subtitle file as the primary locator for key-frame search.
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

## Visualization

For concepts that remain hard to explain with only screenshots and prose, add accurate visualizations.

Two acceptable routes:

- generate LaTeX-native visualizations with TikZ or PGFPlots
- generate figures ahead of time with scripts and include them as images

Use visualizations for:

- process flows
- architecture layouts
- scaling-law plots
- summary diagrams
- comparisons that are clearer as charts than prose

Do not add decorative graphics that do not teach anything.

## Delivery

Deliver all of the following:

- the final `.tex` file
- the downloaded cover image referenced on the front page
- any extracted or generated figure assets referenced by the document
- the compiled PDF

## Asset

- `assets/notes-template.tex`: default LaTeX template to copy and fill
