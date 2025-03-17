import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from backend.auth import Auth  
from frontend.user_manage_data import UserManageData  
from frontend.admin_manage_data import AdminManageData
from frontend.barcode_scanner import BarcodeScanner 
from frontend.bulk_barcode_create import BulkBarcodeCreate
from frontend.user_creation_page import UserCreationPage

class MainWindow(tk.Tk):
    def __init__(self, role):
        super().__init__()
        self.title("Production Management System")
        w, h = int(self.winfo_screenwidth() * 0.9), int(self.winfo_screenheight() * 0.9)
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth() - w) // 2}+{(self.winfo_screenheight() - h) // 2}")
        self.resizable(True, True)
        self.role = role 
        
        self.set_global_font("Arial", 12)
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.create_frames()
        self.create_menu()

        default_frame = "AdminManageData" if self.role == "Admin" else "UserManageData"
        self.show_frame(default_frame)

    def set_global_font(self, font_family="Arial", font_size=12):
        default_font = (font_family, font_size)
        self.option_add("*Font", default_font)  
        self.option_add("*TButton.Font", default_font)  
        self.option_add("*TLabel.Font", default_font)  
        self.option_add("*TEntry.Font", default_font)  
        self.option_add("*TCombobox.Font", default_font)  
        self.option_add("*Treeview.Font", default_font)  
        style = ttk.Style()
        style.configure("TButton", font=default_font)  
        style.configure("Treeview", font=default_font)  
        style.configure("Treeview.Heading", font=(font_family, font_size, "bold"))  
        
    def create_frames(self):
        allowed_frames = []
        
        if self.role == "Admin":
            allowed_frames = [AdminManageData, UserManageData, BarcodeScanner, BulkBarcodeCreate, UserCreationPage]
        elif self.role in ["Cutting", "Sewing", "Packaging"]:
            allowed_frames = [UserManageData, BarcodeScanner, BulkBarcodeCreate]

        for F in allowed_frames:
            frame = F(self.container, self, self.role) if "role" in F.__init__.__code__.co_varnames else F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        navigate_menu = tk.Menu(menu_bar, tearoff=0)

        if self.role in ["Cutting", "Sewing", "Packaging"]:
            navigate_menu.add_command(label="Barcode Manage", command=lambda: self.show_frame("UserManageData")) 
            navigate_menu.add_command(label="Barcode Scanner", command=lambda: self.show_frame("BarcodeScanner"))
            navigate_menu.add_command(label="Barcode Create", command=lambda: self.show_frame("BulkBarcodeCreate"))
        if self.role == "Admin":
            navigate_menu.add_command(label="Management", command=lambda: self.show_frame("AdminManageData"))
            navigate_menu.add_command(label="Users", command=lambda: self.show_frame("UserCreationPage"))
            navigate_menu.add_command(label="Barcode Scanner", command=lambda: self.show_frame("BarcodeScanner"))
            navigate_menu.add_command(label="Barcode Create", command=lambda: self.show_frame("BulkBarcodeCreate"))              

        menu_bar.add_cascade(label="Navigate", menu=navigate_menu)

    def show_frame(self, frame_name):
        frame = self.frames.get(frame_name)
        
        if frame:
            frame.tkraise()
            
            if hasattr(frame, "update_data"):
                frame.update_data()
            
            if isinstance(frame, BarcodeScanner):
                frame.activate_scanner()
            else:
                for f in self.frames.values():
                    if isinstance(f, BarcodeScanner):
                        f.deactivate_scanner()

def login():
    username = username_var.get().strip()
    password = password_var.get().strip()

    if not username or not password:
        messagebox.showerror("Error", "Username and Password cannot be empty!")
        return

    user = Auth.authenticate_user(username, password)

    if user:
        messagebox.showinfo("Success", f"Welcome, {user['username']}!")
        root.destroy()
        open_dashboard(user['role'])
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password.")

def open_dashboard(role):
    app = MainWindow(role)
    app.mainloop()

# **Setup Themed Window**
root = ThemedTk(theme="arc")
root.title("Barcode Management System - Login")
w, h = int(root.winfo_screenwidth() * 0.35), int(root.winfo_screenheight() * 0.4)
root.geometry(f"{w}x{h}+{(root.winfo_screenwidth() - w) // 2}+{(root.winfo_screenheight() - h) // 2}")
root.resizable(False, False)

# **Main Frame**
frame = ttk.Frame(root, padding=30)
frame.pack(expand=True, fill=tk.BOTH)

# **Title Label**
ttk.Label(frame, text="Login", font=("Arial", 18, "bold")).pack(pady=(10, 20))

# **Username & Password Fields**
username_var = tk.StringVar()
password_var = tk.StringVar()

ttk.Label(frame, text="Username:", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
username_entry = ttk.Entry(frame, textvariable=username_var, font=("Arial", 12))
username_entry.pack(fill=tk.X, pady=(0, 10))

ttk.Label(frame, text="Password:", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
password_entry = ttk.Entry(frame, textvariable=password_var, font=("Arial", 12), show="*")
password_entry.pack(fill=tk.X, pady=(0, 10))
password_entry.configure(show="•")


# **Login Button**
login_button = ttk.Button(frame, text="Login", command=login)
login_button.pack(pady=20, fill=tk.X)

root.mainloop()