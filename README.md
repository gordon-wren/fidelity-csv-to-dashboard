# Fidelity CSV to Dashboard

A single-page dashboard that reads a Fidelity activity export (CSV) and shows how much you have contributed over time. Everything runs in your browser: the file is parsed locally and never uploaded. Not affiliated with Fidelity.

## Use it

1. In Fidelity, open **Activity & Orders**, set the date range, then **Download** the CSV.
2. Open `index.html` in a browser (double-click it, or serve the folder with GitHub Pages).
3. Choose one or more CSV files. Selecting several combines accounts or date ranges; rows that appear in more than one file are counted once.

The page opens on made-up sample data until you load your own.

## What it shows

The page has two views, switched by the tabs under the title. A row of status badges sits above both. Problems come first, such as an annual limit exceeded, a file that could not be read, or transaction types the page does not recognise, and each badge links to where you can check or fix it. Red and amber are used only for these problems.

**Overview**, for checking whether you're on track:

- **Annual limit tracker:** progress against IRA, 401(k) and HSA limits, with the monthly amount needed to max out.
- **Headline numbers:** contributed this year against the prior year's pace, then total, average and median per month, withdrawals and net for the selected period.
- **Contributions by month, quarter or year,** with withdrawals shown below the axis.
- **Running total,** net of withdrawals.
- **Year-over-year pace:** one cumulative line per calendar year in the period.
- **Consistency:** a calendar of deposit days, plus streaks and gaps.
- **Purchases by type:** buys split into individual stocks, ETFs, mutual funds and other.
- **Year by month table,** with a button to copy monthly totals as CSV.

**Data and settings**, for checking the numbers are right:

- **Data source:** files loaded, date range, lines skipped and any read errors.
- **Transaction types, accounts and holdings:** how each is counted, with anything not recognised listed first. Each transaction type can be expanded to show its rows exactly as they appear in your file (account numbers are shortened to the last four digits).
- **Transactions:** the rows that were counted, or the rows that were left out.

The account switcher under the tabs shows each account by name and the last four digits of its number, on both dashboards. Pick one to see only that account, or **All accounts** to combine them. With five or more accounts, a search box finds an account by any part of its name or number. The account and period filters apply to everything except the limit tracker, which always covers all accounts.

## How transactions are counted

The export does not say which rows are contributions, so the page guesses from the action text and lets you correct it.

- **Money in:** bank transfers received, direct deposits, cash contributions, employer contributions, rollovers, checks and wires received.
- **Money out:** transfers paid, distributions, withdrawals, checks paid, debit card and bill payments.
- **Left out:** buys, sells, dividends, reinvestments, interest, fees, and "Transferred from/to" (usually a move between your own accounts).

Holding types are guessed from the ticker and name: five-letter tickers ending in X are mutual funds, names containing "ETF" or a known issuer are ETFs, other plain tickers are individual stocks, and money market sweeps are ignored. Index funds are not separated from other funds.

Every guess can be changed under **Data and settings**. Choices are saved in the browser's local storage, not in the file.

## Limits

Built-in limits are the under-50 amounts for 2022 to 2026, plus the 2027 HSA limits. Type over a limit if catch-up applies to you or to enter a year that is not built in. Things to check:

- Account types are guessed from the account name. Set them under **Data and settings**, in **Accounts**, if the guess is wrong.
- Employer match counts toward your progress if the file does not label it separately. Mark that transaction type as left out.
- IRA and HSA deposits made January to April count toward the year before when the action or description says so ("prior year", "prior yr", "PY", "for 2025" and similar). Under **Data and settings › Which tax year deposits count for** you can set the year for any one of those deposits. Rollovers are not counted.

This is a personal tracking tool, not tax advice. Confirm limits and excess contributions with the IRS or a tax professional.

## Privacy

`.gitignore` excludes `*.csv` so a real export is not committed by accident.

## Development

`index.html` is the whole app: no build step and no dependencies.
