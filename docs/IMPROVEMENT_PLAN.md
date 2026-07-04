# Plotly Toolbox — Improvement Plan

Goal: make `plotly_toolbox` the go-to library for creating the most common charts in 1–3 lines,
with consistent styling, and a foundation that a dashboard layer (see
[SPEC-dashboard.md](SPEC-dashboard.md)) can build on.

Current state (v0.1.0): `Graph` / `TwoDimensionGraph` dataclass core, working-ish
`OneLinePlot`, `MultiLinePlot`, `OneAreaPlot`, `MultiAreaPlot`, `BarPlot` family;
empty stubs for `scatter`, `heatmap`, `polar`, `domain`. No tests, no CI, several
latent runtime bugs.

---

## Phase 0 — Packaging & hygiene (blockers)

These prevent the library from being installable/usable as advertised.

1. **Missing dependencies.** `pyproject.toml` only declares `plotly`, but the code imports
   `pandas` (core.py) and `numpy` (line.py trendline). Add both.
2. **Python floor too high.** `requires-python = ">=3.13"` excludes nearly every current
   environment. Nothing in the code needs 3.13; lower to `>=3.10` (needed for `X | Y` unions
   in annotations at runtime) and test on 3.10–3.13.
3. **Repo hygiene.** `dist/` and `__pycache__/` are committed. Add them to `.gitignore` and
   remove from git. Same for `.DS_Store` (already ignored but a modified one is tracked).
4. **Public API.** `plotly_toolbox/__init__.py` does `from core import *` (no `__all__`
   defined) and misses `OneCategoryBars`, `ComparasionBars`, `MultiAreaPlot`. Define an
   explicit `__all__` and export every user-facing class from the top level so users can write
   `from plotly_toolbox import OneLinePlot, BarPlot, Palette, set_option`.
5. **Tooling.** Add `ruff` (lint + format) and `pytest` as dev dependencies; add a minimal
   GitHub Actions workflow: lint + tests on 3.10/3.13.

## Phase 1 — Fix known bugs in the existing code

Found while reading the source; each should get a regression test.

| Where | Bug |
|---|---|
| `core.py` `Graph.update_layout_colors` | Indexes `self.palette_data[f'{theme}_plot_bg']` — `Palette` is a dataclass, not a dict, and has no such keys. Crashes whenever a palette is set. Should read `getattr(palette, theme).plot_bg` etc. |
| `core.py` `TwoDimensionGraph.update_layout_colors` | Uses invalid layout key `plot_bg_color` (Plotly expects `plot_bgcolor`) and nonexistent `self.palette.theme`. Crashes for any 2D plot with a palette. |
| `core.py` `OneDimensionPlot.update_layout` | Passes trace properties (`hoverinfo`, `textinfo`, `marker.colors`) to `fig.update_layout` — invalid; they belong on `update_traces`. |
| `line.py` `LineMode` | Missing comma: `'lines+markers+text' 'none'` concatenates into the invalid literal `'lines+markers+textnone'`, and `'none'` is silently lost. |
| `line.py` `gen_miltiple_line_data` | `for n in size` iterates over an `int` (TypeError); colors are also indexed by category *value* instead of enumeration index. Also fix the typo (`gen_multiple_line_data`, keep an alias if needed). |
| `line.py` `MultiLinePlot` | Hardcodes `mode='lines'`, ignoring the `lines` field. |
| `line.py` `OneLinePlot` | Calls `general_layout_update()` twice. |
| `line.py` `add_trendline` | `np.polyfit` crashes on datetime/categorical x — the most common x-axis for a trendline. Convert to ordinal internally. |
| `area.py` `MultiAreaPlot` | `isinstance(self.fill_type, (str, FillType))` — `FillType` is a `typing.Literal`; `isinstance` against it raises `TypeError` when the value is a list. Check `isinstance(x, str)` only. |
| `bars.py` `ComparasionBars` | Typo in class name (`ComparisonBars`, keep deprecated alias); leftover `print(self.category_values)` debug; rebuilds `self.fig` from scratch discarding the `Graph`-managed figure; skips `general_layout_update()` so money/tick options are ignored. |
| `core.py` `Palette.__post_init__` | Crashes with `TypeError` when the main theme has `colors=None` (the default). Guard it. |
| `core.py` `update_layout_tick_text` | Assumes `tickvals = 1..n`; should use provided `x_tick_vals`/`y_tick_vals` when given, and set `tickmode='array'`. |

## Phase 2 — Consolidate the core (one rendering pipeline)

The biggest structural issue: every subclass builds traces inside `__post_init__`, each
slightly differently, and some bypass `general_layout_update()`. Refactor once so all future
chart types are cheap to add:

1. **Template method.** `Graph` gains `build_traces() -> list[BaseTraceType]` (abstract) and a
   single `render()` that adds traces, then runs `general_layout_update()`. `__post_init__`
   only validates/derives fields. `show()`, `to_html()`, `to_image()` live on `Graph`.
