from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os
from forexfactory_scraper import get_forexfactory_events  # ✅ נכון

app = Flask(__name__)

def load_keywords(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

keywords = load_keywords("keywords.txt")
gold_keywords = load_keywords("gold_keywords.txt")
up_keywords = ["hawkish", "rate hike", "tightening", "inflation rising", "yields up", "strong dollar"]
down_keywords = ["dovish", "rate cut", "easing", "weak dollar", "deflation", "bond buying"]

sources = {
    "Federal Reserve": "https://www.federalreserve.gov/newsevents/pressreleases.htm",
    "ECB": "https://www.ecb.europa.eu/press/pr/date/html/index.en.html",
    "BOJ": "https://www.boj.or.jp/en/announcements/release_2024/index.htm/",
    "Bank of England": "https://www.bankofengland.co.uk/news",
    "US Treasury": "https://home.treasury.gov/news",
}

patterns = [
    r"(\d{1,2}/\d{1,2}/\d{4})", r"(\d{1,2}/\d{1,2})",
    r"(\d{1,2}\.\d{1,2}\.\d{4})", r"(\d{1,2}\s+\w+\s+\d{4})",
    r"(\d{1,2}\s+\w+\s+\d{2})", r"(\w+\s+\d{1,2},?\s*\d{4}?)",
    r"(Published|Date|Updated on):?\s*(\w+\s+\d{1,2},?\s*\d{4}?)"
]

def extract_date(text):
    for p in patterns:
        for match in re.findall(p, text):
            try:
                s = match if isinstance(match, str) else match[-1]
                for fmt in ("%d/%m/%Y", "%d/%m", "%d.%m.%Y", "%d %B %Y", "%d %B %y", "%B %d, %Y", "%B %d"):
                    try:
                        d = datetime.strptime(s.strip(), fmt)
                        return d.replace(year=datetime.now().year) if d.year == 1900 else d
                    except: continue
            except: continue
    return None

def extract_date_from_page(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        if not url.endswith(".htm") and "news" not in url:
            return None
        return extract_date(requests.get(url, headers=headers, timeout=4).text)
    except: return None

def is_relevant(text):
    return any(word in text.lower() for word in keywords)

def is_gold_related(text):
    return any(word in text.lower() for word in gold_keywords)

def get_direction(text):
    txt = text.lower()
    if any(w in txt for w in up_keywords): return "up"
    if any(w in txt for w in down_keywords): return "down"
    return ""

TEMPLATE = """
<!DOCTYPE html><html><head><meta charset='UTF-8'><title>GOLD-news-alerts</title></head><body>
<h2>התראות רלוונטיות לזהב ולדולר</h2>
{% if results %}<ul>
{% for res in results %}<li><b>{{ res['source'] }}</b>: <a href='{{ res['url'] }}' target='_blank'>{{ res['text'] }}</a>
{% if res['gold'] %} <span style='color:orange'>Gold/USD</span>{% endif %}
{% if res['direction'] == 'up' %} UP{% elif res['direction'] == 'down' %} DOWN{% endif %}
{% if res['date'] != "לא מזוהה" %} ({{ res['date'] }}){% endif %}</li>
{% endfor %}</ul>
{% else %}<p style='color:red;'><b>אין תוצאה רלוונטית.</b></p>{% endif %}
</body></html>
"""

@app.route("/")
def index():
    results = []
    today = datetime.now()
    headers = {"User-Agent": "Mozilla/5.0"}

    for name, url in sources.items():
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            soup = BeautifulSoup(resp.text, "html.parser")
            links = [a for a in soup.find_all("a", href=True) if len(a.get_text(strip=True)) > 10][:60]
            for link in links:
                text = link.get_text(strip=True)
                href = link.get("href", "")
                if not href:
                    continue
                if not href.startswith("http"):
                    href = url.rstrip("/") + "/" + href.lstrip("/")
                if is_relevant(text):
                    gold = is_gold_related(text)
                    date_obj = extract_date(text) or extract_date_from_page(href)
                    if not date_obj or date_obj < today:
                        continue
                    results.append({
                        "source": name,
                        "url": href,
                        "text": text,
                        "date": date_obj.strftime("%d/%m/%Y"),
                        "gold": gold,
                        "direction": get_direction(text)
                    })
        except Exception as e:
            results.append({
                "source": name,
                "url": url,
                "text": f"שגיאה: {e}",
                "date": "-",
                "gold": False,
                "direction": ""
            })

    # --- הוספת תוצאות מ־ForexFactory ---
    try:
        ff_events = get_forexfactory_events()
        for event in ff_events:
            if event["date"] >= today:
                results.append(event)
    except Exception as e:
        results.append({
            "source": "ForexFactory",
            "url": "https://www.forexfactory.com/calendar",
            "text": f"שגיאה: {e}",
            "date": "-",
            "gold": False,
            "direction": ""
        })

    return render_template_string(TEMPLATE, results=results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
