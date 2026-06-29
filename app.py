from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DATA_DIR = ROOT / "data"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flowledger.csv_io import parse_uploaded_invoices, parse_uploaded_payments
from flowledger.engine import build_report_data
from flowledger.workbook import create_workbook_bytes


st.set_page_config(
    page_title="FlowLedger",
    page_icon=":bar_chart:",
    layout="wide",
)


st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f4fbff 0%, #e7f4ff 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #dff1ff 0%, #cfe9ff 100%);
    }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(136, 193, 255, 0.45);
        border-radius: 10px;
        padding: 0.9rem 1rem;
        box-shadow: 0 10px 30px rgba(71, 143, 214, 0.08);
    }
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(180deg, #7fc8ff 0%, #5daeea 100%);
        color: #083b66;
        border: 1px solid #5daeea;
        border-radius: 10px;
        font-weight: 600;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: #3f9bdd;
        color: #052b49;
    }
    div[data-testid="stFileUploader"] section {
        background: rgba(255, 255, 255, 0.76);
        border-radius: 12px;
        border: 1px solid rgba(136, 193, 255, 0.45);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _money(value: Decimal) -> str:
    return f"${value:,.2f}"


def _render_metric_row(report_data: dict[str, object]) -> None:
    dashboard = report_data["dashboard"]
    metrics = st.columns(4)
    metrics[0].metric("Collected This Month", _money(dashboard["collected_this_month"]))
    metrics[1].metric("Pending Receivables", _money(dashboard["pending_total"]))
    metrics[2].metric("Overdue Amount", _money(dashboard["overdue_total"]))
    metrics[3].metric("30 Day Forecast", _money(dashboard["forecast_30_day_inflow"]))


def _render_monthly_summary(report_data: dict[str, object]) -> None:
    monthly_rows = report_data["monthly_summary"]
    if not monthly_rows:
        st.info("Upload files to see the monthly cash flow trend.")
        return

    chart_rows = [
        {
            "month": row["month"],
            "invoiced": float(row["invoiced_amount"]),
            "collected": float(row["collected_amount"]),
        }
        for row in monthly_rows
    ]
    st.subheader("Monthly cash flow")
    st.line_chart(chart_rows, x="month", y=["invoiced", "collected"], height=320)


def _render_alerts(report_data: dict[str, object]) -> None:
    alerts = report_data["alerts"]
    st.subheader("Alerts")
    if not alerts:
        st.success("No overdue or due-soon invoices in this reporting window.")
        return
    st.dataframe(alerts, use_container_width=True, hide_index=True)


def _render_tables(report_data: dict[str, object]) -> None:
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Invoices", "Payments", "Clients", "Monthly Summary"]
    )
    with tab1:
        st.dataframe(report_data["invoices"], use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe(report_data["payments"], use_container_width=True, hide_index=True)
    with tab3:
        st.dataframe(report_data["clients"], use_container_width=True, hide_index=True)
    with tab4:
        st.dataframe(report_data["monthly_summary"], use_container_width=True, hide_index=True)


def _sample_file_hint() -> None:
    st.caption(
        "Sample files are included at data/flowledger_invoices_sample.csv and "
        "data/flowledger_payments_sample.csv."
    )


def _load_sample_report_data(as_of: date) -> dict[str, object]:
    invoices_bytes = (DATA_DIR / "flowledger_invoices_sample.csv").read_bytes()
    payments_bytes = (DATA_DIR / "flowledger_payments_sample.csv").read_bytes()
    invoices = parse_uploaded_invoices(invoices_bytes)
    payments = parse_uploaded_payments(payments_bytes)
    report_data = build_report_data(invoices, payments, as_of)
    workbook_bytes = create_workbook_bytes(report_data)
    return {
        "report_data": report_data,
        "workbook_bytes": workbook_bytes,
        "source_label": "sample data",
    }


def main() -> None:
    st.title("FlowLedger")
    st.write(
        "Upload invoice and payment CSV files to generate a freelancer cash flow "
        "dashboard and downloadable Excel report."
    )
    primary_actions = st.columns([1, 1.2, 2.4])
    with primary_actions[0]:
        use_sample_main = st.button("Try Sample Data", use_container_width=True)
    with primary_actions[1]:
        st.download_button(
            "Download Sample Invoices",
            data=(DATA_DIR / "flowledger_invoices_sample.csv").read_bytes(),
            file_name="flowledger_invoices_sample.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with primary_actions[2]:
        st.download_button(
            "Download Sample Payments",
            data=(DATA_DIR / "flowledger_payments_sample.csv").read_bytes(),
            file_name="flowledger_payments_sample.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with st.sidebar:
        st.header("Inputs")
        as_of = st.date_input("Reporting date", value=date.today())
        invoices_file = st.file_uploader("Invoices CSV", type=["csv"])
        payments_file = st.file_uploader("Payments CSV", type=["csv"])
        use_sample = st.button("Try Sample Data", use_container_width=True)
        _sample_file_hint()
        st.download_button(
            "Download Sample Invoices",
            data=(DATA_DIR / "flowledger_invoices_sample.csv").read_bytes(),
            file_name="flowledger_invoices_sample.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            "Download Sample Payments",
            data=(DATA_DIR / "flowledger_payments_sample.csv").read_bytes(),
            file_name="flowledger_payments_sample.csv",
            mime="text/csv",
            use_container_width=True,
        )

    result_bundle: dict[str, object] | None = None
    if use_sample or use_sample_main:
        result_bundle = _load_sample_report_data(as_of)
    elif invoices_file and payments_file:
        try:
            invoices = parse_uploaded_invoices(invoices_file.getvalue())
            payments = parse_uploaded_payments(payments_file.getvalue())
            report_data = build_report_data(invoices, payments, as_of)
            workbook_bytes = create_workbook_bytes(report_data)
            result_bundle = {
                "report_data": report_data,
                "workbook_bytes": workbook_bytes,
                "source_label": "uploaded files",
            }
        except Exception as exc:
            st.error(f"Could not process the uploaded files: {exc}")
            return

    if result_bundle is None:
        st.info("Add both CSV files to start the demo.")
        st.markdown(
            """
            **Expected flow**

            1. Upload an invoices CSV.
            2. Upload a payments CSV.
            3. Review the live dashboard and alerts.
            4. Download the generated Excel workbook.
            """
        )
        return

    report_data = result_bundle["report_data"]
    workbook_bytes = result_bundle["workbook_bytes"]
    st.success(f"Dashboard generated from {result_bundle['source_label']}.")

    _render_metric_row(report_data)

    top_left, top_right = st.columns([1.25, 1])
    with top_left:
        _render_monthly_summary(report_data)
    with top_right:
        _render_alerts(report_data)

    _render_tables(report_data)

    st.download_button(
        "Download Excel Report",
        data=workbook_bytes,
        file_name=f"flowledger_report_{as_of.isoformat()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
