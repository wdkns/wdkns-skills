---
name: tensor-formula-viz
description: Create or refine clean, shape-aware visualizations for tensor, matrix, and vector formulas or tensor code. Use for matrix-block diagrams, entry heatmaps, row/column shard stripes, stacked 3D/4D tensors, attention, tensor parallelism, broadcasting, reductions, contractions, and any explanation where tensor shapes or dimension meanings should be visually aligned with the computation.
---

# Tensor Formula Viz

Turn a formula or tensor-code path into one dense, slide-ready figure with three zones:

1. **Top — formula:** clean mathematical definition, without shape underbraces.
2. **Middle — computation:** colored blocks, stripes, slices, operators, and communication.
3. **Bottom — meaning:** compact explanation of every shape dimension and non-obvious operation.

## Workflow

1. Reduce the input to one primary computation path. Omit equivalent objectives, diagnostics, and secondary metrics unless requested.
2. Build a shape-and-semantics ledger: symbol/code name, semantic kind, dtype/domain, global and local shape, axis meanings, range when meaningful, shape-equivalence class, producer/consumer, and contracted/broadcast/reduced axes.
3. Choose the smallest visual grammar that exposes the mechanism.
4. Reserve non-overlapping stage lanes and object bounding boxes, then draw the three-zone layout.
5. Render, inspect, and correct both mathematical and visual alignment.

For code input, trace concrete `matmul`, `einsum`, `reshape/view`, `transpose/permute`, concat, broadcast, and collective operations. Preserve code variable names when useful; state any inferred shapes or conventions.

## Choose the visual grammar

- **Entry color blocks:** use for masks, sparsity, causal structure, elementwise operations, or row/column roles inside a small matrix.
- **Row/column stripes:** use for sharding, device ownership, tensor parallelism, channel groups, or any operation whose key fact is an entire axis partition.
- **Stacked slices or head panels:** use for 3D/4D tensors such as \(B\times T\times d\) or \(B\times h\times T\times d_h\). Make depth/panels visibly encode the extra axes.
- **Arrows and device/collective nodes:** use for AllReduce, AllGather, ReduceScatter, transpose, reshape, split, concat, or data movement.

Combine grammars only when each adds information. Cell variation may give dense tensors visual texture, but known zeros stay unfilled and masks, diagonals, sparsity, and partitions must encode their exact structure.

## Formula and shape rules

- Keep every displayed formula uncluttered. Never use shape underbraces in algebra; put shapes only under the corresponding blocks in the middle.
- Center the symbol directly below its block; center the shape on the next line.
- Explain dimension semantics at the bottom rather than repeating the shape list.
- Show the contracted dimension explicitly:
  \[
  (m\times k)(k\times n)\rightarrow(m\times n).
  \]
- For last-dimension linear layers, preserve leading axes:
  \[
  (B\times T\times d_{\mathrm{in}})
  (d_{\mathrm{in}}\times d_{\mathrm{out}})
  \rightarrow B\times T\times d_{\mathrm{out}}.
  \]
- Distinguish global shape from per-rank/local shape.
- Make transpose, broadcast, reduction, reshape, split, and concat axis order explicit.
- Treat colors as semantics: keep one color per tensor role, head, or TP rank throughout the figure.

## Symbol semantics and discrete objects

- Classify every non-obvious symbol as value, score/logit, probability, index/coordinate, rank/order, count, ID, mask/support, permutation, or shape parameter. State its dtype/domain and what one entry means; shape alone is insufficient.
- Give one block one semantic object. Never merge a score, index list, and mask under a label such as \(M/S\); show each conversion with an explicit operator and arrow.
- For selection or routing, close the full chain: continuous scores \(\rightarrow\) discrete indices/IDs \(\rightarrow\) gather, scatter, mask, or route \(\rightarrow\) selected values. Distinguish `TopKValues` from `TopKIndices`; if both are used, show both outputs.
- Define index notation and range at first use, for example \(S_t=(s_{t,1},\ldots,s_{t,k})\), \(s_{t,r}\in\{0,\ldots,t\}\). Distinguish source-position axis \(s\) from selected-slot/rank axis \(r\), and state whether ordering, duplicates, padding, or variable cardinality matter.
- Show the address mapping once, such as \(G[b,t,r,:]=X[b,S[b,t,r],:]\). If a mask is also shown, state \(M[b,t,s]=\mathbf 1[s\in S_{b,t}]\); do not imply that the integer index tensor and Boolean mask are the same object.
- Visualize integer indices as ordered slots, position labels, or gather lines; visualize masks as binary structural support; visualize scores and values as magnitude color blocks. Do not render all three with the same heatmap grammar.
- When indices are shared across heads, ranks, or branches, draw the shared selector once and mark the broadcast/reuse axes explicitly.

