"""Core abstractions: global options, palette/theme, and the Graph rendering pipeline.

The rendering pipeline is deliberately split so a chart can emit its *content*
(traces) and a *layout fragment* independently of any concrete ``go.Figure``:

- ``build_traces()`` — implemented by each concrete chart; returns the traces.
- ``layout_patch()`` — returns a plain layout dict (titles, colors, axis config).
- ``render()`` / ``figure`` — compose the two into a ``go.Figure`` lazily.

Keeping traces and layout as data (not a mutated figure) is what lets the same
chart object be reused inside subplots and the dashboard layer without rework.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

import pandas as pd
from pandas import DataFrame as PandasDataFrame
from plotly import graph_objects as go

logger = logging.getLogger("plotly_toolbox")

ThemePalette = Literal['light', 'dark']

PlotlyTemplate = Literal[
    'ggplot2', 'seaborn', 'simple_white', 'plotly',
    'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
    'ygridoff', 'gridon', 'none'
]

PlotlySublotType = Literal[
    "xy",       # Cartesian 2D axes
    "polar",    # Polar axes
    "scene",    # 3D axes
    "geo",      # Geographic map
    "mapbox",   # Mapbox map
    "ternary",  # Ternary plot
    "domain",   # For pie charts, sunburst, etc.
]


# ---------------------------------------------------------------------------
# Global options
# ---------------------------------------------------------------------------

_GLOBAL_OPTIONS = {
    'palette': None,
    'template': 'seaborn',
}


def get_option(key: str):
    """Retrieve a current global option value."""
    if key not in _GLOBAL_OPTIONS:
        raise KeyError(f"Invalid option key: '{key}'. Valid keys: {list(_GLOBAL_OPTIONS)}")
    return _GLOBAL_OPTIONS[key]


def set_option(key: str, value) -> None:
    """Set a global option value used as the default for subsequently created charts."""
    if key not in _GLOBAL_OPTIONS:
        raise KeyError(f"Invalid option key: '{key}'. Valid keys: {list(_GLOBAL_OPTIONS)}")

    if key == 'palette' and value is not None and not isinstance(value, Palette):
        raise TypeError(f"Option 'palette' must be a Palette or None, got {type(value).__name__}")
    if key == 'template' and not isinstance(value, str):
        raise TypeError(f"Option 'template' must be a str, got {type(value).__name__}")

    _GLOBAL_OPTIONS[key] = value
    logger.info("Global option '%s' updated to: %s", key, value)


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------

def deep_merge(base: dict, extra: dict) -> dict:
    """Recursively merge ``extra`` into ``base`` (mutating and returning ``base``).

    Nested dicts are merged rather than replaced, so independent layout fragments
    that each touch e.g. ``xaxis`` can be combined without clobbering one another.
    """
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base


# ---------------------------------------------------------------------------
# Palette / theme
# ---------------------------------------------------------------------------

@dataclass
class ColorRange:
    val: int
    color: str


@dataclass
class Scale:
    color_range: tuple[ColorRange, ...]
    name: Optional[str] = None


@dataclass
class Theme:
    """Visual styling for a single mode (light or dark)."""
    font: str = 'Arial'
    plot_bg: str = 'white'
    paper_bg: str = 'white'
    font_color: str = '#2a2a2a'
    grid_color: Optional[str] = None
    accent: Optional[str] = None
    colors: Optional[list[str]] = None
    scales: Optional[tuple[Scale, ...]] = None


@dataclass
class Palette:
    """A pair of themes (light/dark) plus a discrete color cycle."""
    light: Theme
    dark: Optional[Theme] = None
    main: ThemePalette = 'light'

    def __post_init__(self):
        main_theme = getattr(self, self.main)
        self.colors = main_theme.colors or []
        self.categories = {f'cat_{c}': color for c, color in enumerate(self.colors)}
        for c, color in enumerate(self.colors):
            setattr(self, f"cat_{c}", color)

    def resolve(self, theme: Optional[ThemePalette] = None) -> Optional[Theme]:
        """Return the Theme object for `theme` (defaults to the palette's main theme)."""
        return getattr(self, theme or self.main)

    def color(self, index: int) -> Optional[str]:
        """Return a color from the cycle by index (wraps around). None if no colors."""
        if not self.colors:
            return None
        return self.colors[index % len(self.colors)]


# ---------------------------------------------------------------------------
# Base graph — the rendering pipeline
# ---------------------------------------------------------------------------

@dataclass(kw_only=True)
class Graph:
    """Base class for every chart.

    Subclasses implement :meth:`build_traces` (content) and may extend
    :meth:`layout_patch` (styling). Everything else — figure construction,
    caching, output helpers — is provided here.
    """
    df: PandasDataFrame
    name: str
    palette: Optional[Palette] = field(default_factory=lambda: get_option('palette'))
    template: PlotlyTemplate = field(default_factory=lambda: get_option('template'))
    subplot_type: Optional[PlotlySublotType] = None
    show_legend: bool = True
    subtitle: Optional[str] = None
    # Position hints consumed by subplot / dashboard renderers.
    fig_row_pos: int = 0
    fig_col_pos: int = 0

    def __post_init__(self):
        self._figure: Optional[go.Figure] = None
        self._traces_cache: Optional[list] = None

    # -- contract ----------------------------------------------------------
    def build_traces(self) -> list:
        """Return the list of Plotly traces for this chart. Implemented by subclasses."""
        raise NotImplementedError(
            f"{type(self).__name__} must implement build_traces()"
        )

    def traces(self) -> list:
        """The chart's traces (cached)."""
        if self._traces_cache is None:
            self._traces_cache = list(self.build_traces())
        return self._traces_cache

    def layout_patch(self) -> dict:
        """Return a layout dict to apply on top of the figure. Extended by subclasses."""
        return {}

    # -- rendering ---------------------------------------------------------
    def render(self) -> go.Figure:
        """Build a fresh ``go.Figure`` from the traces and layout patch."""
        figure = go.Figure(data=self.traces())
        patch = self.layout_patch()
        if patch:
            figure.update_layout(**patch)
        return figure

    @property
    def figure(self) -> go.Figure:
        """The rendered figure (built once, then cached)."""
        if self._figure is None:
            self._figure = self.render()
        return self._figure

    @property
    def fig(self) -> go.Figure:
        """Backwards-compatible alias for :attr:`figure`."""
        return self.figure

    # -- output ------------------------------------------------------------
    def show(self, **kwargs) -> None:
        """Display the figure."""
        self.figure.show(**kwargs)

    def to_html(self, path: Optional[str] = None, **kwargs):
        """Return the figure as an HTML string, or write it to ``path`` if given."""
        html = self.figure.to_html(**kwargs)
        if path is not None:
            Path(path).write_text(html)
            return path
        return html

    def to_image(self, path: Optional[str] = None, **kwargs):
        """Return the figure as image bytes, or write it to ``path`` (requires kaleido)."""
        if path is not None:
            self.figure.write_image(path, **kwargs)
            return path
        return self.figure.to_image(**kwargs)

    # -- styling shared by all charts -------------------------------------
    def color_layout(self, theme: Optional[ThemePalette] = None) -> dict:
        """Background/font layout fragment derived from the palette (empty if none)."""
        if self.palette is None:
            return {}
        theme_obj = self.palette.resolve(theme)
        if theme_obj is None:
            return {}
        return {
            'plot_bgcolor': theme_obj.plot_bg,
            'paper_bgcolor': theme_obj.paper_bg,
            'font': {'color': theme_obj.font_color, 'family': theme_obj.font},
        }


@dataclass(kw_only=True)
class OneDimensionPlot(Graph):
    """Base for 1D charts (pie, donut, …)."""

    def layout_patch(self) -> dict:
        return self.color_layout()


# ---------------------------------------------------------------------------
# Category splitting mixin (shared by every multi-series chart)
# ---------------------------------------------------------------------------

@dataclass(kw_only=True)
class CategorySplit:
    """Mixin for charts that draw one series per category.

    Resolves the category values and yields ``(index, category, sub_df, color)``
    tuples so subclasses don't each re-implement the split/color-cycle logic.
    """
    category_col: Optional[str] = None
    category_values: Optional[list] = None
    colors: Optional[list[str]] = None

    def resolve_categories(self) -> None:
        if not self.category_col and self.category_values is None:
            raise ValueError(
                "Provide `category_col` (column name) or `category_values` (iterable); both are None."
            )
        if self.category_col and self.category_values is None:
            values = self.df[self.category_col].unique().tolist()
            if values and isinstance(values[0], (int, float)):
                values.sort()
            self.category_values = values
        elif not isinstance(self.category_values, list):
            self.category_values = [self.category_values]

    def series_color(self, index: int) -> Optional[str]:
        if self.colors:
            return self.colors[index % len(self.colors)]
        palette = getattr(self, 'palette', None)
        if palette is not None and palette.colors:
            return palette.color(index)
        return None

    def iter_series(self):
        for index, category in enumerate(self.category_values):
            if self.category_col:
                sub_df = self.df[self.df[self.category_col] == category]
            else:
                sub_df = self.df
            yield index, category, sub_df, self.series_color(index)


# ---------------------------------------------------------------------------
# 2D graphs
# ---------------------------------------------------------------------------

@dataclass(kw_only=True)
class TwoDimensionGraph(Graph):
    """Base for Cartesian charts (line, scatter, bar, area).

    [Args]
        - x_axis: str = DataFrame column name for the x values
        - y_axis: str = DataFrame column name for the y values
    """
    x_axis: str
    y_axis: str
    cat: int = 0
    x_title: Optional[str] = None
    y_title: Optional[str] = None
    x_tick_text_col: Optional[str] = None
    y_tick_text_col: Optional[str] = None
    is_money: Optional[Literal['x', 'y', 'both']] = None
    number_format: Optional[str] = ',.1s'

    update_tick_text: bool = False
    x_tick_text_vals: Optional[list | tuple | pd.Series] = None
    y_tick_text_vals: Optional[list | tuple | pd.Series] = None

    x_tick_vals: Optional[list | tuple | pd.Series] = None
    y_tick_vals: Optional[list | tuple | pd.Series] = None

    x_is_hours: bool = False

    def __post_init__(self):
        super().__post_init__()
        self._validate_columns()

        if not self.x_title:
            self.x_title = self.x_axis
        if not self.y_title:
            self.y_title = self.y_axis

        self.x_values = self.df[self.x_axis]
        self.y_values = self.df[self.y_axis]

        if self.x_tick_text_col:
            self.x_tick_text_vals = self.df[self.x_tick_text_col]
        if self.y_tick_text_col:
            self.y_tick_text_vals = self.df[self.y_tick_text_col]

        if self.x_tick_text_vals is not None or self.y_tick_text_vals is not None:
            self.update_tick_text = True

    def _validate_columns(self) -> None:
        for col in (self.x_axis, self.y_axis):
            if col not in self.df.columns:
                raise KeyError(
                    f"Column '{col}' not found in DataFrame. Available: {list(self.df.columns)}"
                )
        if self.is_money not in (None, 'x', 'y', 'both'):
            raise ValueError(f"`is_money` must be None, 'x', 'y' or 'both'. Got: {self.is_money!r}")

    # -- layout fragments --------------------------------------------------
    def title_layout(self) -> dict:
        title_data = {'text': self.name}
        if self.subtitle:
            title_data['subtitle'] = {'text': self.subtitle, 'font': {'color': 'gray', 'size': 12}}
        return {
            'title': title_data,
            'xaxis': {'title': {'text': self.x_title}},
            'yaxis': {'title': {'text': self.y_title}},
        }

    def money_layout(self) -> dict:
        patch: dict = {}
        if self.is_money in {'y', 'both'}:
            patch['yaxis'] = {'tickprefix': '$', 'tickformat': self.number_format}
        if self.is_money in {'x', 'both'}:
            patch['xaxis'] = {'tickprefix': '$', 'tickformat': self.number_format}
        return patch

    def tick_text_layout(self) -> dict:
        patch: dict = {}
        if self.x_tick_text_vals is not None:
            tickvals = (
                list(self.x_tick_vals)
                if self.x_tick_vals is not None
                else list(range(1, len(self.x_tick_text_vals) + 1))
            )
            patch['xaxis'] = {
                'tickmode': 'array',
                'ticktext': list(self.x_tick_text_vals),
                'tickvals': tickvals,
            }
        if self.y_tick_text_vals is not None:
            tickvals = (
                list(self.y_tick_vals)
                if self.y_tick_vals is not None
                else list(range(1, len(self.y_tick_text_vals) + 1))
            )
            patch['yaxis'] = {
                'tickmode': 'array',
                'ticktext': list(self.y_tick_text_vals),
                'tickvals': tickvals,
            }
        return patch

    def hours_layout(self) -> dict:
        return {'xaxis': {'tick0': 0, 'dtick': 3}}

    def layout_patch(self) -> dict:
        layout: dict = {}
        if self.palette is not None:
            deep_merge(layout, self.color_layout())
        elif self.template:
            layout['template'] = self.template

        deep_merge(layout, self.title_layout())

        if self.is_money:
            deep_merge(layout, self.money_layout())
        if self.update_tick_text:
            deep_merge(layout, self.tick_text_layout())
        if self.x_is_hours:
            deep_merge(layout, self.hours_layout())

        return layout
