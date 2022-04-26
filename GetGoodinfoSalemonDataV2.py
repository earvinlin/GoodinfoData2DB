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
#profile = webdriver.FirefoxProfile()
#profile.set_preference("browser.download.folderList", 2)
#profile.set_preference("browser.download.manager.showWhenStarting", False)
#profile.set_preference("browser.download.dir", os.getcwd())
##profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

# 設定broser profile(這支程式以chrome為範例，故只適用chrome browser)
outpath = str(os.path)
print(outpath)
options = webdriver.ChromeOptions() 
prefs = {'profile.default_content_settings.popups': 0,
         'download.default_directory': outpath}
options.add_experimental_option('prefs', prefs)

isFinished = False
retryCnt = 0

while (not isFinished):
    # firefox
#    driver = webdriver.Firefox(firefox_profile=profile)
    driver = webdriver.Chrome(options=options)
    driver.get("https://goodinfo.tw/tw/index.asp")

    elem = driver.find_element_by_id("txtStockCode")
    elem.send_keys(stockCode)
    elem.send_keys(Keys.RETURN)

    try:
        # 這種寫法，有時侯會因為網頁載入太慢(>10秒)而失敗
        driver.implicitly_wait(10)
#        web_element = driver.find_element_by_xpath("[@id='StockDetailMenu']/table/tbody/tr/td[1]/table/tbody/tr[7]/td/a")
        web_element = driver.find_element_by_link_text('每月營收')
        web_element.click()
        
        driver.implicitly_wait(15)
        # 變更select
    #    select = Select(driver.find_element_by_id('selSaleMonChartPeriod'))
    #    ele_select = driver.find_element(By.XPATH, "//*[@id='selSaleMonChartPeriod']")
        ele_select = driver.find_element_by_id("selSaleMonChartPeriod")
#        Select(ele_select).select_by_value("2")
#        now = Select(ele_select).first_selected_option
#        print(now.text)
#        select.select_by_visible_text('全部')
#        sleep(15)
        options = Select(ele_select).options
#        for i in options :
#            print("element\'s option : %s" % i.text)
        time.sleep(5)
        options[2].click()
#        options.select_by_value("全部")
        time.sleep(5)
        # 這種寫法，有時侯會因為網頁載入太慢(>15秒)而失敗
    #    driver.implicitly_wait(10)
        button = driver.find_element_by_xpath("//*[@id='divSaleMonChartDetail']/table/tbody/tr/td/input[1]")
        button = driver.find_element_by_xpath("//input[@type='button' and @value='匯出XLS']")
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
        driver.close()
        if retryCnt > 0:
            isFinished = True
"""
    #os.rename('/Users/earvin/Downloads/DividendDetail.xls', '/Users/earvin/Downloads/5388.xls')
    if os.path.isfile(dividendFilename):
        os.rename(dividendFilename, stockFilename)
        isFinished = True
    else:
        if retryCnt >= maxRetryCnt:
            # out errorfile
            with open(logFilename, "a") as logFile:
                logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " failure.\n")
            logFile.close() 
"""