#!/usr/bin/env python3
"""
Convert Slavic401k quarterly statement PDFs to a single CSV.

Usage:
    python3 slavic401k_to_csv.py statements/*.pdf -o summary.csv
    python3 slavic401k_to_csv.py ~/Documents/401k            # a folder works too

Requires:  pip3 install pdfplumber
Everything runs locally; nothing is sent anywhere.
"""
import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.exit("Missing dependency. Run:  pip3 install pdfplumber")

FIELDS = [
    "account_number",
    "start_date",
    "end_date",
    "start_balance",
    "end_balance",
    "additions",
    "transfers",
    "withdrawals",
    "net_earnings",
    "source_file",
]

MONEY = r"\(?-?\$[\d,]+\.\d{2}\)?"
DATE = r"\d{2}/\d{2}/\d{4}"


def parse_money(s):
    """'$1,234.56' -> '1234.56', '($11.41)' -> '-11.41'"""
    neg = s.startswith("(") or "-" in s
    val = s.strip("()").replace("$", "").replace(",", "").replace("-", "")
    return f"-{val}" if neg else val


def iso(d):
    return datetime.strptime(d, "%m/%d/%Y").strftime("%Y-%m-%d")


def find(pattern, text, label, path):
    m = re.search(pattern, text)
    if not m:
        raise ValueError(f"{path.name}: couldn't find {label}")
    return m.group(1)


def account_last4(page):
    """Read the text to the right of 'Account #:' on the same line; keep last 4 digits."""
    words = page.extract_words()
    for i, w in enumerate(words):
        if w["text"] == "#:" and i > 0 and words[i - 1]["text"] == "Account":
            same_line = [
                o["text"]
                for o in words
                if abs(o["top"] - w["top"]) < 3 and o["x0"] > w["x1"]
            ]
            digits = re.sub(r"\D", "", "".join(same_line))
            return digits[-4:] if digits else ""
    return ""


def parse_statement(path):
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text() or ""
        if not text.strip():
            raise ValueError(f"{path.name}: no text on page 1 (scanned image?)")

        # The footer reads "Period: 10/01/2024 to 12/31/2024"
        m = re.search(rf"Period:\s*({DATE})\s*to\s*({DATE})", text) or re.search(
            rf"Statement for ({DATE})\s*-\s*({DATE})", text
        )
        if not m:
            raise ValueError(f"{path.name}: couldn't find statement period")
        start, end = m.groups()

        return {
            "account_number": account_last4(page),
            "start_date": iso(start),
            "end_date": iso(end),
            "start_balance": parse_money(find(rf"Beginning Balance\s+({MONEY})", text, "beginning balance", path)),
            "end_balance": parse_money(find(rf"Ending Balance\s+({MONEY})", text, "ending balance", path)),
            "additions": parse_money(find(rf"Additions\s+({MONEY})", text, "additions", path)),
            "transfers": parse_money(find(rf"Transfers\s+({MONEY})", text, "transfers", path)),
            "withdrawals": parse_money(find(rf"Withdrawals\s+({MONEY})", text, "withdrawals", path)),
            "net_earnings": parse_money(find(rf"Net Earnings\s+({MONEY})", text, "net earnings", path)),
            "source_file": path.name,
        }


def check(row):
    """Warn if the summary doesn't add up (start + changes should equal end)."""
    total = sum(float(row[k]) for k in ("start_balance", "additions", "transfers", "withdrawals", "net_earnings"))
    # Withdrawals are usually shown as positive amounts, so also try subtracting them.
    alt = total - 2 * float(row["withdrawals"])
    end = float(row["end_balance"])
    if abs(total - end) > 0.01 and abs(alt - end) > 0.01:
        print(f"  warning: {row['source_file']} doesn't reconcile (computed {total:.2f}, statement says {end:.2f})", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="PDF files and/or folders containing PDFs")
    ap.add_argument("-o", "--output", default="401k_summary.csv", help="output CSV (default: 401k_summary.csv)")
    args = ap.parse_args()

    pdfs = []
    for p in map(Path, args.inputs):
        pdfs += sorted(p.glob("*.pdf")) if p.is_dir() else [p]

    rows, failed = [], 0
    for path in pdfs:
        try:
            row = parse_statement(path)
            check(row)
            rows.append(row)
            print(f"ok   {path.name}")
        except Exception as e:
            failed += 1
            print(f"FAIL {path.name}: {e}", file=sys.stderr)

    rows.sort(key=lambda r: (r["account_number"], r["start_date"]))
    with open(args.output, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"\nWrote {len(rows)} row(s) to {args.output}" + (f" ({failed} failed)" if failed else ""))


if __name__ == "__main__":
    main()
