"""
取得Goodinfo網站「股利政策」超連結資料
{ 本版本為舊版，請改用最新版 Chrome_GetGoodinfoDividendData2sre.py }

執行程式語法：
<windows>
python Chrome_GetGoodinfoDividendData2.py STOCKS_LIST_dividend.txt 20250712 1 0
<imac / linux>
python3 Chrome_GetGoodinfoDividendData2.py STOCKS_LIST_test.txt test 1 0
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
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import WebDriverException

maxRetryCnt = 3
dividendFilename = "DividendDetail.xls"
logFilename = "__errorlogDD.log"

def setup_driver(download_dir):
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--start-maximized")

    if platform.system() == "Windows":
        service = Service("chromedriver.exe")
    else:
        service = Service("/usr/local/bin/chromedriver")

    return webdriver.Chrome(service=service, options=chrome_options)

def process_stock(driver, stockCode, destination_dir, theDate, theSelectOption, theSelectOption2, logFile):
    stockFilename = f"{stockCode}-dividend-{theDate}.xls"
    target_path = os.path.join(destination_dir, stockFilename)

    if os.path.isfile(target_path):
        print(f"{stockFilename} 已存在，跳過")
        return

    retryCnt = 0
    while retryCnt <= maxRetryCnt:
        try:
            driver.get("https://goodinfo.tw/tw/index.asp")

            # 等待輸入框出現
            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "txtStockCode"))
            )
            
            elem.clear()
            elem.send_keys(stockCode)
            elem.send_keys(Keys.RETURN)

            # 等待「股利政策」連結
            web_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, '股利政策'))
            )
            web_element.click()

            # 選擇主要選項
            dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selSheet"))
            )
            select = Select(dropdown)
            select.select_by_index(int(theSelectOption))

            # 如果需要第二選項
            if theSelectOption in ["0", "1"]:
                dropdown2 = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "selSheet2"))
                )
                select2 = Select(dropdown2)
                select2.select_by_index(int(theSelectOption2))
                print(f"選中：{select.first_selected_option.text}, 子項目：{select2.first_selected_option.text}")
            else:
                print(f"選中：{select.first_selected_option.text}")

            # 點擊下載按鈕
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and @value='XLS']"))
            )
            driver.execute_script("arguments[0].click();", button)

            # 等待檔案下載完成
            time.sleep(8)

            download_path = os.path.join("downloads", dividendFilename)
#            print("download_path= ", download_path, ", target_path= ", target_path)
            if os.path.isfile(download_path):
                os.rename(download_path, target_path)
                print(f"下載完成：{target_path}")
                return
            else:
                print("檔案未下載成功，重試中...")
                retryCnt += 1

        except WebDriverException:
            driver.quit()
            download_dir = os.path.join(os.getcwd(), "downloads")
            driver = setup_driver(download_dir)
            return process_stock(driver, stockCode, destination_dir, theDate, theSelectOption, theSelectOption2, logFile)
        
        except (NoSuchElementException, TimeoutException) as e:
            print(f"錯誤：{e}")
            logFile.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {stockFilename} {e}\n")
            retryCnt += 1

    logFile.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {stockFilename} 下載失敗\n")

def main():
    if len(sys.argv) < 4:
        print("參數不足：theFilename theDate theSelectOption theSelectOption2")
        sys.exit()

    theStocksList = sys.argv[1]
    theDate = sys.argv[2]
    theSelectOption = sys.argv[3]
    theSelectOption2 = sys.argv[4] if theSelectOption != "2" else ""

    if not os.path.isfile(theStocksList):
        print(f"股票清單不存在：{theStocksList}")
        sys.exit()

    destination_dir = os.path.join("Data", "EXCEL", "Origin", "dividend", str(theDate))
    os.makedirs(destination_dir, exist_ok=True)

    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    driver = setup_driver(download_dir)
    with open(logFilename, "a") as logFile, open(theStocksList, "r") as f:
        for processCnt, line in enumerate(f, start=1):
            stockCode = line.strip()
            print(f"處理第 {processCnt} 檔：{stockCode}")
            process_stock(driver, stockCode, destination_dir, theDate, theSelectOption, theSelectOption2, logFile)
    driver.quit()

if __name__ == "__main__":
    main()
