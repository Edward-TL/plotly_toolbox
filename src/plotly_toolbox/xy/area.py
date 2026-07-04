"""Area charts (single and multi-series)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union

from plotly import graph_objects as go

from plotly_toolbox.xy.line import CategoricalLines, LinePlot

FillType = Literal[
    'none',
    'tozeroy', 'tozerox',
    'tonexty', 'tonextx',
    'toself', 'tonext',
]

fill_types_allowed = [
    'none',
    'tozeroy', 'tozerox',
    'tonexty', 'tonextx',
    'toself', 'tonext',
]


@dataclass(kw_only=True)
class AreaPlot(LinePlot):
    fill_type: FillType = 'tozeroy'


@dataclass(kw_only=True)
class OneAreaPlot(AreaPlot):
    """A single-series area plot."""

    def build_traces(self) -> list:
        return [
            go.Scatter(
                x=self.x_values,
                y=self.y_values,
                name=self.name,
                line=self.gen_simple_line_data(),
                showlegend=False,
                fill=self.fill_type,
                mode=self.mode,
            )
        ]


@dataclass(kw_only=True)
class CategoricalAreas(CategoricalLines):
    fill_type: Union[list[FillType], FillType] = 'tonexty'


@dataclass(kw_only=True)
class MultiAreaPlot(CategoricalAreas):
    """An area plot with one filled series per category."""

    def _resolve_fills(self) -> list:
        n = len(self.category_values)
        if isinstance(self.fill_type, str):
            if self.fill_type not in fill_types_allowed:
                raise ValueError(
                    f"`fill_type` must be one of {fill_types_allowed}. Got: {self.fill_type}"
                )
            fills = [self.fill_type] * n
            fills[0] = 'tozeroy'
            return fills
        if isinstance(self.fill_type, (list, tuple)):
            return list(self.fill_type)
        raise ValueError(
            f"`fill_type` must be a str or list of {fill_types_allowed}. Got: {self.fill_type}"
        )

    def build_traces(self) -> list:
        fills = self._resolve_fills()
        layouts = self.line_layouts()
        return [
            go.Scatter(
                x=sub_df[self.x_axis],
                y=sub_df[self.y_axis],
                name=str(category),
                line=layouts[index],
                mode=self.mode,
                fill=fills[index],
                showlegend=self.show_legend,
            )
            for index, category, sub_df, _ in self.iter_series()
        ]
