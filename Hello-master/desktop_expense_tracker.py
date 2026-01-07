import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import io

class ModernExpenseTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💰 Modern Expense Tracker - Desktop")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Initialize database
        self.init_db()
        
        # Create main interface
        self.create_widgets()
        
        # Load initial data
        self.load_categories()
        self.load_expenses()
        self.update_dashboard()
        self.update_charts()
    
    def configure_styles(self):
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        self.style.configure('Modern.TFrame', background='#ffffff', relief='solid', borderwidth=1)
        self.style.configure('Dashboard.TLabelframe', background='#e8f4fd', relief='solid', borderwidth=2)
        self.style.configure('Success.TLabel', foreground='#28a745', font=('Arial', 11, 'bold'))
        self.style.configure('Danger.TLabel', foreground='#dc3545', font=('Arial', 11, 'bold'))
        self.style.configure('Warning.TLabel', foreground='#ffc107', font=('Arial', 11, 'bold'))
        self.style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
    
    def init_db(self):
        self.conn = sqlite3.connect('desktop_expenses.db')
        
        # Create tables with all features
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                date TEXT,
                category TEXT,
                subcategory TEXT,
                description TEXT,
                amount REAL,
                payment_status TEXT DEFAULT 'Pending'
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
        
        # Insert default categories
        cursor = self.conn.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            default_cats = ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Healthcare", "Education", "Other"]
            for cat in default_cats:
                self.conn.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
        
        self.conn.commit()
    
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dashboard Tab
        self.create_dashboard_tab()
        
        # Expenses Tab
        self.create_expenses_tab()
        
        # Analytics Tab
        self.create_analytics_tab()
        
        # Settings Tab
        self.create_settings_tab()
    
    def create_dashboard_tab(self):
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Title
        title_frame = ttk.Frame(dashboard_frame, style='Modern.TFrame', padding="15")
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text="💰 Expense Dashboard", style='Title.TLabel').pack()
        
        # Dashboard cards
        cards_frame = ttk.Frame(dashboard_frame)
        cards_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Budget card
        budget_card = ttk.LabelFrame(cards_frame, text="💳 Budget", style='Dashboard.TLabelframe', padding="15")
        budget_card.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.budget_label = ttk.Label(budget_card, text="$0.00", style='Header.TLabel')
        self.budget_label.pack()
        
        # Spent card
        spent_card = ttk.LabelFrame(cards_frame, text="💸 Paid", style='Dashboard.TLabelframe', padding="15")
        spent_card.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        self.spent_label = ttk.Label(spent_card, text="$0.00", style='Danger.TLabel')
        self.spent_label.pack()
        
        # Pending card
        pending_card = ttk.LabelFrame(cards_frame, text="⏳ Pending", style='Dashboard.TLabelframe', padding="15")
        pending_card.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        
        self.pending_label = ttk.Label(pending_card, text="$0.00", style='Warning.TLabel')
        self.pending_label.pack()
        
        # Remaining card
        remaining_card = ttk.LabelFrame(cards_frame, text="💵 Remaining", style='Dashboard.TLabelframe', padding="15")
        remaining_card.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        
        self.remaining_label = ttk.Label(remaining_card, text="$0.00", style='Success.TLabel')
        self.remaining_label.pack()
        
        # Configure grid weights
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(dashboard_frame, text="⚡ Quick Actions", padding="15")
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(actions_frame, text="💳 Set Budget", command=self.set_budget_dialog, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="➕ Add Expense", command=self.quick_add_expense, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="📊 Refresh Charts", command=self.update_charts, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="📤 Export Excel", command=self.export_excel, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="📄 Export PDF", command=self.export_pdf, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
    
    def create_expenses_tab(self):
        expenses_frame = ttk.Frame(self.notebook)
        self.notebook.add(expenses_frame, text="💸 Expenses")
        
        # Add expense form
        form_frame = ttk.LabelFrame(expenses_frame, text="➕ Add New Expense", padding="15")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Form fields
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill=tk.X)
        
        # Row 1
        ttk.Label(fields_frame, text="Category:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(fields_frame, textvariable=self.category_var, width=15)
        self.category_combo.grid(row=0, column=1, padx=5, sticky=tk.EW)
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        ttk.Label(fields_frame, text="Subcategory:", style='Header.TLabel').grid(row=0, column=2, sticky=tk.W, padx=5)
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(fields_frame, textvariable=self.subcategory_var, width=15)
        self.subcategory_combo.grid(row=0, column=3, padx=5, sticky=tk.EW)
        
        # Row 2
        ttk.Label(fields_frame, text="Description:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.desc_var, width=20).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(fields_frame, text="Amount:", style='Header.TLabel').grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.amount_var, width=15).grid(row=1, column=3, padx=5, pady=5, sticky=tk.EW)
        
        # Row 3
        ttk.Label(fields_frame, text="Payment Status:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, padx=5)
        self.payment_status_var = tk.StringVar(value="Pending")
        status_combo = ttk.Combobox(fields_frame, textvariable=self.payment_status_var, values=["Pending", "Paid"], width=15)
        status_combo.grid(row=2, column=1, padx=5, sticky=tk.EW)
        
        # Configure grid
        for i in range(4):
            fields_frame.columnconfigure(i, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="➕ Add Expense", command=self.add_expense, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📁 Manage Categories", command=self.manage_categories, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(expenses_frame, text="🔍 Filter Expenses", padding="15")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        filter_fields = ttk.Frame(filter_frame)
        filter_fields.pack(fill=tk.X)
        
        ttk.Label(filter_fields, text="Year:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filter_year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(filter_fields, textvariable=self.filter_year_var, values=[str(y) for y in range(2020, 2030)], width=10)
        year_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_fields, text="Month:", style='Header.TLabel').grid(row=0, column=2, sticky=tk.W, padx=5)
        self.filter_month_var = tk.StringVar(value=str(datetime.now().month))
        month_combo = ttk.Combobox(filter_fields, textvariable=self.filter_month_var, values=["All"] + [str(m) for m in range(1, 13)], width=10)
        month_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(filter_fields, text="Status:", style='Header.TLabel').grid(row=0, column=4, sticky=tk.W, padx=5)
        self.filter_status_var = tk.StringVar(value="All")
        status_filter = ttk.Combobox(filter_fields, textvariable=self.filter_status_var, values=["All", "Paid", "Pending"], width=10)
        status_filter.grid(row=0, column=5, padx=5)
        
        ttk.Button(filter_fields, text="🔍 Apply Filter", command=self.load_expenses, style='Primary.TButton').grid(row=0, column=6, padx=10)
        
        # Expenses list
        list_frame = ttk.LabelFrame(expenses_frame, text="📋 Expense History", padding="15")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview
        columns = ("Date", "Category", "Subcategory", "Description", "Amount", "Status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("Date", text="📅 Date")
        self.tree.heading("Category", text="📂 Category")
        self.tree.heading("Subcategory", text="📁 Subcategory")
        self.tree.heading("Description", text="📝 Description")
        self.tree.heading("Amount", text="💵 Amount")
        self.tree.heading("Status", text="💳 Status")
        
        for col in columns:
            self.tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Context menu for expenses
        self.create_context_menu()
    
    def create_analytics_tab(self):
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Charts frame
        charts_frame = ttk.Frame(analytics_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create matplotlib figure
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('💰 Expense Analytics Dashboard', fontsize=16, fontweight='bold')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Budget settings
        budget_frame = ttk.LabelFrame(settings_frame, text="💳 Budget Management", padding="15")
        budget_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(budget_frame, text="Set Monthly Budget:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5)
        self.budget_entry_var = tk.StringVar()
        ttk.Entry(budget_frame, textvariable=self.budget_entry_var, width=20).grid(row=0, column=1, padx=5)
        ttk.Button(budget_frame, text="💾 Save Budget", command=self.set_budget, style='Primary.TButton').grid(row=0, column=2, padx=10)
        
        # Category management
        category_frame = ttk.LabelFrame(settings_frame, text="📁 Category Management", padding="15")
        category_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Category list
        cat_list_frame = ttk.Frame(category_frame)
        cat_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.category_listbox = tk.Listbox(cat_list_frame, height=10)
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        cat_scroll = ttk.Scrollbar(cat_list_frame, orient=tk.VERTICAL, command=self.category_listbox.yview)
        self.category_listbox.configure(yscrollcommand=cat_scroll.set)
        cat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Category buttons
        cat_btn_frame = ttk.Frame(category_frame)
        cat_btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(cat_btn_frame, text="➕ Add Category", command=self.add_category_dialog, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(cat_btn_frame, text="📁 Add Subcategory", command=self.add_subcategory_dialog, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(cat_btn_frame, text="🔄 Refresh", command=self.load_category_list, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        # Load category list
        self.load_category_list()
    
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✅ Mark as Paid", command=self.mark_as_paid)
        self.context_menu.add_command(label="⏳ Mark as Pending", command=self.mark_as_pending)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Delete Expense", command=self.delete_expense)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)
    
    def mark_as_paid(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            expense_id = item['tags'][0]
            self.conn.execute("UPDATE expenses SET payment_status = 'Paid' WHERE id = ?", (expense_id,))
            self.conn.commit()
            self.load_expenses()
            self.update_dashboard()
            self.update_charts()
    
    def mark_as_pending(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            expense_id = item['tags'][0]
            self.conn.execute("UPDATE expenses SET payment_status = 'Pending' WHERE id = ?", (expense_id,))
            self.conn.commit()
            self.load_expenses()
            self.update_dashboard()
            self.update_charts()
    
    def delete_expense(self):
        selected = self.tree.selection()
        if selected:
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
                item = self.tree.item(selected[0])
                expense_id = item['tags'][0]
                self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                self.conn.commit()
                self.load_expenses()
                self.update_dashboard()
                self.update_charts()
    
    def set_budget_dialog(self):
        budget = simpledialog.askfloat("Set Budget", "Enter your monthly budget:")
        if budget:
            self.budget_entry_var.set(str(budget))
            self.set_budget()
    
    def set_budget(self):
        try:
            budget = float(self.budget_entry_var.get())
            self.conn.execute("DELETE FROM budget")
            self.conn.execute("INSERT INTO budget (total_budget) VALUES (?)", (budget,))
            self.conn.commit()
            self.update_dashboard()
            messagebox.showinfo("Success", "Budget updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid budget amount")
    
    def quick_add_expense(self):
        self.notebook.select(1)  # Switch to expenses tab
    
    def load_categories(self):
        cursor = self.conn.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in cursor]
        self.category_combo['values'] = categories
    
    def load_category_list(self):
        self.category_listbox.delete(0, tk.END)
        cursor = self.conn.execute("SELECT name FROM categories ORDER BY name")
        for row in cursor:
            self.category_listbox.insert(tk.END, row[0])
    
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
        
        self.conn.execute("""
            INSERT INTO expenses (date, category, subcategory, description, amount, payment_status) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (date, self.category_var.get(), self.subcategory_var.get(), 
              self.desc_var.get(), amount, self.payment_status_var.get()))
        self.conn.commit()
        
        # Clear form
        self.category_var.set("")
        self.subcategory_var.set("")
        self.desc_var.set("")
        self.amount_var.set("")
        self.payment_status_var.set("Pending")
        
        self.load_expenses()
        self.update_dashboard()
        self.update_charts()
        messagebox.showinfo("Success", "Expense added successfully!")
    
    def load_expenses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Build filter query
        query = "SELECT id, date, category, subcategory, description, amount, payment_status FROM expenses WHERE 1=1"
        params = []
        
        if self.filter_year_var.get():
            query += " AND date LIKE ?"
            params.append(f"{self.filter_year_var.get()}%")
        
        if self.filter_month_var.get() != "All" and self.filter_month_var.get():
            month = self.filter_month_var.get().zfill(2)
            query += " AND date LIKE ?"
            params.append(f"{self.filter_year_var.get()}-{month}%")
        
        if self.filter_status_var.get() != "All":
            query += " AND payment_status = ?"
            params.append(self.filter_status_var.get())
        
        query += " ORDER BY date DESC"
        
        cursor = self.conn.execute(query, params)
        
        for row in cursor:
            expense_id, date, category, subcategory, description, amount, status = row
            subcategory = subcategory or "-"
            status_icon = "✅" if status == "Paid" else "⏳"
            
            self.tree.insert("", tk.END, 
                           values=(date, category, subcategory, description, f"${amount:.2f}", f"{status_icon} {status}"),
                           tags=(expense_id,))
    
    def update_dashboard(self):
        # Get budget
        cursor = self.conn.execute("SELECT total_budget FROM budget LIMIT 1")
        budget_row = cursor.fetchone()
        budget = budget_row[0] if budget_row else 0
        
        # Get totals
        cursor = self.conn.execute("SELECT SUM(amount) FROM expenses WHERE payment_status = 'Paid'")
        spent_row = cursor.fetchone()
        spent = spent_row[0] if spent_row[0] else 0
        
        cursor = self.conn.execute("SELECT SUM(amount) FROM expenses WHERE payment_status = 'Pending'")
        pending_row = cursor.fetchone()
        pending = pending_row[0] if pending_row[0] else 0
        
        remaining = budget - spent
        
        # Update labels
        self.budget_label.config(text=f"${budget:.2f}")
        self.spent_label.config(text=f"${spent:.2f}")
        self.pending_label.config(text=f"${pending:.2f}")
        
        if remaining < 0:
            self.remaining_label.config(text=f"-${abs(remaining):.2f}", style='Danger.TLabel')
        else:
            self.remaining_label.config(text=f"${remaining:.2f}", style='Success.TLabel')
    
    def update_charts(self):
        # Clear previous plots
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        
        # Category pie chart
        cursor = self.conn.execute("SELECT category, SUM(amount) FROM expenses WHERE payment_status = 'Paid' GROUP BY category")
        category_data = cursor.fetchall()
        
        if category_data:
            categories, amounts = zip(*category_data)
            colors_list = plt.cm.Set3(range(len(categories)))
            self.ax1.pie(amounts, labels=categories, autopct='%1.1f%%', colors=colors_list)
            self.ax1.set_title('💰 Expenses by Category')
        
        # Monthly trend
        cursor = self.conn.execute("""
            SELECT strftime('%Y-%m', date) as month, SUM(amount) 
            FROM expenses WHERE payment_status = 'Paid' 
            GROUP BY month ORDER BY month
        """)
        monthly_data = cursor.fetchall()
        
        if monthly_data:
            months, amounts = zip(*monthly_data)
            self.ax2.plot(months, amounts, marker='o', linewidth=2, markersize=6)
            self.ax2.set_title('📈 Monthly Spending Trend')
            self.ax2.tick_params(axis='x', rotation=45)
        
        # Payment status
        cursor = self.conn.execute("SELECT payment_status, SUM(amount) FROM expenses GROUP BY payment_status")
        status_data = cursor.fetchall()
        
        if status_data:
            statuses, amounts = zip(*status_data)
            colors = ['#28a745' if s == 'Paid' else '#ffc107' for s in statuses]
            self.ax3.bar(statuses, amounts, color=colors)
            self.ax3.set_title('💳 Payment Status')
        
        # Top subcategories
        cursor = self.conn.execute("""
            SELECT subcategory, SUM(amount) FROM expenses 
            WHERE payment_status = 'Paid' AND subcategory IS NOT NULL AND subcategory != '' 
            GROUP BY subcategory ORDER BY SUM(amount) DESC LIMIT 5
        """)
        subcat_data = cursor.fetchall()
        
        if subcat_data:
            subcats, amounts = zip(*subcat_data)
            self.ax4.barh(subcats, amounts, color='skyblue')
            self.ax4.set_title('🏆 Top Subcategories')
        
        plt.tight_layout()
        self.canvas.draw()
    
    def manage_categories(self):
        self.notebook.select(3)  # Switch to settings tab
    
    def add_category_dialog(self):
        name = simpledialog.askstring("Add Category", "Enter category name:")
        if name:
            try:
                self.conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
                self.conn.commit()
                self.load_categories()
                self.load_category_list()
                messagebox.showinfo("Success", f"Category '{name}' added successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Category already exists")
    
    def add_subcategory_dialog(self):
        if not self.category_listbox.curselection():
            messagebox.showwarning("Warning", "Please select a category first")
            return
        
        cat_name = self.category_listbox.get(self.category_listbox.curselection()[0])
        subcat_name = simpledialog.askstring("Add Subcategory", f"Enter subcategory for '{cat_name}':")
        
        if subcat_name:
            cursor = self.conn.execute("SELECT id FROM categories WHERE name = ?", (cat_name,))
            cat_id = cursor.fetchone()[0]
            self.conn.execute("INSERT INTO subcategories (category_id, name) VALUES (?, ?)", (cat_id, subcat_name))
            self.conn.commit()
            messagebox.showinfo("Success", f"Subcategory '{subcat_name}' added to '{cat_name}'!")
    
    def export_excel(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Save Excel Report"
            )
            
            if not filename:
                return
            
            # Get data
            cursor = self.conn.execute("SELECT total_budget FROM budget LIMIT 1")
            budget_row = cursor.fetchone()
            budget = budget_row[0] if budget_row else 0
            
            cursor = self.conn.execute("SELECT SUM(amount) FROM expenses WHERE payment_status = 'Paid'")
            spent = cursor.fetchone()[0] or 0
            
            cursor = self.conn.execute("SELECT SUM(amount) FROM expenses WHERE payment_status = 'Pending'")
            pending = cursor.fetchone()[0] or 0
            
            cursor = self.conn.execute("SELECT date, category, subcategory, description, amount, payment_status FROM expenses ORDER BY date DESC")
            expenses = cursor.fetchall()
            
            cursor = self.conn.execute("SELECT category, SUM(amount) FROM expenses WHERE payment_status = 'Paid' GROUP BY category")
            category_data = cursor.fetchall()
            
            # Create Excel file
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Dashboard
                dashboard_df = pd.DataFrame({
                    'Metric': ['Total Budget', 'Paid Expenses', 'Pending Expenses', 'Remaining Budget'],
                    'Amount': [budget, spent, pending, budget - spent]
                })
                dashboard_df.to_excel(writer, sheet_name='Dashboard', index=False)
                
                # Expenses
                expenses_df = pd.DataFrame(expenses, columns=['Date', 'Category', 'Subcategory', 'Description', 'Amount', 'Payment Status'])
                expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
                
                # Category Analytics
                if category_data:
                    category_df = pd.DataFrame(category_data, columns=['Category', 'Total Amount'])
                    category_df.to_excel(writer, sheet_name='Category Analytics', index=False)
            
            messagebox.showinfo("Success", f"Excel report exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {str(e)}")
    
    def export_pdf(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save PDF Report"
            )
            
            if not filename:
                return
            
            # Get data
            cursor = self.conn.execute("SELECT total_budget FROM budget LIMIT 1")
            budget_row = cursor.fetchone()
            budget = budget_row[0] if budget_row else 0
            
            cursor = self.conn.execute("SELECT SUM(amount) FROM expenses WHERE payment_status = 'Paid'")
            spent = cursor.fetchone()[0] or 0
            
            cursor = self.conn.execute("SELECT SUM(amount) FROM expenses WHERE payment_status = 'Pending'")
            pending = cursor.fetchone()[0] or 0
            
            cursor = self.conn.execute("SELECT date, category, subcategory, description, amount, payment_status FROM expenses ORDER BY date DESC LIMIT 50")
            expenses = cursor.fetchall()
            
            # Create PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph('💰 Expense Report', title_style))
            story.append(Spacer(1, 20))
            
            # Dashboard
            story.append(Paragraph('📊 Dashboard Summary', styles['Heading2']))
            dashboard_data = [
                ['Metric', 'Amount'],
                ['Total Budget', f'${budget:.2f}'],
                ['Paid Expenses', f'${spent:.2f}'],
                ['Pending Expenses', f'${pending:.2f}'],
                ['Remaining Budget', f'${budget - spent:.2f}']
            ]
            
            dashboard_table = Table(dashboard_data)
            dashboard_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(dashboard_table)
            story.append(Spacer(1, 30))
            
            # Expenses
            story.append(Paragraph('📋 Recent Expenses', styles['Heading2']))
            expense_data = [['Date', 'Category', 'Subcategory', 'Description', 'Amount', 'Status']]
            
            for expense in expenses:
                expense_data.append([
                    expense[0][:10],
                    expense[1],
                    expense[2] or '-',
                    expense[3][:20] + '...' if len(expense[3]) > 20 else expense[3],
                    f'${expense[4]:.2f}',
                    expense[5]
                ])
            
            expense_table = Table(expense_data)
            expense_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(expense_table)
            
            doc.build(story)
            messagebox.showinfo("Success", f"PDF report exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
    
    def run(self):
        self.root.mainloop()
        self.conn.close()

if __name__ == "__main__":
    app = ModernExpenseTracker()
    app.run()