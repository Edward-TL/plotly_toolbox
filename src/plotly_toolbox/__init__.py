"""Plotly Toolbox — object-oriented, sensible-defaults wrapper around Plotly."""

from plotly_toolbox.core import (
    CategorySplit,
    ColorRange,
    Graph,
    OneDimensionPlot,
    Palette,
    Scale,
    Theme,
    TwoDimensionGraph,
    deep_merge,
    get_option,
    set_option,
)
from plotly_toolbox.domain.pie import DonutPlot, PiePlot
from plotly_toolbox.palettes import DARK, DEFAULT, MINIMAL
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
from plotly_toolbox.xy.distribution import BoxPlot, DistributionPlot, ViolinPlot
from plotly_toolbox.xy.heatmap import Heatmap
from plotly_toolbox.xy.histogram import Histogram
from plotly_toolbox.xy.line import (
    CategoricalLines,
    LinePlot,
    MultiLinePlot,
    OneLinePlot,
)
from plotly_toolbox.xy.scatter import ScatterPlot

__version__ = "0.3.0"

__all__ = [
    # options / config
    "get_option",
    "set_option",
    # palette / theming
    "ColorRange",
    "Scale",
    "Theme",
    "Palette",
    "DEFAULT",
    "DARK",
    "MINIMAL",
    # pipeline primitives
    "Graph",
    "OneDimensionPlot",
    "TwoDimensionGraph",
    "CategorySplit",
    "deep_merge",
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
    # scatter / distribution / heatmap
    "ScatterPlot",
    "Histogram",
    "DistributionPlot",
    "BoxPlot",
    "ViolinPlot",
    "Heatmap",
    # domain
    "PiePlot",
    "DonutPlot",
]
