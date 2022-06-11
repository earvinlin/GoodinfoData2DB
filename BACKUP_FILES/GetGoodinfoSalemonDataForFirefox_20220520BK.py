"""
20220517-0935 01. GetGoodinfoSalemonDataV3ForFirefox.py 更名為 GetGoodinfoSalemonDataForFirefox.py
              02. 調整輸入檔案可透過參數指定
20220518-0901 程式碼微調及確認程式可運作
20220519-2235 修正可於linux上執行(需把geckodriver 複製至 /usr/bin 下)
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
    print("syntax(windows)    : C:\python GetGoodinfoSalemonDataForFirefox.py STOCKS_LIST.txt 20220517")
    print("syntax(imac/linux) : $python3 GetGoodinfoSalemonDataForFirefox.py STOCKS_LIST.txt 20220517")
    sys.exit()

theStocksList = sys.argv[1]
print("filename: " + theStocksList)
if not os.path.isfile(theStocksList) :
    print("股票清單不存在(" + theStocksList + ")，請檢查程式執行目錄是否存在此程式。\n")
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
fileOptions.set_preference('browser.helperApps.neverAsk.saveToDisk', \
    'text/csv,application/x-msexcel,application/excel,application/x-excel,\
    application/vnd.ms-excel,image/png,image/jpeg,text/html,text/plain,\
    application/msword,application/xml')
#fileOptions.set_preference("dom.webnotifications.enabled", False)

# 設定檔案存取路徑
destination_dir = os.path.join("Data", "EXCEL", "Origin", "salemon", str(theDate))
if platform.system() == "Windows" :
    destination_dir += "\\"
else :
    destination_dir += "/"
print("destination dir: " + destination_dir)

# For imac / linux; windows needs other style
# For linux, need put geckodriver in /usr/bin first
service = null
if not platform.system() == "Windows" :
    service = Service('geckodriver')

f = open(theStocksList, 'r')
lines = f.readlines()
for line in lines:
    stockCode = line.rstrip()
    print("Processing stockno = " + stockCode)
    stockFilename = stockCode + "-salemon-" + theDate + ".xls"

    isFinished = False
    retryCnt = 0

    while (not isFinished):
        # 先檢查要抓的資料是否已經存在，若存在則跳
#        if os.path.isfile(stockFilename) :
        if os.path.isfile(destination_dir + stockFilename) :
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " is exist.\n")
            isFinished = True
            continue

        # 判斷何種作業系統(windows OS不需要使用service object)
        driver = null
        if platform.system() == "Windows" : 
            driver = webdriver.Firefox(options = fileOptions)
        else :
#            driver = webdriver.Firefox(service = service, options = fileOptions)
            driver = webdriver.Chrome(service = service, options = fileOptions)
        driver.get("https://goodinfo.tw/tw/index.asp")

        elem = driver.find_element(By.ID, "txtStockCode")
        elem.send_keys(stockCode)
        elem.send_keys(Keys.RETURN)

        try:
            # 這種寫法，有時侯會因為網頁載入太慢(>10秒)而失敗
#            driver.implicitly_wait(10)
            time.sleep(5)

            web_element = driver.find_element(By.LINK_TEXT, '每月營收')
            web_element.click()
#            driver.implicitly_wait(15)
            time.sleep(5)

            ele_select = driver.find_element(By.ID, "selSaleMonChartPeriod")
            selectOptions = Select(ele_select).options
            time.sleep(5)

        #   捲動scrollbar
            js = "var q=document.documentElement.scrollTop=1500"
            driver.execute_script(js)
            time.sleep(5)

#           options.select_by_value("全部") -- 未測試是否可用…
            selectOptions[2].click()
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
            os.rename(dividendFilename, destination_dir + stockFilename)
            isFinished = True
        else:
            if retryCnt >= maxRetryCnt:
                logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " failure.\n")

logFile.close()
f.close()
