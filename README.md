# Business Analytics Dashboard

A polished Streamlit dashboard inspired by the provided Business Analyst UI.

## Features
- Responsive sidebar navigation
- KPI cards for Revenue, Profit, Margin, Orders, Customers and AOV
- Date / Region / Category filters
- Monthly Revenue & Profit charts
- Region, Category and Product analytics
- Customer analysis
- Data quality checks
- SQL analysis with SQLite
- Business insights and recommendations
- CSV and PDF export
- CSV upload validation
- Sample dataset included

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Then open the URL shown by Streamlit, normally:
http://localhost:8501

## Custom data
Use the Settings page and a CSV with these columns:

Date, Region, Category, Product, Customer_Type, Revenue, Cost, Orders, Customer_ID
