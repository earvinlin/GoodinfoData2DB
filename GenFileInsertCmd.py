"""
-- NOT FIN. --
GoodinfoData2DB.CheckFileContent 的 Docstring
CMD : python3 CheckFileContent.py theDirectoryPath theCompareValue thePosition
Example :

"""
import pandas as pd

path = "D:\\workspaces\\GithubProjects\\GoodinfoData2DB\\Data\\EXCEL\\Transfer\\dividend\\20260215_1_2\\"
file_name = "9962-dividend-20260215_1_2.xlsx"
sheet_name = "9962-dividend-20260215_1_2"
df = pd.read_excel(path + file_name, sheet_name=sheet_name)

rows, cols = df.shape
data_list = []

for i in range(rows):
    row_values = []
    for j in range(cols):
        row_values.append(str(df.iloc[i, j]))
    print(row_values)
    data_list.append("\t".join(row_values))

data = "\n".join(data_list)
# print(data)



"""
data = ""
rows, cols = df.shape
for i in range(0, rows) :
    for j in range(0, cols) :
        data = data + "    " + str(df.iloc[i, j]) 
#        print(df.iloc[i, j])


row_index = 5
col_index = 2
value = df.iloc[row_index, col_index]
for i in range(0, 10):
    for j in range(0, 10):
        value = df.iloc[i, j]
        print("content[", i, ",", j, "]= ", value)
"""
