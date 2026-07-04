# SPEC — `plotly_toolbox.dashboard`: simple dashboards, Dash-ready

Status: draft · Target: v0.5.0 · Depends on: Improvement Plan Phase 2 (traces-as-contract)
and Phase 3 `Indicator`.

## 1. Motivation

Building a "few charts + KPIs on a grid" today requires either hand-wiring
`plotly.subplots.make_subplots` (verbose, trace-level) or adopting Dash (a full web framework
with callbacks, layout components, and a server). There is no middle step.

This module provides that middle step: **declare a dashboard as a grid of `Graph` objects**,
render it with zero extra dependencies to a single Plotly figure or a static HTML file — and,
when interactivity is needed, hand the *same* dashboard object to Dash without rewriting it.

## 2. Goals / non-goals

**Goals**
- G1. Build a dashboard from existing `Graph` instances (charts + KPI indicators) with a
  declarative grid: rows, columns, spans, titles.
- G2. Render targets: (a) one `go.Figure` via `make_subplots`, (b) standalone static HTML
  (multiple figures + CSS grid — no Python server needed), (c) Dash `Layout` component tree.
- G3. Core stays dependency-free beyond plotly/pandas; **Dash is an optional extra**
  (`pip install plotly-toolbox[dash]`), imported lazily.
- G4. A `Graph` written for standalone use works unmodified inside a dashboard (same class,
  same fields).

**Non-goals (v1)**
- No callback/filtering engine of our own — interactivity beyond Plotly's built-in
  hover/zoom/legend is delegated to Dash.
- No theming system separate from the existing `Palette` (the dashboard reuses it).
- No live-refresh/streaming.

## 3. Core concepts

```
Dashboard
 ├─ title, subtitle, palette, template
 └─ rows: list[Row]
      └─ cells: list[Cell]
           ├─ item: Graph | Indicator | Text | Spacer
           ├─ span: int        (grid columns this cell occupies)
           └─ height: str|int  (optional row-height hint)
```

- **`Dashboard`** — top-level container; owns page-level styling (palette, template, title).
- **`Row` / `Cell`** — the grid. A 12-column implicit grid (like CSS/Bootstrap): a row's cell
  spans should sum to ≤ 12; unspecified spans divide the remainder equally.
- **Items** — anything implementing the `DashboardItem` protocol (§5). Out of the box:
  every `Graph` subclass, `Indicator` (KPI card), `Text` (markdown block), `Spacer`.

## 4. User-facing API (target)

```python
from plotly_toolbox import OneLinePlot, BarPlot, Indicator
from plotly_toolbox.dashboard import Dashboard, Row, Text

dash_board = Dashboard(
    title="Sales Overview",
    palette=my_palette,           # falls back to get_option('palette')
    rows=[
        Row(
            Indicator(df=kpis, value_col="revenue", delta_col="revenue_mom", name="Revenue"),
            Indicator(df=kpis, value_col="orders",  delta_col="orders_mom",  name="Orders"),
            Indicator(df=kpis, value_col="aov",     name="Avg. order value", is_money=True),
        ),                        # 3 cells → span 4 each
        Row(
            OneLinePlot(df=daily, x_axis="date", y_axis="sales", name="Daily sales", span=8),
            BarPlot(df=by_region, x_axis="region", y_axis="sales", name="By region", span=4),
        ),
        Row(Text("Data as of last ETL run. Source: warehouse.sales_daily")),
    ],
)

dash_board.show()                          # one composed go.Figure (make_subplots)
dash_board.to_html("report.html")          # standalone static HTML page
app = dash_board.to_dash()                 # dash.Dash app, ready for app.run()
```

Notes:
- `span` is accepted via the `DashboardItem` protocol (a plain attribute), so chart classes
  don't need new constructor fields — `Cell(item, span=8)` remains the explicit form and
  `Row(...)` wraps bare items into cells automatically.
- Everything is data; nothing renders until `show()/to_html()/to_dash()` is called
  (requires the Phase 2 refactor where `Graph.__post_init__` stops building figures).

## 5. The `DashboardItem` protocol

The key design decision: **items expose traces and layout fragments, not figures.** This is
what makes one object renderable in all three targets.

