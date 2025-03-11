import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from zebra import Zebra


def generate_barcode_string(brand_id, model_name, size_id, color_id, quantity, layers, serial):
    if None in [brand_id, model_name, size_id, color_id, quantity, layers, serial]:
        raise ValueError("One or more required values are None. Please check your inputs.")

    if not isinstance(model_name, str):
        model_name = str(model_name)

    return f"{int(brand_id):02d}-{model_name}-{int(size_id):03d}-{int(color_id):03d}-{int(quantity):03d}-{int(layers):02d}-{int(serial):03d}"

def generate_barcode_image(barcode_string, model_name, size_value, color_name, quantity, save_path=None, preview_only=False):
    try:
        code128 = barcode.get("code128", barcode_string, writer=ImageWriter())
        barcode_buffer = BytesIO()
        code128.write(barcode_buffer)

        barcode_buffer.seek(0)
        barcode_img = Image.open(barcode_buffer)

        text_info1 = f"Model: {model_name}  |  Size: {size_value}"
        text_info2 = f"Color: {color_name}  |  Qty: {quantity}"

        text_height = 150  
        new_height = barcode_img.height + text_height
        new_img = Image.new("RGB", (barcode_img.width + 20, new_height), "white")

        new_img.paste(barcode_img, (0, 0))

        draw = ImageDraw.Draw(new_img)

        try:
            font = ImageFont.truetype("arial.ttf", 40)  
        except IOError:
            font = ImageFont.load_default()

        text_x = 20  
        text_y1 = barcode_img.height + 20  
        text_y2 = barcode_img.height + 80  

        draw.text((text_x, text_y1), text_info1, fill="black", font=font)
        draw.text((text_x, text_y2), text_info2, fill="black", font=font)

        if preview_only:
            return new_img

        if save_path:
            new_img.save(f"{save_path}.png")
            return save_path
        else:
            raise ValueError("Save path not provided for barcode image.")

    except Exception as e:
        raise RuntimeError(f"Error generating barcode image: {str(e)}")

def print_barcode_zebra(barcode_string, model_name, size_value, color_name, quantity, printer_name):
    z = Zebra(printer_name)
    
    text_info = f"Model: {model_name}| Size: {size_value}"
    text_info2 = f"Color: {color_name}| Qty: {quantity}"
    
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

