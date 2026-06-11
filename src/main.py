from langchain_google_genai import data
from src.alerts import check_alerts
from src.analyzer import generate_report
from src.telegram_bot import send_message
import asyncio
from src.analyzer import generate_report, get_price_summary
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

    report = report.replace("**", "")
    report = report.strip()
    while "\n\n\n" in report:
        report = report.replace("\n\n\n", "\n\n")

    with open(
        "data/latest_report.txt",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(report)
    
    with open(
        "data/report_history.txt",
        "a",
        encoding="utf-8"
    ) as file:
        file.write(
            f"\n\n=== {data['date']} ===\n"
        )

    file.write(report)

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