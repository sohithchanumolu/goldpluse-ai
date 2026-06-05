from langchain_google_genai import data
from alerts import check_alerts
import alerts
from analyzer import generate_report
from telegram_bot import send_message
import asyncio
from analyzer import generate_report, get_price_summary
from database import (
    init_db,
    SessionLocal,
    GoldPrice
)
from fetch_price import get_gold_price


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
    
    summary = get_price_summary()
    report = generate_report()

    telegram_message = f"""
        📈 GoldPulse AI

        📍 Hyderabad

        💵 USD/INR Rate: {data['usd_inr_rate']}

        🥇 24K Gold: ₹{summary['current_24k']}/g
        📊 7-Day Avg: ₹{summary['average_24k']}/g

        💍 22K Gold: ₹{summary['current_22k']}/g
        📊 7-Day Avg: ₹{summary['average_22k']}/g

        📈 Trend: {summary['trend']}

        {report}
        ⚠️ Prices are estimated retail values based on international gold markets and USD/INR exchange rates. Actual local jeweller prices may vary.
    """
    asyncio.run(
        send_message(telegram_message)
    )

    alerts = check_alerts(
        summary["current_22k"],
        summary["current_24k"]
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
        send_message(f"❌ GoldPulse Error\n\n{str(e)}"))