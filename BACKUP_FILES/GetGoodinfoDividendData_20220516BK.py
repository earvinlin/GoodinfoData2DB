from genericpath import isfile
import os
import re
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import false

if len(sys.argv) < 3 :
    print("You need input two parameter(fmt : theStockCode theDate) ")
    print("syntax : C:\python getGoodinfoDividendData.py 2002 20220420")
    sys.exit()

maxRetryCnt = 3
stockCode = sys.argv[1]
logFilename = "__errorlogDD.log"
stockFilename = stockCode + "-dividend-" + sys.argv[2] + ".xls"
dividendFilename = "DividendDetail.xls"

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
    # firefox
    driver = webdriver.Firefox(firefox_profile=profile)
    driver.get("https://goodinfo.tw/tw/index.asp")

    elem = driver.find_element_by_id("txtStockCode")
    elem.send_keys(stockCode)
    elem.send_keys(Keys.RETURN)

    try:
        # 這種寫法，有時侯會因為網頁載入太慢(>10秒)而失敗
        driver.implicitly_wait(10)
        web_element=driver.find_element_by_link_text('股利政策')
        web_element.click()

        # 這種寫法，有時侯會因為網頁載入太慢(>15秒)而失敗
        driver.implicitly_wait(15)
        button = driver.find_element_by_xpath("//input[@type='button' and @value='匯出XLS']")
#        button = driver.find_element(by=By.XPATH, value="//*[@id='StockDetailMenu']/table/tbody/tr/td[1]/table/tbody/tr[12]/td/a")
        driver.execute_script("arguments[0].click();", button)
        
        isFinished = True

    except BaseException:
        retryCnt += 1
        # out errorfile
        with open(logFilename, "a") as logFile:
            logFile.write(stockFilename + " " + str(retryCnt) + " excption.\n")
        logFile.close() 

    finally:
        # 關閉browser
        driver.close()
        if retryCnt > 3:
            isFinished = True


    #os.rename('/Users/earvin/Downloads/DividendDetail.xls', '/Users/earvin/Downloads/5388.xls')
    if os.path.isfile(dividendFilename):
        os.rename(dividendFilename, stockFilename)
        isFinished = True
    else:
        if retryCnt >= maxRetryCnt:
            # out errorfile
            with open(logFilename, "a") as logFile:
                logFile.write(stockFilename + " " + str(retryCnt) + " failure.\n")
            logFile.close() 
