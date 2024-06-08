import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load the CSV into a DataFrame
df = pd.read_csv('BooksDatasetClean.csv')

# Create a PostgreSQL engine
engine = create_engine(f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}")

# Insert data into the PostgreSQL table
df.to_sql('books', engine, if_exists='replace', index=False)
