"""
GoodinfoData2DB.Compare2DirectoryFiles 的 Docstring
CMD : python Compare2DirectoryFiles.py theDirectoryPath1 theDirectoryPath2

Example :
python Compare2DirectoryFiles.py D:\Workspaces\GithubProjects\GoodinfoData2DB\Data\EXCEL\Transfer\dividend\20260215_1_2 D:\Workspaces\GithubProjects\GoodinfoData2DB\Data\EXCEL\Transfer\dividend\20260216_1_4
python Compare2DirectoryFiles.py D:\Workspaces\GithubProjects\GoodinfoData2DB\Data\EXCEL\Transfer\dividend\20260215_1_2 D:\Workspaces\GithubProjects\GoodinfoData2DB\Data\EXCEL\Transfer\dividend\20260216_1_5

"""
import os
import sys


def get_file_prefixes(directory):
    """取得目錄中所有檔案的前綴（以 '-' 分割後的第一段）"""
    try:
        items = os.listdir(directory)
    except Exception as e:
        print(f"讀取目錄失敗：{directory}，錯誤：{e}")
        sys.exit(1)

    prefixes = []

    for item in items:
        full_path = os.path.join(directory, item)

        if os.path.isfile(full_path):
            prefix = item.split("-", 1)[0]  # 只切第一個 '-'
            prefixes.append(prefix)

    return prefixes


def main():
    if len(sys.argv) < 3:
        print("參數不足：theDirectoryPath1 theDirectoryPath2")
        sys.exit(1)

    theDirectoryPath1 = sys.argv[1]
    theDirectoryPath2 = sys.argv[2]

    # 檢查目錄是否存在
    for path in (theDirectoryPath1, theDirectoryPath2):
        if not os.path.isdir(path):
            print(f"目錄不存在：{path}")
            sys.exit(1)

    # 取得前綴清單
    files1_prefix = get_file_prefixes(theDirectoryPath1)
    files2_prefix = get_file_prefixes(theDirectoryPath2)

    print(f"{theDirectoryPath1} 檔案數量: {len(files1_prefix)}")
    print(files1_prefix)

    print(f"{theDirectoryPath2} 檔案數量: {len(files2_prefix)}")
    print(files2_prefix)

    # 比對差異
    diff_a = sorted(list(set(files1_prefix) - set(files2_prefix)))
    diff_b = sorted(list(set(files2_prefix) - set(files1_prefix)))

    # 輸出結果
    output_file = "___compare_result.txt"
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(f"{theDirectoryPath1} 多出的項目: {diff_a}\n")
        out.write(f"{theDirectoryPath2} 多出的項目: {diff_b}\n")

    print(f"比對完成，結果已輸出至 {output_file}")


if __name__ == "__main__":
    main()