
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def get_tradingeconomics_events():
    url = "https://tradingeconomics.com/calendar"
    headers = {"User-Agent": "Mozilla/5.0"}
    events = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("tr.calendar-row")

        for row in rows:
            date_el = row.select_one(".calendar-date")
            impact_el = row.select_one(".calendar-importance")
            title_el = row.select_one(".calendar-event")
            country_el = row.select_one(".calendar-country")

            if not title_el or not country_el or not impact_el:
                continue

            text = title_el.get_text(strip=True)
            country = country_el.get_text(strip=True)
            impact = impact_el.get("title", "").lower()
            date_text = date_el.get_text(strip=True) if date_el else ""

            if not text or "holiday" in text.lower():
                continue

            # Only high-impact events
            if "high" not in impact:
                continue

            # Simple date parsing
            try:
                date_obj = datetime.strptime(date_text, "%b %d")
                date_obj = date_obj.replace(year=datetime.now().year)
            except:
                date_obj = None

            href = "https://tradingeconomics.com/calendar"

            events.append({
                "source": f"TradingEconomics ({country})",
                "text": text,
                "url": href,
                "date": date_obj.strftime("%d/%m/%Y") if date_obj else "לא מזוהה",
                "gold": any(w in text.lower() for w in ["gold", "dollar", "inflation", "interest", "fed", "ecb", "treasury"]),
                "direction": "up" if any(w in text.lower() for w in ["rate hike", "hawkish", "tightening"]) else (
                    "down" if any(w in text.lower() for w in ["rate cut", "dovish", "easing"]) else "")
            })

    except Exception as e:
        events.append({"source": "TradingEconomics", "url": url, "text": f"שגיאה: {e}", "date": "-", "gold": False, "direction": ""})

    return events
