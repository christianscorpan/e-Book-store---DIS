from flask import Flask, render_template, request
import sqlite3

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

if __name__ == '__main__':
    app.run(debug=True)