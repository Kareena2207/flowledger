from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

from .csv_io import load_invoices, load_payments
from .engine import build_report_data
from .workbook import create_workbook


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flowledger",
        description="Generate a freelancer invoice and cash flow workbook from CSV inputs.",
    )
    parser.add_argument("--invoices", required=True, help="Path to the invoices CSV file.")
    parser.add_argument("--payments", required=True, help="Path to the payments CSV file.")
    parser.add_argument("--output", required=True, help="Path to the output workbook.")
    parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Reporting date in YYYY-MM-DD format. Defaults to today.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    as_of = datetime.strptime(args.as_of, "%Y-%m-%d").date()
    invoices = load_invoices(args.invoices)
    payments = load_payments(args.payments)
    report_data = build_report_data(invoices, payments, as_of)
    output = create_workbook(report_data, Path(args.output))
    print(f"Workbook created at {output}")
    return 0
