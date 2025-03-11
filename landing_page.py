import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from backend.auth import Auth  
from main_window import MainWindow 

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

# **Initialize Login Window**
root = ThemedTk(theme="scidgreen")
root.title("Barcode Management System - Login")
root.geometry("400x300")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True)

# **Username & Password Fields**
username_var = tk.StringVar()
password_var = tk.StringVar()

ttk.Label(frame, text="Username:").pack(pady=5)
username_entry = ttk.Entry(frame, textvariable=username_var)
username_entry.pack(pady=5, fill=tk.X)

ttk.Label(frame, text="Password:").pack(pady=5)
password_entry = ttk.Entry(frame, textvariable=password_var, show="*")
password_entry.pack(pady=5, fill=tk.X)

# **Login Button**
login_button = ttk.Button(frame, text="Login", command=login)
login_button.pack(pady=20, fill=tk.X)

root.mainloop()
