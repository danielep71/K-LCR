"""Illustrative derivation: input totals of a case, for the format of TEST_CASES.md.

It reads assets.csv and flows.csv of the case folder named on the command
line with the standard library's csv module, independently of K-LCR's tools,
and prints the total market value of all holdings and the total amount of all
outflow items. It implements no regulatory rule and its values validate
nothing.
"""

import csv
import json
import sys
from decimal import Decimal
from pathlib import Path


def rows(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def main(folder):
    folder = Path(folder)
    market_value = sum((Decimal(row["market_value"]) for row in rows(folder / "assets.csv")), Decimal(0))
    outflows = sum((Decimal(row["amount"]) for row in rows(folder / "flows.csv") if row["direction"] == "OUTFLOW"),
                   Decimal(0))
    print(json.dumps({"outputs": [
        {"quantity": "illustrative_total_market_value", "value": format(market_value, "f")},
        {"quantity": "illustrative_total_outflow_amount", "value": format(outflows, "f")},
    ]}))


if __name__ == "__main__":
    main(sys.argv[1])
