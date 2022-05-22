"""
20220522 (撰寫中) 產生執行InsertData2DbByFile.py的script
         需要輸入的參數：檔案路徑 執行的作業系統(Windows / Linux / iMac) 
         -------------------------------------------------------------------------
         Content :
         -------------------------------------------------------------------------
         <dividend> -- Windows (Linux/iMac -> python3 ...) --
         python InsertData2DbByFile.py Data\TXT\dividend\22020520\ 2002.txt
         ...

         <salemon> -- Windows (Linux/iMac -> python3 ...) --
         python InsertData2DbByFile.py Data\TXT\salemon\22020520\ 2002.txt
         ...

         <BzPerformance> -- Windows (Linux/iMac -> python3 ...) --
         python InsertData2DbByFile.py Data\TXT\BzPerformance\22020520\ 2002.txt
         ...
"""
import mysql.connector
import sys
import os 
import time


print("[InsertData2DbByFile.py] 開始執行時間：" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

insertCnt = 0
errorCnt = 0


print("資料處理完成!! 共 " + str(insertCnt) + " 筆；錯誤 " + str(errorCnt) + " 筆。")
print("[InsertStocksFromPolarisToMySQLDB.py] 結束執行時間：" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
