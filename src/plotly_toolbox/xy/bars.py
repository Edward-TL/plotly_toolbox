

"""
Collection of Two dimensional Graphs
"""

from dataclasses import dataclass, asdict
from typing import Literal, Optional

from plotly import graph_objects as go

from plotly_toolbox.core import TwoDimensionGraph
import pandas as pd




@dataclass(kw_only=True)
class BarPlot(TwoDimensionGraph):
    """
    Representation of Bar Plot
    """
    category_col: Optional[str] = None
    barmode: Literal['group'] = 'group'
    textposition: Literal['auto'] = 'auto'

    def __post_init__(self):
        marker_color = None
        if self.palette is not None:
            marker_color = self.palette_data['cat_0']

        if self.category_col is None:
            self.fig = go.Figure(
                data = go.Bar(
                    x = self.x_values,
                    y = self.y_values,
                    marker_color = marker_color,
                    text = self.df[self.y_axis],
                    textposition = self.textposition
                )
            )
        else:
            go.Figure(
            data = [
                    go.Scatter(
                        x = self.df[[self.category_col] == category][self.x_axis],
                        y = self.df[[self.category_col] == category][self.y_axis],
                        marker_color = self.palette_data[f'cat_{c}'] if self.palette else None,
                        name = category,
                        text = self.df[[self.category_col] == category][self.y_axis],
                        textposition='auto'
                ) for c, category in enumerate(
                    tuple(
                        self.df[self.category_col].unique()
                        )
                    ) 
            ]
        )
        self.fig.update_layout(barmode = self.barmode)
        if self.palette:
            self.update_layout_colors(self.palette.main)
            
        self.update_layout_titles()
