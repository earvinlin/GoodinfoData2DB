"""
讀取 Excel，產生 SQL insert 語法
table: stocks_dividend_CAS_dividend_yield
CMD : python3 GenFileInsertCmd_v2.py theTableName theDirectoryPath
Example :
(mac) python3 GenFileInsertCmd_v2.py stocks_dividend_CAS_dividend_yield /Users/earvin/workspaces/GithubProjects/GoodinfoData2DB/Data/EXCEL/Transfer/dividend/test/
"""

import sys
import os
import pandas as pd

def clean_value(val):
    """將 NaN 轉成空字串，並去除前後空白與單引號"""
    if pd.isna(val):
        return ""
    return str(val).strip().replace("'", "")

def process_file(table_name, directory, file_name, f):
    """處理單一 Excel 檔案，產生 insert SQL，並回傳處理筆數"""
    stock_no = file_name[:4]
    sheet_name = file_name.rsplit(".", 1)[0]
#    print("file_name:", file_name, "sheet_name:", sheet_name)

    df = pd.read_excel(os.path.join(directory, file_name), sheet_name=sheet_name, 
                       header=None, engine="openpyxl")
    rows, cols = df.shape
#    print("rows:", rows, "cols:", cols)

    last_process_year = ""
    record_count = 0  # 記錄處理筆數

    for j in range(4, rows-1):
        process_year = clean_value(df.iloc[j, 0])

        # 判斷是否為數值
        try:
            float(process_year)
            is_numeric = True
        except (ValueError, TypeError):
            is_numeric = False

        values_list = [stock_no]
        if is_numeric:
            # 年度行
            for k in range(cols):
                values_list.append(clean_value(df.iloc[j, k]))
            last_process_year = process_year
        else:
            # 非年度行 → 補上上一筆年度
            values_list.append(last_process_year)
            for k in range(1, cols):
                values_list.append(clean_value(df.iloc[j, k]))

        quoted_values = ",".join(f"'{v}'" for v in values_list)
        insert_cmd = f"insert into {table_name} values ({quoted_values});"

#        print(insert_cmd)
        f.write(insert_cmd + "\n")

        record_count += 1  # 每成功處理一筆就加一

    print(f"檔案 {file_name} 處理完成，共 {record_count} 筆")
    return record_count

def main():
    if len(sys.argv) < 3:
        print("參數不足：theTableName theDirectoryPath")
        sys.exit(1)

    table_name = sys.argv[1]
    directory = sys.argv[2]

    if not os.path.isdir(directory):
        print(f"目錄不存在：{directory}")
        sys.exit(1)

    files = [f for f in os.listdir(directory) if not f.startswith(".") 
             and os.path.isfile(os.path.join(directory, f))]
    files.sort()
    print("檔案數量:", len(files))

    output_file = "__insert_" + table_name + ".txt"
    total_records = 0

    with open(output_file, "w", encoding="utf-8") as f:
        for file_name in files:
            records = process_file(table_name, directory, file_name, f)
            print(f"目前總筆數: {total_records + records}")
            total_records += records

    print(f"全部檔案處理完成，共 {len(files)} 個檔案，總筆數 {total_records}")

if __name__ == "__main__":
    main()