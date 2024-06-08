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
    conn = get_db_connection()
    books = conn.execute('SELECT id, title FROM books WHERE title LIKE ?', (f'%{query}%',)).fetchall()
    conn.close()
    return render_template('books.html', titles=books)

@app.route('/search_by_price')
def search_by_price():
    price = request.args.get('price', '1')
    

    less_than_5 = re.compile(r'^\s*\$?([0-4](\.\d{1,2})?|5(\.0{1,2})?)\s*$')
    between_5_and_10 = re.compile(r'^\s*\$?(5(\.\d{1,2})?|[6-9](\.\d{1,2})?|10(\.0{1,2})?)\s*$')
    more_than_10 = re.compile(r'^\s*\$?(1[1-9](\.\d{1,2})?|[2-9]\d(\.\d{1,2})?|[1-9]\d{2,}(\.\d{1,2})?)\s*$')

    conn = get_db_connection()
    books = conn.execute('SELECT id, title, price FROM books').fetchall()
    conn.close()
    
    if price == '1':
        filtered_books = [book for book in books if less_than_5.match(str(book['price']))]
    elif price == '2':
        filtered_books = [book for book in books if between_5_and_10.match(str(book['price']))]
    elif price == '3':
        filtered_books = [book for book in books if more_than_10.match(str(book['price']))]
    
    return render_template('books.html', titles=[(book['id'], book['title']) for book in filtered_books])

if __name__ == '__main__':
    app.run(debug=True)
