"""Heatmaps from either a wide matrix DataFrame or long (x, y, z) columns.

Example
-------
>>> # long form
>>> Heatmap(df=df, name="Sales", x_col="month", y_col="region", z_col="sales").show()
>>> # wide form: index = y, columns = x, values = z
>>> Heatmap(df=matrix_df, name="Correlation", show_text=True).show()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from plotly import graph_objects as go

from plotly_toolbox.core import Graph, PlotlySublotType


@dataclass(kw_only=True)
class Heatmap(Graph):
    """A heatmap.

    Provide all of ``x_col``/``y_col``/``z_col`` to build from a long DataFrame
    (it is pivoted internally), or none of them to treat ``df`` as a wide matrix
    (its index is the y axis, its columns the x axis).
    """
    subplot_type: Optional[PlotlySublotType] = 'xy'
    x_col: Optional[str] = None
    y_col: Optional[str] = None
    z_col: Optional[str] = None
    colorscale: Optional[str] = None
    show_text: bool = False
    text_format: str = '.0f'

    def __post_init__(self):
        super().__post_init__()
        long_cols = (self.x_col, self.y_col, self.z_col)
        if any(long_cols) and not all(long_cols):
            raise ValueError("Provide all of `x_col`, `y_col`, `z_col` for long form, or none for wide form.")
        for col in long_cols:
            if col is not None and col not in self.df.columns:
                raise KeyError(
                    f"Column '{col}' not found in DataFrame. Available: {list(self.df.columns)}"
                )

    def _matrix(self):
        if self.x_col and self.y_col and self.z_col:
            pivot = self.df.pivot(index=self.y_col, columns=self.x_col, values=self.z_col)
            return pivot.columns.tolist(), pivot.index.tolist(), pivot.values
        return self.df.columns.tolist(), self.df.index.tolist(), self.df.values

    def build_traces(self) -> list:
        x, y, z = self._matrix()
        kwargs = {'x': x, 'y': y, 'z': z, 'name': self.name}
        if self.colorscale:
            kwargs['colorscale'] = self.colorscale
        if self.show_text:
            kwargs['text'] = z
            kwargs['texttemplate'] = '%{text:' + self.text_format + '}'
        return [go.Heatmap(**kwargs)]

    def layout_patch(self) -> dict:
        return self.styled_layout()
