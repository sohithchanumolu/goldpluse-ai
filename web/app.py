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
        7
    )

    current_24k = rows[0].price_24k
    current_22k = rows[0].price_22k

    avg_24k = sum(
        row.price_24k for row in rows
    ) / len(rows)

    avg_22k = sum(
        row.price_22k for row in rows
    ) / len(rows)

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

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "price_24k": current_24k,
            "price_22k": current_22k,
            "trend_24k": trend_24k,
            "trend_22k": trend_22k
        }
    )