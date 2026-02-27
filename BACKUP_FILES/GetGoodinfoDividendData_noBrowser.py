"""
取得Goodinfo網站「股利政策」超連結資料
執行程式語法：
<windows>
python getGoodinfoDividendData.py STOCKS_LIST_dividend.txt 20220517
<imac / linux>
python3 getGoodinfoDividendData.py STOCKS_LIST_dividend.txt 202205

20220517-0935 01. GetGoodinfoDividendData.py 更名為 GetGoodinfoDividendDataForFirefox.py
              02. 調整輸入檔案可透過參數指定
20220520-1327 更改檔案名稱：GetGoodinfoDividendDataForFirefox -> GetGoodinfoDividendData
20220524-1941 新增個股若查無月營收相關資料，則直接查詢下一個股資料
20220526-2027 調整程式呼叫webdriver方式，只初始化一次
20240505-2147 配合網站名稱調整
"""
import os
import re
import sys
import time
import platform
import selenium.webdriver.support.ui as ui
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

if len(sys.argv) < 3 :
    print("You need input two parameter(fmt : theFilename theDate) ")
    print("syntax(windows)    : C:\python getGoodinfoDividendData.py STOCKS_LIST_dividend.txt 20220517")
    print("syntax(imac/linux) : $python3 getGoodinfoDividendData.py STOCKS_LIST_dividend.txt 20220517")
    sys.exit()

theStocksList = sys.argv[1]
print("Filename: " + theStocksList)
if not os.path.isfile(theStocksList) :
    print("股票清單不存在(" + theStocksList + ")，請檢查程式執行目錄是否存在此程式。\n")
    exit()

theDate = sys.argv[2]
maxRetryCnt = 3
processCnt = 0
dividendFilename = "DividendDetail.xls"
logFilename = "__errorlogDD.log"
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

# 20240209 Add 無界面執行 START --
#fileOptions.addArgument('--headless')
fileOptions.add_argument('--headless')
"""
prefs = {
        'profile.default_content_setting_values' :
        {
            'notifications' : 2
        }
}
fileOptions.add_experimental_option('prefs', prefs)
"""
# 20240209 -- END --

# 設定檔案存取路徑
destination_dir = os.path.join("Data", "EXCEL", "Origin", "dividend", str(theDate))
if platform.system() == "Windows" :
    destination_dir += "\\"
else :
    destination_dir += "/"
print("Destination DIR: " + destination_dir)

# For imac / linux; windows needs other style
# For linux, need put geckodriver in /usr/bin first
service = null
if not platform.system() == "Windows" :
    service = Service('geckodriver')

# 判斷何種作業系統(windows OS不需要使用service object)
driver = null
if platform.system() == "Windows" :    
    driver = webdriver.Firefox(options = fileOptions)
else :
#    driver = webdriver.Chrome(service = service, options = fileOptions)
    driver = webdriver.Firefox(service = service, options = fileOptions)

f = open(theStocksList, 'r')
lines = f.readlines()
for line in lines:
    processCnt += 1
    stockCode = line.rstrip()
    print("Processing StockNo (" + str(processCnt) + ") = " + stockCode)
    stockFilename = stockCode + "-dividend-" + theDate + ".xls"

    isFinished = False
    retryCnt = 0

    while (not isFinished):
        # 先檢查要抓的資料是否已經存在，若存在則跳
        if os.path.isfile(destination_dir + stockFilename) :
            print("檔案已存在!!")
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " is exist.\n")
            isFinished = True
#            continue
            break
#       20220527-1704 Add
#        wait = ui.WebDriverWait(driver, 5)

        driver.get("https://goodinfo.tw/tw/index.asp")

        elem = driver.find_element(By.ID, "txtStockCode")
        elem.send_keys(stockCode)
        elem.send_keys(Keys.RETURN)

        try:
            # 這種寫法，有時侯會因為網頁載入太慢(>10秒)而失敗
#            driver.implicitly_wait(10)
            time.sleep(5)


            web_element = driver.find_element(By.LINK_TEXT, '股利政策')
            web_element.click()
#            driver.implicitly_wait(15)
            time.sleep(5)

        #   捲動scrollbar
            js = "var q=document.documentElement.scrollTop=1500"
            driver.execute_script(js)
            time.sleep(5)

#           20220524-1704 Add
#            driver.until(lambda driver: driver.find_element(By.XPATH, "//input[@type='button' and @value='匯出XLS']"))

#20240505   配合網站名稱調整
#            button = driver.find_element(By.XPATH, "//input[@type='button' and @value='匯出XLS']")
            button = driver.find_element(By.XPATH, "//input[@type='button' and @value='XLS']")
            driver.execute_script("arguments[0].click();", button)
        
            isFinished = True

        except EC.NoSuchElementException as err0 :
#           (ErrNo:-2147012894) �瀅��暹�   
#           Unable to locate element: 股利政策         
            print(err0.msg)
            isFinished = True
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(err0) + " excption.\n")

        except BaseException as err1 :
            print(err1)
            retryCnt += 1
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " excption.\n")

        finally:
            time.sleep(10)

            if retryCnt > 2 :
                isFinished = True

        if os.path.isfile(dividendFilename) :
#            os.rename(dividendFilename, stockFilename)
            os.rename(dividendFilename, destination_dir + stockFilename)
            isFinished = True
        else :
            if retryCnt >= maxRetryCnt :
                logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " failure.\n")

# 關閉browser
driver.close()
logFile.close()
f.close()



