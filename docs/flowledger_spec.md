# FlowLedger MVP

FlowLedger is a freelancer-focused invoice and cash flow manager that turns two
simple CSV inputs into an automated Excel workbook.

## MVP features

- import invoices and payments from CSV
- auto-match payments to invoices by `invoice_id`
- calculate paid, pending, overdue, and due-soon invoices
- summarize collections and billing by month and by client
- generate a styled `.xlsx` workbook with dashboard, tables, and charts

## Input schema

### Invoices CSV

- `invoice_id`
- `client_name`
- `issue_date` in `YYYY-MM-DD`
- `due_date` in `YYYY-MM-DD`
- `amount`
- `currency`
- `status` optional

### Payments CSV

- `payment_id`
- `invoice_id`
- `payment_date` in `YYYY-MM-DD`
- `amount`
- `method` optional
- `notes` optional

## Workbook sheets

- `Dashboard`
- `Invoices`
- `Payments`
- `Clients`
- `Monthly Summary`
- `Alerts`

## Streamlit demo

FlowLedger also includes a Streamlit web app entrypoint at `app.py`.

### Local run

```bash
cd "/Users/kareenalakhani/Documents/New project"
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

### Demo flow

- upload an invoices CSV
- upload a payments CSV
- review live metrics, alerts, and tables
- download the generated Excel report

### Streamlit Community Cloud deployment

- push the repository to GitHub
- create a new app in Streamlit Community Cloud
- choose this repository
- set the main file path to `app.py`
- keep dependencies in `requirements.txt`
