from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep

# 開啟Chrome瀏覽器
driver = webdriver.Chrome()

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
