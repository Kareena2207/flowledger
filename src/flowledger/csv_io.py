from __future__ import annotations

import csv
import io
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import TextIO

from .models import Invoice, Payment


DATE_FORMAT = "%Y-%m-%d"
INVOICE_COLUMNS = {
    "invoice_id",
    "client_name",
    "issue_date",
    "due_date",
    "amount",
}
PAYMENT_COLUMNS = {
    "payment_id",
    "invoice_id",
    "payment_date",
    "amount",
}


def _parse_date(value: str):
    return datetime.strptime(value.strip(), DATE_FORMAT).date()


def _parse_decimal(value: str) -> Decimal:
    normalized = value.strip().replace(",", "")
    return Decimal(normalized)


def _validate_columns(reader: csv.DictReader, required: set[str], label: str) -> None:
    fieldnames = set(reader.fieldnames or [])
    missing = sorted(required - fieldnames)
    if missing:
        missing_str = ", ".join(missing)
        raise ValueError(f"{label} is missing required columns: {missing_str}")


def parse_invoices(handle: TextIO) -> list[Invoice]:
    reader = csv.DictReader(handle)
    _validate_columns(reader, INVOICE_COLUMNS, "Invoices CSV")
    return [
        Invoice(
            invoice_id=row["invoice_id"].strip(),
            client_name=row["client_name"].strip(),
            issue_date=_parse_date(row["issue_date"]),
            due_date=_parse_date(row["due_date"]),
            amount=_parse_decimal(row["amount"]),
            currency=row.get("currency", "USD").strip() or "USD",
            status=row.get("status", "").strip(),
        )
        for row in reader
    ]


def load_invoices(path: str | Path) -> list[Invoice]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return parse_invoices(handle)


def parse_payments(handle: TextIO) -> list[Payment]:
    reader = csv.DictReader(handle)
    _validate_columns(reader, PAYMENT_COLUMNS, "Payments CSV")
    return [
        Payment(
            payment_id=row["payment_id"].strip(),
            invoice_id=row["invoice_id"].strip(),
            payment_date=_parse_date(row["payment_date"]),
            amount=_parse_decimal(row["amount"]),
            method=row.get("method", "").strip(),
            notes=row.get("notes", "").strip(),
        )
        for row in reader
    ]


def load_payments(path: str | Path) -> list[Payment]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return parse_payments(handle)


def parse_uploaded_invoices(contents: bytes) -> list[Invoice]:
    text_stream = io.StringIO(contents.decode("utf-8-sig"))
    return parse_invoices(text_stream)


def parse_uploaded_payments(contents: bytes) -> list[Payment]:
    text_stream = io.StringIO(contents.decode("utf-8-sig"))
    return parse_payments(text_stream)
