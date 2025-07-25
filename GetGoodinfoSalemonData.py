"""
取得Goodinfo網站「每月營收」超連結資料
執行程式語法：
<windows>
python GetGoodinfoSalemonData.py STOCKS_LIST_salemon.txt 20240311
<imac / linux>
python3 GetGoodinfoSalemonData.py STOCKS_LIST_salemon.txt 20220517

20220517-0935 01. GetGoodinfoSalemonDataV3ForFirefox.py 更名為 GetGoodinfoSalemonDataForFirefox.py
              02. 調整輸入檔案可透過參數指定
20220518-0901 程式碼微調及確認程式可運作
20220519-2235 修正可於linux上執行(需把geckodriver 複製至 /usr/bin 下)
20220520-1327 更改檔案名稱：GetGoodinfoSalemonDataForFirefox -> GetGoodinfoSalemonData
20220524-1146 新增個股若查無月營收相關資料，則直接查詢下一個股資料
20220526-2027 調整程式呼叫webdriver方式，只初始化一次
20240512-2005 修正firefox執行路徑及在hpnb上的vmubuntu22不需要service參數
20240712-1243 配合網頁調整修正資料取得方式
20250714-2100 新增macos firefox啟動路徑
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
    print("You need input two parameter(fmt : theFilename theDate) ")
    print("syntax(windows)    : C:\python GetGoodinfoSalemonData.py STOCKS_LIST_salemon.txt 20220517")
    print("syntax(imac/linux) : $python3 GetGoodinfoSalemonData.py STOCKS_LIST_salemon.txt 20220517")
    sys.exit()

theStocksList = sys.argv[1]
print("Filename: " + theStocksList)
if not os.path.isfile(theStocksList) :
    print("股票清單不存在(" + theStocksList + ")，請檢查程式執行目錄是否存在此程式。\n")
    exit()

theDate = sys.argv[2]
maxRetryCnt = 3
processCnt = 0
saleMonFilename = "SaleMonDetail.xls"
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
#if platform.system() == "Windows" :
#    destination_dir += "\\"
#    # 20240512 Add
#    fileOptions.binary_location =r"C:/Program Files/Mozilla Firefox/firefox.exe"
#else :
#    destination_dir += "/"
#    # 20240512 Add
#    fileOptions.binary_location =r"/usr/bin/firefox"
if platform.system() == "Windows" :
    destination_dir += "\\"
    # 20240505 Add
    fileOptions.binary_location =r"C:/Program Files/Mozilla Firefox/firefox.exe"
elif platform.system() ==  "linux" :
    destination_dir += "/"
    # 20240505 Add
    fileOptions.binary_location =r"/usr/bin/firefox"
# 20250714 新增macos firefox啟動路徑
else :
    destination_dir += "/"
    fileOptions.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox" 

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
# 20240512 在hpnb上的vmubuntu22不需要service參數
#    driver = webdriver.Firefox(service = service, options = fileOptions)
    driver = webdriver.Firefox(options = fileOptions)

f = open(theStocksList, 'r')
lines = f.readlines()
for line in lines:
    processCnt += 1
    stockCode = line.rstrip()
    print("Processing StockNo (" + str(processCnt) + ") = " + stockCode)
    stockFilename = stockCode + "-salemon-" + theDate + ".xls"

    isFinished = False
    retryCnt = 0

    while (not isFinished):
        # 先檢查要抓的資料是否已經存在，若存在則跳
#        if os.path.isfile(stockFilename) :
        if os.path.isfile(destination_dir + stockFilename) :
            print("檔案已存在!!")
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " is exist.\n")
            isFinished = True
#            continue
            break

        try:
            driver.get("https://goodinfo.tw/tw/index.asp")

            elem = driver.find_element(By.ID, "txtStockCode")
            elem.send_keys(stockCode)
            elem.send_keys(Keys.RETURN)

            # 這種寫法，有時侯會因為網頁載入太慢(>10秒)而失敗
#            driver.implicitly_wait(10)
            time.sleep(8)

            web_element = driver.find_element(By.LINK_TEXT, '每月營收')
            web_element.click()
#            driver.implicitly_wait(15)
            time.sleep(7)

            # 若查無月營收相關資料，則直接查詢下一個股資料
            elem_notfound = driver.find_element(By.ID, "divSaleMonChartDetail")
            if elem_notfound.text == "查無月營收相關資料!!" :
                print("查無月營收相關資料!!")
                isFinished = True
                break

# 20240712  網頁又有調整
#            elem_select = driver.find_element(By.ID, "selSaleMonChartPeriod")
#            selectOptions = Select(elem_select).options
#            time.sleep(5)

# 20241009 網頁又有調整 (不用再查詢，使用預設資料集)
#            button0 = driver.find_element(By.XPATH, "//input[@type='button' and @value='查20年']")
#            driver.execute_script("arguments[0].click();", button0)
#            time.sleep(10)

        #   捲動scrollbar
            js = "var q=document.documentElement.scrollTop=1500"
            driver.execute_script(js)
            time.sleep(5)

#           options.select_by_value("全部") -- 未測試是否可用…
#            selectOptions[2].click()
#            time.sleep(8)

# 20240315  配合網頁調整修正資料取得方式
#            button = driver.find_element(By.XPATH, "//input[@type='button' and @value='匯出XLS']")
            button = driver.find_element(By.XPATH, "//input[@type='button' and @value='XLS']")
            driver.execute_script("arguments[0].click();", button)
        
            isFinished = True

#        except EC.NoSuchElementException as err0 :
#            print(err0)
#            retryCnt += 1
#            isFinished = True
#            logFile.write(print(f"Unexpected {err0=}, {type(err0)=}"))

        except BaseException as err1 :
            retryCnt += 1
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " excption.\n")
#            logFile.write(print(f"Unexpected {err1=}, {type(err1)=}"))

        finally:
            time.sleep(10)

            if retryCnt > 2:
                isFinished = True

        if os.path.isfile(saleMonFilename):
            os.rename(saleMonFilename, destination_dir + stockFilename)
            isFinished = True
        else:
            if retryCnt >= maxRetryCnt:
                logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " failure.\n")

# 關閉browser
driver.close()
logFile.close()
f.close()
