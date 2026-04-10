import os
import sys
import time
from playwright.sync_api import sync_playwright

GOODINFO_URL = "https://goodinfo.tw/tw/index.asp"
LOG_FILENAME = "__errorlogSD.log"
MAX_RETRY_CNT = 3


def apply_stealth(page):
    # 手動做幾個常見 anti-bot patch
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

        window.chrome = {
            runtime: {},
        };

        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3],
        });

        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-TW', 'zh', 'en-US', 'en'],
        });
    """)


def create_browser():
    p = sync_playwright().start()
    browser = p.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-gpu",
            "--disable-software-rasterizer",
        ],
    )
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    apply_stealth(page)
    return p, browser, context, page


def wait_for_selector(page, selector, timeout=15000):
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except:
        return False


def process_stock_once(page, stock_code, destination_dir, the_date):
    stock_filename = f"{stock_code}-salemon-{the_date}.xls"
    target_path = os.path.join(destination_dir, stock_filename)

    # 進首頁（不要用 networkidle）
    page.goto(GOODINFO_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(1500)

    # 等股票輸入框
    if not wait_for_selector(page, "#txtStockCode", timeout=15000):
        print("找不到股票輸入框")
        return False

    page.fill("#txtStockCode", stock_code)
    page.keyboard.press("Enter")

    # 等「每月營收」
    if not wait_for_selector(page, "text=每月營收", timeout=20000):
        print("找不到『每月營收』")
        return False

    page.click("text=每月營收")

    # 查20年
    if not wait_for_selector(page, "input[value='查20年']", timeout=20000):
        print("查20年按鈕失敗")
        return False

    page.click("input[value='查20年']")

    # XLS
    if not wait_for_selector(page, "input[value='XLS']", timeout=20000):
        print("XLS 按鈕失敗")
        return False

    with page.expect_download() as download_info:
        page.click("input[value='XLS']")

    download = download_info.value
    download.save_as(target_path)

    print(f"{stock_code}: 下載完成 → {target_path}")
    return True


def process_stock_with_retry(stock_code, destination_dir, the_date, log_file):
    for attempt in range(1, MAX_RETRY_CNT + 1):
        print(f"第 {attempt} 次嘗試：{stock_code}")
        p, browser, context, page = create_browser()
        try:
            if process_stock_once(page, stock_code, destination_dir, the_date):
                browser.close()
                p.stop()
                return
        except Exception as e:
            msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {stock_code} Error: {e}\n"
            print(msg.strip())
            log_file.write(msg)
        finally:
            browser.close()
            p.stop()
        time.sleep(2)

    print(f"{stock_code} 下載失敗（已達最大重試次數）")


def main():
    if len(sys.argv) < 3:
        print("參數不足：theFilename theDate")
        sys.exit(1)

    the_stocks_list = sys.argv[1]
    the_date = sys.argv[2]

    destination_dir = os.path.join("Data", "EXCEL", "Origin", "salemon", str(the_date))
    os.makedirs(destination_dir, exist_ok=True)

    with open(LOG_FILENAME, "a", encoding="utf-8") as log_file, open(
        the_stocks_list, "r", encoding="utf-8"
    ) as f:
        for line in f:
            stock_code = line.strip()
            if stock_code:
                process_stock_with_retry(stock_code, destination_dir, the_date, log_file)


if __name__ == "__main__":
    main()