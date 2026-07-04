"""Smoke + regression tests for the concrete chart classes.

Plotly validates figure schema on construction, so asserting that
``chart.fig.to_dict()`` succeeds and contains the expected traces is a
cheap correctness check that needs no browser.
"""

from plotly_toolbox import (
    ComparisonBars,
    MultiAreaPlot,
    MultiLinePlot,
    OneAreaPlot,
    OneCategoryBars,
    OneLinePlot,
)


def _n_traces(chart):
    return len(chart.fig.to_dict()["data"])


def test_one_line_plot_renders(daily_df):
    chart = OneLinePlot(df=daily_df, name="Sales", x_axis="date", y_axis="sales")
    assert _n_traces(chart) == 1
    assert chart.fig.to_dict()["data"][0]["type"] == "scatter"


def test_one_line_plot_with_datetime_trendline(daily_df):
    # Regression: np.polyfit used to crash on datetime x-values.
    chart = OneLinePlot(
        df=daily_df, name="Sales", x_axis="date", y_axis="sales", trendline_color="red"
    )
    data = chart.fig.to_dict()["data"]
    assert len(data) == 2  # line + trendline
    names = {tr.get("name") for tr in data}
    assert "trendline" in names


def test_one_line_plot_respects_palette(daily_df, palette):
    chart = OneLinePlot(
        df=daily_df, name="Sales", x_axis="date", y_axis="sales", palette=palette
    )
    layout = chart.fig.to_dict()["layout"]
    # Regression: palette handling used to raise (dict-style indexing of a dataclass).
    assert layout["plot_bgcolor"] == "#ffffff"
    assert layout["paper_bgcolor"] == "#fafafa"


def test_multi_line_plot_with_palette_colors(category_df, palette):
    # Regression: gen_multiple_line_data iterated over an int and mis-indexed colors.
    chart = MultiLinePlot(
        df=category_df,
        name="By region",
        x_axis="month",
        y_axis="sales",
        category_col="region",
        palette=palette,
    )
    data = chart.fig.to_dict()["data"]
    assert len(data) == 2  # north, south
    assert data[0]["line"]["color"] == "#e63946"
    assert data[1]["line"]["color"] == "#457b9d"


def test_multi_line_plot_respects_mode(category_df):
    # Regression: mode was hardcoded to 'lines', ignoring the series mode.
    chart = MultiLinePlot(
        df=category_df,
        name="By region",
        x_axis="month",
        y_axis="sales",
        category_col="region",
        mode="lines+markers",
    )
    assert chart.fig.to_dict()["data"][0]["mode"] == "lines+markers"


def test_one_area_plot_renders(daily_df):
    chart = OneAreaPlot(df=daily_df, name="Sales", x_axis="date", y_axis="sales")
    assert chart.fig.to_dict()["data"][0]["fill"] == "tozeroy"


def test_multi_area_plot_with_list_fill(category_df):
    # Regression: isinstance against a typing.Literal raised TypeError for list input.
    chart = MultiAreaPlot(
        df=category_df,
        name="By region",
        x_axis="month",
        y_axis="sales",
        category_col="region",
        fill_type=["tozeroy", "tonexty"],
    )
    assert _n_traces(chart) == 2


def test_one_category_bars_renders(category_df):
    chart = OneCategoryBars(
        df=category_df.head(3), name="Sales", x_axis="month", y_axis="sales", orientation="v"
    )
    assert chart.fig.to_dict()["data"][0]["type"] == "bar"


def test_comparison_bars_renders(category_df, palette):
    # Regression: class rebuilt the figure and skipped the layout pipeline;
    # also exercises the money-formatting path via general_layout_update.
    chart = ComparisonBars(
        df=category_df,
        name="Sales by region",
        x_axis="month",
        y_axis="sales",
        category_col="region",
        orientation="v",
        palette=palette,
        is_money="y",
    )
    fig = chart.fig.to_dict()
    assert len(fig["data"]) == 2
    assert fig["layout"]["barmode"] == "group"
    # general_layout_update ran → money prefix applied, title set.
    assert fig["layout"]["yaxis"]["tickprefix"] == "$"
    assert fig["layout"]["title"]["text"] == "Sales by region"


def test_comparasion_bars_alias_exists():
    from plotly_toolbox import ComparasionBars, ComparisonBars

    assert ComparasionBars is ComparisonBars
