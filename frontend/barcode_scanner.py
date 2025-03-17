import tkinter as tk
from tkinter import ttk, messagebox
from backend.barcode_scanning import process_scanned_barcode  
from backend.models import Batch

class BarcodeScanner(tk.Frame):    
    def __init__(self, parent, controller, role):
        super().__init__(parent)
        self.controller = controller
        self.user_role = role

        self.scanner_mode = tk.StringVar(value="VIEW")  # Default mode is VIEW
        self.selected_phase = tk.StringVar(value=self.user_role if self.user_role != "Admin" else "Sewing")

        self.scanner_var = tk.StringVar()
        self.current_batch_id = None
        self.scanning_enabled = False 

        self.create_widgets()

    def create_widgets(self):
        """Creates the UI elements."""
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # **Parent frame to hold both scanner mode and phase selection**
        top_frame = ttk.Frame(frame)
        top_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)

        # **Scanner Mode Selection**
        mode_frame = ttk.LabelFrame(top_frame, text="Scanner Mode", padding=10)
        mode_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        mode_frame.columnconfigure(0, weight=1)

        ttk.Radiobutton(mode_frame, text="VIEW", variable=self.scanner_mode, value="VIEW", command=self.update_mode_color).grid(row=0, column=0, padx=10, sticky="w")
        ttk.Radiobutton(mode_frame, text="IN", variable=self.scanner_mode, value="IN", command=self.update_mode_color).grid(row=0, column=1, padx=10, sticky="w")
        ttk.Radiobutton(mode_frame, text="OUT", variable=self.scanner_mode, value="OUT", command=self.update_mode_color).grid(row=0, column=2, padx=10, sticky="w")

        self.mode_color_label = ttk.Label(mode_frame, text="VIEW MODE", font=("Arial", 12, "bold"), background="gray", foreground="white")
        self.mode_color_label.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")

        # **Phase Selection (Admin can change phase)**
        phase_frame = ttk.LabelFrame(top_frame, text="Production Phase", padding=10)
        phase_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        phase_frame.columnconfigure(0, weight=1)

        ttk.Label(phase_frame, text="Select Phase:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        phase_options = ["Cutting", "Sewing", "Packaging"]

        for i, phase in enumerate(phase_options):
            rb = ttk.Radiobutton(phase_frame, text=phase, variable=self.selected_phase, value=phase)
            rb.grid(row=0, column=i + 1, padx=5, pady=5, sticky="w")

            if self.user_role != "Admin" and phase != self.user_role:
                rb.config(state="disabled") 

        # **Scanner Area**
        ttk.Label(frame, text=f"Scan Barcode ({self.user_role} Mode):", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(frame, text="(Automatic input - scan to load batch details)", font=("Arial", 10)).grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.batch_info_frame = ttk.LabelFrame(frame, text="Batch Information", padding=10)
        self.batch_info_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        frame.columnconfigure(0, weight=1)
        self.batch_info_frame.columnconfigure(0, weight=1)
        self.batch_info_frame.columnconfigure(1, weight=1)

        # **Hidden scanner entry to capture scanned input**
        self.hidden_scanner_entry = tk.Entry(self, textvariable=self.scanner_var, font=("Arial", 1), width=1)
        self.hidden_scanner_entry.place(x=-100, y=-100)

    def update_mode_color(self):
        """Updates the mode indicator color based on selection."""
        mode = self.scanner_mode.get()
        colors = {
            "IN": ("IN MODE", "blue"),
            "VIEW": ("VIEW MODE", "gray"),
            "OUT": ("OUT MODE", "green"),
        }
        self.mode_color_label.config(text=colors[mode][0], background=colors[mode][1])

    def activate_scanner(self):
        """Activates scanner when frame is shown."""
        if not self.scanning_enabled:
            self.scanning_enabled = True
            self.hidden_scanner_entry.bind("<Return>", self.on_barcode_scan)
            self.focus_scanner_entry()

    def deactivate_scanner(self):
        """Deactivates scanner when frame is hidden."""
        self.scanning_enabled = False
        self.hidden_scanner_entry.unbind("<Return>")

    def focus_scanner_entry(self):
        """Ensures the scanner entry is always focused when active."""
        if self.scanning_enabled:
            self.hidden_scanner_entry.focus_set()
            self.after(500, self.focus_scanner_entry)

    def on_barcode_scan(self, event=None):
        """Processes scanned barcodes and updates batch information."""
        if not self.scanning_enabled:
            return

        scanned_code = self.scanner_var.get().strip()
        if scanned_code:
            batch = process_scanned_barcode(scanned_code)
            self.update_batch_info(batch)
            self.apply_scanner_mode()
            self.scanner_var.set("")
        return "break"

    def update_batch_info(self, batch):
        """Updates batch details in the UI."""
        for widget in self.batch_info_frame.winfo_children():
            widget.destroy()
                    
        if batch:
            self.current_batch_id = batch["batch_id"]  # ✅ Correct dictionary key access
            self.current_batch_barcode = batch["barcode"]

            # ✅ Define headers and extract corresponding values using dictionary keys
            headers = ["Barcode", "Brand", "Model", "Size", "Color", "Quantity", "Layers", "Serial", "Phase", "Status"]
            values = (
                batch["barcode"], batch["brand_name"], batch["model_name"], 
                batch["size_value"], batch["color_name"], batch["quantity"], 
                batch["layers"], batch["serial"], batch["phase_name"], batch["status"]
            )

            self.current_phase = batch["phase_name"]
            self.current_status = batch["status"]

            # ✅ Display batch details in the UI
            for i, (header, value) in enumerate(zip(headers, values)):
                ttk.Label(self.batch_info_frame, text=f"{header}:", font=("Arial", 10, "bold"), anchor="w").grid(row=i, column=0, sticky="w", padx=10, pady=2)
                ttk.Label(self.batch_info_frame, text=value, font=("Arial", 10), anchor="w").grid(row=i, column=1, sticky="w", padx=10, pady=2)

    def apply_scanner_mode(self):
        """Handles phase transitions based on scanner mode selection."""
        mode = self.scanner_mode.get()
        selected_phase = self.selected_phase.get()

        if not self.current_batch_id:
            return

        if mode == "IN":
            Batch.update_batch_phase(self.current_batch_id, self.get_phase_id(selected_phase))
            Batch.update_batch_status(self.current_batch_id, "In Progress")
            messagebox.showinfo("IN Mode", f"Item {self.current_batch_barcode} started in {selected_phase}.")

        elif mode == "OUT":
            next_phase = self.get_next_phase(selected_phase)

            if next_phase:
                Batch.update_batch_phase(self.current_batch_id, self.get_phase_id(next_phase))
                Batch.update_batch_status(self.current_batch_id, "Pending")
                messagebox.showinfo("OUT Mode", f"Item {self.current_batch_barcode} moved to {next_phase}.")
            else:
                if selected_phase == "Packaging":
                    Batch.update_batch_status(self.current_batch_id, "Completed")
                    messagebox.showinfo("Completion", f"Item {self.current_batch_barcode} has completed production.")
                else:
                    messagebox.showerror("Error", f"Unexpected phase transition from {selected_phase}")

        self.update_batch_info(process_scanned_barcode(self.current_batch_barcode))

    def get_phase_id(self, phase_name):
        """Returns the phase ID given a phase name."""
        phase_mapping = {"Cutting": 1, "Sewing": 2, "Packaging": 3}
        return phase_mapping.get(phase_name, None)

    def get_next_phase(self, current_phase):
        """Determines the next production phase, returning None if at the last phase."""
        phase_sequence = ["Cutting", "Sewing", "Packaging"]
        if current_phase in phase_sequence:
            idx = phase_sequence.index(current_phase)
            return phase_sequence[idx + 1] if idx + 1 < len(phase_sequence) else None
        return None