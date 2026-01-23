"""
取得Goodinfo網站「股利政策」超連結資料
執行程式語法：
<windows>
python Chrome_GetGoodinfoDividendData2.py STOCKS_LIST_dividend.txt 20250712 1 2
<imac / linux>
python3 Chrome_GetGoodinfoDividendData2.py STOCKS_LIST_dividend.txt 20250712 1 2

20260121 Copy from getGoodinfoDividendData2.py，改用chrome抓資料
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
#from selenium.webdriver.firefox.service import Service
#from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


maxRetryCnt = 3
processCnt = 0
dividendFilename = "DividendDetail.xls"
logFilename = "__errorlogDD.log"
logFile = open(logFilename, "a")

"""
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

# 目錄名稱(通常我都以執行程式日期命名)
theDate = sys.argv[2]
# 選擇項目：「股利政策(發放年度)」= 0、「股利政策(所屬年度)」= 1、「除權息日程」= 2
theSelectOption = sys.argv[3]
# 選擇子項目：「股利政策(發放年度)」= 0、「股利政策(所屬年度)」= 1 下，會有另一個選擇項目可選擇
theSelectOption2 = ""
if theSelectOption != "2" :
    theSelectOption2 = sys.argv[4]

print("theStocksList= ", theStocksList, ", theDate= ", theDate, ", theSelectOption= ", theSelectOption, ", theSelectOption2= ", theSelectOption2)

# 設定儲存路徑
destination_dir = os.path.join("Data", "EXCEL", "Origin", "dividend", str(theDate))
os.makedirs(destination_dir, exist_ok=True)
print("Destination DIR:", destination_dir)

# 暫存下載資料夾
download_dir = os.path.join(os.getcwd(), "downloads")
print("Download DIR:", download_dir)
os.makedirs(download_dir, exist_ok=True)

# 設定 Chrome 選項
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--start-maximized")

print("OS is: ", platform.system())

# 設定 ChromeDriver 路徑（請確認已安裝 chromedriver）
# Windows放在執行python的目錄
# Mac / Linux放在 /usr/local/bin的目錄
if platform.system() == "Windows":
    service = Service("chromedriver.exe")
else:
    service = Service("/usr/local/bin/chromedriver")  # Mac/Linux

# 啟動 Chrome (Chrome需使用版本143之後)
driver = webdriver.Chrome(service=service, options=chrome_options)

print("Destination DIR: " + destination_dir)



### 下面都還沒改 ###

# 讀取股票清單
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
#    driver.get("https://goodinfo.tw/tw/index.asp")
#    time.sleep(8)

    while (not isFinished):
        # 先檢查要抓的資料是否已經存在，若存在則跳
#        if os.path.isfile(destination_dir + stockFilename) :
#            print("檔案已存在!!")
#            logFile.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " " + stockFilename + " is exist.\n")
#            isFinished = True
#            break

        try :
            driver.get("https://goodinfo.tw/tw/index.asp")
            time.sleep(7)
            driver.execute_script("document.getElementById('ats-interstitial-container').remove();")
            
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



