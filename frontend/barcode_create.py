import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from models import Batch, Brand, Model, Size, Color
from barcode_generator import generate_barcode_string, generate_barcode_image, print_barcode_zebra
import os
from zebra import Zebra

# Function to update dropdowns dynamically
def update_dropdowns():
    brands = Brand.get_brands()
    sizes = Size.get_sizes()
    colors = Color.get_colors()

    brand_dropdown["values"] = [b[0] for b in brands]
    size_dropdown["values"] = [s[0] for s in sizes]
    color_dropdown["values"] = [c[0] for c in colors]

# Function to get available printers
def get_available_printers():
    try:
        z = Zebra()
        printers = z.getqueues()
        return printers
    except Exception as e:
        return ["No Zebra printers found"]

# Function to generate barcode and preview it
def generate_barcode():
    try:
        brand_id = int(brand_var.get())
        model_name = model_entry.get().strip()
        size_id = int(size_var.get())
        color_id = int(color_var.get())
        quantity = int(quantity_entry.get())
        layers = int(layers_entry.get())
        serial = int(serial_entry.get())

        if len(str(serial)) != 3:
            messagebox.showerror("Error", "Serial must be 3 digits.")
            return

        # Insert model and get ID
        model_id = Model.add_model(model_name)

        # Generate barcode string
        barcode_string = generate_barcode_string(brand_id, model_id, size_id, color_id, quantity, layers, serial)

        # Generate barcode image
        barcode_path = generate_barcode_image(barcode_string)

        # Update UI with barcode preview
        img = Image.open(barcode_path)
        img = img.resize((300, 100), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        barcode_label.config(image=img)
        barcode_label.image = img

        # Save barcode string for later use
        barcode_label.barcode_string = barcode_string

        messagebox.showinfo("Success", "Barcode Generated!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to save batch
def save_batch(print_option=False):
    try:
        barcode_string = barcode_label.barcode_string
        if not barcode_string:
            messagebox.showerror("Error", "No barcode generated yet!")
            return

        # Save batch in DB
        Batch.create_batch(
            barcode_string,
            int(brand_var.get()),
            Model.add_model(model_entry.get().strip()),
            int(size_var.get()),
            int(color_var.get()),
            int(quantity_entry.get()),
            int(layers_entry.get()),
            int(serial_entry.get()),
            1,
            "Pending",
        )

        if print_option:
            print_barcode(barcode_string)

        messagebox.showinfo("Success", "Batch Saved Successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to print barcode
def print_barcode(barcode_string):
    printer_name = printer_var.get()
    if printer_name == "No Zebra printers found":
        messagebox.showerror("Error", "No available Zebra printers!")
        return

    print_barcode_zebra(barcode_string, printer_name)
    messagebox.showinfo("Printing", "Barcode sent to printer!")

# UI Setup
root = tk.Tk()
root.title("Barcode Generator")

# Brand Dropdown + Add Entry
tk.Label(root, text="Brand:").grid(row=0, column=0)
brand_var = tk.StringVar()
brand_dropdown = ttk.Combobox(root, textvariable=brand_var, state="readonly")
brand_dropdown.grid(row=0, column=1)

# Model Input
tk.Label(root, text="Model Name:").grid(row=1, column=0)
model_entry = tk.Entry(root)
model_entry.grid(row=1, column=1)

# Size Dropdown + Add Entry
tk.Label(root, text="Size:").grid(row=2, column=0)
size_var = tk.StringVar()
size_dropdown = ttk.Combobox(root, textvariable=size_var, state="readonly")
size_dropdown.grid(row=2, column=1)

# Color Dropdown + Add Entry
tk.Label(root, text="Color:").grid(row=3, column=0)
color_var = tk.StringVar()
color_dropdown = ttk.Combobox(root, textvariable=color_var, state="readonly")
color_dropdown.grid(row=3, column=1)

# Quantity Input
tk.Label(root, text="Quantity:").grid(row=4, column=0)
quantity_entry = tk.Entry(root)
quantity_entry.grid(row=4, column=1)

# Layers Input
tk.Label(root, text="Layers:").grid(row=5, column=0)
layers_entry = tk.Entry(root)
layers_entry.grid(row=5, column=1)

# Serial Input
tk.Label(root, text="Serial (3 digits):").grid(row=6, column=0)
serial_entry = tk.Entry(root)
serial_entry.grid(row=6, column=1)

# Generate Barcode Button
tk.Button(root, text="Generate Barcode", command=generate_barcode).grid(row=7, column=0, columnspan=2)

# Barcode Preview Label
barcode_label = tk.Label(root)
barcode_label.grid(row=8, column=0, columnspan=3)

# Printer Dropdown
tk.Label(root, text="Select Printer:").grid(row=9, column=0)
printer_var = tk.StringVar()
printers = get_available_printers()
printer_dropdown = ttk.Combobox(root, textvariable=printer_var, values=printers, state="readonly")
printer_dropdown.grid(row=9, column=1)

# Save and Print Buttons
tk.Button(root, text="Save & Print", command=lambda: save_batch(print_option=True)).grid(row=10, column=0)
tk.Button(root, text="Save Only", command=lambda: save_batch(print_option=False)).grid(row=10, column=1)

# Initialize dropdowns with DB values
update_dropdowns()

# Start UI Loop
root.mainloop()
