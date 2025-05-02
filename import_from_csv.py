# Script to import products from CSV
import csv
import sqlite3

# Патека до SQLite базата
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Осигурај се дека табелата постои
c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        name TEXT,
        price REAL,
        sale_price REAL
    )
''')

# Прочитај од CSV и внеси ги податоците
with open('products.csv', encoding='cp1251') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        code = row['Шифра']
        name = row['Име на артикал']
        price = float(row['Продажна цена'].replace(',', '.')) if row['Продажна цена'] else 0.0
        sale_price = float(row['Акциска цена'].replace(',', '.')) if row['Акциска цена'] else None

        c.execute('INSERT INTO products (code, name, price, sale_price) VALUES (?, ?, ?, ?)',
                  (code, name, price, sale_price))

conn.commit()
conn.close()

print("✅ Успешно внесени производите во базата.")
