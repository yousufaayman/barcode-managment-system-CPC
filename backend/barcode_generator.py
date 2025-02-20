import barcode
from barcode.writer import ImageWriter
from zebra import Zebra


def generate_barcode_string(brand_id, model_id, size_id, color_id, quantity, layers, serial):
    return f"{brand_id:02d}-{model_id:07d}-{size_id:03d}-{color_id:03d}-{quantity:02d}-{layers:02d}-{serial:03d}"

def generate_barcode_image(barcode_string):
    code128 = barcode.get("code128", barcode_string, writer=ImageWriter())
    filename = f"barcodes/{barcode_string}.png"
    code128.save(filename)
    return filename

def print_barcode_zebra(barcode_string, printer_name):
    z = Zebra(printer_name)
    barcode_path = f"barcodes/{barcode_string}.png"
    z.print_image(barcode_path)
