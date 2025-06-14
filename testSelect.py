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


fileOptions=Options()
fileOptions.set_preference("browser.download.folderList", 2)
fileOptions.set_preference("browser.download.manager.showWhenStarting", False)
fileOptions.set_preference("browser.download.dir", os.getcwd())
fileOptions.set_preference('browser.helperApps.neverAsk.saveToDisk', \
    'text/csv,application/x-msexcel,application/excel,application/x-excel,\
    application/vnd.ms-excel,image/png,image/jpeg,text/html,text/plain,\
    application/msword,application/xml')
fileOptions.binary_location =r"/usr/bin/firefox"
#fileOptions.binary_location =r"/snap/bin/firefox"


driver = webdriver.Firefox(options = fileOptions)

# 進入百度高階搜尋頁
driver.get("http://tieba.baidu.com/f/search/adv")

# 獲取select下拉框的元素
ele_select = driver.find_element_by_css_selector("select[name='sm']")

# 獲取下拉框中所有選項元素（element）
options = Select(ele_select).options
print("所有選項元素的列表：%s" % options)
for i in options:
    print("元素對應的選項：%s"% i.text)

# 獲取下拉框當前顯示(選中)的元素(element)
options_selected = Select(ele_select).all_selected_options
print("-----------------------分隔符---------------------------")
print(options_selected)
for j in options_selected:
    print("當前選中的選項(預設項)：%s" % j.text)

# 選擇value值為2的選項
Select(ele_select).select_by_value("2")
sleep(1)

# 輸出預設項(當前選中項）
now = Select(ele_select).first_selected_option
print(now.text)
