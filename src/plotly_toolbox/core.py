# Check for the palette object
from typing import Literal, Optional
from dataclasses import dataclass, field

from plotly import graph_objects as go
import pandas as pd

from pandas import DataFrame as PandasDataFrame

ThemePalette = Literal['light', 'dark']

PlotlyTemplate = Literal[
    'ggplot2', 'seaborn', 'simple_white', 'plotly',
    'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
    'ygridoff', 'gridon', 'none'
    ]

PlotlySublotType = Literal[
    "xy",  # Cartesian 2D axes
    "polar",  # Polar axes
    "scene",  # 3D axes
    "geo",  # Geographic map
    "mapbox",  # Mapbox map
    "ternary",  # Ternary plot
    "domain",  # For pie charts, sunburst, etc.
]

_GLOBAL_OPTIONS = {
    'palette': None,
    'template': 'seaborn' 
}

def get_option(key):
    """
    Public function to retrieve a current option value.
    """
    if key not in _GLOBAL_OPTIONS:
        raise KeyError(f"Invalid option key: '{key}'")
    return _GLOBAL_OPTIONS[key]

def set_option(key, value):
    """
    Public function to set a new option value.
    This is the function users will call.
    """
    if key not in _GLOBAL_OPTIONS:
        raise KeyError(f"Invalid option key: '{key}'")
    # Add validation logic here if needed (e.g., check value type)
    _GLOBAL_OPTIONS[key] = value
    print(f"Global option '{key}' updated to: {value}") 

@dataclass
class ColorRange:
    val: int
    color: str

@dataclass
class Scale:
    color_range: tuple[ColorRange]
    name: str = None

@dataclass
class Theme:
    font: str = 'Arial'
    plot_bg: str = 'white'
    paper_bg: str = 'white'
    colors: Optional[list[str]] = None
    scales: Optional[tuple[Scale]] = None


@dataclass
class Palette:
    """
    Group of themes that can be called
    """
    light: Theme
    dark: Optional[Theme] = None
    main: ThemePalette = 'light'

    def __post_init__(self):
        self.colors = getattr(self, self.main).colors
        self.categories = {f'cat_{c}': color for c, color in enumerate(self.colors)}
        for c, color in enumerate(self.colors):
            setattr(self, f"cat_{c}", color)

@dataclass(kw_only=True)
class Graph:
    """
    Minimum representation of a plot
    """
    df: PandasDataFrame
    name: str
    plot: go.Figure = None
    palette: Optional[Palette] = field(default_factory=lambda: get_option('palette'))
    fig: go.Figure = field(default_factory = go.Figure)
    template: PlotlyTemplate = field(default_factory=lambda:get_option('template'))
    fig_row_pos: int = 0
    fig_col_pos: int = 0
    subplot_type: Optional[PlotlySublotType] = None
    show_legend: bool = True
    subtitle: str = None

    def __post_init__(self):
        if self.palette:
            self.palette_data = self.palette

    def show(self):
        """Show the figure"""
        self.fig.show()

    def update_template(self):
        self.fig.update_layout(
            template = self.template
        )
    def update_layout_colors(self, theme: ThemePalette = 'light'):
        self.fig.update_layout(
            plot_bgcolor = self.palette_data[f'{theme}_plot_bg'],
            paper_bgcolor = self.palette_data[f'{theme}_paper_bg'],
            font = {'color': self.palette_data[f'{theme}_font']},
        )

@dataclass(kw_only=True)
class OneDimensionPlot(Graph):
    """
    General representation of a 1D graph, like:
    - Pie
    - Donut
    """
    def update_layout(self):
        """Updates layout"""
        self.fig.update_layout(
                hoverinfo = 'label+percent',
                textinfo = 'value',
                marker = {'colors' : self.palette.colors}
            )
        if self.palette is not None:
            self.update_layout_colors(self.palette.main)

