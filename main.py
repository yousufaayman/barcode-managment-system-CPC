import sqlite3
from backend.models import User, Batch, Shipment, Brand, Model, Size, Color, ProductionPhase

def test_database():
    print("Starting database and model tests...")

    # User.create_user("admin", "Password", "Admin")
    # User.create_user("Packaging1", "Password", "Packaging")
    
    Brand.add_brand("bdtk")
    Size.add_size("small")
    Color.add_color("red")   
    ProductionPhase.add_production_phase("Cutting")
    
if __name__ == "__main__":
    test_database()
