"""
python Chrome_GetGoodinfoDividendData2_1.py \
    --list STOCKS_LIST_dividend.txt \
    --date 20250712 \
    --main 1 \
    --sub 2
"""
import os
import sys
import time
import argparse
import platform
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


# ------------------------------------------------------------
#  Browser Initialization
# ------------------------------------------------------------
def init_browser(download_dir):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    # OS-specific chromedriver path
    if platform.system() == "Windows":
        driver_path = "chromedriver.exe"
    elif platform.system() == "Linux":
        driver_path = "/usr/local/bin/chromedriver"
    else:  # macOS
        driver_path = "/usr/local/bin/chromedriver"

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    return driver, wait


# ------------------------------------------------------------
#  Goodinfo Actions
# ------------------------------------------------------------
def load_homepage(driver, wait):
    driver.get("https://goodinfo.tw/tw/index.asp")
    wait.until(EC.presence_of_element_located((By.ID, "txtStockCode")))


def search_stock(driver, wait, stock_code):
    elem = wait.until(EC.presence_of_element_located((By.ID, "txtStockCode")))
    elem.clear()
    elem.send_keys(stock_code)
    elem.send_keys(Keys.RETURN)

    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "股利政策")))


def open_dividend_page(driver, wait):
    link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "股利政策")))
    link.click()

    wait.until(EC.presence_of_element_located((By.ID, "selSheet")))


def select_main_option(driver, wait, main_index):
    dropdown = wait.until(EC.presence_of_element_located((By.ID, "selSheet")))
    Select(dropdown).select_by_index(main_index)

    wait.until(EC.presence_of_element_located((By.ID, "selSheet")))


def select_sub_option(driver, wait, sub_index):
    dropdown2 = wait.until(EC.presence_of_element_located((By.ID, "selSheet2")))
    Select(dropdown2).select_by_index(sub_index)


def click_xls(driver, wait):
    btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//input[@type='button' and @value='XLS']")))
    btn.click()


# ------------------------------------------------------------
#  Download File Check
# ------------------------------------------------------------
def wait_for_download(filepath, timeout=30):
    """Wait until file exists and is non-empty."""
    print("filepath= ", filepath)
    start = time.time()
    while time.time() - start < timeout:
        if filepath.exists() and filepath.stat().st_size > 0:
            return True
        time.sleep(1)
    return False


# ------------------------------------------------------------
#  Process One Stock
# ------------------------------------------------------------
def process_stock(driver, wait, stock_code, date_str, main_idx, sub_idx, dest_dir, logf):
    filename = f"{stock_code}-dividend-{date_str}.xls"
    filepath = dest_dir / filename

    if filepath.exists():
        logf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {filename} exists.\n")
        return

    retry = 0
    max_retry = 3

    while retry < max_retry:
        try:
            load_homepage(driver, wait)
            search_stock(driver, wait, stock_code)
            open_dividend_page(driver, wait)

            select_main_option(driver, wait, main_idx)

            if main_idx in (0, 1):
                select_sub_option(driver, wait, sub_idx)

            click_xls(driver, wait)

            # Wait for download
            tmpfile = Path("DividendDetail.xls")
            if wait_for_download(tmpfile):
                tmpfile.rename(filepath)
                logf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {filename} OK.\n")
                return
            else:
                raise Exception("Download timeout or empty file")

        except Exception as e:
            retry += 1
            logf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {filename} retry {retry} error: {e}\n")

    logf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {filename} FAILED.\n")


# ------------------------------------------------------------
#  Main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Goodinfo Dividend Data Downloader")
    parser.add_argument("--list", required=True, help="Stock list file")
    parser.add_argument("--date", required=True, help="Date string")
    parser.add_argument("--main", type=int, required=True, help="Main option index")
    parser.add_argument("--sub", type=int, default=None, help="Sub option index")

    args = parser.parse_args()

    stock_list_file = Path(args.list)
    if not stock_list_file.exists():
        print("Stock list file not found.")
        sys.exit(1)
    print("stock_list_file= ", stock_list_file)

    dest_dir = Path("Data/EXCEL/Origin/dividend") / args.date
    dest_dir.mkdir(parents=True, exist_ok=True)

    print("dest_dir= ", dest_dir)

    driver, wait = init_browser(str(dest_dir))

    logf = open("__errorlogDD.log", "a")

    with open(stock_list_file, "r") as f:
        for line in f:
            stock_code = line.strip()
            if not stock_code:
                continue

            process_stock(
                driver, wait,
                stock_code,
                args.date,
                args.main,
                args.sub,
                dest_dir,
                logf
            )

    driver.quit()
    logf.close()


if __name__ == "__main__":
    main()

