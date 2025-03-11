import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
import pandas as pd
from backend.models import Batch, Brand, Model, Size, Color
from backend.bulk_barcode import process_bulk_barcodes
from backend.barcode_gen_print import print_barcode_zebra, get_available_printers

df = None
processed_data = []
error_rows = []
successful_barcodes = []
duplicate_barcodes = set()

def upload_excel():
    global df, processed_data, error_rows, successful_barcodes
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
    if not file_path:
        return

    try:
        df = pd.read_excel(file_path)
        processed_data, error_rows = process_bulk_barcodes(df)
        successful_barcodes.clear()
        duplicate_barcodes.clear()
        display_preview_table()
        messagebox.showinfo("Success", "Excel file loaded and processed successfully.")
        update_print_button()
    except Exception as e:
        messagebox.showerror("Error", f"Error reading file: {e}")

def display_preview_table():
    for widget in preview_frame.winfo_children():
        widget.destroy()

    if not processed_data:
        ttk.Label(preview_frame, text="No valid data to display.").pack()
        return

    global tree
    tree = ttk.Treeview(preview_frame, columns=["Barcode", "Brand", "Model", "Size", "Color", "Quantity", "Layers", "Serial"], show="headings", height=15)

    for col in ["Barcode", "Brand", "Model", "Size", "Color", "Quantity", "Layers", "Serial"]:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)

    for row_index, row_data in enumerate(processed_data):
        row_id = tree.insert("", tk.END, values=[row_data[key] for key in row_data if key != "image"])
        if any(row_index == err_row for err_row, _, _ in error_rows):  # Highlight error rows
            tree.item(row_id, tags=("error",))

    tree.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.tag_configure("error", background="orange", foreground="black")

    if error_rows:
        messagebox.showwarning("Warnings", f"Some rows have errors:\n" + "\n".join(f"Row {i+2}: {msg}" for i, _, msg in error_rows))

def save_to_database():
    if not processed_data:
        messagebox.showerror("Error", "No valid data to save.")
        return

    global duplicate_barcodes
    duplicate_barcodes.clear()
    invalid_rows = {}
    success_count = 0

    for row_index, row in enumerate(processed_data):
        barcode = row["barcode"]

        existing_batch = Batch.get_batch_by_barcode(barcode)
        if existing_batch:
            duplicate_barcodes.add(barcode)
            highlight_row(row_index, "#274AB3")
            continue

        serial = row["serial"].zfill(3)

        try:
            Batch.create_batch(
                barcode,
                Brand.get_brands().get(row["brand"], None),
                Model.get_models().get(row["model"], None),
                Size.get_sizes().get(row["size"], None),
                Color.get_colors().get(row["color"], None),
                int(row["quantity"]),
                int(row["layers"]),
                serial,
                1,
                "Pending",
            )
            successful_barcodes.append(barcode)
            highlight_row(row_index, "#38843e")
            success_count += 1
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save {barcode}: {e}")

    if success_count > 0:
        messagebox.showinfo("Success", f"Successfully saved {success_count} records.")

    if duplicate_barcodes:
        messagebox.showwarning("Duplicates Detected",
                               f"The following barcodes already exist and were not added:\n{', '.join(duplicate_barcodes)}")

    if invalid_rows:
        invalid_messages = "\n".join([f"Row {idx + 1}: {', '.join(errors)}" for idx, errors in invalid_rows.items()])
        messagebox.showwarning("Invalid Data Detected", f"The following rows contain errors:\n{invalid_messages}")

    update_print_button()  # Enable print button if valid data is submitted

def highlight_row(row_index, color):
    tree.tag_configure(color, background=color, foreground="white")
    row_id = tree.get_children()[row_index]
    tree.item(row_id, tags=(color,))

def print_all_barcodes():
    printer_name = printer_var.get().strip()

    if not printer_name or printer_name == "No Zebra printers found":
        messagebox.showerror("Error", "Please select a valid printer before printing!")
        return

    if not successful_barcodes and not duplicate_barcodes:
        messagebox.showwarning("Printing", "No valid barcodes available for printing.")
        return

    barcodes_to_print = set(successful_barcodes) | set(duplicate_barcodes)

    try:
        for row in processed_data:
            if row["barcode"] in barcodes_to_print:
                print_barcode_zebra(row["barcode"], row["model"], row["size"], row["color"], row["quantity"], printer_name)

        messagebox.showinfo("Success", f"Successfully printed {len(barcodes_to_print)} barcodes!")

    except Exception as e:
        messagebox.showerror("Printing Error", f"Failed to print due to: {str(e)}")

def update_print_button():
    if successful_barcodes or duplicate_barcodes:
        print_button["state"] = tk.NORMAL
    else:
        print_button["state"] = tk.DISABLED

root = ThemedTk(theme="scidgreen")
root.title("Bulk Barcode Generator")
root.geometry("900x600")
root.minsize(700, 500)

style = ttk.Style(root)
style.theme_use("scidgreen")

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Button(frame, text="Upload Excel File", command=upload_excel).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
ttk.Button(frame, text="Submit to Database", command=save_to_database).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

print_button = ttk.Button(frame, text="Print All", command=print_all_barcodes, state=tk.DISABLED)  # Initially disabled
print_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

ttk.Label(frame, text="Select Printer:").grid(row=1, column=0, padx=5, pady=5)
printer_var = tk.StringVar()
printer_dropdown = ttk.Combobox(frame, textvariable=printer_var, values=get_available_printers(), state="readonly")
printer_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

preview_frame = ttk.Frame(root, padding=10)
preview_frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
