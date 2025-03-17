import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from backend.auth import Auth

class UserCreationPage(tk.Frame):
    """Page for creating, updating, searching, and deleting users."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.available_roles = ["Admin", "Cutting", "Sewing", "Packaging"]  
        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        """Creates the user management UI."""
        # **Main Frame**
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # **User Creation Section**
        creation_frame = ttk.LabelFrame(frame, text="Create User", padding=10)
        creation_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(creation_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(creation_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(creation_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(creation_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(creation_frame, text="Role:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.role_var = tk.StringVar()
        self.role_dropdown = ttk.Combobox(creation_frame, textvariable=self.role_var, 
                                          values=["Admin", "Cutting", "Sewing", "Packaging"], state="readonly")
        self.role_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(creation_frame, text="Create User", command=self.create_user).grid(row=3, column=0, columnspan=2, pady=10)

        # **Search, Update & Delete Section**
        manage_frame = ttk.LabelFrame(frame, text="Search / Update / Delete", padding=10)
        manage_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(manage_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_entry = ttk.Entry(manage_frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(manage_frame, text="Search", command=self.search_users).grid(row=0, column=2, padx=5, pady=5)

        ttk.Button(manage_frame, text="Reset Password", command=self.reset_password).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(manage_frame, text="Delete User", command=self.delete_user).grid(row=1, column=1, padx=5, pady=5)

        # **Users Table**
        self.tree = ttk.Treeview(frame, columns=["User ID", "Username", "Role"], show="headings", height=10)
        self.tree.heading("User ID", text="User ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Role", text="Role")
        self.tree.column("User ID", width=50, anchor="center")
        self.tree.column("Username", width=150, anchor="center")
        self.tree.column("Role", width=100, anchor="center")
        self.tree.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(1, weight=1)

    def create_user(self):
        """Handles user creation."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if not username or not password or not role:
            messagebox.showerror("Error", "All fields are required!")
            return

        result = Auth.register_user(username, password, role)

        if result["success"]:
            messagebox.showinfo("Success", result["message"])
            self.load_users()
            self.clear_fields()
        else:
            messagebox.showerror("Error", result["message"])
    
    def load_users(self):
        """Loads all users into the table."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        users = Auth.get_users()  # ✅ Fetch users as dictionaries
        for user in users:
            user_values = (user["user_id"], user["username"], user["role"])  # ✅ Extract values as tuple
            self.tree.insert("", tk.END, values=user_values)

    def search_users(self):
        """Filters users based on the search query and hides others."""
        query = self.search_entry.get().strip().lower()

        for row in self.tree.get_children():
            self.tree.delete(row)

        users = Auth.get_users()
        filtered_users = [user for user in users if query in user["username"].lower()]  # ✅ Dictionary key access

        for user in filtered_users:
            user_values = (user["user_id"], user["username"], user["role"])
            self.tree.insert("", tk.END, values=user_values)

    def reset_password(self):
        """Prompts admin to enter a new password for the selected user."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No user selected!")
            return

        user_id = int(self.tree.item(selected_item, "values")[0])  # ✅ Convert to integer for MySQL
        new_password = simpledialog.askstring("Reset Password", "Enter new password:", show="*")

        if new_password:
            result = Auth.reset_user_password(user_id, new_password)
            if result["success"]:
                messagebox.showinfo("Success", "Password reset successfully!")
            else:
                messagebox.showerror("Error", result["message"])

    def delete_user(self):
        """Deletes the selected user."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No user selected!")
            return

        user_id = int(self.tree.item(selected_item, "values")[0])  # ✅ Convert to integer for MySQL

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?")
        if confirm:
            result = Auth.delete_user(user_id)
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.load_users()
            else:
                messagebox.showerror("Error", result["message"])

    def on_double_click(self, event):
            """Allows role to be changed on double-click using a dropdown."""
            selected_item = self.tree.selection()
            if not selected_item:
                return

            item_values = self.tree.item(selected_item, "values")
            user_id = int(item_values[0])
            current_role = item_values[2]

            # **Popup Window for Role Selection**
            role_popup = tk.Toplevel(self)
            role_popup.title("Change Role")
            role_popup.geometry("300x150")
            role_popup.transient(self)
            role_popup.grab_set()

            ttk.Label(role_popup, text="Select new role:").pack(pady=10)
            
            # **Dropdown for Role Selection**
            role_var = tk.StringVar(value=current_role)
            role_dropdown = ttk.Combobox(role_popup, textvariable=role_var, values=self.available_roles, state="readonly")
            role_dropdown.pack(pady=5)

            def update_role():
                """Updates the user role in the database."""
                new_role = role_var.get()
                if new_role and new_role != current_role:
                    result = Auth.update_user_role(user_id, new_role)
                    if result["success"]:
                        messagebox.showinfo("Success", "User role updated successfully!")
                        self.load_users()
                    else:
                        messagebox.showerror("Error", result["message"])
                role_popup.destroy()

            ttk.Button(role_popup, text="Update", command=update_role).pack(pady=10)
    
    def clear_fields(self):
        """Clears input fields."""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.role_var.set("")
