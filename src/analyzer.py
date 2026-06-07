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
    You are a professional Indian gold market analyst.

    City: Hyderabad

    USD/INR Exchange Rate: {usd_inr_rate}

    Current 24K Gold Price: ₹{current_24k}/gram
    7-Day Average 24K Price: ₹{average_24k}/gram

    Current 22K Gold Price: ₹{current_22k}/gram
    7-Day Average 22K Price: ₹{average_22k}/gram

    Market Trend: {trend}

    Generate exactly in this format:

    Market Summary:
    <analysis>

    24K Gold Analysis:
    <analysis>

    22K Gold Analysis:
    <analysis>

    Investor Insight:
    <analysis>

    Do not use markdown.
    Do not use bullet points.
    Keep each section 1-2 sentences.

    Keep it under 120 words.
    """
)

    chain = prompt | llm
    response = chain.invoke(summary)
    return response.content