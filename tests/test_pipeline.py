"""Tests for the Phase 2 rendering pipeline: traces-as-contract, lazy figure,
deprecation shims, built-in palettes, and option validation.
"""

import warnings

import pytest

import plotly_toolbox as ptb
from plotly_toolbox import (
    DARK,
    DEFAULT,
    MultiLinePlot,
    OneLinePlot,
    deep_merge,
    set_option,
)
from plotly_toolbox.core import Graph, _GLOBAL_OPTIONS


def test_deep_merge_combines_nested_dicts():
    base = {"xaxis": {"title": {"text": "x"}}}
    deep_merge(base, {"xaxis": {"tickprefix": "$"}, "barmode": "group"})
    assert base == {
        "xaxis": {"title": {"text": "x"}, "tickprefix": "$"},
        "barmode": "group",
    }


def test_traces_are_contract(daily_df):
    chart = OneLinePlot(df=daily_df, name="Sales", x_axis="date", y_axis="sales")
    traces = chart.traces()
    assert isinstance(traces, list) and len(traces) == 1
    # layout_patch is a plain dict, independent of any figure.
    patch = chart.layout_patch()
    assert patch["title"]["text"] == "Sales"
    assert patch["xaxis"]["title"]["text"] == "date"


def test_figure_is_lazy_and_cached(daily_df):
    chart = OneLinePlot(df=daily_df, name="Sales", x_axis="date", y_axis="sales")
    # Not built until accessed.
    assert chart._figure is None
    first = chart.figure
    assert chart._figure is first
    # fig is an alias for figure and returns the same cached object.
    assert chart.fig is first


def test_base_graph_requires_build_traces(daily_df):
    g = Graph(df=daily_df, name="x")
    with pytest.raises(NotImplementedError):
        g.traces()


def test_line_deprecated_alias_maps_to_mode(daily_df):
    with pytest.warns(DeprecationWarning):
        chart = OneLinePlot(
            df=daily_df, name="Sales", x_axis="date", y_axis="sales", line="lines+markers"
        )
    assert chart.mode == "lines+markers"
    assert chart.fig.to_dict()["data"][0]["mode"] == "lines+markers"


def test_lines_deprecated_alias_maps_to_mode(category_df):
    with pytest.warns(DeprecationWarning):
        chart = MultiLinePlot(
            df=category_df,
            name="By region",
            x_axis="month",
            y_axis="sales",
            category_col="region",
            lines="markers",
        )
    assert chart.mode == "markers"


def test_builtin_palette_applies_background(daily_df):
    chart = OneLinePlot(df=daily_df, name="Sales", x_axis="date", y_axis="sales", palette=DARK)
    layout = chart.fig.to_dict()["layout"]
    assert layout["plot_bgcolor"] == DARK.resolve().plot_bg
    assert layout["font"]["color"] == DARK.resolve().font_color


def test_missing_column_raises(daily_df):
    with pytest.raises(KeyError):
        OneLinePlot(df=daily_df, name="Sales", x_axis="nope", y_axis="sales")


def test_category_split_requires_category(category_df):
    with pytest.raises(ValueError):
        MultiLinePlot(df=category_df, name="x", x_axis="month", y_axis="sales")


def test_set_option_validates_type():
    with pytest.raises(TypeError):
        set_option("palette", "not-a-palette")
    with pytest.raises(KeyError):
        set_option("bogus", 1)


def test_set_option_palette_roundtrip(daily_df):
    original = _GLOBAL_OPTIONS["palette"]
    try:
        set_option("palette", DEFAULT)
        # A chart created without an explicit palette picks up the global default.
        chart = OneLinePlot(df=daily_df, name="Sales", x_axis="date", y_axis="sales")
        assert chart.palette is DEFAULT
    finally:
        _GLOBAL_OPTIONS["palette"] = original


def test_to_html_returns_string(daily_df):
    chart = OneLinePlot(df=daily_df, name="Sales", x_axis="date", y_axis="sales")
    html = chart.to_html()
    assert isinstance(html, str) and "<html" in html.lower()


def test_no_deprecation_warning_on_normal_use(daily_df):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        OneLinePlot(df=daily_df, name="Sales", x_axis="date", y_axis="sales", mode="lines")


def test_top_level_exports_pipeline_primitives():
    for name in ["CategorySplit", "deep_merge", "DEFAULT", "DARK", "MINIMAL"]:
        assert hasattr(ptb, name)