@dataclass(kw_only=True)
class TwoDimensionGraph(Graph):
    """
    Minimum representation of a 2D-plot, like:
    - Line
    - Scatter
    - Bar

    [Args]
        - x_axis: str = Dataframe Column Name
        - y_axis: str = Dataframe Column Name
    """
    x_axis: str
    y_axis: str
    cat: int  = 0
    x_title: Optional[str] = None
    y_title: Optional[str] = None
    x_tick_text_col: Optional[str] = None
    y_tick_text_col: Optional[str] = None
    is_money: Optional[Literal['x', 'y', 'both']] = None
    number_format: Optional[str] = ',.1s'

    update_tick_text: bool = False
    x_tick_text_vals: Optional[list | tuple | pd.Series] = None
    y_tick_text_vals: Optional[list | tuple | pd.Series] = None

    # Just as reference
    x_tick_vals: Optional[list | tuple | pd.Series] = None
    y_tick_vals: Optional[list | tuple | pd.Series] = None

    x_is_hours: bool = False

    def __post_init__(self):
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
        
        if any([self.x_tick_text_vals is not None, self.y_tick_text_vals is not None]):
            self.update_tick_text = True
        
    def update_layout_titles(
            self,
            main: Optional[str] = None, x_axis: Optional[str] = None, y_axis: Optional[str] = None
        ) -> None:
        """
        Updates graph, x_axis and y_axis titles
        """
        if main:
            self.name = main
        if x_axis:
            self.x_title = x_axis
        if y_axis:
            self.y_title = y_axis
        
        title_data = {'text': self.name}

        if self.subtitle:
            title_data['subtitle'] = {
                'text': self.subtitle,
                'font': {
                    'color': 'gray',
                    'size': 12
                }
            }

        self.fig.update_layout(
            title = title_data,
            xaxis_title = self.x_title,
            yaxis_title = self.y_title
        )

    def update_layout_colors(self, theme: Literal['main', 'light', 'dark']) -> None:
        """
        Updates figure layout related to colors
        """

        self.fig.update_layout(
            plot_bg_color = self.palette.theme
        )
    
    def update_layout_tick_text(self) -> None:
        if self.x_tick_text_vals is not None:
            self.fig.update_layout(
                xaxis = {
                    "ticktext" : self.x_tick_text_vals,
                    "tickvals": list(range(1, len(self.x_tick_text_vals)+1))
                    }
                    # tickmode = 'array',
                    # tickvals = [1, 3, 5, 7, 9, 11],
                    # ticktext = self.x_tick_texts
                # )
            )
        
        if self.y_tick_text_vals is not None:
            self.fig.update_layout(
                yaxis = {
                    "ticktext" : self.y_tick_text_vals,
                    "tickvals": list(range(1, len(self.y_tick_text_vals)+1))
                    }
            )

    def set_x_axis_to_hours(self):
        self.fig.update_layout(
            xaxis = {
                'tick0': 0,
                'dtick': 3
            }
        )

    def addapt_money_labels(self):
        """
        Adapts all money related axis
        """
        if self.is_money in {'y', 'both'}:
            self.fig.update_layout(
                yaxis_tickprefix = '$',
                yaxis_tickformat = self.number_format
            )
        
        if self.is_money in {'x', 'both'}:
            self.fig.update_layout(
                xaxis_tickprefix = '$',
                xaxis_tickformat = self.number_format
            )

    def general_layout_update(self):
        """
        Updates layout according to palette, template and other configurations
        """
        if self.template and not self.palette:
            self.update_template()

        if self.palette:
            self.update_layout_colors(self.palette.main)
            
        if self.is_money:
            self.addapt_money_labels()

        if self.update_tick_text:
            self.update_layout_tick_text()

        if self.x_is_hours:
            self.set_x_axis_to_hours()

        self.update_layout_titles()

    
# Test object

# GrafBajas = LinePlot(
#     df = bajas_dia,
#     name = "Bajas por dia",
#     x_axis= bajas_dia.columns[0],
#     y_axis= bajas_dia.columns[1],
# )



# GrafBajas.show()