"""
在新增資料如果卡住，可能是之前的資料庫異動操作還沒有commit
解法就是先開toad，然後執行commit、最後再跑程式
"""
import mysql.connector
import sys
import os 
import time
 
user = 'root'
pwd  = 'lin32ledi'
host = '127.0.0.1'
db   = 'stocksdb'
port = 3306

theLoadFileDir = sys.argv[1]
theInputFile = sys.argv[2]
insertCnt = 0
errorCnt = 0
theInsertCmd = ""

print("[InsertData2DbByFile.py] 開始執行時間：" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
 
cnx = mysql.connector.connect(user=user, password=pwd, host=host, database=db)
cursor = cnx.cursor()

if len(sys.argv) < 2 :
	# 參數 = 相對路徑 + 檔名 (根目錄程式所在處)
	print("You need input two parameter(fmt : relative-path theFileName)")
	print("syntax : C:\python InsertData2DbByFile.py Data\TXT\dividend\ 2002.txt")
	print("syntax : C:\python InsertData2DbByFile.py Data\TXT\salemon\ 2002.txt")
	sys.exit()

try :
	stocks = open(theLoadFileDir + theInputFile, 'r')
	for line in stocks:
		theInsertCmd = line
		print(theInsertCmd)
		try :
			cursor.execute(theInsertCmd) 
			insertCnt += 1
		except BaseException as err :
			print("insert to table failed.")
			print("Error: {}".format(err.msg))
			errorCnt += 1
			continue

except mysql.connector.Error as err:
	print("insert to table failed.")
	print("Error: {}".format(err.msg))
	sys.exit()	

#stocks.close()
cnx.commit()
cursor.close()
cnx.close()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

print("資料處理完成!! 共 " + str(insertCnt) + " 筆；錯誤 " + str(errorCnt) + " 筆。")
print("[InsertStocksFromPolarisToMySQLDB.py] 結束執行時間：" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
