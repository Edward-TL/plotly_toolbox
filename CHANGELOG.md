# Changelog

All notable changes to this project are documented here. This project adheres to
[Semantic Versioning](https://semver.org/).

## [0.2.0] — Core consolidation (Improvement Plan Phase 2)

### Added
- **Traces-as-contract rendering pipeline.** Every chart now implements
  `build_traces()` and may extend `layout_patch()`; `Graph` composes them lazily
  into a figure via `render()` / the `figure` property. This lets a chart emit its
  traces and layout fragment independently of any `go.Figure` — the foundation the
  dashboard layer (Phase 5) builds on.
- `Graph.to_html()` and `Graph.to_image()` output helpers.
- `CategorySplit` mixin: single implementation of "split a DataFrame by category
  and cycle colors", now shared by `MultiLinePlot`, `MultiAreaPlot`, and
  `ComparisonBars`.
- Built-in palettes `DEFAULT`, `DARK`, `MINIMAL` (in `plotly_toolbox.palettes`,
  re-exported at the top level) so charts are styled without defining a `Theme`.
- Richer `Theme` fields: `font_color`, `grid_color`, `accent`.
- `Palette.resolve()` and `Palette.color(i)` helpers; `deep_merge()` layout utility.
- Runtime validation: unknown x/y columns raise `KeyError`; `set_option` validates
  option types.

### Changed
- **Charts no longer build a figure in `__post_init__`** — construction only
  validates and derives fields; the figure is built on first access to `.figure`
  / `.fig`.
- `set_option` now logs via the `plotly_toolbox` logger instead of `print`.
- `BarPlot` marker extraction raises on unsupported types instead of returning
  `None` silently.

### Deprecated
- `line=` (single-series) and `lines=` (multi-series) constructor arguments —
  use `mode=` instead. The old names still work for one release and emit a
  `DeprecationWarning`.

### Fixed
- `subplot_type` for xy charts now actually resolves to `'xy'` (was a no-op
  class-attribute assignment shadowed by the inherited dataclass field default).

## [0.1.1] — Packaging & bug fixes (Improvement Plan Phases 0–1)

### Added
- Declared the previously-missing `pandas` and `numpy` runtime dependencies.
- Explicit public API (`__all__`) exporting every user-facing class from the
  top-level package.
- `pytest` test suite, `ruff` config, and a GitHub Actions CI workflow.

### Changed
- Lowered `requires-python` from `>=3.13` to `>=3.10`.

### Fixed
- Palette handling no longer crashes plots (dict-style indexing of a dataclass;
  invalid `plot_bg_color` layout key).
- `LineMode` missing-comma bug; multi-line color generation iterating over an int;
  `MultiLinePlot` ignoring its mode.
- `add_trendline` no longer crashes on datetime / categorical x-axes.
- `MultiAreaPlot` `isinstance` check against a `typing.Literal`.
- `ComparisonBars` (renamed from `ComparasionBars`, alias kept): removed debug
  `print`, stopped discarding the managed figure, now applies the full layout
  pipeline.
- `Palette` with no colors no longer raises.
