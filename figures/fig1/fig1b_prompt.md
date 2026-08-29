# Figure 1b — AI schematic prompt (unused alternative to the drawn panel)

## Status

This prompt belongs to the same-mean / opposite-minority panel, which is **panel b** since the
retrieval-pipeline panel was inserted ahead of it; it was written when that panel was still
panel a, and the letter in this file's name follows the panel, not the history.

That panel is a **real matplotlib schematic** (`fig1b.py`), which is what the deck builds and what
the manuscript ships. This file is kept as a ready-to-run alternative for producing an illustrated
concept panel instead. It is not part of the build; nothing imports it.

If an AI-generated panel is ever used, it must be treated as a **conceptual illustration, not
evidence**: it carries no measured values, and the caption must say so. It must also be redrawn as
vector objects before it ships, which is what was done for panel a: see the note in `README.md`
under "Panel a provenance". A pasted raster panel fails on three counts at this figure's size, all
of them measured rather than assumed: the returned 1448 x 1086 px image is about 210 dpi at
6.9 in, its 4:3 frame leaves a full-width row mostly empty, and its baked-in text is invisible to
the 5 pt floor that `figstyle.save()` enforces.

## Prompt contract

**Central claim the panel must defend.** Two drugs can produce the *same* mean transcriptomic
response while doing *opposite* things to a small resistant subpopulation, so a mean signature is a
sufficient statistic only when every cell responds alike.

**Entities.** Two compounds (Drug A, Drug B); one untreated cell population containing a majority
state and a small minority state; the two treated populations; the two mean-shift vectors.

**Mechanism to show.** Both drugs shift the population mean by the same vector. Under Drug A the
minority moves with the majority. Under Drug B the minority moves the opposite way and worsens.
The two mean shifts stay visually identical.

**Layout.** Left to right, two parallel tracks that start from one shared untreated population and
end at a shared "identical mean signature" marker. Majority and minority must be distinguishable at
a glance, and the minority must read as a small fraction of the cells.

**Required labels (short, spelled exactly).** `Drug A`, `Drug B`, `majority`, `resistant minority`,
`identical mean signature`. No other text.

**Aspect ratio / format.** 4:3, PNG, opaque white background, 2K, high quality.

## Prompt text

> A clean scientific concept schematic for a Nature-style paper figure, flat vector look, white
> background, no photorealism, no 3D, no shadows, generous whitespace. One untreated cell
> population on the left, drawn as a loose cloud of small round cells: most cells in muted blue
> (#5185C0) labelled `majority`, plus a clearly smaller cluster in muted orange (#E99D4E) labelled
> `resistant minority`. Two arrows lead right to two treated populations, one labelled `Drug A` and
> one labelled `Drug B`. Under Drug A the orange minority cells move in the same direction as the
> blue majority. Under Drug B the orange minority cells move in the opposite direction and appear
> stressed. At the right, a single marker labelled `identical mean signature` shows that both drugs
> produced the same average shift, drawn as two overlapping identical arrows or two identical short
> bars. Muted, restrained palette: blue #5185C0 for the majority, orange #E99D4E for the resistant
> minority, grey #7A7A7A for context and arrows. Thin clean lines, small sans-serif labels, minimal
> text, publication quality.

## Scientific constraints (state these to the model, then verify them afterwards)

- No numbers, axis values, p-values, error bars or scale bars of any kind. This panel is conceptual.
- No extra cell types, organs, tissue, molecular structures or pathway arrows beyond those listed.
- No logos, journal marks, watermarks, author names or institutional marks.
- The minority must read as a small fraction of the population, not an equal second group.
- The two mean shifts must be visually identical; that identity is the entire point of the panel.

## Style constraints tying it to the rest of the deck

- Palette must match the house style exactly: `#5185C0` (majority / distributional), `#E99D4E`
  (minority / mean-collapse), `#7A7A7A` (context), ink `#1A1A1A`. An earlier version of this file
  specified `#2166ac` and `#b2182b`, which match no other panel in the deck; do not use them.
- Glyph logic should match panel 1d: clouds of cells plus an explicit shared-mean marker.
- Panel letters are added by the assembly script, not by the image model.

## How to generate

Call an image-generation API (for example OpenRouter's Images API with `openai/gpt-image-2`),
passing the prompt text above verbatim, with `aspect_ratio 4:3`, `resolution 2K`, `quality high`,
`output_format png`, `background opaque`. Keep the returned image and its request metadata together
so the panel's provenance stays auditable.

## Post-generation QA (all five, before the image is used)

1. Look at the image and confirm the same-mean / opposite-minority contrast is unmistakable.
2. Check that every required label is present and correctly spelled; image models often misspell.
3. List any invented content (extra cells, numbers, structures) and regenerate if any is present.
4. Redraw labels and arrows as vector objects if they will not survive print at 89-183 mm width.
5. State in the caption that panel a is a schematic, so no reader can mistake it for data.
