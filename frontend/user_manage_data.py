import tkinter as tk
from tkinter import ttk, messagebox
from ttkwidgets import CheckboxTreeview
from backend.models import Batch, Brand, Size, Color, ProductionPhase
from backend.barcode_gen_print import get_available_printers, print_barcode_zebra 


class UserManageData(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_filter_frame()
        self.create_table_frame()
        self.populate_dropdowns()
        self.filter_batches()

    def create_filter_frame(self):
        """Creates the filtering frame with dropdowns and entry fields."""
        self.filter_frame = ttk.Frame(self, padding=10)
        self.filter_frame.grid(row=0, column=0, sticky="ew")

        self.grid_columnconfigure(0, weight=1)
        self.filter_frame.grid_columnconfigure(0, weight=0) 
        self.filter_frame.grid_columnconfigure(1, weight=1) 

        # **Filter Variables**
        self.barcode_var = tk.StringVar()
        self.brand_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.size_var = tk.StringVar()
        self.color_var = tk.StringVar()
        self.phase_var = tk.StringVar()
        self.serial_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.printer_var = tk.StringVar()

        # **Ensure correct layout by alternating columns (Label, Input)**
        ttk.Label(self.filter_frame, text="Barcode:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.barcode_entry = ttk.Entry(self.filter_frame, textvariable=self.barcode_var)
        self.barcode_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.filter_frame, text="Brand:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.brand_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.brand_var, state="normal")
        self.brand_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(self.filter_frame, text="Model:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.model_entry = ttk.Entry(self.filter_frame, textvariable=self.model_var)
        self.model_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        ttk.Label(self.filter_frame, text="Size:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.size_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.size_var, state="normal")
        self.size_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.filter_frame, text="Color:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.color_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.color_var, state="normal")
        self.color_dropdown.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(self.filter_frame, text="Serial:").grid(row=1, column=4, padx=5, pady=5, sticky="w")
        self.serial_entry = ttk.Entry(self.filter_frame, textvariable=self.serial_var)
        self.serial_entry.grid(row=1, column=5, padx=5, pady=5, sticky="ew")

        ttk.Label(self.filter_frame, text="Phase:").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.phase_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.phase_var, state="normal")
        self.phase_dropdown.grid(row=0, column=7, padx=5, pady=5, sticky="ew")

        ttk.Label(self.filter_frame, text="Status:").grid(row=1, column=6, padx=5, pady=5, sticky="w")
        self.status_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.status_var, state="readonly")
        self.status_dropdown.grid(row=1, column=7, padx=5, pady=5, sticky="ew")

        # **Filter Buttons**
        filter_button = ttk.Button(self.filter_frame, text="Filter", command=self.filter_batches)
        filter_button.grid(row=0, column=8, padx=5, pady=5, sticky="ew")

        clear_button = ttk.Button(self.filter_frame, text="Clear Filters", command=self.clear_filters)
        clear_button.grid(row=1, column=8, padx=5, pady=5, sticky="ew")

        printers = ["Select Printer"] + get_available_printers()
        self.printer_var = tk.StringVar(value="Select Printer")
        self.printer_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.printer_var, values=printers, state="readonly")
        self.printer_dropdown.grid(row=0, column=9, padx=5, pady=5, sticky="ew")
        
        # **Print Button**
        self.print_button = ttk.Button(self.filter_frame, text="Print Selected", command=self.print_selected_barcodes)
        self.print_button.grid(row=1, column=9, padx=5, pady=5, sticky="ew")

        
        # **Ensure the filter frame resizes properly**
        for i in range(11): 
            self.filter_frame.grid_columnconfigure(i, weight=(1 if i % 2 == 1 else 0))  

    def create_table_frame(self):
        """Creates the table frame and ensures it fills the available space."""
        self.table_frame = ttk.Frame(self, padding=10)
        self.table_frame.grid(row=1, column=0, sticky="nsew")

        # Ensure it expands
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Create the Treeview
        self.tree = CheckboxTreeview(
            self.table_frame,
            columns=["Barcode", "Brand", "Model", "Size", "Color", "Quantity", "Layers", "Serial", "Phase", "Status"],
            show="headings"
        )

        # Configure columns
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120, stretch=True)

        self.tree.grid(row=0, column=0, sticky="nsew")  # Ensure Treeview expands

        # Scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew", columnspan=2)
        self.tree.configure(xscrollcommand=hsb.set)

        # Ensure full expansion
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

    def populate_dropdowns(self):
        self.brand_dropdown["values"] = list(Brand.get_brands().keys())
        self.size_dropdown["values"] = list(Size.get_sizes().keys())
        self.color_dropdown["values"] = list(Color.get_colors().keys())
        self.phase_dropdown["values"] = list(ProductionPhase.get_phases().keys())
        self.status_dropdown["values"] = ["Pending", "In Progress", "Completed"]

    def filter_batches(self):
        filters = {
            "barcode": self.barcode_var.get().strip().lower(),
            "brand": self.brand_var.get().strip().lower(),
            "model": self.model_var.get().strip().lower(),
            "size": self.size_var.get().strip().lower(),
            "color": self.color_var.get().strip().lower(),
            "phase": self.phase_var.get().strip().lower(),
            "serial": self.serial_var.get().strip().lower(),
            "status": self.status_var.get().strip().lower()
        }

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.tree = CheckboxTreeview(
            self.table_frame, 
            columns=["Barcode", "Brand", "Model", "Size", "Color", "Quantity", "Layers", "Serial", "Phase", "Status"],
            show="tree headings"
        )

        self.tree.column("#0", width=50, stretch=False)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120, stretch=True)

        self.select_all_var = tk.BooleanVar()
        self.tree.heading("#0", text="☑", command=self.select_all) 
        
        filter_mapping = {
        "barcode": 0,
        "brand": 1,
        "model": 2,
        "size": 3,
        "color": 4,
        "serial": 7,
        "phase": 8,
        "status": 9
            }

        
        batches = Batch.get_batches()
        for batch in batches:
            batch_id = batch[0]
            display_batch = batch[1:]
            match = True
            for key, idx in filter_mapping.items():
                if filters[key] and filters[key] not in str(display_batch[idx]).lower():
                    match = False
                    break
            if match:
                self.tree.insert("", tk.END, values=display_batch, tags=("unchecked", str(batch_id)))

        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew", columnspan=2)
        self.tree.configure(xscrollcommand=hsb.set)

        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.tree.grid_rowconfigure(0, weight=1)
        self.tree.grid_columnconfigure(0, weight=1)

    def clear_filters(self):
        """Clears all filter inputs and resets the table."""
        self.barcode_var.set('')
        self.brand_var.set('')
        self.model_var.set('')
        self.size_var.set('')
        self.color_var.set('')
        self.phase_var.set('')
        self.serial_var.set('')
        self.status_var.set('')
        self.filter_batches()

    def print_selected_barcodes(self):
        selected_items = self.tree.get_checked()
        if not selected_items:
            messagebox.showerror("Error", "No barcodes selected for printing.")
            return

        printer_name = self.printer_var.get().strip()
        if printer_name == "Select Printer" or not printer_name:
            messagebox.showerror("Error", "Please select a valid printer before printing!")
            return

        try:
            for item in selected_items:
                values = self.tree.item(item, "values")
                barcode = values[0]
                model = values[2]
                size = values[3]
                color = values[4]
                quantity = values[5]

                print_barcode_zebra(barcode, model, size, color, quantity, printer_name)

            messagebox.showinfo("Success", f"Successfully printed {len(selected_items)} barcodes!")

        except Exception as e:
            messagebox.showerror("Printing Error", f"Failed to print due to: {str(e)}")
    
    def select_all(self):
        """Toggles selection of all checkboxes in the treeview."""
        all_items = self.tree.get_children()
        checked_items = self.tree.get_checked()

        if len(checked_items) == len(all_items):  # If all are selected, deselect all
            for item in all_items:
                self.tree.change_state(item, "unchecked")
        else:  # Otherwise, select all
            for item in all_items:
                self.tree.change_state(item, "checked")

