def check_alerts(price_22k, price_24k):
    alerts = []

    if price_22k < 14000:
        alerts.append(
            f"🚨 22K Gold Alert\n"
            f"Current Price: ₹{price_22k}/g\n"
            f"Below ₹14,000 target."
        )

    if price_24k < 15500:
        alerts.append(
            f"🚨 24K Gold Alert\n"
            f"Current Price: ₹{price_24k}/g\n"
            f"Below ₹15,500 target."
        )

    return alerts