"""Ensure the examples gallery stays runnable: every chart it builds must render."""

import sys
from pathlib import Path

import pytest

# Make examples/ importable without packaging it.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

from gallery import build_gallery  # noqa: E402


def test_gallery_builds_all_charts():
    charts = build_gallery()
    assert len(charts) >= 13


@pytest.mark.parametrize("slug", list(build_gallery().keys()))
def test_gallery_chart_renders(slug):
    chart = build_gallery()[slug]
    fig = chart.figure  # lazily renders; raises if the traces/layout are invalid
    assert fig.data, f"{slug} produced no traces"
