from flask import Flask, render_template, request
import sqlite3
import re

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_unique_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT category FROM books').fetchall()
    conn.close()

    unique_categories = set()
    for category in categories:
        category_list = category['category'].split(', ')
        unique_categories.update(category_list)

    return sorted(unique_categories)

@app.route('/')
def index():
    categories = get_unique_categories()
    return render_template('index.html', categories=categories)

@app.route('/store')
def store():
    categories = get_unique_categories()
    return render_template('store.html', categories=categories)

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
    max_price = request.args.get('max_price', '999999999')
    selected_category = request.args.get('category', '')

    conn = get_db_connection()
    books = conn.execute('SELECT id, title, price, category FROM books').fetchall()
    categories = get_unique_categories()
    conn.close()

    # Filter books based on search query using regex
    filtered_books = [book for book in books if re.search(query, book['title'], re.IGNORECASE)]

    # Filter books based on price range
    filtered_books = [book for book in filtered_books if float(min_price) <= book['price'] <= float(max_price)]

    # Filter books based on selected category
    if selected_category:
        filtered_books = [book for book in filtered_books if selected_category in book['category'].split(', ')]
    else:
        selected_category = 'All Genres'

    return render_template('books.html', titles=[(book['id'], book['title']) for book in filtered_books], categories=categories, selected_category=selected_category, min_price=min_price, max_price=max_price, query=query)

if __name__ == '__main__':
    app.run(debug=True)