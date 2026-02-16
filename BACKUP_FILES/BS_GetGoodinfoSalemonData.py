"""
BS_GetGoodinfoSalemonData 的 Docstring
BeautifulSoup 
"""
import os
import sys
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

if len(sys.argv) < 3:
    print("請輸入兩個參數：股票清單檔案 與 日期")
    print("範例：python3 GetGoodinfoSalemonData.py STOCKS_LIST_salemon.txt 20220517")
    sys.exit()

# 讀取參數
stocks_file = sys.argv[1]
the_date = sys.argv[2]

if not os.path.isfile(stocks_file):
    print(f"股票清單不存在({stocks_file})，請檢查檔案路徑。")
    sys.exit()

# 設定儲存路徑
destination_dir = os.path.join("Data", "EXCEL", "Origin", "salemon", str(the_date))
os.makedirs(destination_dir, exist_ok=True)
print(f"儲存資料夾：{destination_dir}")

# 讀取股票代碼清單
with open(stocks_file, "r", encoding="utf-8") as f:
    stock_list = [line.strip() for line in f if line.strip()]

print(f"共讀取 {len(stock_list)} 個股票代碼")

# Goodinfo 每月營收頁面 URL 模板
# base_url = "https://goodinfo.tw/tw/StockBzPerformance.asp?STOCK_ID={}"
base_url = "https://goodinfo.tw/tw/ShowSaleMonChart.asp?STOCK_ID={}"

# 設定 headers 模擬瀏覽器
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for idx, stock_code in enumerate(stock_list, start=1):
    print(f"\n處理第 {idx} 個股票代碼：{stock_code}")
    stock_filename = f"{stock_code}-salemon-{the_date}.xlsx"
    file_path = os.path.join(destination_dir, stock_filename)

    # 如果檔案已存在，跳過
    if os.path.isfile(file_path):
        print("檔案已存在，略過。")
        continue

    try:
        # 發送請求
        url = base_url.format(stock_code)
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"

        if response.status_code != 200:
            print(f"無法取得資料，HTTP狀態碼：{response.status_code}")
            continue

        # 解析 HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # 找到「每月營收」資料表
        table = soup.find("table", class_="b1 p4_2 r10")  # Goodinfo 的表格 class
        if not table:
            print("查無月營收相關資料!!")
            continue

        # 解析表格資料
        rows = table.find_all("tr")
        data = []
        headers_row = [th.text.strip() for th in rows[0].find_all("td")]
        for row in rows[1:]:
            cols = [td.text.strip() for td in row.find_all("td")]
            if cols:
                data.append(cols)

        # 存成 Excel
        df = pd.DataFrame(data, columns=headers_row)
        df.to_excel(file_path, index=False)
        print(f"已儲存：{file_path}")

        time.sleep(2)  # 避免過快請求被封鎖

    except Exception as e:
        print(f"處理 {stock_code} 時發生錯誤：{e}")
        continue

print("\n✅ 批次處理完成！")

