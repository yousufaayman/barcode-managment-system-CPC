from tkinter import ttk
from backend.models import Batch, Brand, Model, Size, Color

def update_font_size(size, style):
    size = int(float(size))
    default_font = ("Arial", size)
    header_font = ("Arial", size + 2, "bold")

    style.configure(".", font=default_font)
    style.configure("TLabel", font=default_font)
    style.configure("TButton", font=header_font, padding=6)
    style.configure("TEntry", font=default_font)
    style.configure("TCombobox", font=default_font)
    
def zoom_slider(root, style):
    zoom_label = ttk.Label(root, text="Zoom:")
    zoom_label.pack(pady=5)

    zoom_slider = ttk.Scale(root, from_=8, to=20, orient="horizontal", command=lambda size: update_font_size(size, style))
    zoom_slider.set(12)
    zoom_slider.pack(pady=5)
    
def search_for(search_term, value):
    value = value.lower()

    if search_term == "Brand":
        results = [(brand_id, brand_name) for brand_name, brand_id in Brand.get_brands().items() if value in brand_name.lower()]
    elif search_term == "Model":
        results = [(model_id, model_name) for model_name, model_id in Model.get_models().items() if value in model_name.lower()]
    elif search_term == "Size":
        results = [(size_id, size_name) for size_name, size_id in Size.get_sizes().items() if value in size_name.lower()]
    elif search_term == "Color":
        results = [(color_id, color_name) for color_name, color_id in Color.get_colors().items() if value in color_name.lower()]
    else:
        return []

    return results 


