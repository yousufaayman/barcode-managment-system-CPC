import tkinter as tk
from tkinter import ttk
from frontend.user_manage_data import UserManageData  
from frontend.admin_manage_data import AdminManageData  

class MainWindow(tk.Tk):
    """Main application managing navigation between different tabs."""
    def __init__(self, role):
        super().__init__()
        self.title("Production Management System")
        self.geometry("1400x700")
        self.minsize(1400, 700) 
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
        """Sets a global font for all widgets in the application."""
        default_font = (font_family, font_size)
        self.option_add("*Font", default_font)  # Apply font to all widgets
        self.option_add("*TButton.Font", default_font)  # Apply to buttons
        self.option_add("*TLabel.Font", default_font)  # Apply to labels
        self.option_add("*TEntry.Font", default_font)  # Apply to entry fields
        self.option_add("*TCombobox.Font", default_font)  # Apply to dropdowns
        self.option_add("*Treeview.Font", default_font)  # Apply to tables
        style = ttk.Style()
        style.configure("TButton", font=default_font)  # Buttons
        style.configure("Treeview", font=default_font)  # Regular Treeview
        style.configure("Treeview.Heading", font=(font_family, font_size, "bold"))  # Header text
        style.configure("Checkbox.Treeview", font=default_font)
        style.configure("Checkbox.Treeview.Heading", font=(font_family, font_size, "bold"))  # Column headings
        style.configure("TButton", font=default_font) 
        
    def create_frames(self):
        """Creates frames based on the user's role."""
        allowed_frames = []
        
        if self.role == "Admin":
            allowed_frames = [AdminManageData, UserManageData]
        elif self.role == "User":
            allowed_frames = [UserManageData]

        for F in allowed_frames:
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def create_menu(self):
        """Creates a navigation menu for switching between tabs based on the role."""
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        navigate_menu = tk.Menu(menu_bar, tearoff=0)

        if self.role in ["Admin", "User"]:
            navigate_menu.add_command(label="User Management", command=lambda: self.show_frame("UserManageData"))

        if self.role == "Admin":
            navigate_menu.add_command(label="Management", command=lambda: self.show_frame("AdminManageData"))

        menu_bar.add_cascade(label="Navigate", menu=navigate_menu)

    def show_frame(self, frame_name):
        """Displays the selected frame."""
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()
        else:
            print(f"Error: Frame '{frame_name}' not found in self.frames.")

if __name__ == "__main__":
    app = MainWindow("Admin")
    app.mainloop()
