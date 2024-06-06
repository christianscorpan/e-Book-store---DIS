from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Read the CSV file
df = pd.read_csv('BooksDatasetClean.csv')

# Convert the DataFrame to a list of dictionaries
books = df.to_dict(orient='records')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store')
def store():
    return render_template('store.html')

@app.route('/books')
def books_list():
    titles = [(index, book['Title']) for index, book in enumerate(books)]
    return render_template('books.html', titles=titles)

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = books[book_id]
    return render_template('book_details.html', book=book)

if __name__ == '__main__':
    app.run(debug=True)
