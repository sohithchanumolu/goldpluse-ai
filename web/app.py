import uuid
import json
import plotly.express as px
from src.gold_assistant import ask_goldpulse, stream_goldpulse
from src.main import main
from fastapi import FastAPI, Request, Response, Cookie, Form, Body
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys
from pathlib import Path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)
from src.database import(
    SessionLocal,
    get_last_n_days,
    get_all_prices,
    get_session_history,
    clear_session_history
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="web/static"), name="static")

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
                "chart_24k": "",
                "chart_22k": "",
                "ai_report": None
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
        row.date.strftime("%d %b")
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

    fig_24k.update_xaxes(
        type="category"
    )

    chart_24k = fig_24k.to_html(
        full_html=False,
        config={'displayModeBar': False, 'responsive': True}
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

    fig_22k.update_xaxes(
        type="category"
    )

    chart_22k = fig_22k.to_html(
        full_html=False,
        config={'displayModeBar': False, 'responsive': True}
    )

    report_file = Path("data/latest_report.txt")
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as file:
            try:
                ai_report = json.loads(file.read())
            except json.JSONDecodeError:
                ai_report = None
    else:
        ai_report = None

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
def history(request: Request, page: int = 1):
    session = SessionLocal()
    prices = get_all_prices(session)
    history_data = []

    for i, row in enumerate(prices):
        if i < len(prices) - 1:
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

    # Pagination logic (7 records per page)
    per_page = 7
    total_records = len(history_data)
    total_pages = (total_records + per_page - 1) // per_page
    
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_data = history_data[start_idx:end_idx]

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "history_data": paginated_data,
            "page": page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    )

@app.get("/analysis")
def analysis(request: Request):
    from pathlib import Path
    report_file = Path("data/latest_report.txt")
    
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as file:
            report = file.read()
    else:
        report = "No AI report generated yet. Run the data pipeline first."

    return templates.TemplateResponse(
        request=request,
        name="analysis.html",
        context={"report": report}
    )

@app.get("/ask")
def ask_page(request: Request, session_id: str = Cookie(None)):
    session = SessionLocal()
    history_records = get_session_history(session, session_id)
    
    # Parse previous answers from stringified JSON back to objects for rendering
    parsed_history = []
    for record in history_records:
        try:
            parsed_history.append({
                "question": record.question,
                "parsed_answer": json.loads(record.answer)
            })
        except:
            parsed_history.append({
                "question": record.question,
                "parsed_answer": record.answer
            })

    response = templates.TemplateResponse(
        request=request,
        name="ask.html",
        context={
            "answer": None,
            "chat_history": parsed_history
        }
    )
    
    # If the user has no session cookie, issue a fresh one
    if not session_id:
        new_session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=new_session_id, httponly=True)
    
    return response


class StreamRequest(BaseModel):
    question: str

@app.post("/ask/stream")
async def ask_stream(request: Request, body: StreamRequest, response: Response, session_id: str = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True)
    
    # We use a generator expression or just pass the generator directly
    generator = stream_goldpulse(body.question, session_id=session_id)
    return StreamingResponse(generator, media_type="text/event-stream")


@app.post("/ask")
def ask_submit(request: Request, response: Response, question: str = Form(...), session_id: str = Cookie(None)):
    # Safeguard if cookies are somehow missing on form submission
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        
    # Generate the contextual memory answer
    answer = ask_goldpulse(question, session_id=session_id)
    
    session = SessionLocal()
    history_records = get_session_history(session, session_id)
    
    parsed_history = []
    for record in history_records:
        try:
            parsed_history.append({
                "question": record.question,
                "parsed_answer": json.loads(record.answer)
            })
        except:
            parsed_history.append({
                "question": record.question,
                "parsed_answer": {"error": record.answer}
            })

    # Create the response object
    response = templates.TemplateResponse(
        request=request,
        name="ask.html",
        context={
            "question": question,
            "answer": answer,
            "chat_history": parsed_history
        }
    )
    
    # FIX: Attach the cookie directly to the TemplateResponse so it saves to the browser
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    
    return response


@app.post("/ask/clear")
def ask_clear(response: Response, session_id: str = Cookie(None)):
    if session_id:
        session = SessionLocal()
        try:
            clear_session_history(session, session_id)
        finally:
            session.close()
    return RedirectResponse(url="/ask", status_code=303)


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

