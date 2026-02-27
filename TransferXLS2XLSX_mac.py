"""
會出現示警視窗，無法自動關閉或繞過，所以這支程式沒用~~"
"""
import os
import sys
import subprocess

if len(sys.argv) < 2:
    print("請輸入資料夾路徑")
    sys.exit(1)

folder = sys.argv[1]

if not os.path.isdir(folder):
    print("資料夾不存在")
    sys.exit(1)

files = sorted(os.listdir(folder))

def convert_xls_to_xlsx(xls_path, xlsx_path):
    # AppleScript 指令
    script = f'''
    tell application "Microsoft Excel"
        open POSIX file "{xls_path}"
        save active workbook in POSIX file "{xlsx_path}" as Excel XML file format
        close active workbook saving no
    end tell
    '''

    # 呼叫 osascript 執行 AppleScript
    process = subprocess.Popen(
        ["osascript", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = process.communicate(script)

    if process.returncode != 0:
        print(f"❌ 轉換失敗：{xls_path}")
        print("原因：", err)
    else:
        print(f"✔ 轉換成功：{xlsx_path}")


for f in files:
    if f.lower().endswith(".xls"):
        xls_path = os.path.join(folder, f)
        xlsx_path = os.path.join(folder, f.replace(".xls", ".xlsx"))

        print(f"轉換中：{xls_path} → {xlsx_path}")
        convert_xls_to_xlsx(xls_path, xlsx_path)
