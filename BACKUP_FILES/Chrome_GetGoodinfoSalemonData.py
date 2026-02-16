"""
取得 Goodinfo 網站「每月營收」超連結資料
{ 本版本為舊版，請改用最新版 Chrome_GetGoodinfoSalemonData2sre.py }

執行語法：
<windows>
python Chrome_GetGoodinfoSalemonData2.py STOCKS_LIST_salemon.txt 202601
<imac / linux>
python3 Chrome_GetGoodinfoSalemonData2.py STOCKS_LIST_salemon.txt 202601
"""
import os
import sys
import time
import platform
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 檢查參數
if len(sys.argv) < 3:
    print("請輸入兩個參數：股票清單檔案 與 日期")
    print("範例：python3 GetGoodinfoSalemonData.py STOCKS_LIST_salemon.txt 20220517")
    sys.exit()

theStocksList = sys.argv[1]
theDate = sys.argv[2]

if not os.path.isfile(theStocksList):
    print(f"股票清單不存在({theStocksList})，請檢查檔案路徑。")
    sys.exit()

# 設定儲存路徑
destination_dir = os.path.join("Data", "EXCEL", "Origin", "salemon", str(theDate))
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

# 如果需要背景執行，可加上 headless 模式
# chrome_options.add_argument("--headless")

# 設定 ChromeDriver 路徑（請確認已安裝 chromedriver）
# Windows放在執行python的目錄
# Mac / Linux放在 /usr/local/bin的目錄
if platform.system() == "Windows":
    service = Service("chromedriver.exe")
else:
    service = Service("/usr/local/bin/chromedriver")  # Mac/Linux

# 啟動 Chrome (Chrome需使用版本143之後)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 讀取股票清單
with open(theStocksList, "r", encoding="utf-8") as f:
    stock_list = [line.strip() for line in f if line.strip()]

print(f"共讀取 {len(stock_list)} 個股票代碼")

maxRetryCnt = 3
saleMonFilename = "SaleMonDetail.xls"

for idx, stockCode in enumerate(stock_list, start=1):
    print(f"\n處理第 {idx} 個股票代碼：{stockCode}")
    stockFilename = f"{stockCode}-salemon-{theDate}.xls"
    file_path = os.path.join(destination_dir, stockFilename)

    if os.path.isfile(file_path):
        print("檔案已存在，略過。")
        continue

    retryCnt = 0
    isFinished = False

    while not isFinished and retryCnt < maxRetryCnt:
        try:
            driver.get("https://goodinfo.tw/tw/index.asp")

            # 輸入股票代碼
            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "txtStockCode"))
            )
            elem.clear()
            elem.send_keys(stockCode)
            elem.send_keys(Keys.RETURN)
            
            time.sleep(3)
            
            # 點擊「每月營收」
            salemon_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "每月營收"))
            )
            salemon_link.click()
            time.sleep(5)

            # 檢查是否有「查無月營收相關資料」
            try:
                elem_notfound = driver.find_element(By.ID, "divSaleMonChartDetail")
                if "查無月營收相關資料" in elem_notfound.text:
                    print("查無月營收相關資料!!")
                    isFinished = True
                    break
            except:
                pass

            # 捲動頁面，確保按鈕可見
            driver.execute_script("window.scrollTo(0, 1500);")
#            time.sleep(2)

            # 點擊「匯出 XLS」按鈕
            download_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and @value='XLS']"))
            )
            driver.execute_script("arguments[0].click();", download_btn)
            print(f"已點擊下載 Excel：{stockCode}")

            # 等待檔案下載完成
            time.sleep(8)

            # 找到最新下載的檔案並重新命名
            files = os.listdir(download_dir)
            if files:
                latest_file = max([os.path.join(download_dir, f) for f in files], key=os.path.getctime)
                shutil.move(latest_file, file_path)
                print(f"檔案已移動到：{file_path}")
                isFinished = True

        except Exception as e:
            retryCnt += 1
            print(f"錯誤：{e}，重試第 {retryCnt} 次...")
            time.sleep(5)

    if not isFinished:
        print(f"❌ 無法取得 {stockCode} 的資料，已達最大重試次數")

driver.quit()
