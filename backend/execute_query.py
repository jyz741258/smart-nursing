import subprocess
import sys

# 使用完整路径运行Python
result = subprocess.run(
    [sys.executable, 'query_orders.py'],
    capture_output=True, text=True,
    cwd=r'c:\Users\Jyz74\smart-nursing\backend'
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr[:500] if result.stderr else "")
print("Return code:", result.returncode)
