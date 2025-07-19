
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_investing_events():
    url = "https://www.investing.com/economic-calendar/"
    headers = {"User-Agent": "Mozilla/5.0"}
    events = []
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("tr.js-event-item")
        for row in rows:
            title = row.get("data-event-title", "")
            date_str = row.get("data-event-datetime", "")
            if not title or not date_str:
                continue
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except:
                continue
            if date_obj < datetime.now():
                continue
            link = "https://www.investing.com/economic-calendar/"
            events.append({
                "source": "Investing",
                "url": link,
                "text": title.strip(),
                "date": date_obj.strftime("%d/%m/%Y"),
                "gold": "gold" in title.lower() or "usd" in title.lower(),
                "direction": ""
            })
    except Exception as e:
        events.append({
            "source": "Investing",
            "url": url,
            "text": f"שגיאה: {e}",
            "date": "-",
            "gold": False,
            "direction": ""
        })
    return events
