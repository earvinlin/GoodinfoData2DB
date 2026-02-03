"""
取得 Goodinfo 網站「每月營收」超連結資料（高穩定版）

執行語法：
<windows>
python Chrome_GetGoodinfoDividendData2_stable.py STOCKS_LIST_dividend.txt 20250712 1 2
<imac / linux>
python3 Chrome_GetGoodinfoDividendData2_stable.py STOCKS_LIST_test.txt test 2 0
"""

import os
import sys
import time
import platform
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)

maxRetryCnt = 3
dividendFilename = "DividendDetail.xls"
logFilename = "__errorlogDD.log"
GOODINFO_URL = "https://goodinfo.tw/tw/index.asp"


def setup_driver(download_dir: str) -> webdriver.Chrome:
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
#    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=800,600")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    if platform.system() == "Windows":
        service = Service("chromedriver.exe")
    else:
        service = Service("/usr/local/bin/chromedriver")

    return webdriver.Chrome(service=service, options=chrome_options)


def close_ads(driver):
    """關閉 Goodinfo 網站可能出現的廣告、彈窗、alert、iframe 廣告。"""

    # 1. 處理 JavaScript alert
    try:
        WebDriverWait(driver, 1).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        print("  已關閉 alert 視窗")
    except:
        pass

    # 2. 處理常見廣告 DIV
    ad_selectors = [
        "//div[contains(@class,'fc-ab-root')]",
        "//div[@id='divPopMsg']",
        "//div[contains(@class,'modal-dialog')]",
        "//div[contains(@class,'fc-dialog-container')]",
        "//div[contains(@style,'z-index') and contains(@style,'position')]",
    ]

    for xpath in ad_selectors:
        try:
            elems = driver.find_elements(By.XPATH, xpath)
            for e in elems:
                driver.execute_script("arguments[0].style.display='none';", e)
                print(f"  已隱藏廣告元素：{xpath}")
        except:
            pass

    # 3. 處理 iframe 廣告
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                driver.execute_script("arguments[0].style.display='none';", iframe)
                print("  已隱藏 iframe 廣告")
            except:
                pass
    except:
        pass


def wait_for_download(download_path: str, timeout: int = 30) -> bool:
    """輪詢等待檔案出現，最多 timeout 秒。"""
    for _ in range(timeout):
        if os.path.isfile(download_path):
            return True
        time.sleep(1)
    return False


def clear_old_download(download_path: str):
    """避免上一檔殘留檔案影響判斷。"""
    if os.path.isfile(download_path):
        try:
            os.remove(download_path)
        except OSError:
            pass


def process_stock_once(
    driver: webdriver.Chrome,
    stockCode: str,
    destination_dir: str,
    theDate: str,
    theSelectOption: str,
    theSelectOption2: str,
    download_dir: str,
) -> bool:
    """單次嘗試處理一檔股票，成功回傳 True，失敗回傳 False（不做 retry）。"""

    stockFilename = f"{stockCode}-dividend-{theDate}.xls"
    target_path = os.path.join(destination_dir, stockFilename)
    download_path = os.path.join(download_dir, dividendFilename)

    # 已存在就直接視為成功
    if os.path.isfile(target_path):
        print(f"{stockFilename} 已存在，跳過")
        return True

    clear_old_download(download_path)

    driver.get(GOODINFO_URL)
    close_ads(driver)

    # 關閉「我知道了」按鈕
    elems = driver.find_elements(By.XPATH, "//input[@value='我知道了']")
    if elems:
        print("按鈕存在")
        elems[0].click()   # 或 driver.execute_script("arguments[0].click();", elems[0])
    else:
        print("按鈕不存在")
#    button = WebDriverWait(driver, 10).until(
#       EC.element_to_be_clickable((By.XPATH, "//input[@value='我知道了']")))
#       button.click()

    # 輸入股票代碼
    elem = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "txtStockCode"))
    )
    elem.clear()
    elem.send_keys(stockCode)
    elem.send_keys(Keys.RETURN)
    close_ads(driver)

    # 等「股利政策」連結
    web_element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "股利政策"))
    )
    web_element.click()
    close_ads(driver)

    #time.sleep(5)

    # 主選單
    dropdown = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "selSheet"))
    )
    select = Select(dropdown)
    select.select_by_index(int(theSelectOption))

    # 子選單（視選項而定）
    if theSelectOption in ["0", "1"]:
        dropdown2 = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "selSheet2"))
        )
        select2 = Select(dropdown2)
        select2.select_by_index(int(theSelectOption2))
        print(
            f"選中：{select.first_selected_option.text}, 子項目：{select2.first_selected_option.text}"
        )
    else:
        print(f"選中：{select.first_selected_option.text}")

    # 點擊 XLS 按鈕
    button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='button' and @value='XLS']")
        )
    )
    driver.execute_script("arguments[0].click();", button)
    close_ads(driver)

    # 等待下載完成
    if not wait_for_download(download_path, timeout=40):
        print(f"{stockCode}: 檔案未下載成功")
        return False

    # 移動檔案
    try:
        os.rename(download_path, target_path)
        print(f"{stockCode}: 下載完成 → {target_path}")
        return True
    except OSError as e:
        print(f"{stockCode}: 檔案搬移失敗：{e}")
        return False


def process_stock_with_retry(
    stockCode: str,
    destination_dir: str,
    theDate: str,
    theSelectOption: str,
    theSelectOption2: str,
    download_dir: str,
    logFile,
):
    """帶 retry 的高穩定流程：每次 retry 都重新啟動 driver。"""

    stockFilename = f"{stockCode}-dividend-{theDate}.xls"
    for attempt in range(1, maxRetryCnt + 1):
        driver = None
        try:
            print(f"  第 {attempt} 次嘗試：{stockCode}")
            driver = setup_driver(download_dir)
            ok = process_stock_once(
                driver,
                stockCode,
                destination_dir,
                theDate,
                theSelectOption,
                theSelectOption2,
                download_dir,
            )
            if ok:
                return
        except (TimeoutException, NoSuchElementException) as e:
            msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {stockFilename} [{attempt}/{maxRetryCnt}] Timeout/NoSuchElement: {e}\n"
            print("  ", msg.strip())
            logFile.write(msg)
        except WebDriverException as e:
            msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {stockFilename} [{attempt}/{maxRetryCnt}] WebDriverException: {e}\n"
            print("  ", msg.strip())
            logFile.write(msg)
        except Exception as e:
            msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {stockFilename} [{attempt}/{maxRetryCnt}] Unexpected: {e}\n"
            print("  ", msg.strip())
            logFile.write(msg)
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass
        time.sleep(2)  # 每次 retry 稍微間隔一下，避免過度壓力

    # 全部嘗試失敗
    fail_msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {stockFilename} 下載失敗（已達最大重試次數 {maxRetryCnt}）\n"
    print("  ", fail_msg.strip())
    logFile.write(fail_msg)


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

    with open(logFilename, "a", encoding="utf-8") as logFile, open(
        theStocksList, "r", encoding="utf-8"
    ) as f:
        for processCnt, line in enumerate(f, start=1):
            stockCode = line.strip()
            if not stockCode:
                continue
            print(f"處理第 {processCnt} 檔：{stockCode}")
            process_stock_with_retry(
                stockCode,
                destination_dir,
                theDate,
                theSelectOption,
                theSelectOption2,
                download_dir,
                logFile,
            )


if __name__ == "__main__":
    main()
