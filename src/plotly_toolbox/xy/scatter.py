"""Scatter plots with optional size/color encodings and a trendline.

Example
-------
>>> ScatterPlot(df=df, name="Height vs weight", x_axis="height", y_axis="weight",
...             size_col="age", color_col="bmi", colorscale="Viridis").show()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from plotly import graph_objects as go

from plotly_toolbox.xy.line import LineMode, LinePlot


@dataclass(kw_only=True)
class ScatterPlot(LinePlot):
    """A scatter plot. Inherits trendline support from :class:`LinePlot`.

    - ``size_col`` / ``color_col`` map DataFrame columns to marker size / color.
    - ``marker_size`` sets a fixed size when ``size_col`` is not given.
    """
    mode: LineMode = 'markers'
    size_col: Optional[str] = None
    color_col: Optional[str] = None
    marker_size: Optional[int] = None
    colorscale: Optional[str] = None
    show_colorbar: bool = True

    def __post_init__(self):
        super().__post_init__()
        for col in (self.size_col, self.color_col):
            if col is not None and col not in self.df.columns:
                raise KeyError(
                    f"Column '{col}' not found in DataFrame. Available: {list(self.df.columns)}"
                )

    def _marker(self) -> dict:
        marker: dict = {}
        if self.palette and self.palette.colors:
            marker['color'] = self.palette.colors[0]
        if self.color:
            marker['color'] = self.color
        if self.marker_size is not None:
            marker['size'] = self.marker_size
        if self.size_col is not None:
            marker['size'] = self.df[self.size_col]
        if self.color_col is not None:
            marker['color'] = self.df[self.color_col]
            marker['showscale'] = self.show_colorbar
            if self.colorscale:
                marker['colorscale'] = self.colorscale
        return marker

    def build_traces(self) -> list:
        traces = [
            go.Scatter(
                x=self.x_values,
                y=self.y_values,
                name=self.name,
                mode=self.mode,
                marker=self._marker() or None,
                showlegend=False,
            )
        ]
        if self.trendline_color:
            traces.append(self._trendline_trace())
        return traces
