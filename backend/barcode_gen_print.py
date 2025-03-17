from zebra import Zebra
from backend.models import Brand, Model, Size, Color
import base36 
import hashlib
import pandas as pd 

def encode_model_name(model_name, length=2):
    hash_digest = hashlib.md5(str(model_name).encode()).hexdigest()
    hash_int = int(hash_digest, 16)
    encoded = base36.dumps(hash_int)
    return encoded[:length].upper()

def generate_barcode_string(brand_id, model_name, size_id, color_id, quantity, layers, serial):
    try:        
        brand_id = int(brand_id) if brand_id is not None else None
        size_id = int(size_id) if size_id is not None else None
        color_id = int(color_id) if color_id is not None else None
        quantity = int(quantity) if quantity is not None else None
        layers = int(layers) if layers is not None else None
        serial = int(serial) if serial is not None else None

        if None in [brand_id, size_id, color_id, quantity, layers, serial]:
            raise ValueError("One or more required values are None!")

        brand_code = base36.dumps(brand_id)

        model_code = encode_model_name(model_name)  

        size_code = base36.dumps(size_id)  

        color_code = base36.dumps(color_id)  

        quantity_code = base36.dumps(quantity)  

        layers_code = base36.dumps(layers)  

        serial_code = base36.dumps(serial)  

        barcode_string = f"{brand_code}-{model_code}-{size_code}-{color_code}-{quantity_code}-{layers_code}-{serial_code}"

        return barcode_string

    except Exception as e:
        raise

def print_barcode_zebra(barcode_string, brand, model_name, size_value, color_name, quantity, printer_name):
    z = Zebra(printer_name)

    text_info = f"Brand: {brand} | Model: {model_name}"
    text_info2 = f"Color: {color_name} | Qty: {quantity} | Size: {size_value}"

    zpl_code = f"""
            ^XA
            ^FO50,50^BY2,2.5,50
            ^BCN,80,Y,N,N
            ^FD{barcode_string}^FS
            ^FO50,210^A0N,35,35^FD{text_info}^FS  ;
            ^FO50,300^A0N,35,35^FD{text_info2}^FS ;
            ^XZ
        """

    z.output(zpl_code)

def get_available_printers():
    try:
        z = Zebra()
        printers = z.getqueues()
        return printers
    except Exception:
        return ["No Zebra printers found"]

def process_bulk_barcodes(df):
    error_rows = []
    processed_data = []

    required_columns = ["brand", "model", "size", "color", "quantity", "layers", "serial"]

    # **Ensure all required columns exist**
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # **Identify original row numbers before dropping**
    df["original_index"] = df.index

    # **Drop any row with missing values in required fields**
    df = df.dropna(subset=required_columns).reset_index(drop=True)

    # **Remove duplicate rows**
    df = df.drop_duplicates(subset=required_columns, keep="first").reset_index(drop=True)

    for _, row in df.iterrows(): 
        try:
            row_number = int(row["original_index"])
            brand_name = str(row["brand"]).strip().lower()
            size_value = str(row["size"]).strip().lower()
            color_name = str(row["color"]).strip().lower()

            # **Handle Model Name Correctly**
            model_name = str(row["model"]).strip()
            if pd.isna(model_name) or model_name == "":
                error_rows.append((row_number, row, "Model name is missing."))
                continue

            model_name = str(model_name)
            if model_name.isdigit(): 
                model_name = str(int(model_name))
            elif model_name.replace(".", "").isdigit():  
                model_name = str(int(float(model_name)))

            model_name = "".join(filter(str.isalnum, model_name))  
            if len(model_name) < 7:
                model_name = model_name.ljust(7, "0")

            # **Ensure Quantity, Layers, and Serial are Valid**
            try:
                quantity = int(row["quantity"])
                layers = int(row["layers"])
                serial = int(row["serial"])
            except ValueError:
                error_rows.append((row_number, row, "Invalid numeric values in quantity, layers, or serial."))
                continue 

            # **Validation Checks**
            row_errors = []
            if len(model_name) < 7 or not model_name.isalnum():
                row_errors.append("Model name must be at least 7 alphanumeric characters.")
            if not (1 <= quantity <= 999):
                row_errors.append("Quantity must be between 1-999.")
            if not (1 <= layers <= 99):
                row_errors.append("Layers must be between 1-99.")
            if not (1<= serial <= 999):
                row_errors.append("Serial must be between 1-999.")

            if row_errors:
                error_rows.append((row_number, row, ", ".join(row_errors)))
                continue  

            # **Fetch or Insert IDs**
            brand_id = Brand.get_brands().get(brand_name, Brand.add_brand(brand_name))
            model_id = Model.get_models().get(model_name, Model.add_model(model_name))
            size_id = Size.get_sizes().get(size_value, Size.add_size(size_value))
            color_id = Color.get_colors().get(color_name, Color.add_color(color_name))
            
            # **Generate Barcode**
            barcode_string = generate_barcode_string(brand_id, model_name, size_id, color_id, quantity, layers, serial)

            # **Append Processed Row**
            processed_data.append({
                "barcode": barcode_string,
                "brand": brand_name,
                "model": model_name,
                "size": size_value,
                "color": color_name,
                "quantity": quantity,
                "layers": layers,
                "serial": serial,
            })

        except Exception as e:
            error_rows.append((row_number, row, f"Unexpected error: {e}"))

    return processed_data, error_rows
