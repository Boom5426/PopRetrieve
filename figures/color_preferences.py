"""Project default colours for manuscript figures.

This is the persistent plotting preference for new figures: a low-saturation Nature-style
palette with dark blue-grey text and pale background washes.  The semantic mapping is stable:
blue for the population route, terracotta for the mean route, sage for externally supplied
information, dusty lilac for tissue or an alternate material, and slate/grey for context.

Figure 4--6 currently use these values.  Existing figures are not recoloured merely by importing
this module; a figure must opt in explicitly.
"""

# Muted semantic colours for large marks and filled regions.
BLUE = "#6F88AE"
ORANGE = "#C9917A"
GREEN = "#91B39A"
PURPLE = "#9E94B8"
SLATE = "#7D8994"
GREY = "#8B8E92"
NAVY = "#3D4B55"

# Pale supporting tones.
BLUE_WASH = "#EEF2F7"
ORANGE_WASH = "#F8F0EC"
GREEN_WASH = "#EEF4EF"
PURPLE_WASH = "#F2F0F6"
FAINT = "#D9DEE4"
HAIRLINE = "#E6E9EC"
TRACK = "#F6F8FA"
MIDPOINT = "#F7F7F7"

__all__ = [
    "BLUE", "ORANGE", "GREEN", "PURPLE", "SLATE", "GREY", "NAVY",
    "BLUE_WASH", "ORANGE_WASH", "GREEN_WASH", "PURPLE_WASH", "FAINT",
    "HAIRLINE", "TRACK", "MIDPOINT",
]
