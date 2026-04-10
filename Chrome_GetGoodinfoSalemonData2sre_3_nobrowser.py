import os
import sys
import time
import platform
from dataclasses import dataclass
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)

GOODINFO_URL = "https://goodinfo.tw/tw/index.asp"
SALEMON_FILENAME = "SaleMonDetail.xls"
LOG_FILENAME = "__errorlogSD.log"
MAX_RETRY_CNT = 3


# ------------------------------------------------------------
#  Browser 封裝
# ------------------------------------------------------------
@dataclass
class BrowserConfig:
    download_dir: str
    headless: bool = True
    page_load_timeout: int = 20
    script_timeout: int = 20


class Browser:
    def __init__(self, config: BrowserConfig):
        self.config = config
        self.driver = self._create_driver()

    def _create_driver(self) -> webdriver.Chrome:
        chrome_options = Options()

        if self.config.headless:
            # 用舊 headless，避免 new headless 被偵測
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        prefs = {
            "download.default_directory": self.config.download_dir,
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
        driver.set_page_load_timeout(self.config.page_load_timeout)
        driver.set_script_timeout(self.config.script_timeout)
        return driver

    # ---------- 基本操作 ----------

    def get(self, url: str):
        self.driver.get(url)

    def wait_visible(self, by, value, timeout=20):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )

    def wait_clickable(self, by, value, timeout=20):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def safe_click(self, xpath: str, timeout=12, retries=3) -> bool:
        for attempt in range(retries):
            try:
                elem = self.wait_clickable(By.XPATH, xpath, timeout=timeout)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", elem
                )
                self.driver.execute_script("arguments[0].click();", elem)
                return True
            except (ElementClickInterceptedException, StaleElementReferenceException):
                time.sleep(1)
            except Exception:
                time.sleep(1)
        return False

    def quit(self):
        try:
            self.driver.quit()
        except Exception:
            pass

    # ---------- 廣告 / 彈窗處理 ----------

    def close_js_alert(self):
        try:
            WebDriverWait(self.driver, 1).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except Exception:
            pass

    def hide_ads(self):
        ad_xpaths = [
            "//div[contains(@class,'fc-ab-root')]",
            "//div[@id='divPopMsg']",
            "//div[contains(@class,'modal-dialog')]",
            "//div[contains(@class,'fc-dialog-container')]",
            "//div[contains(@style,'z-index') and contains(@style,'position')]",
        ]
        for xp in ad_xpaths:
            try:
                for e in self.driver.find_elements(By.XPATH, xp):
                    self.driver.execute_script("arguments[0].style.display='none';", e)
            except Exception:
                pass

        try:
            for iframe in self.driver.find_elements(By.TAG_NAME, "iframe"):
                self.driver.execute_script("arguments[0].style.display='none';", iframe)
        except Exception:
            pass

    def close_interstitial(self):
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "ats-interstitial-button"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            self.driver.execute_script("arguments[0].click();", btn)
            print("[LOG] 成功關閉 interstitial 視窗")
        except Exception as e:
            print(f"[LOG] 找不到或無法點擊 interstitial 視窗按鈕: {e}")

    def close_iknow(self):
        try:
            if self.safe_click("//input[@value='我知道了']", timeout=3):
                print("[LOG] 關閉『我知道了』")
        except Exception:
            pass

    def clean_overlays(self):
        """
        統一做一輪「關彈窗 + 隱藏廣告」，多叫幾次也沒關係。
        """
        self.close_js_alert()
        self.close_interstitial()
        self.hide_ads()
        self.close_iknow()

    def ensure_main_page(self):
        """偵測是否被導到 REINIT，若是就重新載入首頁"""
        current = self.driver.current_url
        if "REINIT" in current:
            print("[LOG] 偵測到 REINIT，自動重新導向首頁")
            self.driver.get(GOODINFO_URL)
            time.sleep(2)
            self.clean_overlays()

# ------------------------------------------------------------
#  檔案處理
# ------------------------------------------------------------
def wait_for_download(download_path: str, timeout: int = 60) -> bool:
    for _ in range(timeout):
        if os.path.isfile(download_path):
            time.sleep(1)  # 確保寫入完成
            return True
        time.sleep(1)
    return False


