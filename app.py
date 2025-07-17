from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import time

app = Flask(__name__)

sources = {
    "Federal Reserve": "https://www.federalreserve.gov/newsevents/speeches.htm",
    "ECB": "https://www.ecb.europa.eu/press/key/html/index.en.html",
    "BOJ": "https://www.boj.or.jp/en/announcements/press/index.htm",
    "IMF": "https://www.imf.org/en/News",
}

keywords = ["powell", "lagarde", "barr", "waller", "bailey", "kuroda", "speech", "remarks", "conference", "testimony", "statement"]
gold_keywords = ["gold", "xauusd", "inflation", "interest", "dollar", "monetary", "rates", "commodities"]

date_patterns = [
    r"(\d{1,2}/\d{1,2}/\d{4})",
    r"(\d{1,2}/\d{1,2})",
    r"(\d{1,2}\s+\w+\s+\d{4})",
    r"(\w+\s+\d{1,2},?\s*\d{4}?)",
    r"(Published|Date|Updated on):?\s*(\w+\s+\d{1,2},?\s*\d{4}?)",
]

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GOLD-news-alerts</title>
</head>
<body>
    <h2>🔔 נאומים קרובים עם פוטנציאל השפעה (היום ומחר) 🔔</h2>
    {% if results %}
        <ul>
            {% for res in results %}
                <li>
                    <b>{{ res['source'] }}</b>:
                    <a href="{{ res['url'] }}" target="_blank">{{ res['text'] }}</a>
                    {% if res['gold'] %} <span style="color:orange">🔶 Gold Impact</span>{% endif %}
                    {% if res['date'] != "לא מזוהה" %} ({{ res['date'] }}){% endif %}
                </li>
            {% endfor %}
        </ul>
    {% else %}
        <p>אין נאומים קרובים שזוהו להיום או מחר.</p>
    {% endif %}
</body>
</html>
"""

def extract_date(text):
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                date_str = match if isinstance(match, str) else match[-1]
                for fmt in ("%d/%m/%Y", "%d/%m", "%d %B %Y", "%B %d, %Y", "%B %d"):
                    try:
                        parsed = datetime.strptime(date_str.strip(), fmt)
                        if parsed.year == 1900:
                            parsed = parsed.replace(year=datetime.now().year)
                        return parsed
                    except:
                        continue
            except:
                continue
    return None

def is_relevant(text):
    return any(word.lower() in text.lower() for word in keywords)

def is_gold_related(text):
    return any(word.lower() in text.lower() for word in gold_keywords)

def extract_date_from_page(url):
    try:
        if not url.endswith(".htm") and not "news" in url:
            return None
        sub_res = requests.get(url, timeout=5)
        sub_text = sub_res.text
        return extract_date(sub_text)
    except:
        return None

@app.route("/")
def index():
    results = []
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    for name, url in sources.items():
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a")[:30]  # בודק רק 30 קישורים

            for link in links:
                text = link.get_text(strip=True)
                href = link.get("href", "")
                if not href:
                    continue
                if not href.startswith("http"):
                    href = url.rstrip("/") + "/" + href.lstrip("/")

                if is_relevant(text):
                    gold_related = is_gold_related(text)
                    date_obj = extract_date(text)

                    if not date_obj:
                        time.sleep(0.5)  # שהייה למניעת עומס
                        date_obj = extract_date_from_page(href)

                    if date_obj:
                        date_str = date_obj.strftime("%d/%m/%Y")
                        if today.date() <= date_obj.date() <= tomorrow.date():
                            results.append({
                                "source": name,
                                "url": href,
                                "text": text,
                                "date": date_str,
                                "gold": gold_related
                            })
                    else:
                        results.append({
                            "source": name,
                            "url": href,
                            "text": text,
                            "date": "לא מזוהה",
                            "gold": gold_related
                        })

        except Exception as e:
            results.append({
                "source": name,
                "url": url,
                "text": f"שגיאה: {str(e)}",
                "date": "-",
                "gold": False
            })

    return render_template_string(TEMPLATE, results=results)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # ברירת מחדל ל־5000 אם אין PORT מהסביבה
    app.run(host="0.0.0.0", port=port)

