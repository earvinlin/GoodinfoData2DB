import re
import sys
import csv
import ssl
import platform
import urllib.parse
import urllib.request


if len(sys.argv) < 3 :
    print("You need input two parameter(fmt : theStockNo theDate(yyyymmdd))")
    print("syntax : C:\python GetTWStocksLegalPersonVolume.py 2014 20220908")
    sys.exit()

theStockNo = sys.argv[1]

theBeginDate = str(int(sys.argv[2]) - 10000)
theBeginDate =  theBeginDate[:4] + "-" + theBeginDate[4:6] + "-" + theBeginDate[6:8]
theEndDate = sys.argv[2]
theEndDate = theEndDate[:4] + "-" + theEndDate[4:6] + "-" + theEndDate[6:8]

print("stockno=", theStockNo, ", ", theBeginDate, ", ", theEndDate)

ssl._create_default_https_context = ssl._create_unverified_context
#url = "https://jsjustweb.jihsun.com.tw/z/zc/zcl/zcl.djhtm?a=2049&c=2021-9-7&d=2022-9-7"
url = "https://jsjustweb.jihsun.com.tw/z/zc/zcl/zcl.djhtm?a=" + theStockNo + \
    "&c=" + theBeginDate + "&d=" + theEndDate

print("url=" + url)

f = urllib.request.urlopen(url)

try :
    saveFileDir = ""
    if platform.system() == "Windows" :
        saveFileDir = "Data\\LEGAL\\"
    else :
        saveFileDir = "./Data/LEGAL/"

    fileName = "法人_" + sys.argv[1] + ".htm"
    print('檔案名稱：' + fileName)
    with open(saveFileDir + fileName, 'w') as out :
#		f.read()是byte型態，需解碼(decode)儲存成字串
        out.write(f.read().decode('big5'))
#        out.write(f.read().decode(encoding='UTF-8'))

    print('資料儲存完成!!')
except IOError as err :
    print('Fie error : ' + str(err))
