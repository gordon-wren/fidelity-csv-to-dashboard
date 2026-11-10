# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page dashboard that parses a Fidelity activity export (CSV) in the browser and charts contributions. The owner files feature requests as GitHub issues (written in the Claude app); code changes happen here in the CLI.

## Layout

- `index.html` is the whole app: markup, CSS and one inline `<script>`. No build step, no dependencies, no network calls.
- `README.md` is user-facing. Update it when behaviour a user would notice changes.
- `.gitignore` excludes `*.csv`. Never commit a real export; use synthetic rows for fixtures.

## Run and check

Open `index.html` in a browser. It loads generated sample data (`sampleCSV()`) on start, which goes through the same parser as real files. There are no tests yet. To check a change, render at 390px wide (phone) and at desktop width, in light and dark, and watch the console for errors. Serving the folder (`python3 -m http.server`) also works, but isn't needed.

## Script map (in file order)

- **Parsing:** `parseCSV`, `parseDate`, `parseAmount`, `ingestFile` (finds the header row by a Date + Amount column, maps columns by name), `ingest` (merges files, counts rows duplicated across files once).
- **Transaction types:** `PREFIXES` maps known Fidelity action prefixes to `in` / `out` / `skip`. `groupOf` normalises an action to a group; `defaultCat` is the fallback; `catOf` applies user overrides. `DEFAULTS = Object.fromEntries(PREFIXES)`, so to change how a known action is treated, edit `PREFIXES`.
- **Holding types:** `guessKind(sym, name)` returns `stock` / `etf` / `fund` / `other` / `skip`; `kindOf` applies overrides; `isBuy` decides what counts as a purchase (a row with a security whose group is in the `BUYS` set or is categorised `in`).
- **Limits:** `LIMITS` table (under-50 amounts by year), `acctKind` guesses account type from its name, `taxYear` shifts "prior year" IRA deposits, `drawLimits`. `drawLimits` reads `S.rows` directly (all accounts, by `taxYear`), not `compute()`; it ignores the account and period filters on purpose. Its own controls redraw only the limits panel.
- **State:** the `S` object (rows, filters, overrides). `load()` replaces the data set, resets the account / period filters and `showAll`, rebuilds the account, period and limit-year controls, then renders. A new filter should be reset there too.
- **`compute()`:** one pass that produces months, periods, totals and purchase buckets for the current account / period / grouping. Every chart except the limit tracker reads from its result.
- **`render()`** calls the `draw*` functions: `drawBars`, `drawLine`, `drawPace`, `drawCal`, `drawBuys`, `drawSecs`, `drawPivot`, `drawTypes`, `drawTx`.

Row shape: `{date:{y,m,d}, t (y*12+m-1), ord (yyyymmdd), account, action, group, amount, desc, sym, sec, secName}`.

localStorage keys (settings only, never account data): `fct-cats`, `fct-secs`, `fct-lim`.

## Conventions

- **DOM helpers:** `$(selector)` is `document.querySelector`; `h(tag, attrs, ...kids)` builds an element (string kids become text nodes, `on*` attrs become listeners).
- **Untrusted text:** anything from the CSV goes into the DOM through `h()` / `textContent`. SVG is built as a string and set with `innerHTML` only from numbers and generated labels. Keep it that way.
- **Theme:** colours are CSS tokens in `:root`, redefined for dark under both the media query and `[data-theme="dark"]`. Style through tokens only.
- **Charts:** hand-written SVG sized from `clientWidth`, redrawn on resize. One y-axis per chart, a hover/tap tooltip on every chart, text in ink tokens (never the series colour), 2px gaps between stacked segments, rounded data ends. Series colours are `--s1` to `--s4` in fixed order; a colour follows the entity, not its rank.
- **Layout:** must read at 390px with no sideways page scroll; wide content scrolls inside its own `.scroll` container.
- **Copy:** plain, short, sentence case. Say what a control does.

## Known gaps

- The parser was written from the documented export layout and has not been checked against a real file. Expect quirks.
- Transaction and holding classification are heuristics; unknown action types default to "leave out", which can undercount silently.
- Loaded data is not kept between visits; choosing files replaces the current set.
- With long histories the bar charts scroll sideways and the y-axis scrolls out of view.
- `drawPivot` and the streak stats use all time for the selected account and ignore the period filter.
- Limits: employer match is counted if the file does not label it; no catch-up toggle; 2027 401(k)/IRA limits are not in `LIMITS` (not yet published when this was written).

## Workflow

Branch from `main`, one issue per branch, open a pull request that references the issue. Keep the app a single file unless an issue says otherwise.
