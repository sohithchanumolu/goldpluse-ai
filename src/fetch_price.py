import requests
from datetime import date

TROY_OUNCE_TO_GRAMS = 31.1035
RETAIL_MULTIPLIER = 1.14

def get_usd_inr_rate():
    try:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=10
        )
        response.raise_for_status()
        return response.json()["rates"]["INR"]

    except Exception:
        return 94.0

def get_gold_price():
    response = requests.get(
        "https://api.gold-api.com/price/XAU",
        timeout=10
    )
    response.raise_for_status()
    gold_data = response.json()
    usd_per_ounce = gold_data["price"]
    usd_to_inr = get_usd_inr_rate()
    price_24k = (
        usd_per_ounce
        * usd_to_inr
        / TROY_OUNCE_TO_GRAMS
        * RETAIL_MULTIPLIER
    )
    price_22k = price_24k * (22 / 24)

    return {
        "date": date.today(),
        "city": "Hyderabad",
        "usd_inr_rate": round(usd_to_inr, 2),
        "price_24k": round(price_24k, 2),
        "price_22k": round(price_22k, 2),
    }


if __name__ == "__main__":
    data = get_gold_price()
    print(f"USD/INR Rate: {data['usd_inr_rate']}")
    print(f"24K Gold: ₹{data['price_24k']}/g")
    print(f"22K Gold: ₹{data['price_22k']}/g")