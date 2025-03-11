import sqlite3
import time

DB_PATH = "barcode_management.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, timeout=10)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=()):
        """Executes a query with retries to handle database locking."""
        for _ in range(5):
            try:
                self.cursor.execute(query, params)
                self.conn.commit()
                return
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower():
                    time.sleep(1)
                else:
                    raise e 
        raise sqlite3.OperationalError("Database is locked and couldn't complete the operation.")

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()

class Batch:
    @staticmethod
    def create_batch(barcode, brand_id, model_id, size_id, color_id, quantity, layers, serial, current_phase, status):
        db = Database()

        # Check if barcode already exists
        existing_batch = db.fetch_one("SELECT batch_id FROM batches WHERE barcode = ?", (barcode,))
        
        if existing_batch:
            print(f"⚠️ Barcode '{barcode}' already exists. Skipping insertion.")
            db.close()
            return

        db.execute_query(
            "INSERT INTO batches (barcode, brand_id, model_id, size_id, color_id, quantity, layers, serial, current_phase, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (barcode, brand_id, model_id, size_id, color_id, quantity, layers, serial, current_phase, status),
        )
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
        db.execute_query("UPDATE batches SET status = ? WHERE batch_id = ?", (status, batch_id))
        db.close()
        
    @staticmethod
    def update_batch_phase(batch_id, phase_id):
        db = Database()
        db.execute_query("UPDATE batches SET current_phase = ? WHERE batch_id = ?", (phase_id, batch_id))
        db.close()

    @staticmethod
    def get_batch_by_barcode(barcode):
        db = Database()
        barcode = barcode.strip()
        query = """
            SELECT 
                b.batch_id, b.barcode, 
                br.brand_name, 
                m.model_name, 
                s.size_value, 
                c.color_name, 
                b.quantity, b.layers, b.serial, 
                p.phase_name, 
                b.status
            FROM batches b
            LEFT JOIN brands br ON b.brand_id = br.brand_id
            LEFT JOIN models m ON b.model_id = m.model_id
            LEFT JOIN sizes s ON b.size_id = s.size_id
            LEFT JOIN colors c ON b.color_id = c.color_id
            LEFT JOIN production_phases p ON b.current_phase = p.phase_id
            WHERE b.barcode = (?);
        """
        batch = db.fetch_one(query, (barcode,))
        db.close()
        return batch

    @staticmethod
    def delete_batch(batch_id):
        """Deletes a batch entry from the database using batch_id."""
        db = Database()
        db.execute_query("DELETE FROM batches WHERE batch_id = ?", (batch_id,))
        db.close()


class ProductionPhase:
    @staticmethod
    def get_phases():
        db = Database()
        phases = db.fetch_all("SELECT phase_id, phase_name FROM production_phases")
        db.close()
        return {p[1]: p[0] for p in phases}

class Brand:
    @staticmethod
    def add_brand(brand_name):
        db = Database()
        db.execute_query("INSERT OR IGNORE INTO brands (brand_name) VALUES (?)", (brand_name,))
        brand = db.fetch_one("SELECT brand_id FROM brands WHERE brand_name = ?", (brand_name,))
        db.close()
        return brand[0] if brand else None

    @staticmethod
    def get_brands():
        db = Database()
        brands = db.fetch_all("SELECT brand_id, brand_name FROM brands")
        db.close()
        return {b[1]: b[0] for b in brands}

class Model:
    @staticmethod
    def add_model(model_name):
        db = Database()
        db.execute_query("INSERT OR IGNORE INTO models (model_name) VALUES (?)", (model_name,))
        model = db.fetch_one("SELECT model_id FROM models WHERE model_name = ?", (model_name,))
        db.close()
        return model[0] if model else None

    @staticmethod
    def get_models():
        db = Database()
        models = db.fetch_all("SELECT model_id, model_name FROM models")
        db.close()
        return {m[1]: m[0] for m in models}

class Size:
    @staticmethod
    def add_size(size_value):
        db = Database()
        db.execute_query("INSERT OR IGNORE INTO sizes (size_value) VALUES (?)", (size_value,))
        size = db.fetch_one("SELECT size_id FROM sizes WHERE size_value = ?", (size_value,))
        db.close()
        return size[0] if size else None

    @staticmethod
    def get_sizes():
        db = Database()
        sizes = db.fetch_all("SELECT size_id, size_value FROM sizes")
        db.close()
        return {s[1]: s[0] for s in sizes}

class Color:
    @staticmethod
    def add_color(color_name):
        db = Database()
        db.execute_query("INSERT OR IGNORE INTO colors (color_name) VALUES (?)", (color_name,))
        color = db.fetch_one("SELECT color_id FROM colors WHERE color_name = ?", (color_name,))
        db.close()
        return color[0] if color else None

    @staticmethod
    def get_colors():
        db = Database()
        colors = db.fetch_all("SELECT color_id, color_name FROM colors")
        db.close()
        return {c[1]: c[0] for c in colors}
