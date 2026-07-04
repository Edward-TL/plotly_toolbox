"""Generate an HTML gallery of every chart type.

Run it directly to write one ``.html`` per chart (plus an ``index.html``) into
``examples/output/`` (gitignored):

    python examples/gallery.py

``build_gallery()`` is also imported by the test-suite so the examples stay
runnable in CI.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from plotly_toolbox import (
    DEFAULT,
    BoxPlot,
    ComparisonBars,
    DonutPlot,
    Graph,
    Heatmap,
    Histogram,
    MultiAreaPlot,
    MultiLinePlot,
    OneAreaPlot,
    OneCategoryBars,
    OneLinePlot,
    PiePlot,
    ScatterPlot,
    ViolinPlot,
)


def sample_data() -> dict[str, pd.DataFrame]:
    """A small, coherent set of DataFrames used across the gallery."""
    rng = np.random.default_rng(42)

    dates = pd.date_range("2024-01-01", periods=24, freq="D")
    daily = pd.DataFrame({"date": dates, "sales": np.linspace(100, 260, 24) + rng.normal(0, 8, 24)})

    regions = ["North", "South"]
    multi = pd.DataFrame(
        {
            "date": list(dates) * 2,
            "sales": np.r_[np.linspace(80, 200, 24), np.linspace(120, 180, 24)] + rng.normal(0, 6, 48),
            "region": np.repeat(regions, 24),
        }
    )

    by_region = pd.DataFrame({"region": ["North", "South", "East", "West"], "sales": [230, 180, 140, 90]})

    months = ["Jan", "Feb", "Mar"]
    comparison = pd.DataFrame(
        {
            "month": months * 2,
            "sales": [120, 150, 170, 90, 110, 130],
            "region": np.repeat(["North", "South"], 3),
        }
    )

    points = pd.DataFrame(
        {
            "height": rng.normal(170, 10, 120),
            "weight": rng.normal(70, 12, 120),
            "age": rng.integers(18, 70, 120),
            "group": rng.choice(["A", "B"], 120),
        }
    )

    heat = pd.DataFrame(
        {
            "month": np.tile(months, 4),
            "region": np.repeat(["North", "South", "East", "West"], 3),
            "sales": rng.integers(20, 100, 12),
        }
    )

    return {
        "daily": daily,
        "multi": multi,
        "by_region": by_region,
        "comparison": comparison,
        "points": points,
        "heat": heat,
    }


def build_gallery(palette=DEFAULT) -> dict[str, Graph]:
    """Return one representative chart per type, keyed by a slug."""
    d = sample_data()
    return {
        "line": OneLinePlot(
            df=d["daily"], name="Daily sales", x_axis="date", y_axis="sales",
            mode="lines+markers", line_shape="spline", trendline_color="#e63946", palette=palette,
        ),
        "multi_line": MultiLinePlot(
            df=d["multi"], name="Sales by region", x_axis="date", y_axis="sales",
            category_col="region", palette=palette,
        ),
        "area": OneAreaPlot(
            df=d["daily"], name="Daily sales (area)", x_axis="date", y_axis="sales", palette=palette,
        ),
        "multi_area": MultiAreaPlot(
            df=d["multi"], name="Stacked sales", x_axis="date", y_axis="sales",
            category_col="region", palette=palette,
        ),
        "bar": OneCategoryBars(
            df=d["by_region"], name="Sales by region", x_axis="region", y_axis="sales",
            is_money="y", palette=palette,
        ),
        "comparison_bar": ComparisonBars(
            df=d["comparison"], name="Monthly sales by region", x_axis="month", y_axis="sales",
            category_col="region", palette=palette,
        ),
        "scatter": ScatterPlot(
            df=d["points"], name="Height vs weight", x_axis="height", y_axis="weight",
            size_col="age", color_col="age", colorscale="Viridis", palette=palette,
        ),
        "histogram": Histogram(
            df=d["points"], name="Weight by group", column="weight", category_col="group", palette=palette,
        ),
        "box": BoxPlot(
            df=d["points"], name="Weight by group", value_col="weight", category_col="group", palette=palette,
        ),
        "violin": ViolinPlot(
            df=d["points"], name="Weight by group", value_col="weight", category_col="group", palette=palette,
        ),
        "heatmap": Heatmap(
            df=d["heat"], name="Sales heatmap", x_col="month", y_col="region", z_col="sales",
            colorscale="Blues", show_text=True, palette=palette,
        ),
        "pie": PiePlot(
            df=d["by_region"], name="Region share", labels_col="region", values_col="sales", palette=palette,
        ),
        "donut": DonutPlot(
            df=d["by_region"], name="Region share", labels_col="region", values_col="sales", palette=palette,
        ),
    }


def main(outdir: str = "examples/output") -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    charts = build_gallery()
    for slug, chart in charts.items():
        chart.to_html(str(out / f"{slug}.html"))

    links = "\n".join(f'<li><a href="{slug}.html">{slug}</a></li>' for slug in charts)
    (out / "index.html").write_text(
        f"<!doctype html><meta charset=utf-8><title>plotly_toolbox gallery</title>"
        f"<h1>plotly_toolbox gallery</h1><ul>{links}</ul>"
    )
    print(f"Wrote {len(charts)} charts + index to {out}/")


if __name__ == "__main__":
    main()