2. **Traces are the contract, not the figure.** `Graph` should be able to emit its traces +
   axis-layout fragment *without* owning a `go.Figure`. This is what makes charts reusable in
   subplots and in the dashboard layer (see SPEC): `graph.traces()` and `graph.layout_patch()`.
3. **One categorical mixin.** `MultiLinePlot`, `MultiAreaPlot`, `ComparisonBars` all
   re-implement "split df by category column, one trace per category, cycle colors". Extract a
   single `CategorySplit` mixin (resolves `category_col`/`category_values`, yields
   `(name, sub_df, color)`), used by all multi-series charts.
4. **Palette/Theme cleanup.**
   - Make `Theme` complete: `font_color`, `grid_color`, `accent`, plus the existing fields.
   - `Palette.resolve(theme) -> Theme`; color cycling via `palette.color(i)` (modulo).
   - Ship 2–3 built-in palettes (e.g. `DEFAULT`, `DARK`, `MINIMAL`) so styling works
     out of the box without the user defining one.
   - `set_option('palette', ...)`: replace the `print()` with `logging`, validate types.
5. **Consistent naming.** Decide on field names once and apply everywhere:
   `x` / `y` (or keep `x_axis`/`y_axis` — but not both styles), `mode` (not `line`/`lines`),
   `colors`, `category_col`. Provide deprecation shims for one release.
6. **Type-checked options.** Keep `Literal` types for IDE help, but validate at runtime in
   `__post_init__` with clear error messages (there is already partial validation in bars).

## Phase 3 — Cover the most common chart types

Target: the "top 15" charts people actually make, each with a one-class, sensible-defaults
API. Priority order:

**Tier 1 (must have)**
- `ScatterPlot` (xy/scatter.py — currently empty): size/color encodings, optional trendline
  (reuse the fixed `add_trendline`).
- `Histogram` (xy/histogram.py): bins, cumulative, overlay of categories.
- `PiePlot` / `DonutPlot` (domain/pie.py): `labels_col`, `values_col`, `hole`.
- `Heatmap` (xy/heatmap.py — currently a stub): from wide df or `(x, y, z)` columns,
  text annotations, colorscale from palette.
- `BoxPlot` / `ViolinPlot` (xy/distribution.py): by-category grouping.
- Vertical/horizontal handled uniformly in `BarPlot` (today `orientation='h'` is the default,
  which is surprising — default to `'v'` like Plotly).

**Tier 2 (high value)**
- `Indicator` / KPI card (domain/indicator.py): value + delta + optional sparkline — this is
  also the building block dashboards need most.
- `Timeline`/`Gantt` (xy/timeline.py).
- `Funnel` (domain/funnel.py).
- `Sunburst` / `Treemap` (domain/hierarchy.py): `path_cols`, `values_col`.
- `RadarPlot` (polar/radar.py — polar package is currently empty).
- `ComboPlot`: bars + line on secondary y-axis (classic "revenue + margin %").

**Tier 3 (nice to have)**
- `ScatterMatrix`, `ParallelCategories` (noted in domain/__init__.py comments),
  `Waterfall`, `CandlestickPlot`, choropleth/geo.

Each chart class ships with: docstring example, a test that it renders (`fig.to_dict()`
doesn't raise and contains expected trace types), and an entry in the examples gallery.

## Phase 4 — Tests, docs, examples

1. **Tests** (`tests/`): unit tests for palette resolution, option handling, category
   splitting, marker generation; smoke tests per chart class using small fixture DataFrames.
   Plotly figures validate their schema on construction, so `Chart(...).fig.to_dict()` is a
   cheap correctness check — no browser needed.
2. **Examples gallery** (`examples/`): one runnable script per chart type writing HTML into
   `examples/output/` (gitignored). Doubles as manual visual QA.
3. **README rewrite**: the current one documents behavior that doesn't exist yet (dark
   glass-morphism theme, zero-dependency claim) and is flagged as unreviewed. Rewrite from the
   real API after Phase 2, with a table of chart classes and screenshots.
4. **Versioning**: bump to 0.2.0 after Phase 2 (breaking renames), keep a `CHANGELOG.md`.

## Phase 5 — Dashboard layer

Implement per [SPEC-dashboard.md](SPEC-dashboard.md): a declarative `Dashboard`/grid API that
composes `Graph` objects into a single subplots figure or static HTML, with an optional Dash
adapter. Phases 2.2 (traces-as-contract) and the `Indicator` chart are its prerequisites.

---

## Suggested execution order

| Milestone | Contents | Outcome |
|---|---|---|
| 0.1.1 | Phase 0 + Phase 1 | Installs correctly; existing charts don't crash |
| 0.2.0 | Phase 2 | Stable core API, built-in palettes |
| 0.3.0 | Phase 3 Tier 1 + Phase 4 tests/examples | "Most common graphs" covered |
| 0.4.0 | Phase 3 Tier 2 (incl. `Indicator`) | KPI building blocks ready |
| 0.5.0 | Phase 5 dashboard layer | `Dashboard` + Dash adapter |
