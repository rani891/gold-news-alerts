
from datetime import datetime, timedelta
import re

def is_relevant(text: str) -> bool:
    keywords = [
        "speech", "speaks", "statement", "testifies", "press conference",
        "rate decision", "interest rate", "FOMC", "ECB", "BOE", "BOJ", "IMF",
        "monetary policy", "fiscal policy", "minutes", "economic outlook"
    ]
    return any(keyword.lower() in text.lower() for keyword in keywords)

def is_gold_related(text: str) -> bool:
    gold_keywords = [
        "gold", "XAUUSD", "inflation", "interest rate", "bond yields",
        "Federal Reserve", "dollar", "USD", "commodities", "safe haven"
    ]
    return any(keyword.lower() in text.lower() for keyword in gold_keywords)

def extract_date(text: str) -> str:
    patterns = [
        r'(\d{1,2} [A-Za-z]+ \d{4})',
        r'([A-Za-z]+ \d{1,2}, \d{4})',
        r'(\d{4}-\d{2}-\d{2})'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return str(datetime.strptime(match.group(1), '%d %B %Y').date())
            except:
                try:
                    return str(datetime.strptime(match.group(1), '%B %d, %Y').date())
                except:
                    try:
                        return str(datetime.strptime(match.group(1), '%Y-%m-%d').date())
                    except:
                        continue
    return ""

def extract_date_from_page(text: str) -> str:
    today = datetime.today().date()
    if "tomorrow" in text.lower():
        return str(today + timedelta(days=1))
    elif "today" in text.lower():
        return str(today)
    return extract_date(text)

def get_direction(text: str) -> str:
    down_words = ["hawkish", "tightening", "raising rates", "restrictive"]
    up_words = ["dovish", "easing", "cutting rates", "stimulus"]
    for word in down_words:
        if word in text.lower():
            return "down"
    for word in up_words:
        if word in text.lower():
            return "up"
    return ""
