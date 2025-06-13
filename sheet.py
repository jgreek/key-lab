import csv
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
from datetime import datetime
from pathlib import Path


class ShortcutViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Keyboard Shortcuts Viewer")
        self.geometry("900x700")
        self.configure(bg="#f5f5f5")

        # Get the directory where the script is located
        self.script_dir = Path(__file__).parent.absolute()

        # Set style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TButton", background="#4a86e8", foreground="black", font=("Arial", 10, "bold"))
        self.style.configure("TLabel", background="#f5f5f5", font=("Arial", 11))
        self.style.configure("Header.TLabel", background="#f5f5f5", font=("Arial", 14, "bold"))

        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))

        self.title_label = ttk.Label(self.header_frame, text="Keyboard Shortcuts Usage", style="Header.TLabel")
        self.title_label.pack(side=tk.LEFT, padx=5)

        self.load_button = ttk.Button(self.header_frame, text="Load CSV File", command=self.load_csv_file)
        self.load_button.pack(side=tk.RIGHT, padx=5)

        # Filter frame
        self.filter_frame = ttk.Frame(self.main_frame)
        self.filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(self.filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(self.filter_frame, textvariable=self.filter_var)
        self.filter_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.filter_entry.bind("<KeyRelease>", self.apply_filter)

        ttk.Button(self.filter_frame, text="Clear Filter", command=self.clear_filter).pack(side=tk.RIGHT, padx=5)

        # Create frame for shortcuts
        self.shortcuts_frame = ttk.Frame(self.main_frame)
        self.shortcuts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create treeview for shortcuts
        columns = ("Shortcut", "Count", "Last Used", "Description")
        self.shortcuts_tree = ttk.Treeview(self.shortcuts_frame, columns=columns, show="headings")

        # Define headings
        for col in columns:
            self.shortcuts_tree.heading(col, text=col)
            self.shortcuts_tree.column(col, width=100)

        self.shortcuts_tree.column("Shortcut", width=120)
        self.shortcuts_tree.column("Count", width=80)
        self.shortcuts_tree.column("Last Used", width=180)
        self.shortcuts_tree.column("Description", width=400)

        # Add scrollbar
        shortcuts_scrollbar = ttk.Scrollbar(self.shortcuts_frame, orient=tk.VERTICAL, command=self.shortcuts_tree.yview)
        self.shortcuts_tree.configure(yscrollcommand=shortcuts_scrollbar.set)

        # Pack widgets
        self.shortcuts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        shortcuts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add sorting functionality
        for col in columns:
            self.shortcuts_tree.heading(col, command=lambda _col=col: self.sort_treeview(_col))

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Load default CSV data
        self.csv_data = []
        self.load_default_csv()

    def load_default_csv(self):
        # Try to load key_listener_actions.csv from the script directory
        default_file = self.script_dir / "key_listener_actions.csv"

        if default_file.exists():
            try:
                self.load_csv_from_file(default_file)
                self.status_var.set(f"Loaded default file: {default_file}")
            except Exception as e:
                self.status_var.set(f"Error loading default file: {str(e)}")
                print(f"Error details: {e}")
        else:
            self.status_var.set(f"Default file '{default_file}' not found. Please load a CSV file.")
            print(f"File not found: {default_file}")
            print(f"Current directory: {Path.cwd()}")
            print(f"Script directory: {self.script_dir}")

            # List files in the script directory to help with debugging
            print("Files in script directory:")
            for file in self.script_dir.iterdir():
                print(f"  {file}")

    def load_csv_file(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=self.script_dir
        )

        if file_path:
            try:
                self.load_csv_from_file(file_path)
                self.status_var.set(f"Loaded: {file_path}")
            except Exception as e:
                self.status_var.set(f"Error loading file: {str(e)}")
                print(f"Error details: {e}")

    def load_csv_from_file(self, file_path):
        self.csv_data = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.csv_data.append(row)

        # Sort by count (ascending)
        self.csv_data.sort(key=lambda x: int(x.get('count', 0)))
        self.display_csv_data()

    def display_csv_data(self):
        # Clear existing data
        self.shortcuts_tree.delete(*self.shortcuts_tree.get_children())

        # Display data
        for row in self.csv_data:
            code = row.get('code', '')
            count = row.get('count', '0')
            last_action = row.get('last_action', '')
            comment = row.get('comment', '')

            # Format the date if it's valid
            try:
                date_obj = datetime.strptime(last_action, "%Y-%m-%d %H:%M:%S")
                last_action = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                pass

            self.shortcuts_tree.insert("", tk.END, values=(code, count, last_action, comment))

    def sort_treeview(self, col):
        # Get all items
        items = [(self.shortcuts_tree.set(item, col), item) for item in self.shortcuts_tree.get_children('')]

        # Sort items
        if col == "Count":
            # Sort numerically for the Count column
            items.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)
        else:
            # Sort alphabetically for other columns
            items.sort()

        # Rearrange items in sorted positions
        for index, (val, item) in enumerate(items):
            self.shortcuts_tree.move(item, '', index)

    def apply_filter(self, event=None):
        filter_text = self.filter_var.get().lower()

        # Clear existing data
        self.shortcuts_tree.delete(*self.shortcuts_tree.get_children())

        # Display filtered data
        for row in self.csv_data:
            code = row.get('code', '').lower()
            comment = row.get('comment', '').lower()

            if filter_text in code or filter_text in comment:
                self.shortcuts_tree.insert("", tk.END, values=(
                    row.get('code', ''),
                    row.get('count', '0'),
                    row.get('last_action', ''),
                    row.get('comment', '')
                ))

    def clear_filter(self):
        self.filter_var.set("")
        self.display_csv_data()


if __name__ == "__main__":
    app = ShortcutViewer()
    app.mainloop()