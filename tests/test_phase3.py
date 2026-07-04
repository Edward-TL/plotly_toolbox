"""Smoke + behavior tests for the Phase 3 chart types."""

import numpy as np
import pandas as pd
import pytest

from plotly_toolbox import (
    BoxPlot,
    DonutPlot,
    Heatmap,
    Histogram,
    PiePlot,
    ScatterPlot,
    ViolinPlot,
)


@pytest.fixture
def points_df():
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "height": rng.normal(170, 10, 50),
            "weight": rng.normal(70, 12, 50),
            "age": rng.integers(18, 70, 50),
            "group": rng.choice(["a", "b"], 50),
        }
    )


@pytest.fixture
def share_df():
    return pd.DataFrame({"region": ["n", "s", "e", "w"], "sales": [10, 20, 30, 40]})


def _types(chart):
    return [tr["type"] for tr in chart.fig.to_dict()["data"]]


# -- scatter ---------------------------------------------------------------

def test_scatter_basic(points_df):
    chart = ScatterPlot(df=points_df, name="H vs W", x_axis="height", y_axis="weight")
    assert _types(chart) == ["scatter"]
    assert chart.fig.to_dict()["data"][0]["mode"] == "markers"


def test_scatter_size_and_color_encoding(points_df):
    chart = ScatterPlot(
        df=points_df, name="H vs W", x_axis="height", y_axis="weight",
        size_col="age", color_col="age", colorscale="Viridis",
    )
    marker = chart.figure.data[0].marker
    assert list(marker.size) == list(points_df["age"])
    assert marker.colorscale  # a colorscale was applied
    assert marker.showscale is True


def test_scatter_with_trendline(points_df):
    chart = ScatterPlot(
        df=points_df, name="H vs W", x_axis="height", y_axis="weight", trendline_color="red"
    )
    assert len(_types(chart)) == 2


def test_scatter_bad_size_col_raises(points_df):
    with pytest.raises(KeyError):
        ScatterPlot(df=points_df, name="x", x_axis="height", y_axis="weight", size_col="nope")


# -- histogram -------------------------------------------------------------

def test_histogram_basic(points_df):
    chart = Histogram(df=points_df, name="Ages", column="age", nbins=10)
    assert _types(chart) == ["histogram"]
    assert chart.fig.to_dict()["data"][0]["nbinsx"] == 10


def test_histogram_category_overlay(points_df):
    chart = Histogram(df=points_df, name="By group", column="weight", category_col="group")
    data = chart.fig.to_dict()["data"]
    assert len(data) == 2
    assert chart.fig.to_dict()["layout"]["barmode"] == "overlay"


# -- pie / donut -----------------------------------------------------------

def test_pie_basic(share_df):
    chart = PiePlot(df=share_df, name="Share", labels_col="region", values_col="sales")
    trace = chart.figure.data[0]
    assert trace.type == "pie"
    assert trace.hole in (0, 0.0)
    assert list(trace.values) == [10, 20, 30, 40]


def test_donut_has_hole(share_df):
    chart = DonutPlot(df=share_df, name="Share", labels_col="region", values_col="sales")
    assert chart.fig.to_dict()["data"][0]["hole"] == 0.5


def test_pie_bad_col_raises(share_df):
    with pytest.raises(KeyError):
        PiePlot(df=share_df, name="x", labels_col="region", values_col="nope")


# -- distribution ----------------------------------------------------------

def test_box_basic(points_df):
    chart = BoxPlot(df=points_df, name="Weights", value_col="weight")
    assert _types(chart) == ["box"]


def test_box_grouped(points_df):
    chart = BoxPlot(df=points_df, name="Weights", value_col="weight", category_col="group")
    assert len(_types(chart)) == 2


def test_violin_uses_violin_trace(points_df):
    chart = ViolinPlot(df=points_df, name="Weights", value_col="weight")
    assert _types(chart) == ["violin"]


def test_distribution_orientation_axis(points_df):
    v = BoxPlot(df=points_df, name="w", value_col="weight", orientation="v")
    h = BoxPlot(df=points_df, name="w", value_col="weight", orientation="h")
    assert "y" in v.fig.to_dict()["data"][0]
    assert "x" in h.fig.to_dict()["data"][0]


# -- heatmap ---------------------------------------------------------------

def test_heatmap_long_form():
    df = pd.DataFrame(
        {
            "month": ["jan", "feb", "jan", "feb"],
            "region": ["n", "n", "s", "s"],
            "sales": [1, 2, 3, 4],
        }
    )
    chart = Heatmap(df=df, name="Sales", x_col="month", y_col="region", z_col="sales")
    d = chart.fig.to_dict()["data"][0]
    assert d["type"] == "heatmap"
    assert sorted(d["x"]) == ["feb", "jan"]
    assert sorted(d["y"]) == ["n", "s"]


def test_heatmap_wide_form():
    matrix = pd.DataFrame([[1, 2], [3, 4]], index=["a", "b"], columns=["x", "y"])
    chart = Heatmap(df=matrix, name="M", show_text=True)
    d = chart.fig.to_dict()["data"][0]
    assert d["type"] == "heatmap"
    assert d["texttemplate"].startswith("%{text")


def test_heatmap_partial_long_cols_raises():
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    with pytest.raises(ValueError):
        Heatmap(df=df, name="x", x_col="a", y_col="b")  # missing z_col


# -- bar default orientation ----------------------------------------------

def test_bar_default_orientation_is_vertical(share_df):
    from plotly_toolbox import OneCategoryBars

    chart = OneCategoryBars(df=share_df, name="Sales", x_axis="region", y_axis="sales")
    assert chart.fig.to_dict()["data"][0]["orientation"] == "v"