```python
class DashboardItem(Protocol):
    name: str
    subplot_type: PlotlySublotType | None      # already on Graph ("xy", "domain", "polar", …)

    def traces(self) -> list[BaseTraceType]: ...
    def layout_patch(self, xaxis: str, yaxis: str) -> dict: ...
        # axis titles, tickformat, money prefixes — keyed to the subplot's axis ids
    def standalone_figure(self) -> go.Figure: ...   # default impl: traces + patch
```

`Graph` implements this in Phase 2; `Indicator`, `Text`, `Spacer` are lightweight items
(`Text` renders as an annotation in figure mode, a `<div>`/`dcc.Markdown` in HTML/Dash modes).

## 6. Renderers

Three renderers consume the same `Dashboard` tree. Renderers own layout mechanics; items own
content. Adding a renderer never touches chart code.

### 6.1 `FigureRenderer` (zero-dependency)
- Maps the grid to `make_subplots(rows, cols, specs=…, column_widths=…, row_heights=…)`,
  using each item's `subplot_type` for `specs` and spans for `column_widths`.
- Injects each item's `traces()` into its `(row, col)` and merges `layout_patch()` into the
  figure layout with correct axis ids.
- Limitations (documented): uniform grid per `make_subplots` semantics; `Text` becomes an
  annotation. Best for quick composition and notebook use.

### 6.2 `HtmlRenderer` (zero-dependency, primary static target)
- Each item renders to its own figure/`<div>`; the page is a CSS grid
  (`grid-template-columns: repeat(12, 1fr)`, cells use `grid-column: span N`).
- One `plotly.js` include for the whole page (`include_plotlyjs='cdn'` or `'embed'` for
  offline files); palette drives page background/fonts.
- Output: a single self-contained `.html` — shareable by email/Slack, no server.

### 6.3 `DashRenderer` (optional extra)
- `to_dash_components() -> list` returns the component tree
  (`html.Div` grid, `dcc.Graph(figure=item.standalone_figure())`, `dcc.Markdown`), so a
  dashboard can be **embedded into an existing Dash app** as one page/tab.
- `to_dash() -> dash.Dash` wraps that tree in a new app for the standalone case.
- Every `dcc.Graph` gets a deterministic id (`slugify(item.name)`), so users can attach their
  own Dash callbacks to dashboard charts — this is the "complemented with Dash" path:
  start static, add callbacks later without restructuring.
- Import guard: `ImportError` with the message
  `pip install plotly-toolbox[dash]` when Dash isn't installed.

## 7. Module layout

```
src/plotly_toolbox/dashboard/
    __init__.py        # Dashboard, Row, Cell, Text, Spacer
    protocol.py        # DashboardItem
    _grid.py           # span resolution, 12-col math (shared by renderers)
    render_figure.py   # FigureRenderer
    render_html.py     # HtmlRenderer + page template
    render_dash.py     # DashRenderer (lazy dash import)
```

`pyproject.toml`:

```toml
[project.optional-dependencies]
dash = ["dash>=2.17"]
```

## 8. Implementation phases

1. **P1 — Protocol + grid model.** `DashboardItem`, `Dashboard/Row/Cell`, span math, and the
   Phase-2 `Graph.traces()/layout_patch()` refactor it depends on. Unit tests on grid math.
2. **P2 — `HtmlRenderer`.** Highest value/effort ratio: honest CSS grid, no `make_subplots`
   constraints. Golden-file tests on generated HTML structure.
3. **P3 — `FigureRenderer`.** For notebooks and single-figure export.
4. **P4 — `Indicator` + `Text` + `Spacer` items.**
5. **P5 — `DashRenderer`** + `[dash]` extra + example app in `examples/dashboard_dash.py`.

## 9. Open questions

- Should `Row` accept a `height` hint in figure mode (maps to `row_heights`) even though HTML
  mode auto-sizes? Proposal: yes, optional, ignored where not applicable.
- Filters: v2 could add a declarative `Filter(col=...)` item that becomes a `dcc.Dropdown` +
  auto-generated callback in Dash mode and is ignored (or pre-applied) in static modes.
- Jinja2 for the HTML template vs. f-strings: start with f-strings to keep zero deps;
  revisit if the template grows.
