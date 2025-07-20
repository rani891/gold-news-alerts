# imf_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from utils import is_relevant, is_gold_related, extract_date, get_direction

def get_imf_events():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.imf.org/en/News/SearchNews")

        # בחר את News Type: Speech
        wait = WebDriverWait(driver, 10)
        news_type_select = wait.until(EC.presence_of_element_located((By.ID, "newsType")))
        news_type_select.send_keys("Speech")

        # לחץ על כפתור Filter
        filter_button = driver.find_element(By.XPATH, '//button[text()="Filter"]')
        filter_button.click()

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card-title a")))

        links = driver.find_elements(By.CSS_SELECTOR, ".card-title a")
        results = []

        for link in links[:30]:
            text = link.text.strip()
            url = link.get_attribute("href")

            if not is_relevant(text):
                continue

            date = extract_date(text)
            if not date or date < datetime.now():
                continue

            results.append({
                "source": "IMF",
                "url": url,
                "text": text,
                "date": date.strftime("%d/%m/%Y"),
                "gold": is_gold_related(text),
                "direction": get_direction(text)
            })

        return results

    finally:
        driver.quit()
