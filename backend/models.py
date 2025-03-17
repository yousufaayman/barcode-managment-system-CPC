import pymysql
import os
import time
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "your_mysql_user"),
    "password": os.getenv("DB_PASSWORD", "your_mysql_password"),
    "database": os.getenv("DB_NAME", "barcode_management"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "autocommit": False 
}

class Database:
    def __init__(self):
        self.conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=()):
        """Executes a query with retries to handle concurrency safely."""
        for _ in range(5):
            try:
                self.cursor.execute(query, params)
                self.conn.commit()
                return
            except pymysql.MySQLError as e:
                if "lock" in str(e).lower():
                    time.sleep(1)  
                else:
                    self.conn.rollback()
                    raise e
        raise pymysql.MySQLError("Database operation failed after multiple retries.")

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.cursor.close()
        self.conn.close()

class Batch:
    @staticmethod
    def create_batch(barcode, brand_id, model_id, size_id, color_id, quantity, layers, serial, current_phase, status):
        db = Database()
        try:
            existing_batch = db.fetch_one("SELECT batch_id FROM batches WHERE barcode = %s", (barcode,))
            if existing_batch:
                print(f"⚠️ Barcode '{barcode}' already exists. Skipping insertion.")
                return
            
            db.execute_query(
                "INSERT INTO batches (barcode, brand_id, model_id, size_id, color_id, quantity, layers, serial, current_phase, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (barcode, brand_id, model_id, size_id, color_id, quantity, layers, serial, current_phase, status)
            )
        finally:
            db.close()

    @staticmethod
    def get_batches():
        db = Database()
        query = """
            SELECT 
                b.batch_id, 
                b.barcode, 
                br.brand_name, 
                m.model_name, 
                s.size_value, 
                c.color_name, 
                b.quantity, 
                b.layers, 
                b.serial, 
                p.phase_name, 
                b.status
            FROM batches b
            LEFT JOIN brands br ON b.brand_id = br.brand_id
            LEFT JOIN models m ON b.model_id = m.model_id
            LEFT JOIN sizes s ON b.size_id = s.size_id
            LEFT JOIN colors c ON b.color_id = c.color_id
            LEFT JOIN production_phases p ON b.current_phase = p.phase_id
        """
        batches = db.fetch_all(query)
        db.close()
        return batches

    @staticmethod
    def update_batch_status(batch_id, status):
        db = Database()
        try:
            db.execute_query("UPDATE batches SET status = %s WHERE batch_id = %s", (status, batch_id))
        finally:
            db.close()
        
    @staticmethod
    def update_batch_phase(batch_id, phase_id):
        db = Database()
        try:
            db.execute_query("UPDATE batches SET current_phase = %s WHERE batch_id = %s", (phase_id, batch_id))
        finally:
            db.close()

    @staticmethod
    def delete_batch(batch_id):
        """Deletes a batch entry from the database using batch_id."""
        db = Database()
        try:
            db.execute_query("DELETE FROM batches WHERE batch_id = %s", (batch_id,))
        finally:
            db.close()

    @staticmethod
    def get_batch_by_barcode(barcode):
        """Fetches a batch and its related details using a barcode."""
        db = Database()
        try:
            barcode = barcode.strip()
            query = """
                SELECT 
                    b.batch_id, 
                    b.barcode, 
                    br.brand_name, 
                    m.model_name, 
                    s.size_value, 
                    c.color_name, 
                    b.quantity, 
                    b.layers, 
                    b.serial, 
                    p.phase_name, 
                    b.status
                FROM batches b
                LEFT JOIN brands br ON b.brand_id = br.brand_id
                LEFT JOIN models m ON b.model_id = m.model_id
                LEFT JOIN sizes s ON b.size_id = s.size_id
                LEFT JOIN colors c ON b.color_id = c.color_id
                LEFT JOIN production_phases p ON b.current_phase = p.phase_id
                WHERE b.barcode = %s;
            """
            batch = db.fetch_one(query, (barcode,))
            return batch 
        
        finally:
            db.close()

class ProductionPhase:
    @staticmethod
    def get_phases():
        db = Database()
        phases = db.fetch_all("SELECT phase_id, phase_name FROM production_phases")
        db.close()
        return {p["phase_name"]: p["phase_id"] for p in phases}

class Brand:
    @staticmethod
    def add_brand(brand_name):
        db = Database()
        try:
            db.execute_query("INSERT IGNORE INTO brands (brand_name) VALUES (%s)", (brand_name,))
            brand = db.fetch_one("SELECT brand_id FROM brands WHERE brand_name = %s", (brand_name,))
            return brand["brand_id"] if brand else None
        finally:
            db.close()

    @staticmethod
    def get_brands():
        db = Database()
        brands = db.fetch_all("SELECT brand_id, brand_name FROM brands")
        db.close()
        return {b["brand_name"]: b["brand_id"] for b in brands}

class Model:
    @staticmethod
    def add_model(model_name):
        db = Database()
        try:
            db.execute_query("INSERT IGNORE INTO models (model_name) VALUES (%s)", (model_name,))
            model = db.fetch_one("SELECT model_id FROM models WHERE model_name = %s", (model_name,))
            return model["model_id"] if model else None
        finally:
            db.close()

    @staticmethod
    def get_models():
        db = Database()
        models = db.fetch_all("SELECT model_id, model_name FROM models")
        db.close()
        return {m["model_name"]: m["model_id"] for m in models}

class Size:
    @staticmethod
    def add_size(size_value):
        db = Database()
        try:
            db.execute_query("INSERT IGNORE INTO sizes (size_value) VALUES (%s)", (size_value,))
            size = db.fetch_one("SELECT size_id FROM sizes WHERE size_value = %s", (size_value,))
            return size["size_id"] if size else None
        finally:
            db.close()

    @staticmethod
    def get_sizes():
        db = Database()
        sizes = db.fetch_all("SELECT size_id, size_value FROM sizes")
        db.close()
        return {s["size_value"]: s["size_id"] for s in sizes}

class Color:
    @staticmethod
    def add_color(color_name):
        db = Database()
        try:
            db.execute_query("INSERT IGNORE INTO colors (color_name) VALUES (%s)", (color_name,))
            color = db.fetch_one("SELECT color_id FROM colors WHERE color_name = %s", (color_name,))
            return color["color_id"] if color else None
        finally:
            db.close()

    @staticmethod
    def get_colors():
        db = Database()
        colors = db.fetch_all("SELECT color_id, color_name FROM colors")
        db.close()
        return {c["color_name"]: c["color_id"] for c in colors}
