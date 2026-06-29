from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from .models import Invoice, Payment


ZERO = Decimal("0.00")


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def _month_key(value: date) -> str:
    return value.strftime("%Y-%m")


def _derive_status(invoice: Invoice, paid_amount: Decimal, as_of: date) -> str:
    if paid_amount >= invoice.amount:
        return "paid"
    if paid_amount > ZERO:
        if invoice.due_date < as_of:
            return "overdue"
        if (invoice.due_date - as_of).days <= 7:
            return "due_soon"
        return "partial"
    if invoice.due_date < as_of:
        return "overdue"
    if (invoice.due_date - as_of).days <= 7:
        return "due_soon"
    return "unpaid"


def build_report_data(
    invoices: list[Invoice], payments: list[Payment], as_of: date
) -> dict[str, object]:
    payments_by_invoice: dict[str, list[Payment]] = defaultdict(list)
    for payment in payments:
        payments_by_invoice[payment.invoice_id].append(payment)

    invoice_rows: list[dict[str, object]] = []
    client_summary: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "client_name": "",
            "invoice_count": 0,
            "billed_amount": ZERO,
            "paid_amount": ZERO,
            "outstanding_amount": ZERO,
        }
    )
    monthly_summary: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "month": "",
            "invoiced_amount": ZERO,
            "collected_amount": ZERO,
        }
    )
    alerts: list[dict[str, object]] = []

    for invoice in sorted(invoices, key=lambda item: (item.due_date, item.invoice_id)):
        linked_payments = sorted(
            payments_by_invoice.get(invoice.invoice_id, []),
            key=lambda item: (item.payment_date, item.payment_id),
        )
        paid_amount = _money(sum((payment.amount for payment in linked_payments), ZERO))
        outstanding_amount = _money(max(invoice.amount - paid_amount, ZERO))
        status = _derive_status(invoice, paid_amount, as_of)
        days_overdue = max((as_of - invoice.due_date).days, 0) if status == "overdue" else 0
        days_until_due = (invoice.due_date - as_of).days

        invoice_rows.append(
            {
                "invoice_id": invoice.invoice_id,
                "client_name": invoice.client_name,
                "issue_date": invoice.issue_date.isoformat(),
                "due_date": invoice.due_date.isoformat(),
                "amount": invoice.amount,
                "paid_amount": paid_amount,
                "outstanding_amount": outstanding_amount,
                "status": status,
                "days_overdue": days_overdue,
                "days_until_due": days_until_due,
                "currency": invoice.currency,
            }
        )

        client = client_summary[invoice.client_name]
        client["client_name"] = invoice.client_name
        client["invoice_count"] += 1
        client["billed_amount"] = _money(client["billed_amount"] + invoice.amount)
        client["paid_amount"] = _money(client["paid_amount"] + paid_amount)
        client["outstanding_amount"] = _money(
            client["outstanding_amount"] + outstanding_amount
        )

        month = _month_key(invoice.issue_date)
        monthly_summary[month]["month"] = month
        monthly_summary[month]["invoiced_amount"] = _money(
            monthly_summary[month]["invoiced_amount"] + invoice.amount
        )

        if status == "overdue":
            alerts.append(
                {
                    "type": "overdue",
                    "invoice_id": invoice.invoice_id,
                    "client_name": invoice.client_name,
                    "message": f"{invoice.invoice_id} is {days_overdue} days overdue.",
                    "amount": outstanding_amount,
                }
            )
        elif outstanding_amount > ZERO and 0 <= days_until_due <= 7:
            alerts.append(
                {
                    "type": "due_soon",
                    "invoice_id": invoice.invoice_id,
                    "client_name": invoice.client_name,
                    "message": f"{invoice.invoice_id} is due in {days_until_due} days.",
                    "amount": outstanding_amount,
                }
            )

    payment_rows: list[dict[str, object]] = []
    for payment in sorted(payments, key=lambda item: (item.payment_date, item.payment_id)):
        payment_rows.append(
            {
                "payment_id": payment.payment_id,
                "invoice_id": payment.invoice_id,
                "payment_date": payment.payment_date.isoformat(),
                "amount": payment.amount,
                "method": payment.method,
                "notes": payment.notes,
            }
        )
        month = _month_key(payment.payment_date)
        monthly_summary[month]["month"] = month
        monthly_summary[month]["collected_amount"] = _money(
            monthly_summary[month]["collected_amount"] + payment.amount
        )

    overdue_total = _money(
        sum(
            (row["outstanding_amount"] for row in invoice_rows if row["status"] == "overdue"),
            ZERO,
        )
    )
    pending_total = _money(
        sum(
            (
                row["outstanding_amount"]
                for row in invoice_rows
                if row["status"] in {"unpaid", "partial", "due_soon", "overdue"}
            ),
            ZERO,
        )
    )
    collected_this_month = _money(
        sum(
            (
                row["amount"]
                for row in payment_rows
                if row["payment_date"].startswith(as_of.strftime("%Y-%m"))
            ),
            ZERO,
        )
    )
    forecast_window_end = as_of + timedelta(days=30)
    forecast_amount = _money(
        sum(
            (
                row["outstanding_amount"]
                for row in invoice_rows
                if row["outstanding_amount"] > ZERO
                and as_of <= date.fromisoformat(row["due_date"]) <= forecast_window_end
            ),
            ZERO,
        )
    )

    dashboard = {
        "as_of": as_of.isoformat(),
        "invoice_count": len(invoice_rows),
        "client_count": len(client_summary),
        "collected_this_month": collected_this_month,
        "pending_total": pending_total,
        "overdue_total": overdue_total,
        "forecast_30_day_inflow": forecast_amount,
    }

    return {
        "dashboard": dashboard,
        "invoices": invoice_rows,
        "payments": payment_rows,
        "clients": sorted(client_summary.values(), key=lambda item: item["client_name"]),
        "monthly_summary": sorted(monthly_summary.values(), key=lambda item: item["month"]),
        "alerts": alerts,
    }
