import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
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
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)

def generate_report():
    summary = get_price_summary()
    prompt = ChatPromptTemplate.from_template(
    """
    You are a Senior Commodities Analyst specializing in the Indian Gold Market.
    Analyze the following daily market data and provide a comprehensive, highly valuable institutional-grade briefing.

    MARKET DATA:
    City: Hyderabad
    USD/INR Exchange Rate: {usd_inr_rate}

    24K Gold (Investment Grade):
    - Current Price: ₹{current_24k}/gram
    - 7-Day Moving Average: ₹{average_24k}/gram

    22K Gold (Retail/Jewellery):
    - Current Price: ₹{current_22k}/gram
    - 7-Day Moving Average: ₹{average_22k}/gram

    Momentum Indicator: {trend}

    You MUST output ONLY a raw JSON object (without any markdown code blocks, backticks, or other text).
    The JSON object MUST have EXACTLY these keys:
    - "summary": A 2-3 sentence macroeconomic and technical summary, explicitly mentioning the USD/INR rate.
    - "trend": "Bullish", "Bearish", or "Neutral".
    - "confidence": An integer representing your confidence score out of 100 (e.g., 92).
    - "risk": "Low", "Medium", or "High".
    - "recommendation": A short, punchy actionable recommendation (e.g., "Buy on dips").
    - "key_insights": A list of 3-4 strings containing specific, practical insights for retail and investment consumers.

    Write in a highly professional, authoritative financial tone. Do not just repeat numbers; provide deep reasoning.
    """
    )

    chain = prompt | llm
    response = chain.invoke(summary)
    
    # Strip any markdown ticks just in case the LLM outputs them
    content = response.content.replace("```json", "").replace("```", "").strip()
    return content