

"""
Collection of Two dimensional Graphs
"""

from dataclasses import dataclass, asdict
from typing import Literal, Optional

from plotly import graph_objects as go

from plotly_toolbox.core import TwoDimensionGraph
import pandas as pd

BarMode = Literal["group", "stack", "relative", "overlay"]
TextPosition = Literal[
    "inside",
    "outside",
    "auto",
    "none"
]

CornerRadiusExample = Literal[30, None, '30%']
# https://plotly.com/python/horizontal-bar-charts/

@dataclass(kw_only=True)
class BarsMarker:
    color: str
    line_color: Optional[str] = None
    line_width: Optional[int] = None
    cornerradius: Optional[CornerRadiusExample | int | str] = "30%"

    def __post_init__(self):
        self.data = {'color': self.color}

        if any([self.line_color is not None, self.line_width is not None]):
            self.data['line'] = {}

            if self.line_color:
                self.data['line']['color'] = self.line_color
            
            if self.line_width:
                self.data['line']['width'] = self.line_width

        if self.cornerradius:
            self.data['cornerradius'] = self.cornerradius

@dataclass(kw_only=True)
class BarPlot(TwoDimensionGraph):
    barmode: BarMode = 'stack'
    orientation: Literal['h', 'v'] = 'h'
    hover_data: Optional[list] = None
    bar_colors: Optional[list] = None
    bar_markers: Optional[list[BarsMarker] | list[dict] | list[str] | list[list]] = None
    text_position: TextPosition = 'auto'
    
    marker_data: Optional[dict] = None
    bars_text_column: Optional[str] = None
    bars_text: Optional[list] = None
    def __post_init__(self):
        super().__post_init__()
        if self.hover_data is None:
            self.hover_data = self.df.columns

        
        if self.bar_markers is None and self.bar_colors is not None:
            self.marker_data = [{'color': color} for color in self.bar_colors]

        if self.bar_markers:
            is_nested_list = False
            try:
                if isinstance(self.bar_markers[0], list):
                    is_nested_list = True
            except:
                is_nested_list = False

            if is_nested_list:
                self.marker_data = [
                    self.generate_markers_data(nested_marker) for nested_marker in self.bar_markers
                    ]
            else:
                self.marker_data = self.generate_markers_data(self.bar_markers)
            
        if self.bars_text_column is not None:
            self.bars_text = self.df[self.bars_text_column]
        
        else:
            if self.orientation == 'h':
                self.bars_text = self.x_values 
            elif self.orientation == 'v':
                self.bars_text = self.y_values
            else:
                msg = f"`orientation` must be a value of 'h' or 'v'. Got: {self.orientation=}"
                raise ValueError(msg)
        
    def extract_markers_data(self, bar_marker: BarsMarker | dict | str | list) -> dict:
        if isinstance(bar_marker, BarsMarker):
            return bar_marker.data
        
        if isinstance(bar_marker, dict):
            return bar_marker

        if isinstance(bar_marker, str):
            return {'color': bar_marker}
        
    def generate_markers_data(self, bar_markers) -> list[dict]:
        if isinstance(bar_markers, list):
            return [
                self.extract_markers_data(bm) for bm in bar_markers
            ]
        
        marker_data = self.extract_markers_data(bar_markers)
        return [marker_data] * len(self.x_values)

@dataclass(kw_only=True)
class OneCategoryBars(BarPlot):
    """
    Representation of a Bar Plot
    """
    def __post_init__(self):
        super().__post_init__()

        self.plot = go.Bar(
            x = self.x_values,
            y = self.y_values,
            marker = self.marker_data,
            text = self.bars_text,
            textposition = self.text_position,
            orientation = self.orientation
        )

        self.fig.add_traces([self.plot])
        self.general_layout_update()



@dataclass(kw_only=True)
class ComparasionBars(BarPlot):
    """
    Representation of Bar Plot
    """
    category_col: Optional[str] = None
    category_values: Optional[list | int | str | float] = None
    barmode: Literal['group'] = 'group'
    textposition: Literal['auto'] = 'auto'

    def __post_init__(self):
        super().__post_init__()
        if not self.category_col and not self.category_values:
            ve_msg = "Needed `category_col` name or `category_values` iterable. Both are `None`"
            raise ValueError(ve_msg)
        
        if self.category_values is None:
            self.category_values = sorted(list(self.df[self.category_col].unique()))

        if not isinstance(self.category_values, list):
            self.category_values = [self.category_values]

        print(self.category_values)
        self.fig = go.Figure(
            data = [
                go.Bar(
                    x = self.df[self.df[self.category_col] == category][self.x_axis],
                    y = self.df[self.df[self.category_col] == category][self.y_axis],
                    name = str(category),
                    marker = self.marker_data[n] if self.marker_data is not None else None,
                    text = self.bars_text,
                    textposition = self.text_position,
                    orientation = self.orientation
                ) for n, category in enumerate(self.category_values)
            ]
        )
        self.fig.update_layout(barmode = self.barmode)
        if self.palette:
            self.update_layout_colors(self.palette.main)
            
        self.update_layout_titles()

    # def gen_categorical_bars_data(self) -> dict:
    #     marker_colors = None
        
    #     bars_data = {'barmode': self.barmode}

    #     if self.palette:
    #         size = len(self.x_values)
    #         marker_colors = [
    #             self.palette.colors[n % size] for n in size
    #         ]

    #     if self.bar_colors:
    #         marker_colors = self.bar_colors

    #     if marker_colors:
    #         bars_layout = [
    #             {
    #                 'color': marker_colors[n]
    #             } for n in self.category_values
    #         ]

    #     else:
    #         bars_layout = [{'color': self.}]
    #     return bars_data