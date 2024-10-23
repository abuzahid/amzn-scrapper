from psycopg2.extras import execute_batch
import psycopg2
from datetime import datetime
import pandas as pd
import streamlit as st
from pathlib import Path
import os
from dotenv import load_dotenv

env_path = '.env'
load_dotenv(dotenv_path=env_path)

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_NAME"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", "5432")
}

def create_database_tables():
    """Create the necessary database tables if they don't exist"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Create products table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            price DECIMAL(10,2),
            brand TEXT,
            model TEXT,
            rating DECIMAL(2,1),
            reviews INTEGER,
            availability BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create updated_at trigger
        cur.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """)
        
        cur.execute("""
        DROP TRIGGER IF EXISTS update_products_updated_at ON products;
        """)
        
        cur.execute("""
        CREATE TRIGGER update_products_updated_at
            BEFORE UPDATE ON products
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)
        
        conn.commit()
        
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        conn.rollback()
        
    finally:
        cur.close()
        conn.close()
# Create database tables if they don't exist
create_database_tables()

def save_to_database(data_df):
    """Save the scraped data to the database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Convert DataFrame rows to list of tuples for batch insert
        values = [
            (
                row.title,
                float(str(row.price).replace('$', '').replace(',', '')) if pd.notna(row.price) else None,
                row.brand if pd.notna(row.brand) else None,
                row.model if pd.notna(row.model) else None,
                float(row.rating) if pd.notna(row.rating) else None,
                int(str(row.reviews).replace(',', '')) if pd.notna(row.reviews) else None,
                True if row.availability == "In Stock" else False
            )
            for _, row in data_df.iterrows()
        ]
        
        # Batch insert using execute_batch
        execute_batch(cur, """
            INSERT INTO products (title, price, brand, model, rating, reviews, availability)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, values)
        
        conn.commit()
        st.success(f"Successfully saved {len(values)} products to database")
        
    except Exception as e:
        conn.rollback()
        st.error(f"Error saving to database: {str(e)}")
        
    finally:
        cur.close()
        conn.close()