import csv
import sys
import os
import sqlite3


def get_db_connection():
    conn = sqlite3.connect('books.db')
    return conn


def create_table():
    conn = get_db_connection()
    cur = conn.cursor()

    # Create the books table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            authors TEXT,
            description TEXT,
            category TEXT,
            publisher TEXT,
            price REAL,
            publish_month INTEGER,
            publish_year INTEGER
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Table 'books' created successfully!")

def import_csv_data():
    conn = get_db_connection()
    cur = conn.cursor()

    month_mapping = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }

    try:
        with open('BooksDatasetClean.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                title, authors, description, category, publisher, price, publish_month, publish_year = row
                publish_month_numeric = month_mapping.get(publish_month, 0)  # Convert month name to numeric value
                cur.execute(
                    "INSERT INTO books (title, authors, description, category, publisher, price, publish_month, publish_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (title, authors, description, category, publisher, float(price.replace('$', '')), publish_month_numeric, int(publish_year))
                )

        conn.commit()
        print("Data imported successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred during data import: {str(e)}")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    create_table()
    import_csv_data()