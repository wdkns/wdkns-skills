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
2. Build a shape ledger: symbol/code name, global and local shape, axis meanings, shape-equivalence class, and contracted/broadcast/reduced axes.
3. Choose the smallest visual grammar that exposes the mechanism.
4. Draw the three-zone layout.
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

## Mandatory geometry invariants

- Map every matrix face \(a\times b\) to height \(a\) and width \(b\). For batched or stacked tensors, use the last two matrix axes for the face and leading axes only for depth or repeated panels.
- Derive one geometry ledger from the shape ledger. Assign each symbolic axis value one nominal physical edge length and reuse it across the entire figure. Equal shapes form an equivalence class and must have identical face width and height across stages, ranks, and semantic roles.
- Draw \(a\times a\) as a square. Draw a transpose by physically swapping face height and width; changing only the label is invalid.
- In \((m\times k)(k\times n)\), render both occurrences of the contracted \(k\) with the same physical edge length. Apply the same rule to `einsum` contractions and attention axes.
- Preserve partition geometry. Explicit shards tile their parent exactly along the split axis; equal shards have equal size; concatenation reverses the split. Size concatenated parts from their declared shapes—Q/K/V are equal segments only when their output shapes are equal. If intermediate shards are elided, show an ellipsis and never stretch the visible shards to impersonate the full parent.
- Change geometry at an explicit reshape, flatten, transpose, split, or concat operator only. State axis identities such as \((h/p)d_h=d/p\); do not silently reuse one generic rectangle before and after an axis change.
- Illustrative cell counts need not match real tensor dimensions, but they never waive equal-shape, square, transpose, contraction, or partition invariants.

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
- Use one full-width, low-contrast bottom box with one left-aligned column. Explain axis meanings plus at most two essential contraction, broadcast, reduction, or reshape facts. Remove content instead of shrinking below `\small`.
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
2. Audit the geometry ledger: equal-shape bounding boxes, square and transpose faces, contracted edge lengths, and split/concat conservation.
3. Verify block multiplication, broadcasting, reductions, and sharding algebra.
4. Render to PNG and visually inspect the latest output.
5. Check the compact top, row-wise algebraic stages, symbol/shape alignment, natural crop, single-column bottom box, and exact structural support. At thumbnail size, audit hue count and reuse, muted base colors, active-level separation, neutral borders, and non-periodic texture against the house style or supplied reference.
6. Reject and redraw any figure that violates a mandatory geometry invariant; then fix overlap, clipping, cramped labels, and unreadable glyphs.
7. Deliver the preview, a short mechanism explanation, and links to editable/vector artifacts.

Do not deliver a figure that is only syntactically valid; require both mathematical correctness and clean visual alignment.