## Mandatory geometry invariants

- Map every matrix face \(a\times b\) to height \(a\) and width \(b\). For batched or stacked tensors, use the last two matrix axes for the face and leading axes only for depth or repeated panels.
- Derive one geometry ledger from the shape ledger. Assign each symbolic axis value one nominal physical edge length and reuse it across the entire figure. Equal shapes form an equivalence class and must have identical face width and height across stages, ranks, and semantic roles.
- Draw \(a\times a\) as a square. Draw a transpose by physically swapping face height and width; changing only the label is invalid.
- In \((m\times k)(k\times n)\), render both occurrences of the contracted \(k\) with the same physical edge length. Apply the same rule to `einsum` contractions and attention axes.
- Preserve partition geometry. Explicit shards tile their parent exactly along the split axis; equal shards have equal size; concatenation reverses the split. Size concatenated parts from their declared shapes—Q/K/V are equal segments only when their output shapes are equal. If intermediate shards are elided, show an ellipsis and never stretch the visible shards to impersonate the full parent.
- Change geometry at an explicit reshape, flatten, transpose, split, or concat operator only. State axis identities such as \((h/p)d_h=d/p\); do not silently reuse one generic rectangle before and after an axis change.
- Illustrative cell counts need not match real tensor dimensions, but they never waive equal-shape, square, transpose, contraction, or partition invariants.

## Mandatory layout invariants

- Treat every tensor, full offset stack, bracket, operator, arrow label, annotation, symbol, shape label, stage heading, and meaning box as a bounding box. Define one base gutter \(g\geq1\,\mathrm{em}\); keep unrelated boxes at least \(g\) apart and stage bands at least \(1.5g\) apart. Tangency counts as collision.
- Allow overlap only inside one declared composite: tiles within their matrix, shards tiling a parent, outline sheets in one stack, a bracket around its tensor, or a connector endpoint on its source/target border. Forbid every other intersection or occlusion.
- Reserve separate vertical lanes for the stage heading, connector annotations, tensor/operator row, symbols, and shapes. Put explanatory prose in the stage subtitle, bottom box, or above its connector; never insert a floating commentary card between operands unless it is a real operation node.
- Route connectors on a background layer, tensors and operators on the main layer, and text on a foreground layer. A connector may not cross a non-endpoint box; a label's white underlay may cover only its own connector, never a tensor or other label.
- Include all offset sheets in a stack's bounding box. Use outline-only or very light back sheets with no hidden semantic content; if slices need individual reading, use separate panels instead of overlap.
- When content does not fit, shorten or remove secondary annotation, widen the natural crop, increase row spacing, or move the whole stage to another row—in that order. Never solve crowding by shrinking below the type hierarchy, compressing the gutter, or covering another object.

For sharded matrix multiplication, expand the block algebra in both the top formula and the relevant middle panel:

\[
\mathbf X\mathbf W
=
[\mathbf X\mathbf W^{(1)}|\cdots|\mathbf X\mathbf W^{(p)}]
=
[\mathbf H^{(1)}|\cdots|\mathbf H^{(p)}],
\]

\[
[\mathbf H^{(1)}|\cdots|\mathbf H^{(p)}]
\begin{bmatrix}
\mathbf W^{(1)}\\ \vdots\\ \mathbf W^{(p)}
\end{bmatrix}
=
\sum_r\mathbf H^{(r)}\mathbf W^{(r)}
=
\sum_r\mathbf P^{(r)}.
\]

## House style

