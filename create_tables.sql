CREATE TABLE books (
    Title TEXT NOT NULL,
    Authors TEXT NOT NULL,
    Description TEXT,
    Category TEXT,
    Publisher TEXT,
    "Price Starting With ($)" DOUBLE PRECISION,
    "Publish Date (Month)" TEXT,
    "Publish Date (Year)" BIGINT
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    book_title TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_address TEXT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
