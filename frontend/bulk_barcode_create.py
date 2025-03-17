import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from backend.models import Batch, Brand, Model, Size, Color
from backend.barcode_gen_print import print_barcode_zebra, get_available_printers, process_bulk_barcodes
import threading

class BulkBarcodeCreate(tk.Frame):
    """Frame for handling bulk barcode uploads, processing, and printing."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # **State Variables**
        self.df = None
        self.processed_data = []
        self.error_rows = []
        self.successful_barcodes = []
        self.duplicate_barcodes = set()

        self.printer_var = tk.StringVar()

        # **Create UI**
        self.create_widgets()
        self.refresh_printers()

    def create_widgets(self):
        """Creates all UI elements within the frame."""
        # **Main Control Panel**
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(control_frame, text="Upload Excel File", command=self.upload_excel).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(control_frame, text="Submit to Database", command=self.save_to_database).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.print_button = ttk.Button(control_frame, text="Print All", command=self.print_all_barcodes, state=tk.DISABLED)
        self.print_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        ttk.Label(control_frame, text="Select Printer:").grid(row=1, column=0, padx=5, pady=5)
        self.printer_dropdown = ttk.Combobox(control_frame, textvariable=self.printer_var, state="readonly")
        self.printer_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(control_frame, text="Generate Template", command=self.generate_template).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # **Progress Bar**
        self.progress_label = ttk.Label(self, text="", font=("Arial", 10))
        self.progress_label.pack(pady=5)
        self.progress_bar = ttk.Progressbar(self, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        # **Preview Table Frame**
        self.preview_frame = ttk.Frame(self, padding=10)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def upload_excel(self):
        """Handles Excel file upload asynchronously."""
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
        if not file_path:
            return

        try:
            self.df = pd.read_excel(file_path)

            if self.df.empty:
                messagebox.showerror("Error", "The uploaded file is empty.")
                return

            # **Run processing in a separate thread**
            self.progress_label.config(text="Processing file... Please wait.")
            self.progress_bar.start()
            threading.Thread(target=self.process_file, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")

    def process_file(self):
        """Processes the uploaded file in a separate thread to prevent UI freezing."""
        try:
            self.processed_data, self.error_rows = process_bulk_barcodes(self.df)

            # **Update UI after processing completes**
            self.controller.after(0, self.on_processing_complete)

        except Exception as e:
            self.controller.after(0, lambda: messagebox.showerror("Error", f"Processing Error: {e}"))

    def on_processing_complete(self):
        """Runs after the file processing is completed to update UI elements."""
        self.progress_bar.stop()
        self.progress_label.config(text="")

        if not self.processed_data:
            messagebox.showerror("Error", "No valid barcode data found in the uploaded file.")
            return

        self.successful_barcodes.clear()
        self.duplicate_barcodes.clear()
        self.display_preview_table()
        messagebox.showinfo("Success", "Excel file loaded and processed successfully.")
        self.update_print_button()
        
    def display_preview_table(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        if not self.processed_data:
            ttk.Label(self.preview_frame, text="No valid data to display.").pack()
            return

        tree = ttk.Treeview(self.preview_frame, columns=["Barcode", "Brand", "Model", "Size", "Color", "Quantity", "Layers", "Serial"], show="headings", height=15)

        for col in ["Barcode", "Brand", "Model", "Size", "Color", "Quantity", "Layers", "Serial"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        for row_index, row_data in enumerate(self.processed_data):
            row_values = [row_data[key] for key in row_data if key != "image"]
            tree.insert("", tk.END, values=row_values)

        tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.preview_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        if self.error_rows:
            messagebox.showwarning("Warnings", f"Some rows have errors:\n" + "\n".join(f"Row {i+2}: {msg}" for i, _, msg in self.error_rows))

    def save_to_database(self):
        """Saves processed data to the database."""
        if not self.processed_data:
            messagebox.showerror("Error", "No valid data to save.")
            return

        self.duplicate_barcodes.clear()
        success_count = 0

        for row in self.processed_data:
            barcode = row["barcode"]

            existing_batch = Batch.get_batch_by_barcode(barcode)
            if existing_batch:
                self.duplicate_barcodes.add(barcode)
                continue

            try:
                Batch.create_batch(
                    barcode,
                    Brand.get_brands().get(row["brand"], None),
                    Model.get_models().get(row["model"], None),
                    Size.get_sizes().get(row["size"], None),
                    Color.get_colors().get(row["color"], None),
                    int(row["quantity"]),
                    int(row["layers"]),
                    "{:03d}".format(int(row["serial"])),
                    1,
                    "Pending",
                )
                self.successful_barcodes.append(barcode)
                success_count += 1
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save {barcode}: {e}")

        messagebox.showinfo("Success", f"Successfully saved {success_count} records.") if success_count else None

        if self.duplicate_barcodes:
            messagebox.showwarning("Duplicates Detected", f"The following barcodes already exist and were not added:\n{', '.join(self.duplicate_barcodes)}")

        self.update_print_button()

    def print_all_barcodes(self):
        printer_name = self.printer_var.get().strip()

        if not printer_name or printer_name == "No Zebra printers found":
            messagebox.showerror("Error", "Please select a valid printer before printing!")
            return

        barcodes_to_print = set(self.successful_barcodes) | set(self.duplicate_barcodes)

        try:
            for row in self.processed_data:
                if row["barcode"] in barcodes_to_print:
                    print_barcode_zebra(row["barcode"], row["brand"], row["model"], row["size"], row["color"], row["quantity"], printer_name)

            messagebox.showinfo("Success", f"Successfully printed {len(barcodes_to_print)} barcodes!")

        except Exception as e:
            messagebox.showerror("Printing Error", f"Failed to print due to: {str(e)}")

    def refresh_printers(self):
        """Refreshes available printers in the dropdown."""
        printers = get_available_printers()
        self.printer_dropdown["values"] = printers if printers else ["No Zebra printers found"]
        self.printer_var.set(printers[0] if printers else "No Zebra printers found")

    def update_print_button(self):
        """Enables/disables the print button based on available barcodes."""
        self.print_button["state"] = tk.NORMAL if self.successful_barcodes or self.duplicate_barcodes else tk.DISABLED

    def generate_template(self):
        """Generates a template Excel file."""
        df_template = pd.DataFrame(columns=["brand", "model", "size", "color", "quantity", "layers", "serial"])
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], title="Save Template", initialfile="bulk_barcode_template.xlsx")
        if file_path:
            df_template.to_excel(file_path, index=False)
            messagebox.showinfo("Template Saved", f"Template saved at:\n{file_path}")