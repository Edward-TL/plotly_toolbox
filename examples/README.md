# Examples

## Gallery

[`gallery.py`](gallery.py) builds one representative chart of every type and writes them to
`examples/output/` (gitignored) as standalone HTML files, plus an `index.html` linking them:

```bash
python examples/gallery.py
open examples/output/index.html   # macOS; use xdg-open on Linux
```

`build_gallery()` returns the chart objects keyed by a slug, so it doubles as a smoke test —
`tests/test_examples.py` renders every chart it produces.
