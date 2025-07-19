
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_forexfactory_alerts(keywords, gold_keywords, up_keywords, down_keywords):
    # ... (אותו הקוד עד השלב של הלולאה)
    current_date = datetime.now().date()

    for row in soup.select("tr.calendar__row"):
        try:
            time_cell = row.select_one(".calendar__time")
            title_cell = row.select_one(".calendar__event-title")
            currency_cell = row.select_one(".calendar__currency")

            text = title_cell.text.strip()
            currency = currency_cell.text.strip()
            time_text = time_cell.text.strip().lower()

            # התעלם משורות ריקות או עבר
            if not text or "all day" in time_text or time_text in ("", "n/a"):
                continue

            # שים תאריך היום
            date_obj = current_date
            url = "https://www.forexfactory.com/calendar"

            is_relevant = any(k in text.lower() for k in keywords)
            is_gold = any(k in text.lower() for k in gold_keywords)
            direction = "up" if any(k in text.lower() for k in up_keywords) else \
                        "down" if any(k in text.lower() for k in down_keywords) else ""

            if is_relevant:
                results.append({
                    "source": "ForexFactory",
                    "url": url,
                    "text": f"{currency} - {text}",
                    "date": date_obj.strftime("%d/%m/%Y"),
                    "gold": is_gold,
                    "direction": direction
                })
        except:
            continue
