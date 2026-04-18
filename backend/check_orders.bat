@echo off
cd /d C:\Users\Jyz74\smart-nursing\backend
chcp 65001 >nul
python -c "import sqlite3; conn = sqlite3.connect('instance/smart_nursing.db'); c = conn.cursor(); c.execute('SELECT COUNT(*) FROM orders'); print('Total:', c.fetchone()[0]); c.execute('SELECT status, COUNT(*) FROM orders GROUP BY status'); print('Stats:', c.fetchall()); conn.close()"
pause
