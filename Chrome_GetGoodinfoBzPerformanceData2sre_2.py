import os
import sys
import time
import platform
import glob
import random
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# -----------------------------
# User-Agent Pool
# -----------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
]


# -----------------------------
# Proxy Pool（可留空）
# -----------------------------
PROXIES = [
    # "http://username:password@proxy1:8080",
    # "http://proxy2:8080",
]


# -----------------------------
# Logging
# -----------------------------
def write_log(log_file, msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write(f"{timestamp} {msg}\n")
    log_file.flush()


# -----------------------------
# Close Ads / iframe
# -----------------------------
def close_ads(driver):
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
                close_buttons = driver.find_elements(By.XPATH, "//div[contains(@class,'close') or contains(text(),'關閉')]")
                for btn in close_buttons:
                    try:
                        btn.click()
                    except:
                        pass
                driver.switch_to.default_content()
            except:
                driver.switch_to.default_content()
    except:
        pass

    try:
        popup_close = driver.find_elements(By.XPATH, "//div[contains(@class,'close') or contains(text(),'關閉')]")
        for btn in popup_close:
            try:
                btn.click()
            except:
                pass
    except:
        pass


# -----------------------------
# Detect Goodinfo Block
# -----------------------------
def is_blocked(driver):
    try:
        if "index.asp" in driver.current_url.lower():
            return True

        body_text = driver.find_element(By.TAG_NAME, "body").text
        block_keywords = ["請稍後再試", "過於頻繁", "Too many", "blocked", "限制"]
        if any(k in body_text for k in block_keywords):
            return True

        if len(driver.find_elements(By.ID, "divDetail")) == 0:
            return True

    except:
        return True

    return False


# -----------------------------
# Wait for file download
# -----------------------------
def wait_for_download(directory, timeout=30):
    end_time = time.time() + timeout
    while time.time() < end_time:
        files = glob.glob(os.path.join(directory, "BzPerformance*.xls"))
        if files:
            return files[0]
        time.sleep(0.5)
    return None


# -----------------------------
# Initialize WebDriver (UA + Proxy rotation)
# -----------------------------
def init_driver(download_dir):
    options = webdriver.ChromeOptions()

    ua = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={ua}")

    if PROXIES:
        proxy = random.choice(PROXIES)
        options.add_argument(f"--proxy-server={proxy}")

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(20)
    return driver


# -----------------------------
# Download one stock
# -----------------------------
def download_stock(driver, stock_code, date_str, download_dir, log_file, max_retry=3):
    output_filename = f"{stock_code}-bzPerformance-{date_str}.xls"
    output_path = os.path.join(download_dir, output_filename)

    if os.path.isfile(output_path):
        write_log(log_file, f"{output_filename} already exists. Skip.")
        return

    retry = 0
    while retry < max_retry:
        try:
            driver.get("https://goodinfo.tw/tw/index.asp")
            close_ads(driver)

            if is_blocked(driver):
                write_log(log_file, f"{output_filename} blocked at homepage. Waiting 15 sec.")
                time.sleep(15)
                raise Exception("Blocked at homepage")

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "txtStockCode"))
            )

            elem = driver.find_element(By.ID, "txtStockCode")
            elem.clear()
            elem.send_keys(stock_code)
            elem.send_keys(Keys.RETURN)
            close_ads(driver)

            if is_blocked(driver):
                write_log(log_file, f"{output_filename} blocked after input. Waiting 15 sec.")
                time.sleep(15)
                raise Exception("Blocked after input")

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'經營績效')]"))
            ).click()
            close_ads(driver)

            if is_blocked(driver):
                write_log(log_file, f"{output_filename} blocked at performance page. Waiting 15 sec.")
                time.sleep(15)
                raise Exception("Blocked at performance page")

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='XLS']"))
            ).click()

            downloaded_file = wait_for_download(download_dir, timeout=30)
            if downloaded_file:
                os.rename(downloaded_file, output_path)
                write_log(log_file, f"{output_filename} downloaded successfully.")
                return
            else:
                raise Exception("Download timeout or file not found.")

        except Exception as e:
            retry += 1
            write_log(log_file, f"{output_filename} retry {retry}: {str(e)}")

            try:
                driver.quit()
            except:
                pass

            driver = init_driver(download_dir)

    write_log(log_file, f"{output_filename} failed after {max_retry} retries.")


# -----------------------------
# Main
# -----------------------------
def main():
    if len(sys.argv) < 3:
        print("Usage: python GetGoodinfoBzPerformanceData.py STOCK_LIST.txt YYYYMMDD")
        sys.exit()

    stock_list_file = sys.argv[1]
    date_str = sys.argv[2]

    if not os.path.isfile(stock_list_file):
        print(f"股票清單不存在: {stock_list_file}")
        sys.exit()

    download_dir = os.path.join("Data", "EXCEL", "Origin", "bzPerformance", date_str)
    os.makedirs(download_dir, exist_ok=True)

    log_file = open("__errorlogBP.log", "a")

    driver = init_driver(download_dir)

    with open(stock_list_file, "r") as f:
        stock_list = [line.strip() for line in f if line.strip()]

    for idx, stock_code in enumerate(stock_list, 1):
        print(f"Processing ({idx}/{len(stock_list)}): {stock_code}")
        download_stock(driver, stock_code, date_str, download_dir, log_file)

    driver.quit()
    log_file.close()


if __name__ == "__main__":
    main()