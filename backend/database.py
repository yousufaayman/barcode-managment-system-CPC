import sqlite3

def initialize_database():
    conn = sqlite3.connect('barcode_management.db')
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('Admin', 'Cutting', 'Sewing', 'Packaging')) NOT NULL
    )''')
    
    # Admin-Managed Data Tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS brands (
        brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_name TEXT UNIQUE NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS models (
        model_id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT UNIQUE NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sizes (
        size_id INTEGER PRIMARY KEY AUTOINCREMENT,
        size_value TEXT UNIQUE NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS colors (
        color_id INTEGER PRIMARY KEY AUTOINCREMENT,
        color_name TEXT UNIQUE NOT NULL
    )''')
    
    # Production Phases Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS production_phases (
        phase_id INTEGER PRIMARY KEY AUTOINCREMENT,
        phase_name TEXT UNIQUE NOT NULL
    )''')
    
    # Batches Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS batches (
        batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT UNIQUE NOT NULL,
        brand_id INTEGER NOT NULL,
        model_id INTEGER NOT NULL,
        size_id INTEGER NOT NULL,
        color_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        layers INTEGER NOT NULL,
        serial TEXT CHECK(LENGTH(serial) = 3) NOT NULL,
        current_phase INTEGER NOT NULL,
        status TEXT CHECK(status IN ('Pending', 'In Progress', 'Completed')) NOT NULL,
        FOREIGN KEY (model_id) REFERENCES models(model_id),
        FOREIGN KEY (brand_id) REFERENCES brands(brand_id),
        FOREIGN KEY (size_id) REFERENCES sizes(size_id),
        FOREIGN KEY (color_id) REFERENCES colors(color_id),
        FOREIGN KEY (current_phase) REFERENCES production_phases(phase_id)
    )''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()