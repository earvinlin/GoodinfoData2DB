import pandas as pd

# 路徑設定
path = "/Users/earvin/workspaces/GithubProjects/GoodinfoData2DB/Data/EXCEL/Transfer/dividend/test/"
stock_no = "0050"
file_name = "0050-dividend-20260215_1_2.xlsx"
sheet_name = "0050-dividend-20260215_1_2"

# 讀取 Excel
df = pd.read_excel(path + file_name, sheet_name=sheet_name, header=None)
#df = df.fillna(" ")

rows, cols = df.shape

# 開啟輸出檔案（寫入模式）
last_process_year = ""
output_file = "___insert_cmd.sql"
with open(output_file, "w", encoding="utf-8") as f:
    for i in range(4, rows-1):
        values = ""
        process_year = str(df.iloc[i, 0]).strip().replace("'", "")
        try:
            float(process_year)
            print("是數值")
            values = "'" + stock_no + "',"
            for j in range(cols):
                values += "'" + str(df.iloc[i, j]).strip().replace("'", "") + "',"
#                print("values1= ", values)
        except (ValueError, TypeError):
            print("不是數值")
            values = "'" + stock_no + "','" + last_process_year + "',"
            for j in range(1, cols):
                values += "'" + str(df.iloc[i, j]).strip().replace("'", "") + "',"
#                print("values2= ", values)

        values = values[:-1]  # 去掉最後一個逗號
        insert_cmd = "insert into stocks_dividend_CAS_dividend_yield values (" + values + ");"
        try :
            float(process_year)
            last_process_year = process_year
        except (ValueError, TypeError):
            pass
        
        print(insert_cmd)      # 仍可在 console 顯示
        f.write(insert_cmd + "\n")  # 寫入檔案，每行一筆 SQL
