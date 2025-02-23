import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from backend.barcode_scanning import process_scanned_barcode  
from backend.models import Batch, ProductionPhase
from utils.helpers import update_font_size, zoom_slider

root = ThemedTk(theme="scidgreen")
root.title("Barcode Management System")
root.geometry("800x600")
root.minsize(600, 500)

style = ttk.Style(root)
style.theme_use("scidgreen")

scanner_var = tk.StringVar()
current_batch_id = None
entry_vars = {}

def update_batch_info(batch):
    global current_batch_id

    if batch:
        current_batch_id = batch[0]

        headers = ["Barcode", "Brand", "Model", "Size", "Color", "Quantity", "Layers", "Serial", "Phase", "Status"]
        values = batch[1:]

        for widget in batch_info_frame.winfo_children():
            widget.grid_forget()

        for i, (header, value) in enumerate(zip(headers, values)):
            ttk.Label(batch_info_frame, text=header + ":", font=("Arial", 10, "bold"), anchor="w").grid(row=i, column=0, sticky="w", padx=10, pady=2)

            if header in ["Phase", "Status"]:
                if header not in entry_vars:
                    entry_vars[header] = tk.StringVar(value=value)

                dropdown = ttk.Combobox(batch_info_frame, textvariable=entry_vars[header], state="readonly")

                if header == "Phase":
                    dropdown["values"] = [p[1] for p in ProductionPhase.get_phases()]
                else:
                    dropdown["values"] = ["Pending", "In Progress", "Completed"]

                dropdown.grid(row=i, column=1, sticky="ew", padx=10, pady=2)

            else:
                ttk.Label(batch_info_frame, text=value, font=("Arial", 10), anchor="w").grid(row=i, column=1, sticky="ew", padx=10, pady=2)

        update_button.grid(row=len(headers), column=0, columnspan=2, pady=10)

    else:
        for widget in batch_info_frame.winfo_children():
            widget.grid_forget()
        ttk.Label(batch_info_frame, text="Batch not found.", font=("Arial", 10, "bold"), foreground="red").grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=10)

def update_batch():
    if current_batch_id:
        new_phase = entry_vars["Phase"].get()
        new_status = entry_vars["Status"].get()

        phase_id = next((p[0] for p in ProductionPhase.get_phases() if p[1] == new_phase), None)

        if phase_id:
            Batch.update_batch_phase(current_batch_id, phase_id)
            Batch.update_batch_status(current_batch_id, new_status)
            messagebox.showinfo("Success", "Batch updated successfully!")
        else:
            messagebox.showerror("Error", "Invalid phase selected.")

def on_barcode_scan(event=None):
    scanned_code = scanner_var.get().strip()
    if scanned_code:
        batch = process_scanned_barcode(scanned_code)
        update_batch_info(batch)
        scanner_var.set("")
    return "break"

hidden_scanner_entry = tk.Entry(root, textvariable=scanner_var, font=("Arial", 1), width=1)
hidden_scanner_entry.place(x=-100, y=-100)
hidden_scanner_entry.bind("<Return>", on_barcode_scan) 

def focus_scanner_entry():
    hidden_scanner_entry.focus_set()
    root.after(500, focus_scanner_entry)

root.after(500, focus_scanner_entry)

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Scan Barcode:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Label(frame, text="(Automatic input - scan to load batch details)", font=("Arial", 10)).grid(row=0, column=1, padx=5, pady=5, sticky="w")

batch_info_frame = ttk.LabelFrame(frame, text="Batch Information", padding=10)
batch_info_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
batch_info_frame.columnconfigure(0, weight=1)
batch_info_frame.columnconfigure(1, weight=1)

update_button = ttk.Button(batch_info_frame, text="Edit", command=update_batch)
update_button.grid(row=11, column=0, columnspan=2, pady=10)

def apply_zoom():
    update_font_size(12, style)
    for widget in batch_info_frame.winfo_children():
        if isinstance(widget, ttk.Label):
            widget.configure(font=("Arial", 12))  

zoom_slider(root, style)
root.bind("<Configure>", lambda e: apply_zoom())

root.mainloop()
