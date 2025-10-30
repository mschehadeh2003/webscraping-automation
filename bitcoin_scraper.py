## Step 2: Write the Selenium Scraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def initializing_driver():
    """Initialize Chrome WebDriver with stable configuration."""
    options = Options()
    options.add_argument("--headless")  # Headless for GitHub Actions
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver


def scrape_bitcoin_data(driver):
    """Scrape Bitcoin details from CoinMarketCap."""
    URL = "https://coinmarketcap.com/currencies/bitcoin/"
    driver.get(URL)

    # Wait for the key element to confirm page load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-test="text-cdp-price-display"]'))
    )

    # Extract Bitcoin Price
    price = driver.find_element(By.CSS_SELECTOR, 'span[data-test="text-cdp-price-display"]').text

    # Extract Market Cap
    market_cap = driver.find_element(
        By.XPATH, "//div[contains(text(),'Market cap')]/ancestor::dt/following-sibling::dd//span"
    ).text

    # Extract 24h Trading Volume
    volume_24h = driver.find_element(
        By.XPATH, "//div[contains(text(),'Volume (24h')]/ancestor::dt/following-sibling::dd//span"
    ).text

    # Extract Circulating Supply
    circulating_supply = driver.find_element(
        By.XPATH, "//div[contains(text(),'Circulating supply')]/ancestor::dt/following-sibling::dd//span"
    ).text

    # Extract 24h Price Change
    price_change_24h = driver.find_element(
        By.CSS_SELECTOR, "p[class*='change-text']"
    ).text

    # Extract Community Sentiment
    bullish_sentiment_elems = driver.find_elements(
        By.CSS_SELECTOR, "span.sc-65e7f566-0.cOjBdO.ratio"
    )
    bearish_sentiment_elems = driver.find_elements(
        By.CSS_SELECTOR, "span.sc-65e7f566-0.iKkbth.ratio"
    )

    bullish = bullish_sentiment_elems[0].text if bullish_sentiment_elems else "N/A"
    bearish = bearish_sentiment_elems[0].text if bearish_sentiment_elems else "N/A"

    # Capture timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Store the data in a dictionary
    bitcoin_data = {
        "timestamp": timestamp,
        "price": price,
        "market_cap": market_cap,
        "volume_24h": volume_24h,
        "circulating_supply": circulating_supply,
        "price_change_24h": price_change_24h,
        "bullish_sentiment": bullish,
        "bearish_sentiment": bearish
    }

    return bitcoin_data


def save_to_csv(data, file_name="bitcoin_hourly_data.csv"):
    """Save scraped data to CSV."""
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "timestamp", "price", "market_cap", "volume_24h",
            "circulating_supply", "price_change_24h",
            "bullish_sentiment", "bearish_sentiment"
        ])

    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(file_name, index=False)


if __name__ == "__main__":
    print("Scraping Bitcoin Data...")
    driver = initializing_driver()

    try:
        scraped_data = scrape_bitcoin_data(driver)
        if scraped_data:
            save_to_csv(scraped_data)
            print("✅ Data saved to bitcoin_hourly_data.csv")
        else:
            print("❌ Failed to scrape data.")
    finally:
        driver.quit()