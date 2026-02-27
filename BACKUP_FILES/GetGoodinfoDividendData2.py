"""
取得Goodinfo網站「股利政策」超連結資料
執行程式語法：
<windows>
python getGoodinfoDividendData2.py STOCKS_LIST_dividend.txt 20250712 1 2
<imac / linux>
python3 getGoodinfoDividendData2.py STOCKS_LIST_dividend.txt 20250712 1 2

20250711-0818 配合該網頁改版，新增抓取「所屬年度」資料
20250918-0801 配合「股利政策」頁面改版，調整程式
"""
import os
import re
import sys
import time
import platform
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.ui import Select
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

"""
20250918
arg[2] : 選擇項目：「股利政策(發放年度)」= 0、「股利政策(所屬年度)」= 1、「除權息日程」= 2
arg[3] : 
    when arg[2] == 0 or 1
        第2選擇項目：
        現金殖利率(=0)、股票殖利率(=1)、現金+股票殖利率(=2)、除權/息價殖利率(=3)、
        年均價殖利率(=4)、成交價殖利率(=5)、盈餘分配率(=6)
note: arg[2] = 2 無子選項
"""
if len(sys.argv) < 4 :
    print("You need input three parameter(fmt : theFilename theDate theSelectOption theSelectOption2) ")
    print("syntax(windows)    : C:\python getGoodinfoDividendData.py STOCKS_LIST_dividend.txt 202509POD 1 2")
    print("syntax(imac/linux) : $ python3 getGoodinfoDividendData.py STOCKS_LIST_dividend.txt 202509POD 1 2")
    sys.exit()

theStocksList = sys.argv[1]
print("Filename: " + theStocksList)
if not os.path.isfile(theStocksList) :
    print("股票清單不存在(" + theStocksList + ")，請檢查程式執行目錄是否存在此程式。\n")
    exit()

theDate = sys.argv[2]
# 選擇項目：「股利政策(發放年度)」= 0、「股利政策(所屬年度)」= 1、「除權息日程」= 2
theSelectOption = sys.argv[3]
# 20250918 選擇項目：「股利政策(發放年度)」= 0、「股利政策(所屬年度)」= 1 下，會有另一個選擇項目可選擇
theSelectOption2 = ""
if theSelectOption != "2" :
    theSelectOption2 = sys.argv[4]

print("theStocksList= ", theStocksList, ", theDate= ", theDate, ", theSelectOption= ", theSelectOption, ", theSelectOption2= ", theSelectOption2)

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

# 設定檔案存取路徑
destination_dir = os.path.join("Data", "EXCEL", "Origin", "dividend", str(theDate))

print("OS is: ", platform.system())
if platform.system() == "Windows" :
    destination_dir += "\\"
    # 20240505 Add
    fileOptions.binary_location =r"C:/Program Files/Mozilla Firefox/firefox.exe"
elif platform.system() ==  "Linux" :
    destination_dir += "/"
    # 20240505 Add
    fileOptions.binary_location =r"/usr/bin/firefox"
# 20250708 macos要設定firefox啟動路徑
else :
    destination_dir += "/"
    fileOptions.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox" 

print("Destination DIR: " + destination_dir)

# For imac / linux; windows needs other style
# For linux, need put geckodriver in /usr/bin first
service = null
# Linux /MacNB OS
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

#   20250531 移到迴圈外，以結省時間
    driver.get("https://goodinfo.tw/tw/index.asp")
    time.sleep(8)

    while (not isFinished):
        # 先檢查要抓的資料是否已經存在，若存在則跳
        if os.path.isfile(destination_dir + stockFilename) :
            print("檔案已存在!!")
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " is exist.\n")
            isFinished = True
            break

        try :
            elem = driver.find_element(By.ID, "txtStockCode")
            elem.send_keys(stockCode)
            elem.send_keys(Keys.RETURN)

            # 這種寫法，有時侯會因為網頁載入太慢(>10秒)而失敗
#            driver.implicitly_wait(10)
            time.sleep(7)

            web_element = driver.find_element(By.LINK_TEXT, '股利政策')
            web_element.click()
#            driver.implicitly_wait(15)
            time.sleep(7)

        #   捲動scrollbar
            js = "var q=document.documentElement.scrollTop=1500"
            driver.execute_script(js)
            time.sleep(5)
  
        #   項目：elementId="selSheet" -> 「股利發放年度」、「股利所屬年度」、「除權息日程」3項目
            dropdown = driver.find_element(By.ID, "selSheet")
            # 建立 Select 物件
            select = Select(dropdown)

            # 選擇項目：「股利政策(發放年度)」= 0、「股利政策(所屬年度)」= 1、「除權息日程」= 2
            select.select_by_index(theSelectOption) # 依索引（從 0 開始）
#            select.select_by_value("股利所屬年度") # 依 value 屬性
#            select.select_by_visible_text("股利政策(所屬年度)")    # 依顯示文字
            time.sleep(8)

            option_list = select.options
            selected_option = select.first_selected_option
            selected_item = selected_option.text

        #   20250918 「股利發放年度」、「股利所屬年度」會有第2個選項可供選擇
            if theSelectOption == "0" or theSelectOption == "1" :
                dropdown2 = driver.find_element(By.ID, "selSheet2")
                select2 = Select(dropdown2)
                select2.select_by_index(theSelectOption2)
                option_list = select2.options
                selected_option = select2.first_selected_option
                print("目前選中的項目是：", selected_item, ", 子項目是：", selected_option.text)
            else :
                print("目前選中的項目是：", selected_item)

#           --- END ---

            time.sleep(8)

            button = driver.find_element(By.XPATH, "//input[@type='button' and @value='XLS']")
            driver.execute_script("arguments[0].click();", button)
        
            isFinished = True

        except EC.NoSuchElementException as err0 :
#           Unable to locate element: 股利政策         
            print(err0.msg)
            isFinished = True
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(err0) + " excption.\n")

        except BaseException as err1 :
            print(err1)
            retryCnt += 1
            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " excption.\n")

        finally:
            time.sleep(8)

            if retryCnt > 2 :
                isFinished = True

        if os.path.isfile(dividendFilename) :
            os.rename(dividendFilename, destination_dir + stockFilename)
            isFinished = True
        else :
            if retryCnt >= maxRetryCnt :
                logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " " + str(retryCnt) + " failure.\n")

# 關閉browser
driver.close()
logFile.close()
f.close()