- When entry-level matrix blocks are central or Kimi-like styling is requested, inspect `assets/kimi-matrix-style-reference.png` with an image viewer before drawing. Use it only to calibrate tile spacing, rounding, neutral brackets, restrained hue, lightness separation, and structural whitespace; do not copy its formula/content or embed the asset in the output.
- Use a white background and the natural `standalone` crop. Do not force a 16:9 canvas unless requested.
- Add no title by default. The top contains at most two compact formula lines: the primary chain and, only if essential, one companion definition.
- Make each stage one horizontal algebraic row with a shared visual baseline. Use the fewest stages that preserve the primary path; do not create unrelated branches or dashboard panels.
- Reuse this type hierarchy: `\large` formula, centered `\small\bfseries` muted stage label, `\Large` operators, `\small` symbols, `\scriptsize` muted shapes, and `\small` bottom prose.
- Build entry matrices from separate tiles with small white gutters and subtle \(0.5\)–\(1\) pt corner rounding. Use thin neutral brackets or `black!55`–`black!70` outer borders; avoid saturated tensor-colored outlines and continuous spreadsheet grids. Use shallow stacks or repeated panels for extra axes.
- Encode support before magnitude: leave every known zero white/unfilled and color every shown nonzero. For diagonal, block-diagonal, triangular, masked, or sparse matrices, fill exactly the structural support; a diagonal matrix must read instantly as colored diagonal cells on a white field.
- Start from muted, mid-chroma paper colors rather than raw saturated primaries. A safe default palette is teal `#4F8FA5`, orange `#EE995B`, coral `#C95B5B`, violet `#8A74B5`, and neutral gray `#85898F`.
- Give each tensor role one semantic color and reuse it across stages. Default to at most four active hue families per algebraic row plus neutral gray; vary lightness or reuse the related input/output family before adding a hue. If sign matters, use hue for sign and intensity for magnitude.
- Maintain visible contrast through lightness separation, not maximum saturation. Reserve white or near-white for zero/absence and use at least three separated active levels when values vary; `role!30`, `role!55`, and `role!80` are practical defaults. Do not render all data cells with `role!5`–`role!15` pastel fills.
- For illustrative dense tensors, use two or three non-periodic lightness levels. Do not generate checkerboards, regular stripes, or symmetric motifs unless they encode real structure.
- Center the symbol immediately below each block and its shape on the next line.
- Use one full-width, low-contrast bottom box with one reading column and at most three fixed-label rows: **Axes** for dimension meanings, **Objects** for semantic kind/domain/range, and **Mechanism** for at most two essential mappings, contractions, broadcasts, or boundaries; localize these labels to the figure language. Use a narrow bold label rail, left-aligned ragged-right `\small` content, \(8\)–\(10\) pt inner padding, and \(0.4\)–\(0.6\) em row gaps. Keep each row compact; prioritize symbol semantics over numeric configuration or secondary commentary, and remove content instead of adding cards, columns, or smaller type.
- Place one centered identification line below the bottom meaning box, outside the box, in low-contrast neutral gray and `\scriptsize` or smaller. Format it as `<concise visualization subject>@五道口纳什`, replacing the angle-bracketed placeholder with what the figure visualizes and omitting the literal angle brackets; keep it on one line with a small but visible vertical gap. Example: `TP-FFN（GeLU + All-Reduce）@五道口纳什`.
- Avoid charts or metric insets not present in the primary formula, decorative pills, banners, shadows, repeated separators, and explanatory cards.
- Keep illustrative cell counts visually consistent; state once that they show axis structure rather than literal dimensions without weakening the mandatory geometry invariants.
- For Chinese figures, use concise Chinese labels with standard English terms where helpful.

## Rendering and validation

Default to editable TikZ for formula-heavy figures. For Chinese TikZ, require XeLaTeX and the portable TeX Live font set:

```tex
\usepackage[UTF8,fontset=fandol]{ctex}
```

Do not select OS-specific CJK fonts by default. Override Fandol only when the user explicitly requests a brand/system font and accepts reduced portability. Keep mathematical symbols in LaTeX rather than raw Unicode. Export source plus PDF, SVG, transparent PNG, and white-background PNG when the environment supports them.

Before delivery:

1. Recompute every shape independently.
2. Audit the semantics ledger: every discrete or overloaded symbol has one type/domain/range, distinct score/index/mask objects, and a closed producer-to-consumer mapping.
3. Audit the geometry ledger: equal-shape bounding boxes, square and transpose faces, contracted edge lengths, and split/concat conservation.
4. Verify block multiplication, broadcasting, reductions, and sharding algebra.
5. Render to PNG and visually inspect the latest output.
6. At full size, audit every bounding box, gutter, stack extent, connector route, and layer for forbidden intersection, tangency, clipping, or occlusion.
7. Check the compact top, row-wise algebraic stages, symbol/shape alignment, natural crop, three-row bottom box, centered identification line, and exact structural support. Confirm that the identification line names the actual visualization, stays outside the meaning box, and is neither clipped nor visually dominant. At thumbnail size, audit hue count and reuse, muted base colors, active-level separation, neutral borders, and non-periodic texture against the house style or supplied reference.
8. Reject and redraw any figure that violates a mandatory semantic, geometry, or layout invariant.
9. Deliver the preview, a short mechanism explanation, and links to editable/vector artifacts.

Do not deliver a figure that is only syntactically valid; require both mathematical correctness and clean visual alignment.
