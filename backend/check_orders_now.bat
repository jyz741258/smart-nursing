@echo off
echo 正在查询数据库...
cd /d C:\Users\Jyz74\smart-nursing\backend
python -c "import sqlite3; conn = sqlite3.connect('instance/smart_nursing.db'); c = conn.cursor(); c.execute('SELECT COUNT(*) FROM orders'); total = c.fetchone()[0]; print('总订单数:', total); c.execute('SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status'); print('状态统计:'); [print(f'  status={r[0]}: {r[1]}条') for r in c.fetchall()]; c.execute('SELECT id, status, order_no FROM orders ORDER BY id DESC LIMIT 10'); print('最近10条订单:'); [print(f'  ID={r[0]}, status={r[1]}, order_no={r[2]}') for r in c.fetchall()]; conn.close()" > db_output.txt 2>&1
type db_output.txt
echo.
echo 结果已保存到 db_output.txt
pause
