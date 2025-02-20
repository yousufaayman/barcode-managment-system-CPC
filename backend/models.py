import sqlite3

DB_PATH = "barcode_management.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()

# User Model
class User:
    @staticmethod
    def create_user(username, password, role):
        db = Database()
        db.execute_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                         (username, password, role))
        db.close()

    @staticmethod
    def get_user(username):
        db = Database()
        user = db.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
        db.close()
        return user
    
    @staticmethod
    def delete_user(username):
        db = Database()
        user = db.execute_query("DELETE FROM users WHERE username = ?", (username,))
        db.close()
        return user

# Batch Model
class Batch:
    @staticmethod
    def create_batch(barcode, brand_id, model_id, size_id, color_id, quantity, layers, serial, current_phase, status):
        db = Database()
        db.execute_query(
            "INSERT INTO batches (barcode, brand_id, model_id, size_id, color_id, quantity, layers, serial, current_phase, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (barcode, brand_id, model_id, size_id, color_id, quantity, layers, serial, current_phase, status),
        )
        db.close()

    @staticmethod
    def get_batches():
        db = Database()
        batches = db.fetch_all("SELECT * FROM batches")
        db.close()
        return batches

    @staticmethod
    def update_batch_status(batch_id, status):
        db = Database()
        db.execute_query("UPDATE batches SET status = ? WHERE batch_id = ?", (status, batch_id))
        db.close()

# Production Phase Model
class ProductionPhase:
    def add_production_phase(phase_name):
        db = Database()
        db.execute_query("INSERT INTO production_phases (phase_name) VALUES (?)",
                         (phase_name,))
        db.close()
    @staticmethod
    def get_phases():
        db = Database()
        phases = db.fetch_all("SELECT * FROM production_phases")
        db.close()
        return phases

# Admin-Managed Data Models
class Brand:
    @staticmethod
    def add_brand(brand_name):
        db = Database()
        db.execute_query("INSERT INTO brands (brand_name) VALUES (?)",
                         (brand_name,))
        db.close()
        
    @staticmethod 
    def get_brands():
        db = Database()
        brands = db.fetch_all("SELECT * FROM brands")
        db.close()
        return brands

class Model:
    @staticmethod
    def add_model(model_name):
        db = Database()
        db.execute_query("INSERT INTO models (model_name) VALUES (?)",
                         (model_name,))
        db.close()
    
    @staticmethod
    def get_models():
        db = Database()
        models = db.fetch_all("SELECT * FROM models")
        db.close()
        return models

class Size:
    @staticmethod
    def add_size(size_value):
        db = Database()
        db.execute_query("INSERT INTO sizes (size_value) VALUES (?)",
                         (size_value,))
        db.close()
    
    @staticmethod
    def get_sizes():
        db = Database()
        sizes = db.fetch_all("SELECT * FROM sizes")
        db.close()
        return sizes

class Color:
    @staticmethod
    def add_color(color_name):
        db = Database()
        db.execute_query("INSERT INTO colors (color_name) VALUES (?)",
                         (color_name,))
        db.close()
    
    @staticmethod
    def get_colors():
        db = Database()
        colors = db.fetch_all("SELECT * FROM colors")
        db.close()
        return colors
