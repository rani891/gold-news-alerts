
from bs4 import BeautifulSoup
import requests

def get_forexfactory_events():
    url = "https://www.forexfactory.com/calendar"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        for row in soup.select("tr.calendar__row"):
            title = row.select_one(".calendar__event-title")
            impact = row.select_one(".impact--high")  # לדוגמה, נוכל לבדוק אם יש השפעה גבוהה
            time = row.select_one(".calendar__time")
            if title and impact:
                text = title.get_text(strip=True)
                link = url  # אפשר לשפר בהמשך אם יש קישור ישיר
                results.append({
                    "source": "ForexFactory",
                    "url": link,
                    "text": text,
                    "date": time.get_text(strip=True) if time else "לא מזוהה",
                    "gold": any(x in text.lower() for x in ["gold", "dollar", "usd", "fomc", "powell"]),
                    "direction": ""
                })
        return results
    except Exception as e:
        return [{
            "source": "ForexFactory",
            "url": url,
            "text": f"שגיאה: {e}",
            "date": "-",
            "gold": False,
            "direction": ""
        }]
