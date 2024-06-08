from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

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

@app.route('/')
def index():
    return render_template('index.html')

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
        return render_template('index.html', error='Invalid username or password')

@app.route('/store')
def store():
    if 'username' in session:
        return render_template('store.html')
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
    min_price = request.args.get('min_price', 0)
    max_price = request.args.get('max_price', 999999999)
    category = request.args.get('category', '')

    conn = get_db_connection()
    sql_query = 'SELECT id, title FROM books WHERE title LIKE ? AND price >= ? AND price <= ?'
    params = [f'%{query}%', min_price, max_price]

    if category:
        sql_query += ' AND category = ?'
        params.append(category)
    
    books = conn.execute(sql_query, params).fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM books').fetchall()
    conn.close()
    return render_template('books.html', titles=books, categories=[cat['category'] for cat in categories], query=query, min_price=min_price, max_price=max_price, selected_category=category)

if __name__ == '__main__':
    init_db()
    add_default_user()  # Ensure there is one specific user for this example
    app.run(debug=True)