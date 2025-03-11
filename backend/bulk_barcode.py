import pandas as pd
from backend.models import Batch, Brand, Model, Size, Color
from backend.barcode_gen_print import generate_barcode_string, generate_barcode_image

def process_bulk_barcodes(df):
    error_rows = []
    processed_data = []

    required_columns = ["brand_name", "model_name", "size_value", "color_name", "quantity", "layers", "serial"]

    # **Identify rows with missing values and log errors**
    missing_values_rows = df[df[required_columns].isnull().any(axis=1)]
    for index, row in missing_values_rows.iterrows():
        error_rows.append((index, row, "Missing required values."))

    # **Drop rows with missing values in critical fields**
    df = df.dropna(subset=required_columns).reset_index(drop=True)

    # **Remove duplicate rows based on all fields**
    df = df.drop_duplicates(subset=required_columns, keep="first").reset_index(drop=True)

    for index, row in df.iterrows():
        try:
            brand_name = str(row["brand_name"]).strip().lower()
            model_name = str(row["model_name"]).strip().lower()
            size_value = str(row["size_value"]).strip().lower()
            color_name = str(row["color_name"]).strip().lower()
            quantity = str(row["quantity"]).strip()
            layers = str(row["layers"]).strip()
            serial = str(row["serial"]).strip().zfill(3) 

            row_errors = []

            if len(model_name) < 7 or not model_name.isalnum():
                row_errors.append("Model name must be at least 7 alphanumeric characters.")
            if not quantity.isdigit() or not (1 <= int(quantity) <= 999):
                row_errors.append("Quantity must be between 1-999.")
            if not layers.isdigit() or not (1 <= int(layers) <= 99):
                row_errors.append("Layers must be between 1-99.")
            if not serial.isdigit() or len(serial) != 3:
                row_errors.append("Serial must be exactly 3 digits.")

            if row_errors:
                error_rows.append((index, row, ", ".join(row_errors)))
                continue  

            brand_id = Brand.get_brands().get(brand_name, Brand.add_brand(brand_name))
            model_id = Model.get_models().get(model_name, Model.add_model(model_name))
            size_id = Size.get_sizes().get(size_value, Size.add_size(size_value))
            color_id = Color.get_colors().get(color_name, Color.add_color(color_name))

            barcode_string = generate_barcode_string(brand_id, model_name, size_id, color_id, quantity, layers, serial)

            barcode_img = generate_barcode_image(barcode_string, model_name, size_value, color_name, quantity, preview_only=True)

            processed_data.append({
                "barcode": barcode_string,
                "brand": brand_name,
                "model": model_name,
                "size": size_value,
                "color": color_name,
                "quantity": quantity,
                "layers": layers,
                "serial": serial,
                "image": barcode_img
            })

        except Exception as e:
            error_rows.append((index, row, f"Unexpected error: {e}"))

    return processed_data, error_rows
