"""Backward-compatible alias for the project plotting colour preference.

New figure code should import :mod:`color_preferences`.  This name is retained because the
first adoption of the softened palette was made while matching the provided Figure 1 reference.
"""

from color_preferences import (BLUE, BLUE_WASH, FAINT, GREEN, GREEN_WASH, GREY, HAIRLINE,
                               MIDPOINT, NAVY, ORANGE, ORANGE_WASH, PURPLE, PURPLE_WASH,
                               SLATE, TRACK)
