def check_alerts(current_22k, current_24k, avg_22k, avg_24k):
    alerts = []
    
    # Define trigger thresholds (1.0% drop is significant for gold)
    drop_threshold = 1.0 
    surge_threshold = 1.5

    # 24K Logic (Investment Grade)
    diff_24k = ((current_24k - avg_24k) / avg_24k) * 100
    if diff_24k <= -drop_threshold:
        alerts.append(
            f"🚨 24K STRONG BUY ALERT 🚨\n\n"
            f"Price has dropped {abs(diff_24k):.2f}% below the 7-day average. This indicates a potential buying window.\n\n"
            f"Current: ₹{current_24k}/g\n"
            f"7-Day Avg: ₹{avg_24k:.2f}/g"
        )
    elif diff_24k >= surge_threshold:
        alerts.append(
            f"📈 24K SURGE ALERT 📈\n\n"
            f"Price has surged {diff_24k:.2f}% above the 7-day average.\n\n"
            f"Current: ₹{current_24k}/g\n"
            f"7-Day Avg: ₹{avg_24k:.2f}/g"
        )

    # 22K Logic (Retail/Jewellery Grade)
    diff_22k = ((current_22k - avg_22k) / avg_22k) * 100
    if diff_22k <= -drop_threshold:
        alerts.append(
            f"💍 22K RETAIL OPPORTUNITY 💍\n\n"
            f"Jewellery gold is currently {abs(diff_22k):.2f}% cheaper than the weekly average.\n\n"
            f"Current: ₹{current_22k}/g\n"
            f"7-Day Avg: ₹{avg_22k:.2f}/g"
        )

    return alerts