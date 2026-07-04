import pandas as pd
import pytest

from plotly_toolbox import Palette, Theme


@pytest.fixture
def daily_df():
    return pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10),
            "sales": [120, 135, 150, 165, 180, 200, 210, 225, 240, 260],
        }
    )


@pytest.fixture
def category_df():
    return pd.DataFrame(
        {
            "month": [1, 2, 3, 1, 2, 3],
            "sales": [10, 20, 30, 15, 25, 35],
            "region": ["north", "north", "north", "south", "south", "south"],
        }
    )


@pytest.fixture
def palette():
    light = Theme(font="Arial", plot_bg="#ffffff", paper_bg="#fafafa", colors=["#e63946", "#457b9d", "#2a9d8f"])
    dark = Theme(font="Arial", plot_bg="#111111", paper_bg="#000000", colors=["#e63946", "#457b9d", "#2a9d8f"])
    return Palette(light=light, dark=dark, main="light")


@pytest.fixture
def empty_palette():
    """Palette whose main theme has no colors — used to exercise the None-colors guard."""
    return Palette(light=Theme(), main="light")
