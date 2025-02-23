import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
from backend.seed_database import load_excel, seed_database, generate_template  

df_dict = {}

def upload_excel():
    """Opens file dialog to upload an Excel file and load its sheets."""
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
    if not file_path:
        return

    try:
        global df_dict
        df_dict = load_excel(file_path)
        
        sheet_listbox.delete(0, tk.END)
        for sheet in df_dict.keys():
            sheet_listbox.insert(tk.END, sheet)

        messagebox.showinfo("Success", "Excel file loaded successfully. Select a sheet to view.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def display_sheet():
    """Displays the selected sheet in a scrollable table format."""
    selected_sheet = sheet_listbox.get(tk.ACTIVE)
    if not selected_sheet:
        return

    df = df_dict[selected_sheet]

    for widget in table_frame.winfo_children():
        widget.destroy()

    tree = ttk.Treeview(table_frame, columns=list(df.columns), show="headings", height=15)
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    for _, row in df.iterrows():
        tree.insert("", tk.END, values=row.tolist())

    tree.pack(fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

def submit_to_database():
    """Processes and inserts the Excel data into the database."""
    try:
        result = seed_database(df_dict)
        messagebox.showinfo("Success", result)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def create_template():
    """Allows the user to download a properly formatted template."""
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if not file_path:
        return

    try:
        result = generate_template(file_path)
        messagebox.showinfo("Success", result)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Apply ThemedTk styling
root = ThemedTk(theme="scidgreen")
root.title("Database Seeder")
root.geometry("800x600")
root.minsize(600, 500)

style = ttk.Style(root)
style.theme_use("scidgreen")

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Button(frame, text="Upload Excel File", command=upload_excel).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
ttk.Button(frame, text="Generate CSV Template", command=create_template).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

sheet_listbox = tk.Listbox(frame, height=5)
sheet_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

ttk.Button(frame, text="View Sheet", command=display_sheet).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
ttk.Button(frame, text="Submit to Database", command=submit_to_database).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

table_frame = ttk.Frame(root, padding=10)
table_frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
