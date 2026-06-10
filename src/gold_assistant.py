from src.database import (
    SessionLocal,
    get_last_n_days
)

from src.analyzer import llm


def load_gold_knowledge():

    try:
        with open(
            "data/gold_knowledge.txt",
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    except:
        return ""


def load_report_history():

    try:
        with open(
            "data/report_history.txt",
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    except:
        return ""


def ask_goldpulse(question):

    session = SessionLocal()

    rows = get_last_n_days(
        session,
        30
    )

    if not rows:
        return "No gold price data available."

    latest = rows[0]

    avg_24k = (
        sum(
            row.price_24k
            for row in rows
        )
        / len(rows)
    )

    avg_22k = (
        sum(
            row.price_22k
            for row in rows
        )
        / len(rows)
    )

    knowledge = load_gold_knowledge()

    reports = load_report_history()

    context = f"""
    Current 24K Price: {latest.price_24k}

    Current 22K Price: {latest.price_22k}

    30 Day Average 24K Price: {avg_24k:.2f}

    30 Day Average 22K Price: {avg_22k:.2f}

    Historical Reports:
    {reports}

    Gold Knowledge:
    {knowledge}
    """

    prompt = f"""
    You are GoldPulse AI.

    You are a gold market assistant.

    Use the provided data
    and historical reports
    to answer the user.

    If the question is unrelated
    to gold, politely refuse.

    DATA:

    {context}

    QUESTION:

    {question}

    Answer using:

    Market Summary:
    ...

    Key Insights:
    ...

    Recommendation:
    ...

    Keep formatting clean.
    Do not use markdown symbols like **.
    """

    response = llm.invoke(
        prompt
    )

    return response.content