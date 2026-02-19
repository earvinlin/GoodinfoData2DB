"""
GoodinfoData2DB.Compare2DirectoryFiles 的 Docstring
CMD : python Compare2DirectoryFiles.py theDirectoryPath1 theDirectoryPath2
Example :

python Compare2DirectoryFiles.py D:\Workspaces\GithubProjects\GoodinfoData2DB\Data\EXCEL\Transfer\dividend\20260215_1_2 D:\Workspaces\GithubProjects\GoodinfoData2DB\Data\EXCEL\Transfer\dividend\20260216_1_4

python Compare2DirectoryFiles.py D:\Workspaces\GithubProjects\GoodinfoData2DB\Data\EXCEL\Transfer\dividend\20260215_1_2 D:\Workspaces\GithubProjects\GoodinfoData2DB\Data\EXCEL\Transfer\dividend\20260216_1_5

"""
import os
import sys

if len(sys.argv) < 3:
    print("參數不足：theDirectoryPath1 theDirectoryPath2")
    sys.exit(1)

theDirectoryPath1 = sys.argv[1]
theDirectoryPath2 = sys.argv[2]

if not os.path.isdir(theDirectoryPath1):
    print(f"目錄不存在：{theDirectoryPath1}")
    sys.exit(1)

if not os.path.isdir(theDirectoryPath2):
    print(f"目錄不存在：{theDirectoryPath2}")
    sys.exit(1)

files1 = os.listdir(theDirectoryPath1)
#print("files= ", files)
file1_count = sum(1 for f in files1 if os.path.isfile(os.path.join(theDirectoryPath1, f)))
print("檔案數量:", file1_count)

files1a = []
for i in range(0, file1_count) :
    result = files1[i].split("-")[0]
    files1a.append(result)
print(files1a)

files2 = os.listdir(theDirectoryPath2)
#print("files= ", files)
file2_count = sum(1 for f in files2 if os.path.isfile(os.path.join(theDirectoryPath2, f)))
print("檔案數量:", file2_count)

files2a = []
for i in range(0, file2_count) :
    result = files2[i].split("-")[0]
    files2a.append(result)
print(files2a)

diff_a = list(set(files1a) - set(files2a))  # a 有但 b 沒有
diff_b = list(set(files2a) - set(files1a))  # b 有但 a 沒有

# 建立一個紀錄檔案
output_file = "___compare_result.txt"
with open(output_file, "w", encoding="utf-8") as out:
    out.write(f"{theDirectoryPath1}: {diff_a}\n")
    out.write(f"{theDirectoryPath2}: {diff_b}\n")
