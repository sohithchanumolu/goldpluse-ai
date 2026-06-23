import os
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.fetch_price import get_usd_inr_rate
from src.database import (
    SessionLocal,
    get_last_n_days
)

def get_price_summary(days=7):
    session = SessionLocal()
    rows = get_last_n_days(session, days)

    if not rows:
        return {
            "usd_inr_rate": get_usd_inr_rate(),
            "current_24k": 0,
            "average_24k": 0,
            "current_22k": 0,
            "average_22k": 0,
            "trend": "No Data"
        }

    data = [
        {
            "date": r.date,
            "price_24k": r.price_24k,
            "price_22k": r.price_22k
        }
        for r in rows
    ]

    df = pd.DataFrame(data)

    # df.iloc[0] is the most recent row fetched from the database
    current_24k = df.iloc[0]["price_24k"]
    average_24k = df["price_24k"].mean()

    current_22k = df.iloc[0]["price_22k"]
    average_22k = df["price_22k"].mean()

    trend = (
        "UP"
        if current_24k > average_24k
        else "DOWN"
    )

    return {
        "usd_inr_rate": get_usd_inr_rate(),
        "current_24k": round(current_24k, 2),
        "average_24k": round(average_24k, 2),
        "current_22k": round(current_22k, 2),
        "average_22k": round(average_22k, 2),
        "trend": trend
    }

load_dotenv()

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
)

def generate_report():
    summary = get_price_summary()
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert Senior Commodities Analyst specializing strictly in the Indian Gold Market.\n"
            "CRITICAL RULES:\n"
            "1. You MUST evaluate, analyze, and state all gold values exclusively in Indian Rupees (INR / ₹) per gram.\n"
            "2. Do NOT convert numbers to US Dollars ($ / USD) or ounces under any circumstances.\n"
            "3. The USD/INR exchange rate should only be referenced to explain macroeconomic pressure on Indian imports.\n"
            "4. You MUST output ONLY a raw JSON object matching the exact keys requested by the human, without markdown formatting or backticks."
        ),
        (
            "human",
            "Analyze the following daily market data for Hyderabad:\n\n"
            "USD/INR Exchange Rate: {usd_inr_rate}\n\n"
            "24K Gold Price: ₹{current_24k}/gram\n"
            "24K 7-Day Moving Average: ₹{average_24k}/gram\n\n"
            "22K Gold Price: ₹{current_22k}/gram\n"
            "22K 7-Day Moving Average: ₹{average_22k}/gram\n\n"
            "Momentum Indicator: {trend}\n\n"
            "Provide the output as a raw JSON object with exactly these keys:\n"
            "- \"summary\": A 2-3 sentence macroeconomic and technical analysis written in an authoritative tone, discussing trends strictly in Indian Rupees (₹) and mentioning the USD/INR rate.\n"
            "- \"trend\": \"Bullish\", \"Bearish\", or \"Neutral\".\n"
            "- \"confidence\": An integer score out of 100.\n"
            "- \"risk\": \"Low\", \"Medium\", or \"High\".\n"
            "- \"recommendation\": A short, punchy action step.\n"
            "- \"key_insights\": A list of 3-4 specific insight strings for Indian retail buyers."
        )
    ])

    chain = prompt | llm
    response = chain.invoke(summary)
    
    # Strip any potential markdown artifacts
    content = response.content.replace("```json", "").replace("```", "").strip()
    return content