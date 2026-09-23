
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_NAME = os.getenv('DB_NAME', 'neonatal_watch_ai')

print('Connecting to MySQL...')
try:
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute(f'CREATE DATABASE IF NOT EXISTS {DB_NAME};')
    print(f'Database {DB_NAME} ensured.')
    conn.commit()
    cursor.close()
    conn.close()
except Exception as e:
    print('Error:', e)

