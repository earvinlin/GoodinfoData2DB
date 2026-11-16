import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

# 啟動防偵測的 Chrome
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

driver = uc.Chrome(options=options)

try:
    # 進入 Goodinfo 股利政策頁面 (以台積電2330為例)
    url = "https://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID=2330"
    driver.get(url)

    # 等待頁面載入完成
    time.sleep(3)

    # 取得完整 HTML
    html = driver.page_source

    # 用 BeautifulSoup 解析
    soup = BeautifulSoup(html, "html.parser")

    # 找到主要表格 (class 名稱可能會變動，需依實際情況調整)
    table = soup.find("table", {"class": "solid_1_padding_4_0_tbl"})

    # 輸出表格內容
    for row in table.find_all("tr"):
        cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
        print(cells)

finally:
    driver.quit()
