# Plotly Toolbox

An object-oriented, sensible-defaults wrapper around [Plotly](https://plotly.com/python/).
Each chart is a small dataclass: pass a `DataFrame` and the column names, get a styled
figure. No boilerplate, and you can still drop down to the underlying `go.Figure` whenever
you need to.

```python
import pandas as pd
from plotly_toolbox import OneLinePlot

df = pd.DataFrame({
    "date": pd.date_range("2024-01-01", periods=10),
    "sales": [120, 135, 150, 165, 180, 200, 210, 225, 240, 260],
})

OneLinePlot(
    df=df,
    name="Monthly Sales",
    x_axis="date",
    y_axis="sales",
    mode="lines+markers",
    line_shape="spline",
    trendline_color="red",
).show()
```

## Installation

```bash
pip install plotly-toolbox
```

Requires Python ≥ 3.10. Depends on `plotly`, `pandas`, and `numpy`.

## Chart catalog

| Chart | Class(es) | Import |
|---|---|---|
| Line | `OneLinePlot`, `MultiLinePlot` | `plotly_toolbox` |
| Area | `OneAreaPlot`, `MultiAreaPlot` | `plotly_toolbox` |
| Bar | `OneCategoryBars`, `ComparisonBars` | `plotly_toolbox` |
| Scatter | `ScatterPlot` | `plotly_toolbox` |
| Histogram | `Histogram` | `plotly_toolbox` |
| Box / Violin | `BoxPlot`, `ViolinPlot` | `plotly_toolbox` |
| Heatmap | `Heatmap` | `plotly_toolbox` |
| Pie / Donut | `PiePlot`, `DonutPlot` | `plotly_toolbox` |

Every class accepts a DataFrame plus the relevant column names and a `name` (the title).
Common options: `palette`, `template`, `subtitle`, `show_legend`, and for Cartesian charts
`x_title` / `y_title`, `is_money` (`'x'`/`'y'`/`'both'`), and tick-text overrides.

```python
from plotly_toolbox import (
    MultiLinePlot, ComparisonBars, ScatterPlot, Histogram,
    BoxPlot, Heatmap, PiePlot, DonutPlot,
)

# multiple series from one long DataFrame
MultiLinePlot(df=df, name="By region", x_axis="date", y_axis="sales", category_col="region")

# grouped comparison bars
ComparisonBars(df=df, name="Monthly", x_axis="month", y_axis="sales", category_col="region")

# scatter with size + color encodings
ScatterPlot(df=df, name="H vs W", x_axis="height", y_axis="weight",
            size_col="age", color_col="bmi", colorscale="Viridis")

# heatmap from long columns (pivoted for you) or a wide matrix
Heatmap(df=df, name="Sales", x_col="month", y_col="region", z_col="sales", show_text=True)

# pie / donut
DonutPlot(df=df, name="Share", labels_col="region", values_col="sales")
```

See [`examples/gallery.py`](examples/gallery.py) for one runnable example of every chart —
`python examples/gallery.py` writes them as HTML into `examples/output/`.

## Palettes & theming

A `Palette` is a light/dark pair of `Theme`s plus a color cycle. Three are built in:

```python
from plotly_toolbox import OneLinePlot, DEFAULT, DARK, MINIMAL, set_option

# per chart
OneLinePlot(df=df, name="Sales", x_axis="date", y_axis="sales", palette=DARK)

# or globally, for every chart created afterwards
set_option("palette", DEFAULT)
```

Define your own:

```python
from plotly_toolbox import Palette, Theme

my_palette = Palette(
    light=Theme(plot_bg="#ffffff", paper_bg="#ffffff", font_color="#222",
                colors=["#457b9d", "#e63946", "#2a9d8f"]),
    dark=Theme(plot_bg="#1a1a1f", paper_bg="#111116", font_color="#eee",
               colors=["#7cb6d6", "#e63946", "#2a9d8f"]),
    main="light",
)
```

## How it works — traces as the contract

Charts don't eagerly build a figure. Each implements `build_traces()` (its content) and
`layout_patch()` (its styling); the base `Graph` composes them lazily:

```python
chart = OneLinePlot(df=df, name="Sales", x_axis="date", y_axis="sales")
chart.traces()        # -> list of Plotly traces
chart.layout_patch()  # -> a plain layout dict
chart.figure          # -> composed go.Figure (built once, cached; `.fig` is an alias)
chart.to_html("out.html")
```

Because a chart can emit its traces and layout independently of any concrete figure, the same
object can be reused inside subplots and the planned dashboard layer without rework — see
[`docs/SPEC-dashboard.md`](docs/SPEC-dashboard.md).

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

Roadmap and design notes live in [`docs/IMPROVEMENT_PLAN.md`](docs/IMPROVEMENT_PLAN.md);
changes are tracked in [`CHANGELOG.md`](CHANGELOG.md).

## License

MIT — see [`LICENSE`](LICENSE).
