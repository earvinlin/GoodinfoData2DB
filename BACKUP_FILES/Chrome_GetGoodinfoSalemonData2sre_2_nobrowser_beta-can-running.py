"""
取得Goodinfo網站「每月營收」超連結資料 (高穩定版)

執行程式語法：
<windows>
python Chrome_GetGoodinfoSalemonData2sre_2_nobrowser.py STOCKS_LIST_v2.txt 202602
<imac / linux>
python3 Chrome_GetGoodinfoSalemonData2sre_2_nobrowser.py STOCKS_LIST_v2.txt 202602
python3 Chrome_GetGoodinfoSalemonData2sre_2_nobrowser.py STOCKS_LIST_v2_running.txt 202602
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
salemonFilename = "SaleMonDetail.xls"
logFilename = "__errorlogSD.log"
maxRetryCnt = 3


# ------------------------------------------------------------
#  Driver Setup
# ------------------------------------------------------------
# 不會開啟browser 
def setup_driver(download_dir: str) -> webdriver.Chrome:
    chrome_options = Options()

    # Headless 模式（新版 Chrome 必須使用 new headless）
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # 避免 headless 模式下被網站偵測
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # 下載設定
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # 避免 Linux / macOS sandbox 問題
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # chromedriver 路徑
    service_path = (
        "chromedriver.exe"
        if platform.system() == "Windows"
        else "/usr/local/bin/chromedriver"
    )
    service = Service(service_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(20)
    driver.set_script_timeout(20)
    return driver


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


def close_interstitial(driver):
    try:
        # 等待按鈕出現並可點擊
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "ats-interstitial-button"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        driver.execute_script("arguments[0].click();", btn)
        print("[LOG] 成功關閉 interstitial 視窗")
    except Exception as e:
        print(f"[LOG] 找不到或無法點擊 interstitial 視窗按鈕: {e}")


def close_iknow(driver):
    safe_click(driver, "//input[@value='我知道了']", timeout=3)


def wait_for_download(download_path, timeout=40):
    for _ in range(timeout):
        if os.path.isfile(download_path):
            return True
        time.sleep(1)
    return False


def process_stock_once(driver, stockCode, destination_dir, theDate, download_dir):

    stockFilename = f"{stockCode}-salemon-{theDate}.xls"
    target_path = os.path.join(destination_dir, stockFilename)
    download_path = os.path.join(download_dir, salemonFilename)

    if os.path.isfile(target_path):
        print(f"{stockFilename} 已存在，跳過")
        return True

    if os.path.isfile(download_path):
        os.remove(download_path)

    # Load main page
    driver.get(GOODINFO_URL)
    close_interstitial(driver)    
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

    close_interstitial(driver)
    close_ads(driver)

    # Click 每月營收
#    if not safe_click(driver, "//a[text()='每月營收']", timeout=20):
#        print("找不到『每月營收』連結")
#        return False
    print("查每月營收")
    driver.find_element(By.LINK_TEXT, "每月營收").click()

#    close_interstitial(driver)
#    close_ads(driver)

    print("查20年a")
    button = driver.find_element(By.XPATH, "//input[@value='查20年']")
    button.click()
    print("查20年b")

    time.sleep(2)
    
    button = driver.find_element(By.XPATH, "//input[@type='button' and @value='XLS']")
    driver.execute_script("arguments[0].click();", button)


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
                             download_dir, logFile):

    stockFilename = f"{stockCode}-salemon-{theDate}.xls"

    for attempt in range(1, maxRetryCnt + 1):
        driver = None
        try:
            print(f"  第 {attempt} 次嘗試：{stockCode}")
            driver = setup_driver(download_dir)

            if process_stock_once(driver, stockCode, destination_dir, theDate, download_dir):
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
    if len(sys.argv) < 3:
        print("參數不足：theFilename theDate ")
        sys.exit(1)

    theStocksList = sys.argv[1]
    theDate = sys.argv[2]

    if not os.path.isfile(theStocksList):
        print(f"股票清單不存在：{theStocksList}")
        sys.exit(1)

    destination_dir = os.path.join("Data", "EXCEL", "Origin", "salemon", str(theDate))
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
                download_dir, logFile
            )


if __name__ == "__main__":
    main()
