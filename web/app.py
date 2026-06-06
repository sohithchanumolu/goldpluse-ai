import plotly.express as px
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import sys
from pathlib import Path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)
from src.database import(
    SessionLocal,
    get_last_n_days
)

app = FastAPI()

templates = Jinja2Templates(
    directory="web/templates"
)


@app.get("/")
def dashboard(request: Request):
    session = SessionLocal()
    rows = get_last_n_days(
        session,
        30
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

    with open(
        "data/latest_report.txt",
        "r",
        encoding="utf-8"
    ) as file:
        ai_report = file.read()

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