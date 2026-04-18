import sqlite3

conn = sqlite3.connect(r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute('SELECT COUNT(*) as total FROM orders')
total = c.fetchone()['total']
print(f'数据库总订单数: {total}')

c.execute('SELECT status, COUNT(*) as cnt FROM orders GROUP BY status ORDER BY status')
print('按状态统计:')
for row in c.fetchall():
    print(f'  status={row["status"]}: {row["cnt"]}条')

c.execute('SELECT id, status, actual_amount, total_amount FROM orders ORDER BY id DESC LIMIT 10')
print('\n最近10条订单:')
for row in c.fetchall():
    print(f'  ID={row["id"]}, status={row["status"]}, actual_amount={row["actual_amount"]}, total_amount={row["total_amount"]}')

conn.close()
input('\n按回车退出...')
