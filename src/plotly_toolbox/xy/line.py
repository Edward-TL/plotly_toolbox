"""
Collection of Two dimensional Graphs
"""

from dataclasses import dataclass, asdict
from typing import Literal, Optional

from plotly import graph_objects as go

import numpy as np
import pandas as pd

from plotly_toolbox.core import TwoDimensionGraph


LineMode = Literal[
    'lines', 'markers', 'text',
    'lines+markers', 'lines+text', 'markers+text',
    'lines+markers+text'
    'none'
]

LineShape = Literal['linear', 'spline', 'hv', 'vh', 'hvh', 'vhv']


@dataclass(kw_only=True)
class LinePlot(TwoDimensionGraph):
    subplot_type = 'xy'
    color: Optional[str] = None
    line: LineMode = 'lines'
    line_shape: LineShape = 'linear'
    trendline_color: Optional[str] = None
    trendline_name: str = 'trendline'

    def __post_init__(self):
        super().__post_init__()

    def gen_simple_line_data(self) -> dict:
        line_layout = {'shape': self.line_shape}

        if self.palette:
            line_layout["color"] = self.palette.colors[0]
        if self.color:
            line_layout["color"] = self.color

        return line_layout
    
    def add_trendline(self):
        slope, intercept = np.polyfit(self.x_values, self.y_values, 1)
        # Generate trendline y-values
        self.trendline_y = slope * self.x_values + intercept

        trendline_data = {
            'dash': 'dash',
            'shape': self.line_shape
            }
        if self.trendline_color:
            trendline_data['color'] = self.trendline_color

        self.fig.add_trace(
            go.Scatter(
                x = self.x_values,
                y = self.trendline_y,
                mode = 'lines',
                line = trendline_data,
                name = self.trendline_name
            )
        )


@dataclass(kw_only=True)
class OneLinePlot(LinePlot):
    """
    Representation of Line Plot
    """
    color: Optional[str] = None
    def __post_init__(self):
        super().__post_init__()
        
        line_layout = self.gen_simple_line_data()
        
        self.plot = go.Scatter(
            x = self.x_values,
            y = self.y_values,
            name = self.name,
            line = line_layout,
            showlegend = False,
            mode = self.line
        )

        self.fig.add_traces([self.plot])
        self.general_layout_update()

        if self.trendline_color:
            self.add_trendline()

        self.general_layout_update()


@dataclass(kw_only=True)
class CategoricalLines(TwoDimensionGraph):
    colors: Optional[str] = None
    lines: LineMode = 'lines'
    line_shape: LineShape = 'linear'

    category_col: Optional[str] = None
    category_values: Optional[list | tuple | pd.Series] = None
    color_col: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        if not self.category_col and not self.category_values:
            ve_msg = "Needed `category_col` name or `category_values` iterable. Both are `None`"
            raise ValueError(ve_msg)
        
        if self.category_col:
            self.category_values = self.df[self.category_col].unique().tolist()

            if isinstance(self.category_values[0], int):
                self.category_values.sort()

    def gen_miltiple_line_data(self) -> dict:
        area_colors = None
        if self.palette:
            size = len(self.x_values)
            area_colors = [
                self.palette.colors[n % size] for n in size
            ]

        if self.colors:
            area_colors = self.colors

        if area_colors:
            line_layout = [
                {
                'shape': self.line_shape,
                'color': area_colors[n]
                } for n in self.category_values
            ]
        else:
            line_layout = [{'shape': self.line_shape}] * len(self.category_values)

        return line_layout

@dataclass(kw_only=True)
class MultiLinePlot(CategoricalLines):
    """Representation of a Graph with multiple Lines"""
    
    def __post_init__(self):
        super().__post_init__()

        lines_data = self.gen_miltiple_line_data()
        self.fig.add_traces(
            [
                go.Scatter(
                    x = self.df[self.df[self.category_col] == category][self.x_axis],
                    y = self.df[self.df[self.category_col] == category][self.y_axis],
                    mode = 'lines',
                    name = category,
                    line = lines_data[n],
                    showlegend = self.show_legend
                ) for n, category in enumerate(self.category_values)
            ]
        )
        
        self.general_layout_update()

    # def add_trendline(self):
    #     y_trendline = np.polyfit(
    #         self.x_values,
    #     )
    #     self.fig.add_trace()
