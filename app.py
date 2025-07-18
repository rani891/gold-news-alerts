
from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os

def load_keywords(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

keywords = load_keywords("keywords.txt")
gold_keywords = load_keywords("gold_keywords.txt")
up_keywords = ["hawkish", "rate hike", "tightening", "inflation rising", "yields up", "strong dollar"]
down_keywords = ["dovish", "rate cut", "easing", "weak dollar", "deflation", "bond buying"]

app = Flask(__name__)

sources = {
    "Federal Reserve": "https://www.federalreserve.gov/newsevents/pressreleases.htm",
    "ECB": "https://www.ecb.europa.eu/press/pr/date/html/index.en.html",
    "BOJ": "https://www.boj.or.jp/en/announcements/release_2024/index.htm/",
    "IMF": "https://www.imf.org/en/News",
}

date_patterns = [
    r"(\d{1,2}/\d{1,2}/\d{4})",
    r"(\d{1,2}/\d{1,2})",
    r"(\d{1,2}\.\d{1,2}\.\d{4})",
    r"(\d{1,2}\s+\w+\s+\d{4})",
    r"(\d{1,2}\s+\w+\s+\d{2})",
    r"(\w+\s+\d{1,2},?\s*\d{4}?)",
    r"(Published|Date|Updated on):?\s*(\w+\s+\d{1,2},?\s*\d{4}?)",
]

TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>GOLD-news-alerts</title></head>
<body>
    <h2>🔔 כל ההודעות הרלוונטיות לזהב ולדולר 🔔</h2>
    {% if results %}
        <ul>
            {% for res in results %}
                <li>
                    <b>{{ res['source'] }}</b>:
                    <a href="{{ res['url'] }}" target="_blank">{{ res['text'] }}</a>
                    {% if res['gold'] %} <span style="color:orange">🔶 Gold/USD</span>{% endif %}
                    {% if res['direction'] == 'up' %} 🔼{% elif res['direction'] == 'down' %} 🔽{% endif %}
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
    return any(word in text.lower() for word in keywords)

def is_gold_related(text):
    return any(word in text.lower() for word in gold_keywords)

def get_direction(text):
    txt = text.lower()
    if any(word in txt for word in up_keywords):
        return "up"
    elif any(word in txt for word in down_keywords):
        return "down"
    return ""

def extract_date_from_page(url):
    try:
        if not url.endswith(".htm") and not "news" in url:
            return None
        sub_res = requests.get(url, timeout=3)
        sub_text = sub_res.text
        return extract_date(sub_text)
    except:
        return None

@app.route("/")
def index():
    results = []
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
                        date_obj = extract_date_from_page(href)
                    results.append({
                        "source": name,
                        "url": href,
                        "text": text,
                        "date": date_obj.strftime("%d/%m/%Y") if date_obj else "לא מזוהה",
                        "gold": gold_related,
                        "direction": get_direction(text)
                    })
        except Exception as e:
            results.append({
                "source": name,
                "url": url,
                "text": f"שגיאה: {str(e)}",
                "date": "-",
                "gold": False,
                "direction": ""
            })
    return render_template_string(TEMPLATE, results=results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
