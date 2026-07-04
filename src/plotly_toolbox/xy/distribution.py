"""Distribution charts: box and violin, with optional category grouping.

Example
-------
>>> BoxPlot(df=df, name="Scores", value_col="score", category_col="group").show()
>>> ViolinPlot(df=df, name="Scores", value_col="score").show()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from plotly import graph_objects as go

from plotly_toolbox.core import CategorySplit, Graph, PlotlySublotType, deep_merge


@dataclass(kw_only=True)
class DistributionPlot(CategorySplit, Graph):
    """Base for box/violin charts over ``value_col``. Group with ``category_col``."""
    subplot_type: Optional[PlotlySublotType] = 'xy'
    value_col: str
    orientation: Literal['v', 'h'] = 'v'

    #: Plotly trace class used to draw each series (overridden by subclasses).
    _trace_cls = go.Box

    def __post_init__(self):
        super().__post_init__()
        if self.value_col not in self.df.columns:
            raise KeyError(
                f"Column '{self.value_col}' not found in DataFrame. Available: {list(self.df.columns)}"
            )
        if self.category_col is not None:
            self.resolve_categories()

    def _trace(self, values, name: str, color: Optional[str]):
        axis = 'y' if self.orientation == 'v' else 'x'
        kwargs = {axis: values, 'name': name}
        if color:
            kwargs['marker'] = {'color': color}
        return type(self)._trace_cls(**kwargs)

    def build_traces(self) -> list:
        if self.category_col is not None:
            return [
                self._trace(sub_df[self.value_col], str(category), color)
                for _, category, sub_df, color in self.iter_series()
            ]
        return [self._trace(self.df[self.value_col], self.name, self.series_color(0))]

    def layout_patch(self) -> dict:
        layout = self.styled_layout()
        value_axis = 'yaxis' if self.orientation == 'v' else 'xaxis'
        deep_merge(layout, {value_axis: {'title': {'text': self.value_col}}})
        return layout


@dataclass(kw_only=True)
class BoxPlot(DistributionPlot):
    """A box-and-whisker plot."""
    _trace_cls = go.Box


@dataclass(kw_only=True)
class ViolinPlot(DistributionPlot):
    """A violin plot."""
    _trace_cls = go.Violin
