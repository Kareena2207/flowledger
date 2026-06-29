from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    client_name: str
    issue_date: date
    due_date: date
    amount: Decimal
    currency: str
    status: str = ""


@dataclass(frozen=True)
class Payment:
    payment_id: str
    invoice_id: str
    payment_date: date
    amount: Decimal
    method: str = ""
    notes: str = ""
