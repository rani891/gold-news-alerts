import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_investing_events():
    url = "https://www.investing.com/news/economy"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("a.title")
        results = []
        for article in articles[:30]:
            title = article.get_text(strip=True)
            href = article["href"]
            full_url = "https://www.investing.com" + href
            results.append({
                "source": "Investing",
                "url": full_url,
                "text": title
            })
        return results
    except Exception as e:
        return [{"source": "Investing", "url": url, "text": f"שגיאה: {e}"}]