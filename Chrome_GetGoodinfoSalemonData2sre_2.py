"""
取得Goodinfo網站「股利政策」超連結資料 (高穩定版)
 -- 20260211 : 尚未完成，依…2res.py來修改

執行程式語法：
<windows>
python Chrome_GetGoodinfoDividendData2sre.py STOCKS_LIST_dividend.txt 20260203 1 0
<imac / linux>
python3 Chrome_GetGoodinfoDividendData2sre.py STOCKS_LIST_test.txt 20260203 1 0
"""
import os
import sys
import time
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException
)

GOODINFO_URL = "https://goodinfo.tw/tw/index.asp"
dividendFilename = "DividendDetail.xls"
logFilename = "__errorlogDD.log"
maxRetryCnt = 3


# ------------------------------------------------------------
#  Driver Setup
# ------------------------------------------------------------
def setup_driver(download_dir: str) -> webdriver.Chrome:
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--window-size=800,600")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    service_path = "chromedriver.exe" if platform.system() == "Windows" else "/usr/local/bin/chromedriver"
    service = Service(service_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(20)
    driver.set_script_timeout(20)
    return driver


# ------------------------------------------------------------
#  Utility: Safe Click
# ------------------------------------------------------------
def safe_click(driver, xpath, timeout=10):
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", elem)
        time.sleep(0.2)
        driver.execute_script("arguments[0].click();", elem)
        return True
    except:
        return False


# ------------------------------------------------------------
#  Close Ads / Popups
# ------------------------------------------------------------
def close_ads(driver):
    # Close JS alert
    try:
        WebDriverWait(driver, 1).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
    except:
        pass

    # Hide common ad divs
    ad_xpaths = [
        "//div[contains(@class,'fc-ab-root')]",
        "//div[@id='divPopMsg']",
        "//div[contains(@class,'modal-dialog')]",
        "//div[contains(@class,'fc-dialog-container')]",
        "//div[contains(@style,'z-index') and contains(@style,'position')]",
    ]
    for xp in ad_xpaths:
        try:
            for e in driver.find_elements(By.XPATH, xp):
                driver.execute_script("arguments[0].style.display='none';", e)
        except:
            pass

    # Hide iframes
    try:
        for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
            driver.execute_script("arguments[0].style.display='none';", iframe)
    except:
        pass


# ------------------------------------------------------------
#  Close "我知道了" Button
# ------------------------------------------------------------
def close_iknow(driver):
    safe_click(driver, "//input[@value='我知道了']", timeout=3)


# ------------------------------------------------------------
#  Wait for download
# ------------------------------------------------------------
def wait_for_download(download_path, timeout=40):
    for _ in range(timeout):
        if os.path.isfile(download_path):
            return True
        time.sleep(1)
    return False


# ------------------------------------------------------------
#  Process one stock
# ------------------------------------------------------------
def process_stock_once(driver, stockCode, destination_dir, theDate,
                       theSelectOption, theSelectOption2, download_dir):

    stockFilename = f"{stockCode}-dividend-{theDate}.xls"
    target_path = os.path.join(destination_dir, stockFilename)
    download_path = os.path.join(download_dir, dividendFilename)

    if os.path.isfile(target_path):
        print(f"{stockFilename} 已存在，跳過")
        return True

    if os.path.isfile(download_path):
        os.remove(download_path)

    # Load main page
    driver.get(GOODINFO_URL)
    close_ads(driver)
    close_iknow(driver)

    # Input stock code
    try:
        box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "txtStockCode"))
        )
        box.clear()
        box.send_keys(stockCode)
        box.send_keys(Keys.RETURN)
    except:
        print("找不到股票輸入框")
        return False

    close_ads(driver)

    # Click 股利政策
    if not safe_click(driver, "//a[text()='股利政策']", timeout=20):
        print("找不到『股利政策』連結")
        return False

    close_ads(driver)

    # Select main dropdown
    try:
        dropdown = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "selSheet"))
        )
        Select(dropdown).select_by_index(int(theSelectOption))
    except:
        print("主選單選取失敗")
        return False

    # Select sub dropdown
    if theSelectOption in ["0", "1"]:
        try:
            dropdown2 = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "selSheet2"))
            )
            Select(dropdown2).select_by_index(int(theSelectOption2))
        except:
            print("子選單選取失敗")
            return False

    # 等待 AJAX 載入完成（最關鍵）
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table[contains(@class,'tbl')]")
            )
        )
    except:
        print("資料表未載入完成")
        return False

    close_ads(driver)

    # Click XLS
    try:
        elem = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='XLS']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", elem)
        time.sleep(0.3)
        elem.click()
    except:
        print("XLS 按鈕點擊失敗")
        return False

    # Wait for download
    if not wait_for_download(download_path):
        print(f"{stockCode}: 檔案未下載成功")
        return False

    # Move file
    try:
        os.rename(download_path, target_path)
        print(f"{stockCode}: 下載完成 → {target_path}")
        return True
    except Exception as e:
        print(f"{stockCode}: 檔案搬移失敗：{e}")
        return False


# ------------------------------------------------------------
#  Retry wrapper
# ------------------------------------------------------------
def process_stock_with_retry(stockCode, destination_dir, theDate,
                             theSelectOption, theSelectOption2,
                             download_dir, logFile):

    stockFilename = f"{stockCode}-dividend-{theDate}.xls"

    for attempt in range(1, maxRetryCnt + 1):
        driver = None
        try:
            print(f"  第 {attempt} 次嘗試：{stockCode}")
            driver = setup_driver(download_dir)

            if process_stock_once(driver, stockCode, destination_dir, theDate,
                                  theSelectOption, theSelectOption2, download_dir):
                return

        except Exception as e:
            msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {stockFilename} [{attempt}/{maxRetryCnt}] Error: {e}\n"
            print("  ", msg.strip())
            logFile.write(msg)

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

        time.sleep(2)

    fail_msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {stockFilename} 下載失敗（已達最大重試次數）\n"
    print("  ", fail_msg.strip())
    logFile.write(fail_msg)


# ------------------------------------------------------------
#  Main
# ------------------------------------------------------------
def main():
    if len(sys.argv) < 4:
        print("參數不足：theFilename theDate theSelectOption theSelectOption2")
        sys.exit(1)

    theStocksList = sys.argv[1]
    theDate = sys.argv[2]
    theSelectOption = sys.argv[3]
    theSelectOption2 = sys.argv[4] if theSelectOption != "2" else ""

    if not os.path.isfile(theStocksList):
        print(f"股票清單不存在：{theStocksList}")
        sys.exit(1)

    destination_dir = os.path.join("Data", "EXCEL", "Origin", "dividend", str(theDate))
    os.makedirs(destination_dir, exist_ok=True)

    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    with open(logFilename, "a", encoding="utf-8") as logFile, open(theStocksList, "r", encoding="utf-8") as f:
        for processCnt, line in enumerate(f, start=1):
            stockCode = line.strip()
            if not stockCode:
                continue
            print(f"處理第 {processCnt} 檔：{stockCode}")
            process_stock_with_retry(
                stockCode, destination_dir, theDate,
                theSelectOption, theSelectOption2,
                download_dir, logFile
            )


if __name__ == "__main__":
    main()
