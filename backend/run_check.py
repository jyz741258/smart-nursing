import subprocess
result = subprocess.run(
    ['python', 'check_db.py'],
    capture_output=True, text=True,
    cwd=r'c:\Users\Jyz74\smart-nursing\backend',
    encoding='utf-8'
)
with open(r'c:\Users\Jyz74\smart-nursing\backend\db_check_output.txt', 'w', encoding='utf-8') as f:
    f.write("STDOUT:\n")
    f.write(result.stdout)
    f.write("\nSTDERR:\n")
    f.write(result.stderr)
print("输出已保存到 db_check_output.txt")
