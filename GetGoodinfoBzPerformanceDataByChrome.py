"""
取得Goodinfo網站「經營績效」超連結資料
執行程式語法：
<windows>
python GetGoodinfoBzPerformanceData.py STOCKS_LIST_bzperformance.txt 20220517
<imac / linux>
python3 GetGoodinfoBzPerformanceData.py STOCKS_LIST_bzperformance.txt 20220517
"""

import os
import re
import sys
import time
import platform
from time import sleep
from genericpath import isfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -----------------------------
# 參數檢查
# -----------------------------
if len(sys.argv) < 3:
    print("You need input two parameter(fmt : theFilename theDate) ")
    print("syntax(windows)    : C:\\python GetGoodinfoBzPerformanceData.py STOCKS_LIST_bzperformance.txt 20220517")
    print("syntax(imac/linux) : $python3 GetGoodinfoBzPerformanceData.py STOCKS_LIST_bzperformance.txt 20220517")
    sys.exit()

theStocksList = sys.argv[1]
print("filename: " + theStocksList)
if not os.path.isfile(theStocksList):
    print("股票清單不存在(" + theStocksList + ")，請檢查程式執行目錄是否存在此程式。\n")
    exit()

theDate = sys.argv[2]
maxRetryCnt = 3
processCnt = 0
bzPerformanceFilename = "BzPerformance.xls"
logFilename = "__errorlogBP.log"
logFile = open(logFilename, "a")

# -----------------------------
# Chrome Options 設定
# -----------------------------
chromeOptions = Options()

# ✅ 下載設定
prefs = {
    "download.default_directory": os.getcwd(),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_settings.popups": 0,
    "profile.default_content_setting_values.automatic_downloads": 1,
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.images": 1,
}
chromeOptions.add_experimental_option("prefs", prefs)

# ✅ 反偵測（Goodinfo 對 Chrome 最友善）
chromeOptions.add_argument("--disable-blink-features=AutomationControlled")
chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
chromeOptions.add_experimental_option("useAutomationExtension", False)

# ✅ 降噪（避免背景連線噪音）
chromeOptions.add_argument("--disable-notifications")
chromeOptions.add_argument("--disable-popup-blocking")
chromeOptions.add_argument("--disable-default-apps")
chromeOptions.add_argument("--no-sandbox")
chromeOptions.add_argument("--disable-dev-shm-usage")

# ✅ 可選：無頭模式
# chromeOptions.add_argument("--headless=new")

# -----------------------------
# 設定檔案存取路徑
# -----------------------------
destination_dir = os.path.join("Data", "EXCEL", "Origin", "bzPerformance", str(theDate))
if platform.system() == "Windows":
    destination_dir += "\\"
else:
    destination_dir += "/"
print("Destination DIR: " + destination_dir)

# -----------------------------
# 啟動 Chrome WebDriver
# -----------------------------
service = None
if platform.system() != "Windows":
    service = Service('chromedriver')

driver = webdriver.Chrome(service=service, options=chromeOptions)

# -----------------------------
# 主程式流程
# -----------------------------
f = open(theStocksList, 'r')
lines = f.readlines()

for line in lines:
    processCnt += 1
    stockCode = line.rstrip()
    print("Processing StockNo (" + str(processCnt) + ") = " + stockCode)
    stockFilename = stockCode + "-bzPerformance-" + theDate + ".xls"

    isFinished = False
    retryCnt = 0

    while not isFinished:

        # ✅ 若檔案已存在 → 跳過
        if os.path.isfile(destination_dir + stockFilename):
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +
                          " " + stockFilename + " is exist.\n")
            isFinished = True
            continue

        driver.get("https://goodinfo.tw/tw/index.asp")
        time.sleep(5)

        elem = driver.find_element(By.ID, "txtStockCode")
        elem.send_keys(stockCode)
        elem.send_keys(Keys.RETURN)

        try:
            time.sleep(5)

            web_element = driver.find_element(By.LINK_TEXT, '經營績效')
            web_element.click()
            time.sleep(5)

            # 捲動scrollbar
            js = "var q=document.documentElement.scrollTop=1500"
            driver.execute_script(js)
            time.sleep(5)

            # 20240402 Goodinfo 改按鈕名稱
            button = driver.find_element(By.XPATH, "//input[@type='button' and @value='XLS']")
            driver.execute_script("arguments[0].click();", button)

            isFinished = True

        except Exception as err:
            print(err)
            retryCnt += 1
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +
                          " " + stockFilename + " " + str(retryCnt) + " exception.\n")

        finally:
            time.sleep(10)

            if retryCnt > maxRetryCnt:
                isFinished = True

        # ✅ 下載成功 → 改名
        if os.path.isfile(bzPerformanceFilename):
            os.rename(bzPerformanceFilename, destination_dir + stockFilename)
            isFinished = True
        else:
            if retryCnt >= maxRetryCnt:
                logFile.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +
                              " " + stockFilename + " " + str(retryCnt) + " failure.\n")

# -----------------------------
# 結束
# -----------------------------
driver.close()
logFile.close()
f.close()