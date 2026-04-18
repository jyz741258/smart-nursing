import subprocess
result = subprocess.run(
    ['python', 'check_db_final.py'],
    capture_output=True, text=True,
    cwd=r'c:\Users\Jyz74\smart-nursing\backend'
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:200])
