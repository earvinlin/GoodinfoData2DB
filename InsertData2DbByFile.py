"""
在新增資料如果卡住，可能是之前的資料庫異動操作還沒有commit
解法就是先開toad，然後執行commit、最後再跑程式
20220524-1046	處理新增資料時出現「mysql.connector.errors.ProgrammingError: 1115 (42000):Unknown \
              	character set: 'utf8mb4'」訊息
			  	處理方式就是建立connector時增加參數 charset = 'utf8'
			  	(目前還是先點掉，因為現行資料庫均可正常執行本程式)
20220622-0832	修正print訊息
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
charset = 'utf8'

theLoadFileDir = sys.argv[1]
theInputFile = sys.argv[2]
insertCnt = 0
errorCnt = 0
theInsertCmd = ""

print("[InsertData2DbByFile.py] 開始執行時間：" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

# mysql.connector.errors.ProgrammingError: 1115 (42000): Unknown character set: ‘utf8mb4’處理方式
#cnx = mysql.connector.connect(user = user, password = pwd, host = host, database = db, charset = charset)
cnx = mysql.connector.connect(user = user, password = pwd, host = host, database = db)
cursor = cnx.cursor()

if len(sys.argv) < 2 :
	# 參數 = 相對路徑 + 檔名 (根目錄程式所在處)
	# imac下，相對路徑不能運作，因為起始路徑與windows不同
	print("You need input two parameter(fmt : relative-path theFileName)")
	print("=== Windows ===")
	print("syntax : C:\python InsertData2DbByFile.py Data\TXT\dividend\22020520\ 2002.txt")
	print("syntax : C:\python InsertData2DbByFile.py Data\TXT\salemon\22020520\ 2002.txt")
	print("syntax : C:\python InsertData2DbByFile.py Data\TXT\BzPerformance\22020520\ 2002.txt")
	print("=== iMac / Linux (要寫全路徑) ===")
	print("syntax : $python3 InsertData2DbByFile.py ~/workspaces/GithubProjects/GoodinfoData2DB/Data/TXT/dividend/22020520/ 2002.txt")
	print("syntax : $python3 InsertData2DbByFile.py ~/workspaces/GithubProjects/GoodinfoData2DB/Data/TXT/salemon/22020520/ 2002.txt")
	print("syntax : $python3 InsertData2DbByFile.py ~/workspaces/GithubProjects/GoodinfoData2DB/Data/TXT/BzPerformance/22020520/ 2002.txt")
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

cnx.commit()
cursor.close()
cnx.close()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

print(theInputFile + "資料處理完成!! 共 " + str(insertCnt) + " 筆；錯誤 " + str(errorCnt) + " 筆。")
print("[InsertStocksFromPolarisToMySQLDB.py] 結束執行時間：" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
