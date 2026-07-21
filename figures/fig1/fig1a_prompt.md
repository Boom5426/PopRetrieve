# Figure 1a AI schematic prompt

## Purpose
Concept art for the paper's opening biological tension: two drugs that look identical by average
(mean) transcriptomic signature but have OPPOSITE effects on a hidden resistant minority
subpopulation. This is the phenomenon that mean-signature retrieval cannot see and that motivates
distribution-aware retrieval.

## Suggested prompt (for an image model, e.g. DALL-E / Imagen / Midjourney)

"A clean scientific figure illustration, flat vector style, white background, for a Nature Methods
paper. Two drug molecules on the left (labeled Drug 1 and Drug 2), each with an arrow pointing to a
population of cells. Both populations have the SAME average color/state (shown as an identical mean
bar or centroid). But zoomed in, Drug 1's population is uniformly healthy blue cells, while Drug 2's
population contains a small cluster of red 'resistant minority' cells that are getting worse. A small
inset shows the two mean signatures as nearly identical bars (to emphasize they look the same on
average), while the full distributions differ. Muted palette: blue (#2166ac) for majority/healthy,
red (#b2182b) for the resistant minority, grey for context. Minimalist, publication-quality, no
photorealism, clear labels, generous whitespace."

## Consistency requirements (must match the data panels)
- Blue = #2166ac (distributional / majority), Red = #b2182b (minority / collapse), Grey = context.
- The "same mean, different distribution" idea must be unmistakable: show identical mean markers.
- The minority must be visually small (a fraction alpha of the population) and marked as worsening.
- Keep glyphs consistent with panel 1c (two clouds vs a single shared-mean blob).

## Placement
Drop the returned image as fig1/fig1a.png. The assembly script (fig1_assemble.py) will replace the
placeholder box with the real image if fig1/fig1a.png exists.
