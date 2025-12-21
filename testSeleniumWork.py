"""
測試Seleinum是否可正常運作

執行程式語法：
<windows>
python testSeleniumWork.py www.google.com
<imac / linux>
python3 testSeleniumWork.py www.google.com
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

print("END!!!!")

# 關閉browser
driver.close()
