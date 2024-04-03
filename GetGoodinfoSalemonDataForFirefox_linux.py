"""
20220517-0935 01. GetGoodinfoSalemonDataV3ForFirefox.py 更名為 GetGoodinfoSalemonDataForFirefox.py
              02. 調整輸入檔案可透過參數指定
"""
import os
import re
import sys
import time
import platform
from time import sleep
from genericpath import isfile
from sqlalchemy import false, null
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if len(sys.argv) < 3 :
    print("You need input two parameter(fmt : theStocksList theDate) ")
    print("syntax(windows)    : C:\python GetGoodinfoSalemonDataForFirefox.py STOCKS_LIST 20220517")
    print("syntax(imac/linux) : $python3 GetGoodinfoSalemonDataForFirefox.py STOCKS_LIST 20220517")
    sys.exit()

STOCK_LIST = sys.argv[1]
print("filename: " + STOCK_LIST)
if not os.path.isfile(STOCK_LIST) :
    print("股票清單不存在(" + STOCK_LIST + ")，請檢查程式執行目錄是否存在此程式。\n")
    exit()

theDate = sys.argv[2]
maxRetryCnt = 3
dividendFilename = "SaleMonDetail.xls"
logFilename = "__errorlogSD.log"
logFile = open(logFilename, "a")

# 設定profile
fileOptions=Options()
fileOptions.set_preference("browser.download.folderList", 2)
fileOptions.set_preference("browser.download.manager.showWhenStarting", False)
fileOptions.set_preference("browser.download.dir", os.getcwd())

# For imac (linux maybe ok); windows needs other style
service = null
#if not platform.system() == "Windows" :
#    service = Service('geckodriver')
if platform.system() == "Linux" :
    service = Service('./geckodriver')
elif platform.system() == "Darwin" :
    service = Service('geckodriver')

f = open(STOCK_LIST, 'r')
lines = f.readlines()
for line in lines:
    stockCode = line.rstrip()
    print("Processing stockno = " + stockCode)
    stockFilename = stockCode + "-salemon-" + theDate + ".xls"

    isFinished = False
    retryCnt = 0

    while (not isFinished):
        # 先檢查要抓的資料是否已經存在，若存在則跳
        if os.path.isfile(stockFilename) :
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " is exist.\n")
            isFinished = True
            continue

        # 判斷何種作業系統
        driver = null
        if platform.system() == "Windows" : 
            driver = webdriver.Firefox(options = fileOptions)
        else :
            driver = webdriver.Firefox(service = service, options = fileOptions)
        driver.get("https://goodinfo.tw/tw/index.asp")

        elem = driver.find_element(By.ID, "txtStockCode")
        elem.send_keys(stockCode)
        elem.send_keys(Keys.RETURN)

        try:
            # 這種寫法，有時侯會因為網頁載入太慢(>10秒)而失敗
            driver.implicitly_wait(10)
            web_element = driver.find_element(By.LINK_TEXT, '每月營收')
            web_element.click()
            driver.implicitly_wait(15)

            ele_select = driver.find_element(By.ID, "selSaleMonChartPeriod")
            selectOptions = Select(ele_select).options
            time.sleep(5)

        #   捲動scrollbar
            js = "var q=document.documentElement.scrollTop=1500"
            driver.execute_script(js)
            time.sleep(5)

#           options.select_by_value("全部") -- 未測試是否可用…
            selectOptions[2].click()
            time.sleep(15)

# 20240315  配合網站名稱調整
#            button = driver.find_element(By.XPATH, "//input[@type='button' and @value='匯出XLS']")
            button = driver.find_element(By.XPATH, "//input[@type='button' and @value='XLS']")

            driver.execute_script("arguments[0].click();", button)
        
            isFinished = True

        except BaseException:
            retryCnt += 1
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " excption.\n")

        finally:
            time.sleep(10)
            # 關閉browser
            driver.close()
#           driver.quit()

            if retryCnt > 2:
                isFinished = True

        if os.path.isfile(dividendFilename):
            os.rename(dividendFilename, stockFilename)
            isFinished = True
        else:
            if retryCnt >= maxRetryCnt:
                logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " failure.\n")

logFile.close()
f.close()
