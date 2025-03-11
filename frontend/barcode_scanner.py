import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from backend.barcode_scanning import process_scanned_barcode  
from backend.models import Batch, ProductionPhase

root = ThemedTk(theme="scidgreen")
root.title("Barcode Management System")
root.geometry("800x600")
root.minsize(600, 500)

style = ttk.Style(root)
style.theme_use("scidgreen")

scanner_var = tk.StringVar()
current_batch_id = None
scanning_enabled = True  

def open_edit_popup():
    global scanning_enabled
    if not current_batch_id:
        messagebox.showerror("Error", "No batch selected.")
        return

    scanning_enabled = False  
    popup = tk.Toplevel(root)
    popup.title("Edit Batch")
    popup.geometry("300x200")
    
    popup.transient(root)  
    popup.grab_set()       

    ttk.Label(popup, text="Select Phase:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    phase_var = tk.StringVar(value=current_phase)
    phase_dropdown = ttk.Combobox(popup, textvariable=phase_var, state="readonly")
    phase_dropdown["values"] = [p[1] for p in ProductionPhase.get_phases()]
    phase_dropdown.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(popup, text="Select Status:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    status_var = tk.StringVar(value=current_status)
    status_dropdown = ttk.Combobox(popup, textvariable=status_var, state="readonly")
    status_dropdown["values"] = ["Pending", "In Progress", "Completed"]
    status_dropdown.grid(row=1, column=1, padx=10, pady=5)

    def save_changes():
        global scanning_enabled
        new_phase = phase_var.get()
        new_status = status_var.get()
        phase_id = next((p[0] for p in ProductionPhase.get_phases() if p[1] == new_phase), None)

        if phase_id:
            Batch.update_batch_phase(current_batch_id, phase_id)
            Batch.update_batch_status(current_batch_id, new_status)
            messagebox.showinfo("Success", "Batch updated successfully!", parent=popup)
            popup.destroy()
            scanning_enabled = True  
            focus_scanner_entry()  
            update_batch_info(process_scanned_barcode(current_batch_barcode))  
        else:
            messagebox.showerror("Error", "Invalid phase selected.", parent=popup)

    ttk.Button(popup, text="Save", command=save_changes).grid(row=2, column=0, columnspan=2, pady=10)

    def on_popup_close():
        global scanning_enabled
        scanning_enabled = True  
        focus_scanner_entry()  
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", on_popup_close)  

def update_batch_info(batch):
    global current_batch_id, current_phase, current_status, current_batch_barcode

    for widget in batch_info_frame.winfo_children():
        widget.destroy()

    if batch:
        current_batch_id = batch[0]
        current_batch_barcode = batch[1]  
        headers = ["Barcode", "Brand", "Model", "Size", "Color", "Quantity", "Layers", "Serial", "Phase", "Status"]
        values = batch[1:]
        current_phase = values[-2]
        current_status = values[-1]

        for i, (header, value) in enumerate(zip(headers, values)):
            ttk.Label(batch_info_frame, text=header + ":", font=("Arial", 10, "bold"), anchor="w").grid(row=i, column=0, sticky="w", padx=10, pady=2)
            ttk.Label(batch_info_frame, text=value, font=("Arial", 10), anchor="w").grid(row=i, column=1, sticky="w", padx=10, pady=2)

        ttk.Button(batch_info_frame, text="Edit", command=open_edit_popup).grid(row=len(headers), column=0, columnspan=2, pady=10)

    else:
        ttk.Label(batch_info_frame, text="Batch not found.", font=("Arial", 10, "bold"), foreground="red").grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=10)

def on_barcode_scan(event=None):
    if not scanning_enabled:  
        return

    scanned_code = scanner_var.get().strip()
    if scanned_code:
        batch = process_scanned_barcode(scanned_code)
        update_batch_info(batch)
        scanner_var.set("")
    return "break"

def focus_scanner_entry():
    if scanning_enabled:
        hidden_scanner_entry.focus_set()
        root.after(500, focus_scanner_entry)

hidden_scanner_entry = tk.Entry(root, textvariable=scanner_var, font=("Arial", 1), width=1)
hidden_scanner_entry.place(x=-100, y=-100)
hidden_scanner_entry.bind("<Return>", on_barcode_scan)  

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

root.mainloop()




