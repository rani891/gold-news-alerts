from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import time
import os

app = Flask(__name__)

# =================== קישורי המקורות ===================
sources = {
    "Federal Reserve": "https://www.federalreserve.gov/newsevents/pressreleases.htm",
    "ECB": "https://www.ecb.europa.eu/press/pr/date/html/index.en.html",
    "BOJ": "https://www.boj.or.jp/en/announcements/release_2024/index.htm/",
    "IMF": "https://www.imf.org/en/News",
}

# =================== מילות מפתח ===================
keywords = [
    # אנשים
    "powell", "lagarde", "yellen", "barr", "waller", "bailey", "kuroda", "kashkari", "goolsbee",

    # הודעות שמשפיעות
    "fomc", "ecb", "boj", "imf", "central bank",
    "interest rate", "rate hike", "rate decision",
    "monetary policy", "fiscal policy", "statement",
    "press release", "testimony", "conference", "minutes", "remarks"
]

gold_keywords = [
    "gold", "xauusd", "inflation", "interest", "dollar", "commodities",
    "usd", "rates", "yield", "bond", "tightening", "hawkish", "dovish"
]

# =================== תבניות תאריך ===================
date_patterns = [
    r"(\d{1,2}/\d{1,2}/\d{4})",
    r"(\d{1,2}/\d{1,2})",
    r"(\d{1,2}\.\d{1,2}\.\d{4})",
    r"(\d{1,2}\s+\w+\s+\d{4})",
    r"(\d{1,2}\s+\w+\s+\d{2})",
    r"(\w+\s+\d{1,2},?\s*\d{4}?)",
    r"(Published|Date|Updated on):?\s*(\w+\s+\d{1,2},?\s*\d{4}?)",
]

# =================== HTML ===================
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GOLD-news-alerts</title>
</head>
<body>
    <h2>🔔 התראות רלוונטיות לזהב ולדולר – היום ומחר 🔔</h2>
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
        <p style="color:red;"><b>⚠️ אין תוצאה רלוונטית.</b></p>
    {% endif %}
</body>
</html>
"""

# =================== עוזרי ניתוח טקסט ===================
def extract_date(text):
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                date_str = match if isinstance(match, str) else match[-1]
                for fmt in ("%d/%m/%Y", "%d/%m", "%d.%m.%Y", "%d %B %Y", "%d %B %y", "%B %d, %Y", "%B %d"):
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

# =================== דף התראות ===================
@app.route("/")
def index():
    results = []
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    for name, url in sources.items():
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a")[:100]

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
                        time.sleep(0.5)
                        date_obj = extract_date_from_page(href)

                    if date_obj and today.date() <= date_obj.date() <= tomorrow.date():
                        results.append({
                            "source": name,
                            "url": href,
                            "text": text,
                            "date": date_obj.strftime("%d/%m/%Y"),
                            "gold": gold_related
                        })
                    elif not date_obj and gold_related:
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

# =================== הרצה ===================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
