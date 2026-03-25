"""
取得Goodinfo網站「經營績效」超連結資料 (不顯示瀏灠器版本) --Enchance from Chrome_GetGoodinfoBzPerformanceData2sre_2_nobrowser.py
執行程式語法：
Syntax : python Chrome_GetGoodinfoBzPerformanceData2sre_3_nobrowser.py theStockList theDirectory theSelection
theStockList : 要處理的股票清單
theDirectory : 抓取的資料要放的目錄名稱
theSelection " 選擇的下拉選單 (0 : 獲利指標; 1 : 年增統計; 2 : PER/PBR)

<windows>
python Chrome_GetGoodinfoBzPerformanceData2sre_3_nobrowser.py STOCKS_LIST_v2.txt 2026Q1 0
<imac / linux>
python3 Chrome_GetGoodinfoBzPerformanceData2sre_3_nobrowser.py STOCKS_LIST_v2.txt 2026Q1 1
python3 Chrome_GetGoodinfoBzPerformanceData2sre_3_nobrowser.py STOCKS_LIST_test.txt 2026Q1 2
"""
import os
import sys
import time
import platform
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

class Logger:
    def __init__(self, filename="__errorlog.log"):
        self.filename = filename

    def write(self, msg):
        with open(self.filename, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} {msg}\n")

class FileHelper:
    @staticmethod
    def wait_for_file(path, timeout=40):
        for _ in range(timeout):
            if os.path.isfile(path):
                return True
            time.sleep(1)
        return False

class DriverFactory:
    @staticmethod
    def create(download_dir):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        service_path = (
            "chromedriver.exe"
            if platform.system() == "Windows"
            else "/usr/local/bin/chromedriver"
        )
        service = Service(service_path)

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(20)
        driver.set_script_timeout(20)
        return driver

class GoodinfoClient:
    BASE_URL = "https://goodinfo.tw/tw/index.asp"
    XLS_FILENAME = "BzPerformance.xls"

    def __init__(self, driver):
        self.driver = driver

    # -----------------------------
    # Ads / Popups
    # -----------------------------
    def close_ads(self):
        try:
            WebDriverWait(self.driver, 1).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except:
            pass

        ad_xpaths = [
            "//div[contains(@class,'fc-ab-root')]",
            "//div[@id='divPopMsg']",
            "//div[contains(@class,'modal-dialog')]",
            "//div[contains(@class,'fc-dialog-container')]",
            "//div[contains(@style,'z-index') and contains(@style,'position')]",
        ]
        for xp in ad_xpaths:
            for e in self.driver.find_elements(By.XPATH, xp):
                self.driver.execute_script("arguments[0].style.display='none';", e)

        for iframe in self.driver.find_elements(By.TAG_NAME, "iframe"):
            self.driver.execute_script("arguments[0].style.display='none';", iframe)

    def close_interstitial(self):
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "ats-interstitial-button"))
            )
            self.driver.execute_script("arguments[0].click();", btn)
        except:
            pass

    def close_iknow(self):
        try:
            btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='我知道了']"))
            )
            self.driver.execute_script("arguments[0].click();", btn)
        except:
            pass

    # -----------------------------
    # Core Actions
    # -----------------------------
    def load_home(self):
        self.driver.get(self.BASE_URL)
        self.close_interstitial()
        self.close_ads()
        self.close_iknow()

    def enter_stock(self, stock_code):
        box = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "txtStockCode"))
        )
        box.clear()
        box.send_keys(stock_code)
        box.send_keys(Keys.RETURN)

    def click_performance(self):
        elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'經營績效')]"))
        )
        self.driver.execute_script("arguments[0].click();", elem)

    def select_sheet(self, index):
        dropdown = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "selSheet"))
        )
        Select(dropdown).select_by_index(int(index))

    def wait_ajax(self):
        WebDriverWait(self.driver, 30).until(
            lambda d: d.find_element(By.ID, "divDetail").text.strip() != ""
        )

    def download_xls(self):
        elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='XLS']"))
        )
        self.driver.execute_script("arguments[0].click();", elem)

class StockDownloader:
    def __init__(self, destination_dir, select_option, download_dir, logger):
        self.dest_dir = destination_dir
        self.select_option = select_option
        self.download_dir = download_dir
        self.logger = logger

    def process_once(self, stock_code):
        target_filename = f"{stock_code}-bzPerformance.xls"
        target_path = os.path.join(self.dest_dir, target_filename)
        download_path = os.path.join(self.download_dir, GoodinfoClient.XLS_FILENAME)

        if os.path.isfile(target_path):
            print(f"{target_filename} 已存在，跳過")
            return True

        if os.path.isfile(download_path):
            os.remove(download_path)

        driver = DriverFactory.create(self.download_dir)
        client = GoodinfoClient(driver)

        try:
            client.load_home()
            client.enter_stock(stock_code)
            client.close_ads()
            client.click_performance()
            client.close_ads()
            client.select_sheet(self.select_option)
            time.sleep(2)
            client.wait_ajax()
            client.download_xls()

            if not FileHelper.wait_for_file(download_path):
                print(f"{stock_code}: 檔案未下載成功")
                return False

            os.rename(download_path, target_path)
            print(f"{stock_code}: 下載完成 → {target_path}")
            return True

        except Exception as e:
            self.logger.write(f"{stock_code} Error: {e}")
            return False

        finally:
            driver.quit()

class RetryManager:
    def __init__(self, downloader, max_retry=3):
        self.downloader = downloader
        self.max_retry = max_retry

    def run(self, stock_code):
        for attempt in range(1, self.max_retry + 1):
            print(f"  第 {attempt} 次嘗試：{stock_code}")
            if self.downloader.process_once(stock_code):
                return True
            time.sleep(2)

        print(f"{stock_code} 下載失敗（已達最大重試次數）")
        return False

def main():
    if len(sys.argv) < 4:
        print("參數不足：theFilename theDirectory theSelectOption")
        sys.exit(1)

    stock_list_file = sys.argv[1]
    theDirectory = sys.argv[2]
    select_option = sys.argv[3]

    if not os.path.isfile(stock_list_file):
        print(f"股票清單不存在：{stock_list_file}")
        sys.exit(1)

    dest_dir = os.path.join("Data", "EXCEL", "Origin", "bzPerformance", str(theDirectory))
    os.makedirs(dest_dir, exist_ok=True)

    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    logger = Logger()

    downloader = StockDownloader(dest_dir, select_option, download_dir, logger)
    retry = RetryManager(downloader)

    with open(stock_list_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            stock_code = line.strip()
            if not stock_code:
                continue
            print(f"處理第 {idx} 檔：{stock_code}")
            retry.run(stock_code)


if __name__ == "__main__":
    main()
