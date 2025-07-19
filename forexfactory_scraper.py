
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_forexfactory_alerts(keywords, gold_keywords, up_keywords, down_keywords):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.forexfactory.com/calendar")

    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    results = []
    today = datetime.now().date()

    for row in soup.select("tr.calendar__row"):
        try:
            time_cell = row.select_one(".calendar__time")
            title_cell = row.select_one(".calendar__event-title")
            impact_cell = row.select_one(".calendar__impact-icon")
            currency_cell = row.select_one(".calendar__currency")

            text = title_cell.text.strip()
            currency = currency_cell.text.strip()
            date_obj = today
            url = "https://www.forexfactory.com/calendar"  # No specific post link

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

    return results
