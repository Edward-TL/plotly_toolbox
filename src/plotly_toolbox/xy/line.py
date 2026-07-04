"""Line charts (single and multi-series)."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Literal, Optional

import numpy as np
import pandas as pd
from plotly import graph_objects as go

from plotly_toolbox.core import (
    CategorySplit,
    PlotlySublotType,
    TwoDimensionGraph,
)

LineMode = Literal[
    'lines', 'markers', 'text',
    'lines+markers', 'lines+text', 'markers+text',
    'lines+markers+text',
    'none',
]

LineShape = Literal['linear', 'spline', 'hv', 'vh', 'hvh', 'vhv']


@dataclass(kw_only=True)
class LinePlot(TwoDimensionGraph):
    subplot_type: Optional[PlotlySublotType] = 'xy'
    color: Optional[str] = None
    mode: LineMode = 'lines'
    line_shape: LineShape = 'linear'
    trendline_color: Optional[str] = None
    trendline_name: str = 'trendline'
    # Deprecated: use `mode` instead.
    line: Optional[LineMode] = None

    def __post_init__(self):
        super().__post_init__()
        if self.line is not None:
            warnings.warn(
                "`line=` is deprecated; use `mode=` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.mode = self.line

    def gen_simple_line_data(self) -> dict:
        line_layout = {'shape': self.line_shape}
        if self.palette and self.palette.colors:
            line_layout["color"] = self.palette.colors[0]
        if self.color:
            line_layout["color"] = self.color
        return line_layout

    def _trendline_trace(self) -> go.Scatter:
        # np.polyfit needs numeric x; map datetime/categorical x to ordinals for the
        # fit while still plotting the trendline against the original x values.
        x_series = pd.Series(self.x_values).reset_index(drop=True)
        if pd.api.types.is_numeric_dtype(x_series):
            x_numeric = x_series.to_numpy(dtype=float)
        else:
            x_numeric = np.arange(len(x_series), dtype=float)

        y_numeric = np.asarray(self.y_values, dtype=float)
        slope, intercept = np.polyfit(x_numeric, y_numeric, 1)
        self.trendline_y = slope * x_numeric + intercept

        trendline_data = {'dash': 'dash', 'shape': self.line_shape}
        if self.trendline_color:
            trendline_data['color'] = self.trendline_color

        return go.Scatter(
            x=self.x_values,
            y=self.trendline_y,
            mode='lines',
            line=trendline_data,
            name=self.trendline_name,
        )


@dataclass(kw_only=True)
class OneLinePlot(LinePlot):
    """A single-series line plot, with an optional trendline."""

    def build_traces(self) -> list:
        traces = [
            go.Scatter(
                x=self.x_values,
                y=self.y_values,
                name=self.name,
                line=self.gen_simple_line_data(),
                showlegend=False,
                mode=self.mode,
            )
        ]
        if self.trendline_color:
            traces.append(self._trendline_trace())
        return traces


@dataclass(kw_only=True)
class CategoricalLines(CategorySplit, TwoDimensionGraph):
    subplot_type: Optional[PlotlySublotType] = 'xy'
    mode: LineMode = 'lines'
    line_shape: LineShape = 'linear'
    color_col: Optional[str] = None
    # Deprecated: use `mode` instead.
    lines: Optional[LineMode] = None

    def __post_init__(self):
        super().__post_init__()
        if self.lines is not None:
            warnings.warn(
                "`lines=` is deprecated; use `mode=` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.mode = self.lines
        self.resolve_categories()

    def line_layouts(self) -> list[dict]:
        """One line-style dict per category, coloured from the palette/`colors`."""
        layouts = []
        for index in range(len(self.category_values)):
            layout = {'shape': self.line_shape}
            color = self.series_color(index)
            if color:
                layout['color'] = color
            layouts.append(layout)
        return layouts

    # Backwards-compatible alias for the previous method name.
    def gen_multiple_line_data(self) -> list[dict]:
        return self.line_layouts()

    gen_miltiple_line_data = gen_multiple_line_data


@dataclass(kw_only=True)
class MultiLinePlot(CategoricalLines):
    """A line plot with one line per category."""

    def build_traces(self) -> list:
        layouts = self.line_layouts()
        return [
            go.Scatter(
                x=sub_df[self.x_axis],
                y=sub_df[self.y_axis],
                mode=self.mode,
                name=str(category),
                line=layouts[index],
                showlegend=self.show_legend,
            )
            for index, category, sub_df, _ in self.iter_series()
        ]
