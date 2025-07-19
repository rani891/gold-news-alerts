from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from forexfactory_scraper import get_forexfactory_events
from dailyfx_scraper import get_dailyfx_events
from investing_scraper import get_investing_events
from utils import is_relevant, is_gold_related, extract_date, extract_date_from_page, get_direction

app = Flask(__name__)

sources = {
    "IMF": "https://www.imf.org/en/News",
    "G7": "https://www.international.gc.ca/world-monde/international_relations-relations_internationales/g7/news-nouvelles.aspx?lang=eng",
    "Bank of England": "https://www.bankofengland.co.uk/news",
}

@app.route("/")
def index():
    results = []
    today = datetime.now()
    cutoff = today - timedelta(days=1)
    headers = {"User-Agent": "Mozilla/5.0"}

    for name, url in sources.items():
        try:
    response = requests.get(url, timeout=20)
    # ...
except requests.exceptions.RequestException:
    return f"שגיאה זמנית: לא ניתן להתחבר ל־{source_name}"
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
            results.append({"source": name, "text": f"שגיאה: {e}", "url": "#", "date": "-", "gold": False, "direction": ""})

    for fetcher in [get_forexfactory_events, get_dailyfx_events, get_investing_events]:
        try:
            for item in fetcher():
                if item["date"] < today:
                    continue
                results.append(item)
        except Exception as e:
            results.append({"source": fetcher.__name__.replace("get_", "").replace("_events", "").capitalize(), "text": f"שגיאה: {e}", "url": "#", "date": "-", "gold": False, "direction": ""})

    results = sorted(results, key=lambda x: x["date"])
    html = "<h2>🔔 כל ההודעות הרלוונטיות לזהב ולדולר 🔔</h2><ul>"
    for r in results:
        direction = f"({r['direction']})" if r.get("direction") else ""
        html += f"<li><b>{r['source']}</b>: <a href='{r['url']}' target='_blank'>{r['text']}</a> {direction} ({r['date']})</li>"
    html += "</ul>"

    return render_template_string(html)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
