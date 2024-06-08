import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from flask import Flask, render_template, request, g, redirect, url_for
from psycopg2.extras import RealDictCursor

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Configure PostgreSQL connection
connection_pool = pool.SimpleConnectionPool(1, 20, 
    host="localhost",
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD')
)

def get_db():
    if 'db' not in g:
        g.db = connection_pool.getconn()
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        connection_pool.putconn(db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store')
def store():
    return render_template('store.html')

@app.route('/books')
def books():
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT "Title", "Authors" FROM books')
    books = cur.fetchall()
    cur.close()
    return render_template('books.html', books=books)

@app.route('/book_details/<string:title>')
def book_details(title):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM books WHERE "Title" = %s', (title,))
    book = cur.fetchone()
    cur.close()
    return render_template('book_details.html', book=book)

@app.route('/search')
def search():
    query = request.args.get('query')
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT "Title", "Authors" FROM books WHERE "Title" LIKE %s', ('%' + query + '%',))
    books = cur.fetchall()
    cur.close()
    return render_template('books.html', books=books)

@app.route('/order/<string:title>', methods=['GET', 'POST'])
def order(title):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        db = get_db()
        cur = db.cursor()
        cur.execute('''
            INSERT INTO orders (book_title, customer_name, customer_email, customer_address)
            VALUES (%s, %s, %s, %s)
        ''', (title, name, email, address))
        db.commit()
        cur.close()
        return redirect(url_for('order_confirmation', title=title))
    return render_template('order.html', title=title)

@app.route('/order_confirmation/<string:title>')
def order_confirmation(title):
    return render_template('order_confirmation.html', title=title)

@app.route('/orders')
def orders():
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM orders')
    orders = cur.fetchall()
    cur.close()
    return render_template('orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
