"""Regression tests for the core palette/theme and layout helpers."""

import plotly_toolbox as ptb
from plotly_toolbox import Palette, Theme


def test_public_api_exports():
    for name in [
        "OneLinePlot",
        "MultiLinePlot",
        "OneAreaPlot",
        "MultiAreaPlot",
        "BarPlot",
        "OneCategoryBars",
        "ComparisonBars",
        "Palette",
        "Theme",
        "set_option",
        "get_option",
    ]:
        assert hasattr(ptb, name), f"{name} not exported from top-level package"


def test_palette_with_no_colors_does_not_crash():
    # Regression: Palette.__post_init__ used to raise on colors=None.
    p = Palette(light=Theme(), main="light")
    assert p.colors == []
    assert p.color(0) is None


def test_palette_color_cycles():
    p = Palette(light=Theme(colors=["#a", "#b"]), main="light")
    assert p.color(0) == "#a"
    assert p.color(1) == "#b"
    assert p.color(2) == "#a"  # wraps


def test_palette_resolve_returns_theme():
    light = Theme(plot_bg="#fff")
    dark = Theme(plot_bg="#000")
    p = Palette(light=light, dark=dark, main="dark")
    assert p.resolve() is dark
    assert p.resolve("light") is light
