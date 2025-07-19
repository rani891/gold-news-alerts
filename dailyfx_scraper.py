import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_dailyfx_events():
    url = "https://www.dailyfx.com/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("a", class_="dfx-articleCard_link__PbG1W")
        results = []
        for article in articles[:30]:
            title = article.get_text(strip=True)
            href = article["href"]
            full_url = href if href.startswith("http") else "https://www.dailyfx.com" + href
            results.append({
                "source": "DailyFX",
                "url": full_url,
                "text": title
            })
        return results
    except Exception as e:
        return [{"source": "DailyFX", "url": url, "text": f"שגיאה: {e}"}]