import os
import re
import sys
import time
import platform
from time import sleep
from sqlalchemy import false, null
from genericpath import isfile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if len(sys.argv) < 2 :
    print("You need input two parameter(fmt : theStockCode theDate) ")
    print("syntax : C:\python getGoodinfoDividendData.py 20220420")
    sys.exit()

STOCK_LIST = "STOCKS_LIST_test.txt"
if not os.path.isfile(STOCK_LIST) :
    print("股票清單不存在(STOCK_LIST.txt)，請檢查程式執行目錄是否存在此程式。\n")
    exit()

tradeDate = sys.argv[1]
maxRetryCnt = 3
processCnt = 0
dividendFilename = "DividendDetail.xls"
logFilename = "__errorlogDD.log"
logFile = open(logFilename, "a")

#if not os.path.isfile(logFilename):
#    open(logFilename, "a")

# 設定profile
fileOptions=Options()
fileOptions.set_preference("browser.download.folderList", 2)
fileOptions.set_preference("browser.download.manager.showWhenStarting", False)
fileOptions.set_preference("browser.download.dir", os.getcwd())

# For imac (linux maybe ok); windows needs other style
service = null
if not platform.system() == "Windows" :
    service = Service('geckodriver')

f = open(STOCK_LIST, 'r')
lines = f.readlines()
for line in lines:
    processCnt += 1
    stockCode = line.rstrip()
    print("Processing stockno (" + str(processCnt) + ") = " + stockCode)
    stockFilename = stockCode + "-dividend-" + tradeDate +".xls"

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
            driver = webdriver.Firefox(options=fileOptions)
        else :
            driver = webdriver.Firefox(service=service, options=fileOptions)
        driver.get("https://goodinfo.tw/tw/index.asp")

        elem = driver.find_element(By.ID, "txtStockCode")
        elem.send_keys(stockCode)
        elem.send_keys(Keys.RETURN)

        try:
            # 這種寫法，有時侯會因為網頁載入太慢(>10秒)而失敗
            driver.implicitly_wait(10)
            web_element = driver.find_element(By.LINK_TEXT, '股利政策')
            web_element.click()
            driver.implicitly_wait(15)

        #   捲動scrollbar
            js = "var q=document.documentElement.scrollTop=1500"
            driver.execute_script(js)
            time.sleep(5)

            button = driver.find_element(By.XPATH, "//input[@type='button' and @value='匯出XLS']")
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



