from flask import Flask, get_flashed_messages, render_template, request, redirect, url_for, session, flash
from functools import wraps
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

def get_unique_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT category FROM books').fetchall()
    conn.close()
    unique_categories = set()
    for category in categories:
        category_list = category['category'].split(', ')
        unique_categories.update(category_list)
    return sorted(unique_categories)

# Decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to redirect logged-in users
def redirect_if_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            return redirect(url_for('store'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@redirect_if_logged_in
def index():
    categories = get_unique_categories()
    return render_template('index.html', categories=categories)

@app.route('/register', methods=['GET', 'POST'])
@redirect_if_logged_in
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        
        conn = get_db_connection()
        user_exists = conn.execute('SELECT * FROM USERS WHERE username = ?', (username,)).fetchone()
        
        if user_exists:
            flash('Username already exists.', 'error')
            conn.close()
            return redirect(url_for('register'))
        
        conn.execute('INSERT INTO USERS (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

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
@login_required
def store():
    categories = get_unique_categories()
    return render_template('store.html', categories=categories)

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/books')
@login_required
def books_list():
    conn = get_db_connection()
    books = conn.execute('SELECT id, title FROM books').fetchall()
    conn.close()
    return render_template('books.html', titles=books)

@app.route('/book/<int:book_id>')
@login_required
def book_details(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    conn.close()
    return render_template('book_details.html', book=book)

@app.route('/search')
@login_required
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
@login_required
def add_to_cart(book_id):
    cart = session.get('cart', [])
    cart.append(book_id)
    session['cart'] = cart
    return redirect(url_for('book_details', book_id=book_id))

@app.route('/cart')
@login_required
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
@login_required
def remove_from_cart(book_id):
    cart = session.get('cart', [])
    if book_id in cart:
        cart.remove(book_id)
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM USERS WHERE username = ? AND password = ?', (session['username'], old_password)).fetchone()
        
        if user:
            conn.execute('UPDATE USERS SET password = ? WHERE username = ?', (new_password, session['username']))
            conn.commit()
            conn.close()
            flash('Password changed successfully.', 'success')
        else:
            flash('Old password is incorrect.', 'error')
        
        return redirect(url_for('change_password'))

    flashed_messages = get_flashed_messages(with_categories=True)
    return render_template('change_password.html', flashed_messages=flashed_messages)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)