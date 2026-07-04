"""Bar charts (single-series and grouped comparison)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Union

from plotly import graph_objects as go

from plotly_toolbox.core import CategorySplit, PlotlySublotType, TwoDimensionGraph

BarMode = Literal["group", "stack", "relative", "overlay"]
TextPosition = Literal["inside", "outside", "auto", "none"]

CornerRadiusExample = Literal[30, None, '30%']
# https://plotly.com/python/horizontal-bar-charts/


@dataclass(kw_only=True)
class BarsMarker:
    color: str
    line_color: Optional[str] = None
    line_width: Optional[int] = None
    cornerradius: Optional[Union[CornerRadiusExample, int, str]] = "30%"

    def __post_init__(self):
        self.data = {'color': self.color}

        if self.line_color is not None or self.line_width is not None:
            self.data['line'] = {}
            if self.line_color:
                self.data['line']['color'] = self.line_color
            if self.line_width:
                self.data['line']['width'] = self.line_width

        if self.cornerradius:
            self.data['cornerradius'] = self.cornerradius


@dataclass(kw_only=True)
class BarPlot(TwoDimensionGraph):
    subplot_type: Optional[PlotlySublotType] = 'xy'
    barmode: BarMode = 'stack'
    orientation: Literal['h', 'v'] = 'h'
    hover_data: Optional[list] = None
    bar_colors: Optional[list] = None
    bar_markers: Optional[Union[list["BarsMarker"], list[dict], list[str], list[list]]] = None
    text_position: TextPosition = 'auto'

    marker_data: Optional[Union[dict, list]] = None
    bars_text_column: Optional[str] = None
    bars_text: Optional[list] = None

    def __post_init__(self):
        super().__post_init__()
        if self.orientation not in ('h', 'v'):
            raise ValueError(f"`orientation` must be 'h' or 'v'. Got: {self.orientation!r}")

        if self.hover_data is None:
            self.hover_data = self.df.columns

        if self.bar_markers is None and self.bar_colors is not None:
            self.marker_data = [{'color': color} for color in self.bar_colors]

        if self.bar_markers:
            is_nested_list = False
            try:
                is_nested_list = isinstance(self.bar_markers[0], list)
            except (IndexError, TypeError):
                is_nested_list = False

            if is_nested_list:
                self.marker_data = [
                    self.generate_markers_data(nested) for nested in self.bar_markers
                ]
            else:
                self.marker_data = self.generate_markers_data(self.bar_markers)

        if self.bars_text_column is not None:
            self.bars_text = self.df[self.bars_text_column]
        elif self.orientation == 'h':
            self.bars_text = self.x_values
        else:
            self.bars_text = self.y_values

    def extract_markers_data(self, bar_marker) -> dict:
        if isinstance(bar_marker, BarsMarker):
            return bar_marker.data
        if isinstance(bar_marker, dict):
            return bar_marker
        if isinstance(bar_marker, str):
            return {'color': bar_marker}
        raise TypeError(f"Unsupported bar marker type: {type(bar_marker).__name__}")

    def generate_markers_data(self, bar_markers) -> list[dict]:
        if isinstance(bar_markers, list):
            return [self.extract_markers_data(bm) for bm in bar_markers]
        marker_data = self.extract_markers_data(bar_markers)
        return [marker_data] * len(self.x_values)

    def layout_patch(self) -> dict:
        layout = super().layout_patch()
        layout['barmode'] = self.barmode
        return layout


@dataclass(kw_only=True)
class OneCategoryBars(BarPlot):
    """A single-series bar plot."""

    def build_traces(self) -> list:
        return [
            go.Bar(
                x=self.x_values,
                y=self.y_values,
                marker=self.marker_data,
                text=self.bars_text,
                textposition=self.text_position,
                orientation=self.orientation,
            )
        ]


@dataclass(kw_only=True)
class ComparisonBars(CategorySplit, BarPlot):
    """A grouped bar plot comparing a category across series."""
    barmode: Literal['group'] = 'group'
    text_position: TextPosition = 'auto'

    def __post_init__(self):
        super().__post_init__()
        self.resolve_categories()

    def _marker_for(self, index: int):
        if isinstance(self.marker_data, list):
            return self.marker_data[index]
        return self.marker_data

    def build_traces(self) -> list:
        return [
            go.Bar(
                x=sub_df[self.x_axis],
                y=sub_df[self.y_axis],
                name=str(category),
                marker=self._marker_for(index),
                text=self.bars_text,
                textposition=self.text_position,
                orientation=self.orientation,
            )
            for index, category, sub_df, _ in self.iter_series()
        ]


# Backwards-compatible alias for the previous (misspelled) class name.
ComparasionBars = ComparisonBars
