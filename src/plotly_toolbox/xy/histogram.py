"""Histograms, with optional category overlay.

Example
-------
>>> Histogram(df=df, name="Age distribution", column="age", nbins=20).show()
>>> Histogram(df=df, name="By group", column="score", category_col="group").show()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from plotly import graph_objects as go

from plotly_toolbox.core import CategorySplit, Graph, PlotlySublotType, deep_merge

HistNorm = Literal['', 'percent', 'probability', 'density', 'probability density']


@dataclass(kw_only=True)
class Histogram(CategorySplit, Graph):
    """A histogram over ``column``. Pass ``category_col`` to overlay one series
    per category."""
    subplot_type: Optional[PlotlySublotType] = 'xy'
    column: str
    nbins: Optional[int] = None
    cumulative: bool = False
    histnorm: HistNorm = ''
    barmode: Literal['overlay', 'stack', 'group', 'relative'] = 'overlay'
    opacity: float = 0.75

    def __post_init__(self):
        super().__post_init__()
        if self.column not in self.df.columns:
            raise KeyError(
                f"Column '{self.column}' not found in DataFrame. Available: {list(self.df.columns)}"
            )
        if self.category_col is not None:
            self.resolve_categories()

    def _trace(self, values, name: str, color: Optional[str]) -> go.Histogram:
        return go.Histogram(
            x=values,
            name=name,
            nbinsx=self.nbins,
            cumulative={'enabled': self.cumulative},
            histnorm=self.histnorm,
            opacity=self.opacity,
            marker={'color': color} if color else None,
        )

    def build_traces(self) -> list:
        if self.category_col is not None:
            return [
                self._trace(sub_df[self.column], str(category), color)
                for _, category, sub_df, color in self.iter_series()
            ]
        return [self._trace(self.df[self.column], self.name, self.series_color(0))]

    def layout_patch(self) -> dict:
        layout = self.styled_layout()
        deep_merge(layout, {'xaxis': {'title': {'text': self.column}}, 'barmode': self.barmode})
        return layout
