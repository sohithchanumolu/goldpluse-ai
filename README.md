# GoldPulse AI

## Overview

GoldPulse AI is an intelligent gold-price monitoring system that collects gold market data, stores historical records, analyzes trends using AI, and delivers daily market reports directly to Telegram.

The project combines data engineering, database management, AI-powered analysis, and automated notifications into a single end-to-end application.

---

## Features

* Daily gold price tracking
* Live USD/INR exchange rate integration
* Historical data storage with SQLite
* Trend analysis using Pandas
* AI-generated market reports using Gemini
* Telegram report delivery
* Gold price alert system
* Hyderabad-focused retail price estimation
* Modular and extensible architecture

---

## Tech Stack

### Backend

* Python

### Database

* SQLite
* SQLAlchemy

### Data Processing

* Pandas

### AI & LLM

* LangChain
* Google Gemini

### Integrations

* Telegram Bot API
* Requests

---

## Project Structure

```text
goldpulse-ai/
│
├── data/
│   └── gold_prices.db
│
├── src/
│   ├── fetch_price.py
│   ├── database.py
│   ├── analyzer.py
│   ├── telegram_bot.py
│   ├── alerts.py
│   └── main.py
│
├── .env
├── requirements.txt
└── README.md
```

---

## Architecture

```text
Gold API
    ↓
USD/INR Conversion
    ↓
Retail Price Estimation
    ↓
SQLite Database
    ↓
Pandas Analysis
    ↓
Gemini AI
    ↓
Telegram Report
    ↓
Price Alerts
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd goldpulse-ai
```

### Create Environment

```bash
conda create -n goldpulse python=3.11
conda activate goldpulse
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key

TELEGRAM_BOT_TOKEN=your_bot_token

TELEGRAM_CHAT_ID=your_chat_id
```

---

## Usage

Run the application:

```bash
python src/main.py
```

The system will:

1. Fetch the latest gold price
2. Calculate Hyderabad retail estimates
3. Store data in SQLite
4. Analyze historical trends
5. Generate an AI-powered report
6. Send the report to Telegram
7. Trigger alerts if price conditions are met

---

## Sample Report

```text
📈 GoldPulse AI

📍 Hyderabad

💵 USD/INR Rate: 95.84

🥇 24K Gold: ₹15,604.51/g
📊 7-Day Avg: ₹15,480.20/g

💍 22K Gold: ₹14,304.13/g
📊 7-Day Avg: ₹14,190.18/g

📈 Trend: UP

Market Summary:
Gold remains above its weekly average, indicating
continued bullish momentum in the market.

Investor Insight:
Long-term investors may consider gradual
accumulation while monitoring short-term
price fluctuations.
```

---

## Future Improvements

* Real Indian retail gold price integration
* Multi-city support
* Automated scheduling
* Gold price forecasting
* Interactive dashboard
* Web application deployment
* Multi-user Telegram subscriptions
* Email notifications

---

## Learning Outcomes

This project demonstrates:

* API Integration
* Database Design
* Data Engineering
* AI Application Development
* LangChain Integration
* Prompt Engineering
* Telegram Bot Development
* End-to-End AI System Design

---

## Author

Sohith Chanumolu

Built as a practical AI engineering project to explore data pipelines, LLM integration, automation, and intelligent reporting systems.
