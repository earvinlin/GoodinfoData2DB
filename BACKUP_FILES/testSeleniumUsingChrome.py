import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 設定下載路徑（暫存資料夾）
download_dir = os.path.join(os.getcwd(), "downloads")
os.makedirs(download_dir, exist_ok=True)

# 設定目標資料夾
destination_dir = "Data/EXCEL/Origin/bzPerformance/test/"
os.makedirs(destination_dir, exist_ok=True)

# 設定 Chrome 下載選項
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,  # 自動下載到指定資料夾
    "download.prompt_for_download": False,       # 不顯示下載提示
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)

# 目標網址
url = "https://goodinfo.tw/tw/StockDetail.asp"
stock_code = "1101"

try:
    driver.get(url)

    # 切換 iframe（如果有）
    try:
        driver.switch_to.frame("frmMain")
    except:
        print("沒有 iframe，略過切換")

    # 等待輸入框出現
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

    # 等待下載按鈕出現並點擊
    download_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'匯出Excel')]"))
    )
    download_btn.click()
    print("已點擊下載 Excel")

    # 等待檔案下載完成
    time.sleep(5)  # 可改成檢查檔案是否存在

    # 找到最新下載的檔案
    files = os.listdir(download_dir)
    if files:
        latest_file = max([os.path.join(download_dir, f) for f in files], key=os.path.getctime)
        print(f"下載完成：{latest_file}")

        # 移動檔案到目標資料夾
        shutil.move(latest_file, os.path.join(destination_dir, os.path.basename(latest_file)))
        print(f"檔案已移動到：{destination_dir}")

except Exception as e:
    print(f"發生錯誤: {e}")

finally:
    driver.close()