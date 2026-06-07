import plotly.express as px
from src.main import main
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import sys
from pathlib import Path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)
from src.database import(
    SessionLocal,
    get_last_n_days,
    get_all_prices
)

app = FastAPI()

templates = Jinja2Templates(
    directory="web/templates"
)

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )

@app.get("/dashboard")
def dashboard(request: Request):
    session = SessionLocal()
    rows = get_last_n_days(
        session,
        30
    )

    if not rows:
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "price_24k": 0,
                "price_22k": 0,
                "trend_24k": "No Data",
                "trend_22k": "No Data",
                "records_count": 0,
                "chart_24k": "",
                "chart_22k": "",
                "ai_report": "No data available yet. Run the data pipeline first."
        }
    )

    latest = rows[0]

    current_24k = latest.price_24k
    current_22k = latest.price_22k

    avg_24k = (
        sum(row.price_24k for row in rows)
        / len(rows)
    )

    avg_22k = (
        sum(row.price_22k for row in rows)
        / len(rows)
    )

    trend_24k = (
        "UP 📈"
        if current_24k > avg_24k
        else "DOWN 📉"
    )

    trend_22k = (
        "UP 📈"
        if current_22k > avg_22k
        else "DOWN 📉"
    )

    chart_rows = list(reversed(rows))

    dates = [
        row.date
        for row in chart_rows
    ]

    prices_24k = [
        row.price_24k
        for row in chart_rows
    ]

    prices_22k = [
        row.price_22k
        for row in chart_rows
    ]

    fig_24k = px.line(
        x=dates,
        y=prices_24k,
        title="30-Day 24K Gold Price Trend"
    )

    fig_24k.update_layout(
        height=250,
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        template="plotly_white"
    )

    chart_24k = fig_24k.to_html(
        full_html=False
    )

    fig_22k = px.line(
        x=dates,
        y=prices_22k,
        title="30-Day 22K Gold Price Trend"
    )

    fig_22k.update_layout(
        height=250,
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        template="plotly_white"
    )

    chart_22k = fig_22k.to_html(
        full_html=False
    )

    report_file = Path("data/latest_report.txt")
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as file:
            ai_report = file.read()
    else:
        ai_report = "No AI report generated yet."

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "price_24k": current_24k,
            "price_22k": current_22k,
            "trend_24k": trend_24k,
            "trend_22k": trend_22k,
            "chart_24k": chart_24k,
            "chart_22k": chart_22k,
            "record_count": len(rows),
            "last_updated": latest.date,
            "ai_report": ai_report
        }
    )


@app.get("/history")
def history(request:Request):
    session = SessionLocal()
    prices = get_all_prices(session)
    history_data=[]

    for i,row in enumerate(prices):
        if i<len(prices)-1:
            previous_price = prices[i+1].price_24k
            daily_change = row.price_24k - previous_price
        else:
            daily_change = 0
        
        history_data.append({
            "date": row.date,
            "city": row.city,
            "price_24k": row.price_24k,
            "price_22k": row.price_22k,
            "daily_change": daily_change
        })

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "history_data": history_data
        }
    )

@app.get("/analysis")
def analysis(request: Request):

    with open(
        "data/latest_report.txt",
        "r",
        encoding="utf-8"
    ) as file:
        report = file.read()

    return templates.TemplateResponse(
        request=request,
        name="analysis.html",
        context={
            "report": report
        }
    )

@app.get("/about")
def about(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="about.html"
    )


@app.get("/run")
def run_pipeline():
    try:
        main()
        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": str(e)}