"""Pie and donut charts.

Example
-------
>>> PiePlot(df=df, name="Share", labels_col="region", values_col="sales").show()
>>> DonutPlot(df=df, name="Share", labels_col="region", values_col="sales").show()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from plotly import graph_objects as go

from plotly_toolbox.core import OneDimensionPlot, PlotlySublotType


@dataclass(kw_only=True)
class PiePlot(OneDimensionPlot):
    """A pie chart from a labels column and a values column."""
    subplot_type: Optional[PlotlySublotType] = 'domain'
    labels_col: str
    values_col: str
    hole: float = 0.0
    text_info: str = 'percent'

    def __post_init__(self):
        super().__post_init__()
        for col in (self.labels_col, self.values_col):
            if col not in self.df.columns:
                raise KeyError(
                    f"Column '{col}' not found in DataFrame. Available: {list(self.df.columns)}"
                )

    def build_traces(self) -> list:
        marker = None
        if self.palette and self.palette.colors:
            marker = {'colors': self.palette.colors}
        return [
            go.Pie(
                labels=self.df[self.labels_col],
                values=self.df[self.values_col],
                hole=self.hole,
                textinfo=self.text_info,
                name=self.name,
                marker=marker,
                showlegend=self.show_legend,
            )
        ]


@dataclass(kw_only=True)
class DonutPlot(PiePlot):
    """A pie chart with a hole in the middle."""
    hole: float = 0.5
