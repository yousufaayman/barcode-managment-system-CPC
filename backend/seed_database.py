import pandas as pd
import sqlite3
from backend.models import Brand, Model, Size, Color  

DB_PATH = "barcode_management.db"

def load_excel(file_path):
    """Loads an Excel file and returns its sheet data as a dictionary."""
    try:
        return pd.read_excel(file_path, sheet_name=None)
    except Exception as e:
        raise Exception(f"Error reading Excel file: {e}")

def seed_database(df_dict):
    """Seeds the database with data from the provided DataFrame dictionary."""
    table_mappings = {
        "brands": ("brand_name", Brand.add_brand),
        "models": ("model_name", Model.add_model),
        "sizes": ("size_value", Size.add_size),
        "colors": ("color_name", Color.add_color),
    }

    try:
        success_count = 0
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for sheet, df in df_dict.items():
            if sheet in table_mappings:
                _, insert_func = table_mappings[sheet]

                print(f"\nProcessing Sheet: {sheet}")  # Debugging
                print(df)  # Print sheet content

                if df.empty:
                    print(f"❌ {sheet} is EMPTY! Skipping...")
                    continue

                for index, row in df.iterrows():
                    try:
                        values = tuple(row)
                        print(f"Inserting into {sheet}: {values}")  # Debugging Output
                        insert_func(*values)  
                        success_count += 1
                    except Exception as e:
                        print(f"Skipping duplicate or error in {sheet}: {row} - {e}")  

        conn.commit()
        conn.close()

        return f"Database seeded successfully. {success_count} records inserted."
    except Exception as e:
        raise Exception(f"Failed to seed database: {e}")



def generate_template(file_path):
    """Creates an Excel file template without empty columns."""
    try:
        # Define correct column structure
        data = {
            "brand_name": [],
            "model_name": [],
            "size_value": [],
            "color_name": []
        }

        df_template = pd.DataFrame(data)

        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            df_template.to_excel(writer, sheet_name="Data", index=False)

        return "Template generated successfully."
    except Exception as e:
        raise Exception(f"Failed to generate template: {e}")
