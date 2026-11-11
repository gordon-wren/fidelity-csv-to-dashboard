# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page dashboard that parses a Fidelity activity export (CSV) in the browser and charts contributions. The owner files feature requests as GitHub issues (written in the Claude app); code changes happen here in the CLI.

## Layout

- `index.html` is the whole app: markup, CSS and one inline `<script>`. No build step, no dependencies, no network calls.
- `README.md` is user-facing. Update it when behaviour a user would notice changes.
- `.gitignore` excludes `*.csv`. Never commit a real export; use synthetic rows for fixtures.

## Run and check

Open `index.html` in a browser. It loads generated sample data (`sampleCSV()`) on start, which goes through the same parser as real files. There are no tests yet. To check a change, render at 390px wide (phone) and at desktop width, in light and dark, and watch the console for errors. Check both views (`#overview`, `#data`). Headless Chrome on macOS won't make a window narrower than 500px, so for a real 390px check, load the page in a 390px-wide iframe served over `http://` (for example `python3 -m http.server`). Serving the folder (`python3 -m http.server`) also works, but isn't needed.

## Two views

The page has two dashboards that share the header, filters and status strip. **Overview** (`#v-overview`) answers "am I on track": limits and headline numbers at the top, trend charts in the middle, the pivot table last. **Data and settings** (`#v-data`) answers "is the number right": data health at the top, classification settings in the middle, raw transaction rows last. Keep it that way: settings and raw rows go on the Data view, never on the Overview.

`route()` picks the view from the URL hash: `#data`, or the id of any element inside `#v-data`, opens Data, and anything else opens Overview. Then it scrolls to the target, so links like `href="#typesCard"` work from anywhere. `render()` draws only the visible view, because charts are sized from `clientWidth` and a hidden view measures 0.

## Script map (in file order)

- **Parsing:** `parseCSV`, `parseDate`, `parseAmount`, `ingestFile` (finds the header row by a Date + Amount column, maps columns by name), `ingest` (merges files, counts rows duplicated across files once).
- **Transaction types:** `PREFIXES` maps known Fidelity action prefixes to `in` / `out` / `skip`. `groupOf` normalises an action to a group; `defaultCat` is the fallback; `catOf` applies user overrides. `unrecognised()` lists groups with no known prefix and no override; it drives the status strip warning and sorts those types first on the Data view. `DEFAULTS = Object.fromEntries(PREFIXES)`, so to change how a known action is treated, edit `PREFIXES`.
- **Holding types:** `guessKind(sym, name)` returns `stock` / `etf` / `fund` / `other` / `skip`; `kindOf` applies overrides; `isBuy` decides what counts as a purchase (a row with a security whose group is in the `BUYS` set or is categorised `in`).
- **Limits:** `LIMITS` table (under-50 amounts by year), `acctKind` guesses account type from its name, `taxYear` shifts "prior year" IRA deposits, `limitKinds` lists the limit types present, `limitFor(kind, year)` sums one limit, `drawLimits`, `drawAccounts` (account type settings, Data view). `drawLimits` and the status strip read `S.rows` directly (all accounts, by `taxYear`), not `compute()`; it ignores the account and period filters on purpose. The limit input redraws only the limits panel and the status strip.
- **State:** the `S` object (rows, filters, overrides, `view`, `txMode`, and `src`, a summary of the last load). `load()` replaces the data set, resets the account / period filters and `showAll`, rebuilds the account, period and limit-year controls, then renders. A new filter should be reset there too.
- **`compute()`:** one pass that produces months, periods, totals and purchase buckets for the current account / period / grouping. Every chart except the limit tracker reads from its result.
- **`render()`** always calls `drawHealth` (the status strip), then the visible view's `draw*` functions. Overview: tiles, `drawBars`, `drawLine`, `drawLimits`, `drawPace`, `drawCal`, `drawBuys`, `drawPivot`. Data: `drawSource`, `drawTypes`, `drawAccounts`, `drawSecs`, `drawTx`.
- **Period filter:** everything from `compute()` covers `lo`..`hi` (month indexes). The pivot, streaks and copy button use `C.months`; the pace chart shows each calendar year that overlaps the period, in full, from `C.allMonths`.

Row shape: `{date:{y,m,d}, t (y*12+m-1), ord (yyyymmdd), account, action, group, amount, desc, sym, sec, secName, raw, header}`. `raw` is the row's cells from the file; `header` is shared by every row from the same file (`{cells, num}`, where `num` is the Account Number column index). `rawRows()` uses them on the Data view to show each transaction type's rows as they appear in the file, with account numbers shortened to the last four digits.

localStorage keys (settings only, never account data): `fct-cats`, `fct-secs`, `fct-lim`.

## Conventions

- **DOM helpers:** `$(selector)` is `document.querySelector`; `h(tag, attrs, ...kids)` builds an element (string kids become text nodes, `on*` attrs become listeners).
- **Untrusted text:** anything from the CSV goes into the DOM through `h()` / `textContent`. SVG is built as a string and set with `innerHTML` only from numbers and generated labels. Keep it that way.
- **Theme:** colours are CSS tokens in `:root`, redefined for dark under both the media query and `[data-theme="dark"]`. Style through tokens only.
- **Charts:** hand-written SVG sized from `clientWidth`, redrawn on resize. One y-axis per chart, a hover/tap tooltip on every chart, text in ink tokens (never the series colour), 2px gaps between stacked segments, rounded data ends. Series colours are `--s1` to `--s4` (blue, aqua, violet, magenta) in fixed order; a colour follows the entity, not its rank. `--sx` is the neutral series (withdrawals). The palette passed the dataviz skill's validator in both modes; re-run it if you change a hue.
- **Status colours:** `--warn` (amber) and `--crit` (red) are only for active problems: an over-limit meter, a file that could not be read, unrecognised transaction types. Never use them for a series, and never show "OK" in green. Always pair them with an icon and words.
- **Status strip:** `drawHealth` puts alerts first (crit, then warn), then neutral facts. Each badge links to the panel that explains or fixes it.
- **Sizing:** a 12-column grid from 860px (`.w4`…`.w12`); one column below that, in DOM order, so the DOM order is the phone's reading order. Critical panels get the large spans; background stats are `.tile.sm`.
- **Layout:** must read at 390px with no sideways page scroll; wide content scrolls inside its own `.scroll` container.
- **Copy:** plain, short, sentence case. Say what a control does.

## Known gaps

- The parser was written from the documented export layout and has not been checked against a real file. Expect quirks.
- Transaction and holding classification are heuristics; unknown action types default to "leave out", which can undercount silently.
- Loaded data is not kept between visits; choosing files replaces the current set.
- With long histories the bar charts scroll sideways and the y-axis scrolls out of view.
- Limits: employer match is counted if the file does not label it; no catch-up toggle; 2027 401(k)/IRA limits are not in `LIMITS` (not yet published when this was written).

## Workflow

Branch from `main` and open a pull request. A GitHub issue is optional; when work has one, use one branch per issue and reference it in the PR. Keep the app a single file unless an issue says otherwise.
