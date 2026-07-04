"""Plotly Toolbox — object-oriented, sensible-defaults wrapper around Plotly."""

from plotly_toolbox.core import (
    ColorRange,
    Graph,
    OneDimensionPlot,
    Palette,
    Scale,
    Theme,
    TwoDimensionGraph,
    get_option,
    set_option,
)
from plotly_toolbox.xy.area import (
    AreaPlot,
    CategoricalAreas,
    MultiAreaPlot,
    OneAreaPlot,
)
from plotly_toolbox.xy.bars import (
    BarPlot,
    BarsMarker,
    ComparasionBars,  # deprecated alias
    ComparisonBars,
    OneCategoryBars,
)
from plotly_toolbox.xy.line import (
    CategoricalLines,
    LinePlot,
    MultiLinePlot,
    OneLinePlot,
)

__version__ = "0.1.1"

__all__ = [
    # options / config
    "get_option",
    "set_option",
    # palette / theming
    "ColorRange",
    "Scale",
    "Theme",
    "Palette",
    # base classes
    "Graph",
    "OneDimensionPlot",
    "TwoDimensionGraph",
    # line
    "LinePlot",
    "OneLinePlot",
    "CategoricalLines",
    "MultiLinePlot",
    # area
    "AreaPlot",
    "OneAreaPlot",
    "CategoricalAreas",
    "MultiAreaPlot",
    # bars
    "BarsMarker",
    "BarPlot",
    "OneCategoryBars",
    "ComparisonBars",
    "ComparasionBars",
]
