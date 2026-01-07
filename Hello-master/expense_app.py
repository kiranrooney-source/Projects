import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import calendar

class ExpenseApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💰 Modern Expense Tracker")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Modern styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.init_db()
        self.create_widgets()
        self.load_categories()
        self.load_expenses()
    
    def configure_styles(self):
        self.style.configure('Title.TLabel', font=('Arial', 14, 'bold'), background='#f0f0f0')
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        self.style.configure('Modern.TFrame', background='#ffffff', relief='solid', borderwidth=1)
        self.style.configure('Dashboard.TLabelframe', background='#e8f4fd', relief='solid', borderwidth=2)
        self.style.configure('Success.TLabel', foreground='#28a745', font=('Arial', 11, 'bold'))
        self.style.configure('Danger.TLabel', foreground='#dc3545', font=('Arial', 11, 'bold'))
        self.style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
    
    def init_db(self):
        self.conn = sqlite3.connect('expenses.db')
        
        # Check if subcategory column exists, if not add it
        cursor = self.conn.execute("PRAGMA table_info(expenses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'subcategory' not in columns:
            # Create new table with subcategory
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS expenses_new (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    category TEXT,
                    subcategory TEXT,
                    description TEXT,
                    amount REAL
                )
            ''')
            
            # Copy existing data
            if 'expenses' in [table[0] for table in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
                self.conn.execute('''
                    INSERT INTO expenses_new (id, date, category, subcategory, description, amount)
                    SELECT id, date, category, NULL, description, amount FROM expenses
                ''')
                self.conn.execute("DROP TABLE expenses")
            
            self.conn.execute("ALTER TABLE expenses_new RENAME TO expenses")
        else:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    category TEXT,
                    subcategory TEXT,
                    description TEXT,
                    amount REAL
                )
            ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY,
                total_budget REAL
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS subcategories (
                id INTEGER PRIMARY KEY,
                category_id INTEGER,
                name TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Insert default categories if none exist
        cursor = self.conn.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            default_cats = ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"]
            for cat in default_cats:
                self.conn.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
        
        self.conn.commit()
    
    def create_widgets(self):
        # Title
        title_frame = ttk.Frame(self.root, style='Modern.TFrame', padding="15")
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text="💰 Modern Expense Tracker", style='Title.TLabel').pack()
        
        # Budget frame
        budget_frame = ttk.LabelFrame(self.root, text="💳 Budget Management", style='Modern.TFrame', padding="15")
        budget_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(budget_frame, text="Total Budget:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.budget_var = tk.StringVar()
        ttk.Entry(budget_frame, textvariable=self.budget_var, width=15, font=('Arial', 11)).grid(row=0, column=1, padx=10)
        ttk.Button(budget_frame, text="💾 Set Budget", command=self.set_budget, style='Primary.TButton').grid(row=0, column=2, padx=10)
        
        # Category management
        ttk.Button(budget_frame, text="📁 Manage Categories", command=self.manage_categories, style='Primary.TButton').grid(row=0, column=3, padx=10)
        
        # Dashboard frame
        dash_frame = ttk.LabelFrame(self.root, text="📊 Dashboard", style='Dashboard.TLabelframe', padding="15")
        dash_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.budget_label = ttk.Label(dash_frame, text="💰 Budget: $0.00", style='Header.TLabel')
        self.budget_label.grid(row=0, column=0, sticky=tk.W, padx=10)
        
        self.spent_label = ttk.Label(dash_frame, text="💸 Spent: $0.00", style='Header.TLabel')
        self.spent_label.grid(row=0, column=1, padx=20, sticky=tk.W)
        
        self.remaining_label = ttk.Label(dash_frame, text="💵 Remaining: $0.00", style='Success.TLabel')
        self.remaining_label.grid(row=0, column=2, padx=20, sticky=tk.W)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(self.root, text="🔍 Date Filter", style='Modern.TFrame', padding="15")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="📅 Year:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(filter_frame, textvariable=self.year_var, width=10,
                                values=[str(y) for y in range(2020, 2030)], font=('Arial', 10))
        year_combo.grid(row=0, column=1, padx=10)
        
        ttk.Label(filter_frame, text="📅 Month:", style='Header.TLabel').grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.month_var = tk.StringVar(value=str(datetime.now().month))
        month_combo = ttk.Combobox(filter_frame, textvariable=self.month_var, width=10,
                                 values=[str(m) for m in range(1, 13)], font=('Arial', 10))
        month_combo.grid(row=0, column=3, padx=10)
        
        ttk.Label(filter_frame, text="📅 Day:", style='Header.TLabel').grid(row=0, column=4, sticky=tk.W, padx=(20,0))
        self.day_var = tk.StringVar(value="All")
        day_combo = ttk.Combobox(filter_frame, textvariable=self.day_var, width=10,
                               values=["All"] + [str(d) for d in range(1, 32)], font=('Arial', 10))
        day_combo.grid(row=0, column=5, padx=10)
        
        ttk.Button(filter_frame, text="🔍 Apply Filter", command=self.load_expenses, style='Primary.TButton').grid(row=0, column=6, padx=20)
        
        # Input frame
        input_frame = ttk.LabelFrame(self.root, text="➕ Add New Expense", style='Modern.TFrame', padding="15")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="📂 Category:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, width=15, font=('Arial', 10))
        self.category_combo.grid(row=0, column=1, padx=10, sticky=tk.EW)
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        ttk.Label(input_frame, text="📁 Subcategory:", style='Header.TLabel').grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(input_frame, textvariable=self.subcategory_var, width=15, font=('Arial', 10))
        self.subcategory_combo.grid(row=0, column=3, padx=10, sticky=tk.EW)
        
        ttk.Label(input_frame, text="📝 Description:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        self.desc_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.desc_var, font=('Arial', 10)).grid(row=1, column=1, padx=10, sticky=tk.EW, pady=(10,0))
        
        ttk.Label(input_frame, text="💵 Amount:", style='Header.TLabel').grid(row=1, column=2, sticky=tk.W, padx=(20,0), pady=(10,0))
        self.amount_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.amount_var, font=('Arial', 10)).grid(row=1, column=3, padx=10, sticky=tk.EW, pady=(10,0))
        
        # Buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        ttk.Button(btn_frame, text="➕ Add Expense", command=self.add_expense, style='Primary.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="🗑️ Delete Selected", command=self.delete_expense, style='Primary.TButton').pack(side=tk.LEFT, padx=10)
        
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # Expenses list
        list_frame = ttk.LabelFrame(self.root, text="📋 Expense History", style='Modern.TFrame', padding="15")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("Date", "Category", "Subcategory", "Description", "Amount")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.tree.heading("Date", text="📅 Date")
        self.tree.heading("Category", text="📂 Category")
        self.tree.heading("Subcategory", text="📁 Subcategory")
        self.tree.heading("Description", text="📝 Description")
        self.tree.heading("Amount", text="💵 Amount")
        
        for col in columns:
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load initial data
        self.load_budget()
        self.load_expenses()
    
    def set_budget(self):
        try:
            budget = float(self.budget_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid budget amount")
            return
        
        self.conn.execute("DELETE FROM budget")
        self.conn.execute("INSERT INTO budget (total_budget) VALUES (?)", (budget,))
        self.conn.commit()
        
        self.load_budget()
        self.update_dashboard()
    
    def load_budget(self):
        cursor = self.conn.execute("SELECT total_budget FROM budget LIMIT 1")
        row = cursor.fetchone()
        if row:
            self.budget_var.set(str(row[0]))
    
    def manage_categories(self):
        cat_window = tk.Toplevel(self.root)
        cat_window.title("📁 Manage Categories")
        cat_window.geometry("600x400")
        cat_window.configure(bg='#f0f0f0')
        
        # Category section
        cat_frame = ttk.LabelFrame(cat_window, text="Categories", padding="10")
        cat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Category list
        cat_list = tk.Listbox(cat_frame, height=8, font=('Arial', 10))
        cat_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        cat_scroll = ttk.Scrollbar(cat_frame, orient=tk.VERTICAL, command=cat_list.yview)
        cat_list.configure(yscrollcommand=cat_scroll.set)
        cat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load categories
        cursor = self.conn.execute("SELECT name FROM categories ORDER BY name")
        for row in cursor:
            cat_list.insert(tk.END, row[0])
        
        # Category buttons
        cat_btn_frame = ttk.Frame(cat_window)
        cat_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def add_category():
            name = simpledialog.askstring("Add Category", "Enter category name:")
            if name:
                try:
                    self.conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
                    self.conn.commit()
                    cat_list.insert(tk.END, name)
                    self.load_categories()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Category already exists")
        
        def add_subcategory():
            if not cat_list.curselection():
                messagebox.showwarning("Warning", "Please select a category first")
                return
            
            cat_name = cat_list.get(cat_list.curselection()[0])
            subcat_name = simpledialog.askstring("Add Subcategory", f"Enter subcategory for '{cat_name}':")
            if subcat_name:
                cursor = self.conn.execute("SELECT id FROM categories WHERE name = ?", (cat_name,))
                cat_id = cursor.fetchone()[0]
                self.conn.execute("INSERT INTO subcategories (category_id, name) VALUES (?, ?)", (cat_id, subcat_name))
                self.conn.commit()
                messagebox.showinfo("Success", f"Subcategory '{subcat_name}' added to '{cat_name}'")
        
        ttk.Button(cat_btn_frame, text="➕ Add Category", command=add_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(cat_btn_frame, text="📁 Add Subcategory", command=add_subcategory).pack(side=tk.LEFT, padx=5)
    
    def load_categories(self):
        cursor = self.conn.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in cursor]
        self.category_combo['values'] = categories
    
    def on_category_change(self, event=None):
        category = self.category_var.get()
        if category:
            cursor = self.conn.execute("""
                SELECT s.name FROM subcategories s 
                JOIN categories c ON s.category_id = c.id 
                WHERE c.name = ? ORDER BY s.name
            """, (category,))
            subcategories = [row[0] for row in cursor]
            self.subcategory_combo['values'] = subcategories
            self.subcategory_var.set("")
    
    def add_expense(self):
        if not all([self.category_var.get(), self.desc_var.get(), self.amount_var.get()]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        self.conn.execute("INSERT INTO expenses (date, category, subcategory, description, amount) VALUES (?, ?, ?, ?, ?)",
                         (date, self.category_var.get(), self.subcategory_var.get(), self.desc_var.get(), amount))
        self.conn.commit()
        
        self.category_var.set("")
        self.subcategory_var.set("")
        self.desc_var.set("")
        self.amount_var.set("")
        
        self.load_expenses()
        self.update_dashboard()
        messagebox.showinfo("Success", "Expense added successfully!")
    
    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
        
        item = self.tree.item(selected[0])
        expense_id = item['tags'][0]
        
        self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        
        self.load_expenses()
        self.update_dashboard()
    
    def load_expenses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Build filter query
        query = "SELECT id, date, category, subcategory, description, amount FROM expenses WHERE 1=1"
        params = []
        
        if self.year_var.get():
            query += " AND date LIKE ?"
            params.append(f"{self.year_var.get()}%")
        
        if self.month_var.get():
            month = self.month_var.get().zfill(2)
            query += " AND date LIKE ?"
            params.append(f"{self.year_var.get()}-{month}%")
        
        if self.day_var.get() != "All" and self.day_var.get():
            day = self.day_var.get().zfill(2)
            query += " AND date LIKE ?"
            params.append(f"{self.year_var.get()}-{self.month_var.get().zfill(2)}-{day}%")
        
        query += " ORDER BY date DESC"
        
        cursor = self.conn.execute(query, params)
        
        for row in cursor:
            expense_id, date, category, subcategory, description, amount = row
            subcategory = subcategory or "-"
            self.tree.insert("", tk.END, values=(date, category, subcategory, description, f"${amount:.2f}"), tags=(expense_id,))
        
        self.update_dashboard()
    
    def update_dashboard(self):
        # Get budget
        cursor = self.conn.execute("SELECT total_budget FROM budget LIMIT 1")
        budget_row = cursor.fetchone()
        budget = budget_row[0] if budget_row else 0
        
        # Get total expenses for current filter
        query = "SELECT SUM(amount) FROM expenses WHERE 1=1"
        params = []
        
        if self.year_var.get():
            query += " AND date LIKE ?"
            params.append(f"{self.year_var.get()}%")
        
        if self.month_var.get():
            month = self.month_var.get().zfill(2)
            query += " AND date LIKE ?"
            params.append(f"{self.year_var.get()}-{month}%")
        
        if self.day_var.get() != "All" and self.day_var.get():
            day = self.day_var.get().zfill(2)
            query += " AND date LIKE ?"
            params.append(f"{self.year_var.get()}-{self.month_var.get().zfill(2)}-{day}%")
        
        cursor = self.conn.execute(query, params)
        spent_row = cursor.fetchone()
        spent = spent_row[0] if spent_row[0] else 0
        
        remaining = budget - spent
        
        self.budget_label.config(text=f"Budget: ${budget:.2f}")
        self.spent_label.config(text=f"Spent: ${spent:.2f}")
        
        if remaining < 0:
            self.remaining_label.config(text=f"🚨 Over Budget: ${abs(remaining):.2f}", style='Danger.TLabel')
        else:
            self.remaining_label.config(text=f"💵 Remaining: ${remaining:.2f}", style='Success.TLabel')
    
    def run(self):
        self.root.mainloop()
        self.conn.close()

if __name__ == "__main__":
    app = ExpenseApp()
    app.run()