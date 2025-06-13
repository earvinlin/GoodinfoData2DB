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

# 設定broser profile(這支程式以chrome為範例，故只適用chrome browser)
#outpath = "/Users/earvin/Dropbox/myStocksPGMs/GoodinfoData2DB"
#outpath = "D:\\"
#print(outpath)
options = webdriver.ChromeOptions() 

options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
#options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False})

isFinished = False
retryCnt = 0

while (not isFinished):
#    driver = webdriver.Chrome(options=options)
#    driver = webdriver.Chrome(executable_path='/Users/earvin/PROGRAMS/drivers/chromedriver)', options=options)
    driver = webdriver.Chrome(chrome_options=options)

    driver.get("https://goodinfo.tw/tw/index.asp")

#    elem = driver.find_element_by_id("txtStockCode")
    elem = driver.find_element(By.ID, "txtStockCode")
    elem.send_keys(stockCode)
    elem.send_keys(Keys.RETURN)

    try:
        # 這種寫法，有時侯會因為網頁載入太慢(>10秒)而失敗
        driver.implicitly_wait(10)
#        web_element = driver.find_element_by_xpath("[@id='StockDetailMenu']/table/tbody/tr/td[1]/table/tbody/tr[7]/td/a")
#        web_element = driver.find_element_by_link_text('每月營收')
        web_element = driver.find_element(By.LINK_TEXT, '每月營收')
        web_element.click()
        
        driver.implicitly_wait(15)

        #=== 變更select ===
    #    select = Select(driver.find_element_by_id('selSaleMonChartPeriod'))
    #    ele_select = driver.find_element(By.XPATH, "//*[@id='selSaleMonChartPeriod']")
    #    ele_select = driver.find_element_by_id("selSaleMonChartPeriod")
        ele_select = Select(driver.find_element(By.ID,"selSaleMonChartPeriod"))
        options = Select(ele_select).options
        time.sleep(5)
        options[2].click()
##        options.select_by_value("全部")
        time.sleep(5)

        # 這種寫法，有時侯會因為網頁載入太慢(>15秒)而失敗
    #    driver.implicitly_wait(10)
#        button = driver.find_element_by_xpath("//*[@id='divSaleMonChartDetail']/table/tbody/tr/td/input[1]")
#        button = driver.find_element_by_xpath("//input[@type='button' and @value='匯出XLS']")
#        button = driver.find_element(By.XPATH, "//*[@id='divSaleMonChartDetail']/table/tbody/tr/td/input[1]")
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
        driver.implicitly_wait(15)    
        # 關閉browser
#        driver.close()
        driver.quit()
        if retryCnt > 1:
            isFinished = True

"""
    # chrome會下載到預設路徑
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