from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database and create the USERS table if it doesn't exist
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS USERS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Add a specific username and password to the database for demonstration
def add_default_user():
    conn = get_db_connection()
    conn.execute('DELETE FROM USERS')  # Clear existing users for this example
    conn.execute('INSERT INTO USERS (username, password) VALUES (?, ?)', ('test', '123'))
    conn.commit()
    conn.close()

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

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM USERS WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    if user:
        session['username'] = username
        return redirect(url_for('store'))
    else:
        return render_template('index.html', error='Invalid username or password', categories=get_unique_categories())

@app.route('/store')
def store():
    if 'username' in session:
        categories = get_unique_categories()
        return render_template('store.html', categories=categories)
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

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

@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    cart = session.get('cart', [])
    cart.append(book_id)
    session['cart'] = cart
    return redirect(url_for('book_details', book_id=book_id))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    if len(cart) == 0:
        return render_template('cart.html', cart_books=[], total_price=0)

    conn = get_db_connection()
    cart_books = conn.execute('SELECT * FROM books WHERE id IN ({})'.format(','.join('?' * len(cart))), cart).fetchall()
    total_price = sum(book['price'] for book in cart_books)
    conn.close()
    return render_template('cart.html', cart_books=cart_books, total_price=total_price)

@app.route('/remove_from_cart/<int:book_id>', methods=['POST'])
def remove_from_cart(book_id):
    cart = session.get('cart', [])
    if book_id in cart:
        cart.remove(book_id)
        session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))

if __name__ == '__main__':
    init_db()
    add_default_user()  # Ensure there is one specific user for this example
    app.run(debug=True)