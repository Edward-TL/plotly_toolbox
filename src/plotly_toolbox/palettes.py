"""Ready-to-use palettes so charts look good without defining a Theme by hand.

Use directly (``OneLinePlot(..., palette=DEFAULT)``) or set globally
(``set_option('palette', DARK)``).
"""

from __future__ import annotations

from plotly_toolbox.core import Palette, Theme

_CYCLE = ["#457b9d", "#e63946", "#2a9d8f", "#e9c46a", "#8d99ae", "#9b5de5"]

DEFAULT = Palette(
    light=Theme(
        font="Arial",
        plot_bg="#ffffff",
        paper_bg="#ffffff",
        font_color="#2a2a2a",
        grid_color="#ececec",
        accent="#457b9d",
        colors=_CYCLE,
    ),
    dark=Theme(
        font="Arial",
        plot_bg="#1a1a1f",
        paper_bg="#111116",
        font_color="#e8e8e8",
        grid_color="#33333a",
        accent="#7cb6d6",
        colors=_CYCLE,
    ),
    main="light",
)

DARK = Palette(
    light=DEFAULT.light,
    dark=DEFAULT.dark,
    main="dark",
)

MINIMAL = Palette(
    light=Theme(
        font="Helvetica, Arial, sans-serif",
        plot_bg="#ffffff",
        paper_bg="#ffffff",
        font_color="#222222",
        grid_color="#f0f0f0",
        accent="#333333",
        colors=["#222222", "#7a7a7a", "#b3b3b3", "#d0d0d0"],
    ),
    main="light",
)

__all__ = ["DEFAULT", "DARK", "MINIMAL"]
