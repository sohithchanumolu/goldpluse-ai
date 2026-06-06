# GoldPulse AI

## Track Gold. Understand Trends.

GoldPulse AI is an AI-powered gold market intelligence platform that combines live gold price tracking, historical data analysis, interactive dashboards, and automated AI-generated market insights.

The system collects gold market data, stores historical records, analyzes trends using Google Gemini, and presents the results through a modern web dashboard and Telegram notifications.

---

## Features

### Live Gold Monitoring

* 24K gold price tracking
* 22K gold price tracking
* USD/INR exchange rate integration
* Hyderabad retail price estimation

### AI Market Analysis

* Gemini-powered market insights
* Trend analysis
* Investor recommendations
* Automated daily reports

### Interactive Dashboard

* Landing page
* Dashboard page
* Historical records page
* AI analysis page
* About page

### Data Visualization

* 24K price trend charts
* 22K price trend charts
* Daily change tracking
* Historical data storage

### Notifications

* Telegram alerts
* Daily gold market reports
* Price monitoring system

---

## Website Pages

### Home

Landing page introducing GoldPulse AI.

### Dashboard

Displays:

* Current 24K gold price
* Current 22K gold price
* Trend indicators
* Historical charts
* AI market analysis

### History

Displays:

* Historical gold prices
* Daily price changes
* Stored records

### Analysis

Displays:

* Latest AI-generated market report

### About

Displays:

* Project overview
* Technology stack
* Architecture
* Roadmap

---

## Technology Stack

### Backend

* Python
* FastAPI

### Database

* SQLite
* SQLAlchemy

### Data Processing

* Pandas

### AI

* Google Gemini
* LangChain

### Visualization

* Plotly

### Notifications

* Telegram Bot API

### Frontend

* HTML
* CSS
* Jinja2 Templates

---

## Architecture

```text
Gold Price API
        ↓
USD/INR Exchange Rate
        ↓
Price Processing
        ↓
SQLite Database
        ↓
Historical Analysis
        ↓
Gemini AI
        ↓
Dashboard + Telegram
```

## Project Structure

```text
goldpulse-ai/
│
├── data/
│   ├── gold_prices.db
│   └── latest_report.txt
│
├── src/
│   ├── fetch_price.py
│   ├── database.py
│   ├── analyzer.py
│   ├── telegram_bot.py
│   ├── alerts.py
│   └── main.py
│
├── web/
│   ├── app.py
│   └── templates/
│       ├── home.html
│       ├── dashboard.html
│       ├── history.html
│       ├── analysis.html
│       └── about.html
│
├── requirements.txt
├── .env
├── README.md
└── .gitignore
```

## Installation

```bash
git clone <repository-url>

cd goldpulse-ai

pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_key

TELEGRAM_BOT_TOKEN=your_token

TELEGRAM_CHAT_ID=your_chat_id
```

## Run Dashboard

```bash
uvicorn web.app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Run Daily Analysis Pipeline

```bash
python src/main.py
```

This will:

1. Fetch gold prices
2. Update the database
3. Generate AI analysis
4. Save latest report
5. Send Telegram notification

## Future Improvements

* Gold price prediction
* Multi-city support
* Email notifications
* User accounts
* Portfolio tracking
* Mobile application
* Advanced analytics

## Author

Sohith Chanumolu

Built as an end-to-end AI engineering project combining data engineering, automation, AI analysis, and web development.
