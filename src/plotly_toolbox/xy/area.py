"""
Core of line and area plots
"""

from dataclasses import dataclass, asdict
from typing import Literal, Optional

from plotly import graph_objects as go
import pandas as pd


from plotly_toolbox.core import TwoDimensionGraph
from plotly_toolbox.xy.line import LineMode, LineShape, LinePlot, CategoricalLines

FillType = Literal[
    'none',
    'tozeroy', 'tozerox',
    'tonexty', 'tonextx',
    'toself', 'tonext'
]

fill_types_allowed = [
    'none',
    'tozeroy', 'tozerox',
    'tonexty', 'tonextx',
    'toself', 'tonext'
]

@dataclass(kw_only=True)
class AreaPlot(LinePlot):
    subplot_type = 'xy'
    fill_type: FillType = 'tozeroy'
    def __post_init__(self):
        super().__post_init__()


@dataclass(kw_only=True)
class OneAreaPlot(AreaPlot):
    """
    Representation of Line Plot
    """
    def __post_init__(self):
        super().__post_init__()
        
        line_data = self.gen_simple_line_data()
        
        self.plot = go.Scatter(
            x = self.x_values,
            y = self.y_values,
            name = self.name,
            line = line_data,
            showlegend = False,
            fill = self.fill_type,
            mode = self.line
        )

        self.fig.add_traces([self.plot])
        self.general_layout_update()


@dataclass(kw_only=True)
class CategoricalAreas(CategoricalLines):
    colors: Optional[str] = None
    fill_type: list[FillType] | FillType = 'tonexty'

    def __post_init__(self):
        super().__post_init__()
        
@dataclass(kw_only=True)
class MultiAreaPlot(CategoricalAreas):
    """
    Representation of multiple lines Plot
    """
    def __post_init__(self):
        super().__post_init__()
            
        if isinstance(self.fill_type, str):
            if self.fill_type not in fill_types_allowed:
                ft_err = f"`fill_type` must be one of {fill_types_allowed}. Got: {self.fill_type}"
                raise ValueError(ft_err)
            fill_type = [self.fill_type] * len(self.category_values)
            fill_type[0] = 'tozeroy'

        elif isinstance(self.fill_type, (list, tuple)):
            fill_type = list(self.fill_type)

        else:
            ft_err = f"`fill_type` must be a str or list of {fill_types_allowed}. Got: {self.fill_type}"
            raise ValueError(ft_err)

        line_data = self.gen_multiple_line_data()

        self.fig.add_traces(
            [
                go.Scatter(
                    x = self.df[self.df[self.category_col] == category][self.x_axis],
                    y = self.df[self.df[self.category_col] == category][self.y_axis],
                    name = category,
                    line = line_data[n],
                    mode = self.lines,
                    fill = fill_type[n],
                    showlegend = self.show_legend
                ) for n, category in enumerate(self.category_values)
            ]
        )

        self.general_layout_update()     
