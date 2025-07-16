from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# מקורות לבדיקה
sources = {
    "Federal Reserve": "https://www.federalreserve.gov/newsevents/speeches.htm",
    "ECB": "https://www.ecb.europa.eu/press/key/html/index.en.html",
    "BOJ": "https://www.boj.or.jp/en/announcements/press/index.htm",
    "IMF": "https://www.imf.org/en/News",
}

# מילות מפתח רלוונטיות
keywords = ["powell", "lagarde", "barr", "waller", "bailey", "kuroda", "speech", "remarks", "testimony", "conference", "gold", "us30", "inflation", "interest", "rates"]

# תבנית HTML בסיסית
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
                <li><b>{{ res['source'] }}</b>: <a href="{{ res['url'] }}" target="_blank">{{ res['text'] }}</a> ({{ res['date'] }})</li>
            {% endfor %}
        </ul>
    {% else %}
        <p>אין נאומים קרובים שזוהו להיום או מחר.</p>
    {% endif %}
</body>
</html>
"""

def is_relevant(text):
    return any(word.lower() in text.lower() for word in keywords)

@app.route("/")
def index():
    results = []

    for name, url in sources.items():
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a")

            for link in links:
                text = link.get_text().strip()
                href = link.get("href", "")
                if not href.startswith("http"):
                    href = url.rstrip("/") + "/" + href.lstrip("/")

                if is_relevant(text):
                    results.append({
                        "source": name,
                        "url": href,
                        "text": text,
                        "date": "תאריך לא מזוהה"
                    })

        except Exception as e:
            results.append({
                "source": name,
                "url": url,
                "text": f"שגיאה בטעינה: {str(e)}",
                "date": "-"
            })

    return render_template_string(TEMPLATE, results=results)

app.run(host="0.0.0.0", port=5000)
