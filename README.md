# FlowLedger

FlowLedger is a freelancer-focused finance dashboard that turns invoice and
payment CSV files into a live Streamlit demo and a downloadable Excel report.

## What it does

- uploads invoice and payment CSV files
- calculates paid, overdue, due-soon, and outstanding invoices
- shows monthly cash flow trends
- highlights alerts that need follow-up
- exports a multi-sheet Excel workbook

## Tech stack

- Python
- Streamlit
- OpenPyXL

## Project structure

- `app.py`: Streamlit app entrypoint
- `src/flowledger`: finance logic and Excel generation
- `data`: sample CSV files for demo uploads
- `tests`: unit tests
- `docs`: short project spec

## Run locally

```bash
cd "/Users/kareenalakhani/Documents/flowledger"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open `http://127.0.0.1:8501`.

## Demo flow

1. Upload an invoices CSV.
2. Upload a payments CSV.
3. Review the dashboard, alerts, and detailed tables.
4. Download the generated Excel report.

You can also use the built-in sample data buttons for a quick demo.

## Sample files

- `data/flowledger_invoices_sample.csv`
- `data/flowledger_payments_sample.csv`
- `data/flowledger_invoices_demo_large.csv`
- `data/flowledger_payments_demo_large.csv`

## Demo

- Video walkthrough: `demo/flowledger.mp4`
- Quick browser demo:
  1. Click `Try Sample Data`, or upload the CSV files from `data/`
  2. Review the dashboard, alerts, and tables
  3. Download the generated Excel report

## Test

```bash
cd "/Users/kareenalakhani/Documents/flowledger"
source .venv/bin/activate
PYTHONPATH=src python -m unittest tests/test_flowledger.py
```

## Deploy for free

This project is ready to deploy on Streamlit Community Cloud:

1. Push the repository to GitHub.
2. Create a new Streamlit Community Cloud app.
3. Select this repository.
4. Set the main file path to `app.py`.