# ------------------------------------------------------------
#  核心流程：處理單一股票
# ------------------------------------------------------------
def process_stock_once(
    browser: Browser,
    stock_code: str,
    destination_dir: str,
    the_date: str,
    download_dir: str,
) -> bool:
    stock_filename = f"{stock_code}-salemon-{the_date}.xls"
    target_path = os.path.join(destination_dir, stock_filename)
    download_path = os.path.join(download_dir, SALEMON_FILENAME)

    if os.path.isfile(target_path):
        print(f"{stock_filename} 已存在，跳過")
        return True

    if os.path.isfile(download_path):
        os.remove(download_path)

    # 進入首頁
    browser.get(GOODINFO_URL)
    time.sleep(3)  # 等待彈窗真正出現
    browser.clean_overlays()
    browser.ensure_main_page()

    # 找股票輸入框
    print("START GOTO 股票輸入框")
    try:
        browser.ensure_main_page()
        box = browser.wait_visible(By.ID, "txtStockCode", timeout=20)
        box.clear()
        box.send_keys(stock_code)
        box.send_keys(Keys.RETURN)
    except TimeoutException:
        print("找不到股票輸入框（Timeout）")
        return False
    except Exception as e:
        print(f"找不到股票輸入框：{e}")
        return False

    browser.clean_overlays()

    print("START GOTO 「每月營收」")
    # 點「每月營收」
    browser.ensure_main_page()
    if not browser.safe_click("//a[text()='每月營收']", timeout=20):
        print("找不到『每月營收』")
        return False

    browser.clean_overlays()

    # 點「查20年」
    print("查20年")
    browser.ensure_main_page()
    if not browser.safe_click("//input[@value='查20年']", timeout=20):
        print("查20年按鈕失敗")
        return False

    time.sleep(2)

    # 點「XLS」下載
    print("下載 XLS")
    browser.ensure_main_page()
    if not browser.safe_click("//input[@type='button' and @value='XLS']", timeout=20):
        print("XLS 按鈕失敗")
        return False

    if not wait_for_download(download_path):
        print(f"{stock_code}: 檔案未下載成功")
        return False

    try:
        os.rename(download_path, target_path)
        print(f"{stock_code}: 下載完成 → {target_path}")
        return True
    except Exception as e:
        print(f"{stock_code}: 檔案搬移失敗：{e}")
        return False


# ------------------------------------------------------------
#  Retry wrapper
# ------------------------------------------------------------
def process_stock_with_retry(
    stock_code: str,
    destination_dir: str,
    the_date: str,
    download_dir: str,
    log_file,
):
    stock_filename = f"{stock_code}-salemon-{the_date}.xls"

    for attempt in range(1, MAX_RETRY_CNT + 1):
        browser: Optional[Browser] = None
        try:
            print(f"  第 {attempt} 次嘗試：{stock_code}")
#           切換是否顯示browser
#            cfg = BrowserConfig(download_dir=download_dir, headless=True)
            cfg = BrowserConfig(download_dir=download_dir, headless=False)
            browser = Browser(cfg)

            if process_stock_once(
                browser, stock_code, destination_dir, the_date, download_dir
            ):
                return

        except Exception as e:
            msg = (
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
                f"{stock_filename} [{attempt}/{MAX_RETRY_CNT}] Error: {e}\n"
            )
            print("  ", msg.strip())
            log_file.write(msg)

        finally:
            if browser:
                browser.quit()

        time.sleep(2)

    fail_msg = (
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
        f"{stock_filename} 下載失敗（已達最大重試次數）\n"
    )
    print("  ", fail_msg.strip())
    log_file.write(fail_msg)


# ------------------------------------------------------------
#  Main
# ------------------------------------------------------------
def main():
    if len(sys.argv) < 3:
        print("參數不足：theFilename theDate")
        sys.exit(1)

    the_stocks_list = sys.argv[1]
    the_date = sys.argv[2]

    if not os.path.isfile(the_stocks_list):
        print(f"股票清單不存在：{the_stocks_list}")
        sys.exit(1)

    destination_dir = os.path.join("Data", "EXCEL", "Origin", "salemon", str(the_date))
    os.makedirs(destination_dir, exist_ok=True)

    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    with open(LOG_FILENAME, "a", encoding="utf-8") as log_file, open(
        the_stocks_list, "r", encoding="utf-8"
    ) as f:
        for process_cnt, line in enumerate(f, start=1):
            stock_code = line.strip()
            if not stock_code:
                continue
            print(f"處理第 {process_cnt} 檔：{stock_code}")
            process_stock_with_retry(
                stock_code, destination_dir, the_date, download_dir, log_file
            )


if __name__ == "__main__":
    main()