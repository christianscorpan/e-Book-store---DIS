from flask import Flask, render_template, request
import sqlite3
import re

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store')
def store():
    return render_template('store.html')

@app.route('/books')
def books_list():
    conn = get_db_connection()
    books = conn.execute('SELECT id, title FROM books').fetchall()
    conn.close()
    return render_template('books.html', titles=books)

@app.route('/book/<int:book_id>')
def book_details(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    conn.close()
    return render_template('book_details.html', book=book)


@app.route('/search')
def search():
    query = request.args.get('query', '')
    min_price = request.args.get('min_price', '0')
    max_price = request.args.get('max_price', '0')

    if not min_price:
        min_price = '0'
    if not max_price:
        max_price = '999999999'  # A large value to include all prices if max_price is not provided

    conn = get_db_connection()
    books = conn.execute('SELECT id, title, price FROM books WHERE title LIKE ? AND price BETWEEN ? AND ?',
                         (f'%{query}%', min_price, max_price)).fetchall()
    conn.close()

    return render_template('books.html', titles=[(book['id'], book['title']) for book in books])

if __name__ == '__main__':
    app.run(debug=True)