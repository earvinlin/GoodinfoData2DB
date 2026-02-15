"""
測試Seleinum是否可正常運作

執行程式語法：
<windows>
python testSeleniumWork.py www.google.com
<imac / linux>
python3 testSeleniumWork.py www.google.com
"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 啟動 Chrome
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # 如果需要無頭模式可取消註解
driver = webdriver.Chrome(options=options)

# 目標網址
url = "https://goodinfo.tw/tw/StockDetail.asp"

# 股票代碼
stock_code = "1216"

# 最大重試次數
max_retries = 3
retry_count = 0

while retry_count < max_retries:
    try:
        print(f"嘗試載入網頁，第 {retry_count + 1} 次...")
        driver.get(url)

        # 檢查是否載入錯誤頁面
        page_source = driver.page_source
        if "ASP 0115" in page_source or "ASP 0240" in page_source:
            print("伺服器錯誤，稍後重試...")
            retry_count += 1
            time.sleep(5)
            continue

        # 如果有 iframe，先切換
        try:
            driver.switch_to.frame("frmMain")  # 假設 iframe 名稱是 frmMain，請依實際 HTML 修改
        except:
            print("沒有 iframe 或名稱不同，略過切換")

        # 顯式等待輸入框出現
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtStockCode"))
        )

        # 輸入股票代碼
        elem.clear()
        elem.send_keys(stock_code)

        # 點擊查詢按鈕
        search_btn = driver.find_element(By.ID, "btnStockSearch")
        search_btn.click()

        print("股票代碼輸入完成並送出查詢")
        break  # 成功後跳出迴圈

    except Exception as e:
        print(f"發生錯誤: {e}")
        retry_count += 1
        time.sleep(5)

if retry_count == max_retries:
    print("重試次數已達上限，請檢查網頁或伺服器狀態")





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
if len(sys.argv) < 1 :
    print("You need input one parameter(fmt : theAddress) ")
    print("syntax(windows)    : C:\\python testSeleniumWork.py https://www.google.com ")
    print("syntax(imac/linux) : $python3 testSeleniumWork.py www.google.com ")
    sys.exit()
theAddress = sys.argv[1]
print("Browse address: " + theAddress)
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

if platform.system() == "Windows" :
    fileOptions.binary_location =r"C:/Program Files/Mozilla Firefox/firefox.exe"
# 20250824 更改字串 linux 為 Linux
elif platform.system() ==  "Linux" :
    fileOptions.binary_location =r"/usr/bin/firefox"
# 20250714 新增macos firefox啟動路徑
else :
    fileOptions.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox" 
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
# 20240512 在hpnb上的vmubuntu22不需要service參數
#    driver = webdriver.Firefox(service = service, options = fileOptions)
    driver = webdriver.Firefox(options = fileOptions)
#driver.get("https://www.google.com")
driver.get(theAddress)
print(driver.current_url)
print(driver.page_source[:1000])  # 顯示前 100

print("END!!!!")
# 關閉browser
driver.close()

"""