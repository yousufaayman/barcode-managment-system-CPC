import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from ttkthemes import ThemedTk
from backend.models import Batch, Brand, Model, Size, Color
from backend.barcode_gen_print import generate_barcode_string, generate_barcode_image, print_barcode_zebra, get_available_printers
from utils.helpers import update_font_size, zoom_slider, search_for

root = ThemedTk(theme="scidgreen")
root.title("Barcode Management System")
root.geometry("700x600")
root.minsize(400, 400)

style = ttk.Style(root)
style.theme_use("scidgreen")

def update_dropdowns():
    brand_mapping = Brand.get_brands()
    size_mapping = Size.get_sizes()
    color_mapping = Color.get_colors()

    brand_dropdown["values"] = list(brand_mapping.keys())
    size_dropdown["values"] = list(size_mapping.keys()) 
    color_dropdown["values"] = list(color_mapping.keys())

    global brand_dict, size_dict, color_dict
    brand_dict = brand_mapping
    size_dict = size_mapping
    color_dict = color_mapping

def generate_barcode():
    try:
        global brand_name, model_name, size_name, color_name, quantity
        brand_name = brand_var.get()
        model_name = model_entry.get().strip()
        size_name = size_var.get()
        color_name = color_var.get()
        quantity = int(quantity_entry.get().strip())
        layers = int(layers_entry.get().strip())
        serial = int(serial_entry.get().strip())

        brand_id = brand_dict.get(brand_name)
        size_id = size_dict.get(size_name)
        color_id = color_dict.get(color_name)
        
        print(f"Debug: brand_id={brand_id}, model_name='{model_name}', size_id={size_id}, color_id={color_id}, quantity={quantity}, layers={layers}, serial={serial}")

        if not all([brand_id, model_name, size_id, color_id, quantity, layers, serial]):
            messagebox.showerror("Error", "All fields must be filled before generating a barcode.")
            return

        if len(str(serial)) != 3:
            messagebox.showerror("Error", "Serial must be exactly 3 digits.")
            return

        barcode_string = generate_barcode_string(brand_id, model_name, size_id, color_id, quantity, layers, serial)

        img = generate_barcode_image(barcode_string, model_name, size_name, color_name, quantity, preview_only=True, )

        img = img.resize((300, 100), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        barcode_label.config(image=img)
        barcode_label.image = img
        barcode_label.barcode_string = barcode_string

        messagebox.showinfo("Success", "Barcode Generated!")

    except ValueError:
        messagebox.showerror("Error", "Numeric fields must contain valid numbers.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_batch(print_option=False):
    try:   
        barcode_string = barcode_label.barcode_string
        if not barcode_string:
            messagebox.showerror("Error", "No barcode generated yet!")
            return

        model_names = Model.get_models()

        model_name = model_entry.get().strip()

        if model_name in model_names:
            model_id = model_names[model_name]
        else:
            Model.add_model(model_name)
            model_names = Model.get_models()
            model_id = model_names[model_name]

        
        
        file_path = filedialog.asksaveasfilename(
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")],
            title="Save Barcode Image"
        )

        if not file_path: 
            return

        generate_barcode_image(barcode_string, model_name, size_name, color_name, quantity, save_path=file_path, preview_only=False)

        
        Batch.create_batch(
            barcode_string,
            int(brand_dict.get(brand_var.get())),
            int(model_id), 
            int(size_dict.get(size_var.get())),
            int(color_dict.get(color_var.get())),
            int(quantity_entry.get()),
            int(layers_entry.get()),
            int(serial_entry.get()),
            1,
            "Pending",
        )

        if print_option:
            print_barcode(barcode_string)

        messagebox.showinfo("Success", f"Barcode saved successfully!\nSaved at: {file_path}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def print_barcode(barcode_string):
    printer_name = printer_var.get()
    if printer_name == "No Zebra printers found":
        messagebox.showerror("Error", "No available Zebra printers!")
        return

    print_barcode_zebra(barcode_string, model_name, size_name, color_name, quantity, printer_name)
    messagebox.showinfo("Printing", "Barcode sent to printer!")

def open_search_popup(search_term, entry_widget):
    popup = tk.Toplevel(root)
    popup.title(f"Search {search_term}")
    popup.geometry("300x300")
    
    search_var = tk.StringVar()
    search_entry = ttk.Entry(popup, textvariable=search_var)
    search_entry.pack(pady=5, padx=5, fill="x")
    
    results_listbox = tk.Listbox(popup)
    results_listbox.pack(pady=5, padx=5, fill="both", expand=True)
    
    def update_results(event=None):
        query = search_var.get()
        results_listbox.delete(0, tk.END)
        results = search_for(search_term, query)

        for _, name in results:
            results_listbox.insert(tk.END, name)

    search_var.trace_add("write", lambda *args: update_results())
    
    def select_item(event=None):
        selected_item = results_listbox.get(tk.ACTIVE)
        if selected_item:
            if isinstance(entry_widget, tk.StringVar):  
                entry_widget.set(selected_item)
            elif isinstance(entry_widget, ttk.Combobox):  
                entry_widget.set(selected_item)
            elif isinstance(entry_widget, tk.Entry):  
                entry_widget.delete(0, tk.END)  
                entry_widget.insert(0, selected_item)  
            popup.destroy()

    results_listbox.bind("<Double-Button-1>", select_item)  
    search_entry.bind("<Return>", lambda event: select_item())  

    update_results()
    popup.mainloop()

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

frame.columnconfigure(1, weight=1)

zoom_slider(root, style)

ttk.Label(frame, text="Brand:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
brand_var = tk.StringVar()
brand_dropdown = ttk.Combobox(frame, textvariable=brand_var, state="readonly")
brand_dropdown.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
ttk.Button(frame, text="🔍", command=lambda: open_search_popup("Brand", brand_var)).grid(row=0, column=2, padx=5, pady=5)

ttk.Label(frame, text="Model Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
model_entry = ttk.Entry(frame)
model_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
ttk.Button(frame, text="🔍", command=lambda: open_search_popup("Model", model_entry)).grid(row=1, column=2, padx=5, pady=5)

ttk.Label(frame, text="Size:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
size_var = tk.StringVar()
size_dropdown = ttk.Combobox(frame, textvariable=size_var, state="readonly")
size_dropdown.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
ttk.Button(frame, text="🔍", command=lambda: open_search_popup("Size", size_var)).grid(row=2, column=2, padx=5, pady=5)

ttk.Label(frame, text="Color:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
color_var = tk.StringVar()
color_dropdown = ttk.Combobox(frame, textvariable=color_var, state="readonly")
color_dropdown.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
ttk.Button(frame, text="🔍", command=lambda: open_search_popup("Color", color_var)).grid(row=3, column=2, padx=5, pady=5)

ttk.Label(frame, text="Quantity:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
quantity_entry = ttk.Entry(frame)
quantity_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

ttk.Label(frame, text="Layers:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
layers_entry = ttk.Entry(frame)
layers_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

ttk.Label(frame, text="Serial (3 digits):").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
serial_entry = ttk.Entry(frame)
serial_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=5)

ttk.Button(frame, text="Generate Barcode", command=generate_barcode).grid(row=7, column=0, columnspan=2, pady=10)

barcode_label = ttk.Label(frame)
barcode_label.grid(row=8, column=0, columnspan=2, pady=10)

ttk.Label(frame, text="Select Printer:").grid(row=9, column=0, sticky=tk.W, padx=5, pady=5)
printer_var = tk.StringVar()
printer_dropdown = ttk.Combobox(frame, textvariable=printer_var, values=get_available_printers(), state="readonly")
printer_dropdown.grid(row=9, column=1, sticky="ew", padx=5, pady=5)

button_frame = ttk.Frame(frame)
button_frame.grid(row=10, column=0, columnspan=2, pady=10, sticky="ew")
button_frame.columnconfigure(0, weight=1)
button_frame.columnconfigure(1, weight=1)

ttk.Button(button_frame, text="Save & Print", command=lambda: save_batch(print_option=True)).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
ttk.Button(button_frame, text="Save Only", command=lambda: save_batch(print_option=False)).grid(row=0, column=1, padx=5, pady=5, sticky="ew")


update_font_size(12, style)
update_dropdowns()
root.mainloop()
