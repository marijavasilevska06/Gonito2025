from flask import Flask, render_template, request, redirect, url_for, session
import csv
import sqlite3

app = Flask(__name__)
app.secret_key = 'tajna_lozinka'

DB = 'database.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 25
    offset = (page - 1) * per_page

    conn = get_db()
    if search:
        rows = conn.execute("SELECT * FROM products WHERE name LIKE ? LIMIT ? OFFSET ?", 
                            (f'%{search}%', per_page, offset)).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM products WHERE name LIKE ?", 
                             (f'%{search}%',)).fetchone()[0]
    else:
        rows = conn.execute("SELECT * FROM products LIMIT ? OFFSET ?", 
                            (per_page, offset)).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    conn.close()

    pages = (total + per_page - 1) // per_page
    start = max(1, page - 2)
    end = min(pages, page + 2)

    return render_template('products.html',
                           products=rows,
                           current_page=page,
                           pages=pages,
                           search=search,
                           start=start,
                           end=end)

@app.route('/sales')
def sales():
    conn = get_db()
    rows = conn.execute("SELECT * FROM products WHERE sale_price IS NOT NULL AND sale_price != ''").fetchall()
    conn.close()
    return render_template('sales.html', products=rows)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Погрешно корисничко име или лозинка.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 25
    offset = (page - 1) * per_page

    conn = get_db()

    if search:
        rows = conn.execute(
            "SELECT * FROM products WHERE name LIKE ? LIMIT ? OFFSET ?",
            (f'%{search}%', per_page, offset)
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM products WHERE name LIKE ?",
            (f'%{search}%',)
        ).fetchone()[0]
    else:
        rows = conn.execute(
            "SELECT * FROM products LIMIT ? OFFSET ?",
            (per_page, offset)
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

    conn.close()

    pages = (total + per_page - 1) // per_page

    return render_template(
        'admin.html',
        products=rows,
        current_page=page,
        pages=pages,
        search=search,
        min=min,
        max=max
    )


@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    conn = get_db()
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        price = request.form['price']
        sale_price = request.form['sale_price']
        conn.execute("UPDATE products SET code=?, name=?, price=?, sale_price=? WHERE id=?",
                     (code, name, price, sale_price, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    row = conn.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template('edit.html', product=row)

@app.route('/add', methods=['POST'])
def add():
    if not session.get('admin'):
        return redirect(url_for('login'))
    code = request.form['code']
    name = request.form['name']
    price = request.form['price']
    sale_price = request.form['sale_price']
    conn = get_db()
    conn.execute("INSERT INTO products (code, name, price, sale_price) VALUES (?, ?, ?, ?)",
                 (code, name, price, sale_price))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
