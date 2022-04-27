from genericpath import isfile
import os
import re
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from sqlalchemy import false
from time import sleep

if len(sys.argv) < 3 :
    print("You need input one parameter(fmt : theStockCode theDate) ")
    print("syntax : C:\python GetGoodinfoSalemonDataV2.py 2002 20220420")
    sys.exit()

maxRetryCnt = 3
stockCode = sys.argv[1]
logFilename = "__errorlogSD.log"
stockFilename = stockCode + "-salemon-" + sys.argv[2] +".xls"
dividendFilename = "SaleMonDetail.xls"

if not os.path.isfile(logFilename):
    open(logFilename, "a")

# 設定broser profile(這支程式以firefox為範例，故只適用firefox browser)
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", os.getcwd())
#profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

isFinished = False
retryCnt = 0

while (not isFinished):
    driver = webdriver.Firefox(firefox_profile=profile)
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

#       使用firefox瀏灠器        
        # 變更select
        ele_select = driver.find_element(By.ID, "selSaleMonChartPeriod")
        options = Select(ele_select).options
        time.sleep(5)
#        options.select_by_value("全部") -- 未測試是否可用…
        options[2].click()
        time.sleep(15)

        button = driver.find_element(By.XPATH, "//input[@type='button' and @value='匯出XLS']")
        driver.execute_script("arguments[0].click();", button)
        
        isFinished = True

    except BaseException:
        retryCnt += 1
        # out errorfile
        with open(logFilename, "a") as logFile:
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " excption.\n")
        logFile.close() 

    finally:
        # 關閉browser
        time.sleep(10)
        driver.close()
        if retryCnt > 2:
            isFinished = True

    #os.rename('/Users/earvin/Downloads/DividendDetail.xls', '/Users/earvin/Downloads/5388.xls')
    if os.path.isfile(dividendFilename):
        os.rename(dividendFilename, stockFilename)
        isFinished = True
    else:
        if retryCnt >= maxRetryCnt:
            # write errorfile
            with open(logFilename, "a") as logFile:
                logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " failure.\n")
            logFile.close() 
