# Plotly Toolbox

## ✨ Overview

**Plotly Toolbox** is a lightweight, high‑performance Python library that provides a clean, object‑oriented interface for creating beautiful Plotly visualisations. It abstracts away the repetitive boilerplate of Plotly's low‑level API while preserving full flexibility, allowing you to build sophisticated charts with just a few lines of code.

- 🎨 **Rich aesthetics** – modern dark theme, gradient colours, glass‑morphism backgrounds.
- 📊 **Versatile chart types** – line, area, bar, scatter, polar, ternary and more.
- 🛠️ **Fully typed** – dataclasses and type hints for IDE autocompletion.
- ⚡ **Zero‑dependency** beyond Plotly and Pandas.

## 📦 Installation

```bash
pip install plotly-toolbox
```

> The package requires Python ≥ 3.13 and Plotly ≥ 6.3.1.

## 🚀 Quick Start

```python
import pandas as pd
from plotly_toolbox.xy.line import OneLinePlot

# Sample data
df = pd.DataFrame({
    "date": pd.date_range(start="2024-01-01", periods=10),
    "sales": [120, 135, 150, 165, 180, 200, 210, 225, 240, 260]
})

# Create a line plot
plot = OneLinePlot(
    df=df,
    name="Monthly Sales",
    x_axis="date",
    y_axis="sales",
    line="lines+markers",
    line_shape="spline",
    trendline_color="red"
)
plot.show()
```

The snippet above produces a sleek, dark‑themed line chart with a smooth spline curve and a red trendline – exactly the style showcased in the image above.

## 📚 API Highlights

- **`Graph`** – base class handling DataFrames, palettes, and global options.
- **`OneLinePlot`**, **`MultiLinePlot`**, **`OneAreaPlot`**, **`OneCategoryBars`**, etc. – ready‑to‑use concrete chart classes.
- **Palette system** – define custom colour palettes and switch between light/dark themes effortlessly.
- **Global options** – `set_option('palette', my_palette)` and `set_option('template', 'plotly_dark')` affect all subsequent plots.

## 🛡️ License

Distributed under the MIT License. See the `LICENSE` file for more information.

---
*Until here it's removed, README file has not been checked by me (Edward TL) yet*

*Generated with a custom AI‑assistant that ensures the README looks premium and ready for GitHub.*

