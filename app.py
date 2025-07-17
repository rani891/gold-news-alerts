from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# מקורות
sources = {
    "Federal Reserve": "https://www.federalreserve.gov/newsevents/speeches.htm",
    "ECB": "https://www.ecb.europa.eu/press/key/html/index.en.html",
    "BOJ": "https://www.boj.or.jp/en/announcements/press/index.htm",
    "IMF": "https://www.imf.org/en/News",
}

# מילות מפתח כלליות לזיהוי נאומים חשובים
keywords = ["powell", "lagarde", "barr", "waller", "bailey", "kuroda", "speech", "remarks", "conference", "testimony", "statement"]

# מילות מפתח שמשפיעות במיוחד על זהב
gold_keywords = ["gold", "xauusd", "inflation", "interest", "dollar", "monetary", "rates", "commodities"]

# תבניות לזיהוי תאריכים
date_patterns = [
    r"(\d{1,2}/\d{1,2}/\d{4})",           # 17/07/2025
    r"(\d{1,2}/\d{1,2})",                 # 17/07
    r"(\d{1,2}\s+\w+\s+\d{4})",           # 17 July 2025
    r"(\w+\s+\d{1,2},?\s*\d{4}?)",        # July 17, 2025
]

# תבנית תצוגה
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
        match = re.search(pattern, text)
        if match:
            try:
                date_str = match.group(1)
                # נסה לפרש תאריכים שונים
                for fmt in ("%d/%m/%Y", "%d/%m", "%d %B %Y", "%B %d, %Y", "%B %d"):
                    try:
                        parsed = datetime.strptime(date_str, fmt)
                        # אם חסר שנה - נוסיף את השנה הנוכחית
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

@app.route("/")
def index():
    results = []
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    for name, url in sources.items():
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a")

            for link in links:
                text = link.get_text(strip=True)
                href = link.get("href", "")
                if not href.startswith("http"):
                    href = url.rstrip("/") + "/" + href.lstrip("/")

                if is_relevant(text):
                    gold_related = is_gold_related(text)
                    date_obj = extract_date(text)

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

app.run(host="0.0.0.0", port=5000)
