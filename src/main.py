import asyncio
import json
from src.alerts import check_alerts
from src.analyzer import generate_report, get_price_summary
from src.telegram_bot import send_message
from src.rag_engine import initialize_vector_db
from src.database import (
    DATABASE_URL,
    init_db,
    SessionLocal,
    GoldPrice
)
from src.fetch_price import get_gold_price


def main():
    init_db()
    data = get_gold_price()
    session = SessionLocal()
    existing = (
        session.query(GoldPrice)
        .filter_by(date=data["date"])
        .first()
    )

    if existing:
        print("Today's record already exists.")
    else:
        record = GoldPrice(
            date=data["date"],
            city=data["city"],
            price_24k=data["price_24k"],
            price_22k=data["price_22k"]
        )
        session.add(record)
        session.commit()
        print("Gold price saved successfully")
        print("Database connected successfully")
    
    summary = get_price_summary()
    report = generate_report()

    try:
        report_data = json.loads(report)
        formatted_report = f"🤖 AI Summary: {report_data.get('summary', '')}\n\n"
        formatted_report += f"💡 Recommendation: {report_data.get('recommendation', '')}\n"
        formatted_report += f"⚠️ Risk Level: {report_data.get('risk', '')}\n"
        formatted_report += f"🎯 Confidence: {report_data.get('confidence', '')}%\n\n"
        if "key_insights" in report_data:
            formatted_report += "🔑 Key Insights:\n"
            for insight in report_data["key_insights"]:
                formatted_report += f"- {insight}\n"
    except json.JSONDecodeError:
        formatted_report = report

    # Save to the latest report file (for the web dashboard)
    with open(
        "data/latest_report.txt",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(report)
    
    # Save to the history file (for the AI memory)
    with open(
        "data/report_history.txt",
        "a",
        encoding="utf-8"
    ) as file:
        file.write(f"\n\n=== {data['date']} ===\n")
        file.write(report)
    
    # Initialize Vector DB (Wrapped in try/except so it doesn't break alerts if it fails)
    try:
        initialize_vector_db()
    except Exception as e:
        print(f"Warning: ChromaDB failed to initialize: {e}")

    # Telegram Message (Flush left to prevent weird spacing on mobile)
    telegram_message = f"""📈 GoldPulse AI Daily Brief

                        📍 {data['city']}
                        💵 USD/INR Rate: {data['usd_inr_rate']}

                        🥇 24K Gold: ₹{summary['current_24k']}/g
                        📊 7-Day Avg: ₹{summary['average_24k']}/g

                        💍 22K Gold: ₹{summary['current_22k']}/g
                        📊 7-Day Avg: ₹{summary['average_22k']}/g

                        📈 Trend: {summary['trend']}

                        {formatted_report}

                        ⚠️ Prices are estimated retail values. Actual local jeweller prices may vary. """
    
    asyncio.run(
        send_message(telegram_message)
    )

    alerts = check_alerts(
        summary["current_22k"],
        summary["current_24k"],
        summary["average_22k"],
        summary["average_24k"]
    )
    
    for alert in alerts:
        asyncio.run(
            send_message(alert)
        )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        asyncio.run(
            send_message(f"❌ GoldPulse Error\n\n{str(e)}")
        )