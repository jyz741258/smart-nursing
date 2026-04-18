import subprocess
result = subprocess.run(
    ['python', 'inspect_orders.py'],
    capture_output=True, text=True,
    cwd=r'c:\Users\Jyz74\smart-nursing\backend'
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
