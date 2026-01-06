from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import sqlite3
from datetime import datetime
import os
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('web_expenses.db')
    
    # Check if subcategory column exists
    cursor = conn.execute("PRAGMA table_info(expenses)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Check for payment_status and is_savings columns
    has_payment_status = 'payment_status' in columns
    has_savings = 'is_savings' in columns
    
    if 'subcategory' not in columns or not has_payment_status or not has_savings:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses_new (
                id INTEGER PRIMARY KEY,
                date TEXT,
                category TEXT,
                subcategory TEXT,
                description TEXT,
                amount REAL,
                payment_status TEXT DEFAULT 'Pending',
                is_savings INTEGER DEFAULT 0
            )
        ''')
        
        if 'expenses' in [table[0] for table in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
            if 'subcategory' in columns and has_payment_status and has_savings:
                conn.execute('''
                    INSERT INTO expenses_new (id, date, category, subcategory, description, amount, payment_status, is_savings)
                    SELECT id, date, category, subcategory, description, amount, payment_status, is_savings FROM expenses
                ''')
            elif 'subcategory' in columns and has_payment_status:
                conn.execute('''
                    INSERT INTO expenses_new (id, date, category, subcategory, description, amount, payment_status, is_savings)
                    SELECT id, date, category, subcategory, description, amount, payment_status, 
                    CASE WHEN LOWER(category) = 'savings' THEN 1 ELSE 0 END FROM expenses
                ''')
            elif 'subcategory' in columns:
                conn.execute('''
                    INSERT INTO expenses_new (id, date, category, subcategory, description, amount, payment_status, is_savings)
                    SELECT id, date, category, subcategory, description, amount, 'Pending',
                    CASE WHEN LOWER(category) = 'savings' THEN 1 ELSE 0 END FROM expenses
                ''')
            else:
                conn.execute('''
                    INSERT INTO expenses_new (id, date, category, subcategory, description, amount, payment_status, is_savings)
                    SELECT id, date, category, NULL, description, amount, 'Pending',
                    CASE WHEN LOWER(category) = 'savings' THEN 1 ELSE 0 END FROM expenses
                ''')
            conn.execute("DROP TABLE expenses")
        
        conn.execute("ALTER TABLE expenses_new RENAME TO expenses")
    else:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                date TEXT,
                category TEXT,
                subcategory TEXT,
                description TEXT,
                amount REAL,
                payment_status TEXT DEFAULT 'Pending',
                is_savings INTEGER DEFAULT 0
            )
        ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            total_budget REAL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS subcategories (
            id INTEGER PRIMARY KEY,
            category_id INTEGER,
            name TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS lends_borrows (
            id INTEGER PRIMARY KEY,
            date TEXT,
            name TEXT,
            amount REAL,
            type TEXT,
            description TEXT,
            status TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scheduler_settings (
            id INTEGER PRIMARY KEY,
            email_hour INTEGER DEFAULT 9,
            email_minute INTEGER DEFAULT 0
        )
    ''')
    
    # Insert default categories and subcategories
    cursor = conn.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        default_data = {
            "Food": ["Groceries", "Restaurants", "Fast Food", "Snacks", "Beverages"],
            "Transport": ["Fuel", "Public Transport", "Taxi/Uber", "Parking", "Vehicle Maintenance"],
            "Entertainment": ["Movies", "Games", "Sports", "Books", "Music"],
            "Bills": ["Electricity", "Water", "Internet", "Phone", "Gas", "Insurance"],
            "Shopping": ["Clothing", "Electronics", "Home Items", "Personal Care", "Gifts"],
            "Savings": ["Emergency Fund", "Investment", "Fixed Deposit", "Mutual Funds"],
            "Other": ["Medical", "Education", "Travel", "Miscellaneous"]
        }
        
        for category, subcategories in default_data.items():
            cursor = conn.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            cat_id = cursor.lastrowid
            for subcat in subcategories:
                conn.execute("INSERT INTO subcategories (category_id, name) VALUES (?, ?)", (cat_id, subcat))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    from datetime import datetime, timedelta
    current_date = datetime.now()
    
    conn = sqlite3.connect('web_expenses.db')
    
    # Get budget
    cursor = conn.execute("SELECT total_budget FROM budget LIMIT 1")
    budget_row = cursor.fetchone()
    budget = budget_row[0] if budget_row else 0
    
    # Get categories
    cursor = conn.execute("SELECT name FROM categories ORDER BY name")
    categories = [row[0] for row in cursor]
    
    # Get current month or requested month
    selected_month = request.args.get('month', current_date.strftime('%Y-%m'))
    
    # Get expenses for the selected month grouped by date
    cursor = conn.execute("""
        SELECT id, date, category, subcategory, description, amount, payment_status, is_savings 
        FROM expenses 
        WHERE date LIKE ? 
        ORDER BY date DESC, id DESC
    """, (f"{selected_month}%",))
    all_expenses = cursor.fetchall()
    
    # Group expenses by date
    expenses_by_date = {}
    for expense in all_expenses:
        expense_date = expense[1]  # date is at index 1
        if expense_date not in expenses_by_date:
            expenses_by_date[expense_date] = []
        expenses_by_date[expense_date].append(expense)
    
    # Sort dates in descending order
    sorted_dates = sorted(expenses_by_date.keys(), reverse=True)
    expenses = expenses_by_date
    
    # Get available months for navigation
    cursor = conn.execute("""
        SELECT DISTINCT strftime('%Y-%m', date) as month 
        FROM expenses 
        ORDER BY month DESC
    """)
    available_months = [row[0] for row in cursor.fetchall()]
    
    # Format selected month for display
    try:
        selected_month_obj = datetime.strptime(selected_month, '%Y-%m')
        selected_month_display = selected_month_obj.strftime('%B %Y')
    except:
        selected_month_display = current_month
    
    # Calculate totals for selected month (only paid expenses, excluding savings)
    cursor = conn.execute("SELECT SUM(amount) FROM expenses WHERE payment_status = 'Paid' AND is_savings = 0 AND date LIKE ?", (f"{selected_month}%",))
    spent_row = cursor.fetchone()
    spent = spent_row[0] if spent_row[0] else 0
    
    # Get pending amount for selected month (excluding savings)
    cursor = conn.execute("SELECT SUM(amount) FROM expenses WHERE payment_status = 'Pending' AND is_savings = 0 AND date LIKE ?", (f"{selected_month}%",))
    pending_row = cursor.fetchone()
    pending = pending_row[0] if pending_row[0] else 0
    
    # Get savings amount for selected month
    cursor = conn.execute("SELECT SUM(amount) FROM expenses WHERE is_savings = 1 AND date LIKE ?", (f"{selected_month}%",))
    savings_row = cursor.fetchone()
    savings = savings_row[0] if savings_row[0] else 0
    
    # Get analytics data for selected month (excluding savings)
    cursor = conn.execute("SELECT category, SUM(amount) FROM expenses WHERE payment_status = 'Paid' AND is_savings = 0 AND date LIKE ? GROUP BY category", (f"{selected_month}%",))
    category_data = cursor.fetchall()
    
    cursor = conn.execute("SELECT subcategory, SUM(amount) FROM expenses WHERE payment_status = 'Paid' AND is_savings = 0 AND subcategory IS NOT NULL AND subcategory != '' AND date LIKE ? GROUP BY subcategory", (f"{selected_month}%",))
    subcategory_data = cursor.fetchall()
    
    # Get previous month data
    current_month = current_date.strftime("%B %Y")
    
    # Calculate previous month
    if current_date.month == 1:
        prev_month_date = current_date.replace(year=current_date.year-1, month=12)
    else:
        prev_month_date = current_date.replace(month=current_date.month-1)
    
    previous_month = prev_month_date.strftime("%B %Y")
    prev_month_str = prev_month_date.strftime("%Y-%m")
    
    # Get previous month expenses
    cursor = conn.execute("SELECT SUM(amount) FROM expenses WHERE payment_status = 'Paid' AND is_savings = 0 AND date LIKE ?", (f"{prev_month_str}%",))
    prev_spent_row = cursor.fetchone()
    prev_spent = prev_spent_row[0] if prev_spent_row[0] else 0
    
    cursor = conn.execute("SELECT SUM(amount) FROM expenses WHERE is_savings = 1 AND date LIKE ?", (f"{prev_month_str}%",))
    prev_savings_row = cursor.fetchone()
    prev_savings = prev_savings_row[0] if prev_savings_row[0] else 0
    
    # Get total savings across all months
    cursor = conn.execute("SELECT SUM(amount) FROM expenses WHERE is_savings = 1")
    total_savings_all_row = cursor.fetchone()
    total_savings_all = total_savings_all_row[0] if total_savings_all_row[0] else 0
    
    # Get lends and borrows data for selected month
    cursor = conn.execute("""
        SELECT id, date, name, amount, type, description, status 
        FROM lends_borrows 
        WHERE date LIKE ? 
        ORDER BY date DESC, id DESC
    """, (f"{selected_month}%",))
    lends_borrows = cursor.fetchall()
    
    # Calculate total lends and borrows for ALL months (not just selected month)
    cursor = conn.execute("SELECT SUM(amount) FROM lends_borrows WHERE type = 'Lend'")
    total_lends_row = cursor.fetchone()
    total_lends = total_lends_row[0] if total_lends_row[0] else 0
    
    cursor = conn.execute("SELECT SUM(amount) FROM lends_borrows WHERE type = 'Borrow'")
    total_borrows_row = cursor.fetchone()
    total_borrows = total_borrows_row[0] if total_borrows_row[0] else 0
    
    # Get scheduler settings
    cursor = conn.execute("SELECT email_hour, email_minute FROM scheduler_settings LIMIT 1")
    scheduler_row = cursor.fetchone()
    if scheduler_row:
        email_hour, email_minute = scheduler_row
    else:
        email_hour, email_minute = 9, 0
    
    # Assume same budget for previous month (you can modify this logic)
    prev_budget = budget
    prev_remaining = prev_budget - prev_spent
    
    conn.close()
    
    return render_template('index.html', 
                         budget=budget, 
                         spent=spent,
                         pending=pending,
                         savings=savings,
                         remaining=budget-spent,
                         categories=categories, 
                         expenses=expenses,
                         sorted_dates=sorted_dates,
                         selected_month=selected_month,
                         selected_month_display=selected_month_display,
                         available_months=available_months,
                         category_data=category_data,
                         subcategory_data=subcategory_data,
                         current_month=current_month,
                         previous_month=previous_month,
                         prev_budget=prev_budget,
                         prev_spent=prev_spent,
                         prev_savings=prev_savings,
                         prev_remaining=prev_remaining,
                         current_date=current_date.strftime('%Y-%m-%d'),
                         total_savings_all=total_savings_all,
                         total_lends=total_lends,
                         total_borrows=total_borrows,
                         lends_borrows=lends_borrows,
                         email_hour=email_hour,
                         email_minute=email_minute)

@app.route('/get_category_data')
def get_category_data():
    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    conn = sqlite3.connect('web_expenses.db')
    cursor = conn.execute("""
        SELECT category, SUM(amount) 
        FROM expenses 
        WHERE payment_status = 'Paid' AND is_savings = 0 AND date LIKE ? 
        GROUP BY category 
        ORDER BY SUM(amount) DESC
    """, (f"{selected_month}%",))
    category_data = cursor.fetchall()
    conn.close()
    return jsonify([{'category': cat, 'amount': amount} for cat, amount in category_data])

@app.route('/get_expense/<int:expense_id>')
def get_expense(expense_id):
    conn = sqlite3.connect('web_expenses.db')
    cursor = conn.execute("SELECT id, date, category, subcategory, description, amount, payment_status, is_savings FROM expenses WHERE id = ?", (expense_id,))
    expense = cursor.fetchone()
    conn.close()
    
    if expense:
        return jsonify({
            'id': expense[0],
            'date': expense[1],
            'category': expense[2],
            'subcategory': expense[3] or '',
            'description': expense[4],
            'amount': expense[5],
            'payment_status': expense[6],
            'is_savings': expense[7]
        })
    return jsonify({'error': 'Expense not found'}), 404

@app.route('/get_expenses_by_date')
def get_expenses_by_date():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    conn = sqlite3.connect('web_expenses.db')
    
    if start_date and end_date:
        cursor = conn.execute("""
            SELECT id, date, category, subcategory, description, amount, payment_status, is_savings 
            FROM expenses 
            WHERE date BETWEEN ? AND ? 
            ORDER BY date DESC, id DESC
        """, (start_date, end_date))
    else:
        cursor = conn.execute("""
            SELECT id, date, category, subcategory, description, amount, payment_status, is_savings 
            FROM expenses 
            ORDER BY date DESC, id DESC 
            LIMIT 50
        """)
    
    expenses = cursor.fetchall()
    conn.close()
    
    # Group by date
    expenses_by_date = {}
    for expense in expenses:
        expense_date = expense[1]
        if expense_date not in expenses_by_date:
            expenses_by_date[expense_date] = []
        expenses_by_date[expense_date].append({
            'id': expense[0],
            'date': expense[1],
            'category': expense[2],
            'subcategory': expense[3],
            'description': expense[4],
            'amount': expense[5],
            'payment_status': expense[6],
            'is_savings': expense[7]
        })
    
    return jsonify(expenses_by_date)

@app.route('/set_budget', methods=['POST'])
def set_budget():
    budget = float(request.form['budget'])
    conn = sqlite3.connect('web_expenses.db')
    conn.execute("DELETE FROM budget")
    conn.execute("INSERT INTO budget (total_budget) VALUES (?)", (budget,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    # Handle custom category
    custom_category = request.form.get('custom_category', '').strip()
    if custom_category:
        category = custom_category
        # Add the custom category to database if it doesn't exist
        conn = sqlite3.connect('web_expenses.db')
        cursor = conn.execute("SELECT id FROM categories WHERE name = ?", (category,))
        if not cursor.fetchone():
            conn.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            conn.commit()
        conn.close()
    else:
        category = request.form['category']
    
    subcategory = request.form.get('subcategory', '')
    custom_subcategory = request.form.get('custom_subcategory', '')
    description = request.form['description']
    amount = float(request.form['amount'])
    payment_status = request.form.get('payment_status', 'Pending')
    date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
    is_savings = 1 if category.lower() == 'savings' else 0
    
    # Use custom subcategory if provided
    if custom_subcategory.strip():
        subcategory = custom_subcategory.strip()
        
        # Add the custom subcategory to database if it doesn't exist
        conn = sqlite3.connect('web_expenses.db')
        cursor = conn.execute("SELECT id FROM categories WHERE name = ?", (category,))
        cat_row = cursor.fetchone()
        
        if cat_row:
            cat_id = cat_row[0]
            # Check if subcategory already exists
            cursor = conn.execute("SELECT id FROM subcategories WHERE category_id = ? AND name = ?", (cat_id, subcategory))
            if not cursor.fetchone():
                # Add new subcategory
                conn.execute("INSERT INTO subcategories (category_id, name) VALUES (?, ?)", (cat_id, subcategory))
        conn.close()
    
    conn = sqlite3.connect('web_expenses.db')
    conn.execute("INSERT INTO expenses (date, category, subcategory, description, amount, payment_status, is_savings) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (date, category, subcategory, description, amount, payment_status, is_savings))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/get_subcategories/<category>')
def get_subcategories(category):
    conn = sqlite3.connect('web_expenses.db')
    cursor = conn.execute("""
        SELECT s.name FROM subcategories s 
        JOIN categories c ON s.category_id = c.id 
        WHERE c.name = ? 
        ORDER BY s.name
    """, (category,))
    subcategories = [row[0] for row in cursor]
    conn.close()
    return jsonify(subcategories)

@app.route('/update_payment_status', methods=['POST'])
def update_payment_status():
    expense_id = request.form['expense_id']
    status = request.form['status']
    conn = sqlite3.connect('web_expenses.db')
    conn.execute("UPDATE expenses SET payment_status = ? WHERE id = ?", (status, expense_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    conn = sqlite3.connect('web_expenses.db')
    
    if request.method == 'POST':
        # Update expense
        category = request.form['category']
        subcategory = request.form.get('subcategory', '')
        description = request.form['description']
        amount = float(request.form['amount'])
        payment_status = request.form.get('payment_status', 'Pending')
        date = request.form.get('date')
        is_savings = 1 if category.lower() == 'savings' else 0
        
        conn.execute("UPDATE expenses SET date = ?, category = ?, subcategory = ?, description = ?, amount = ?, payment_status = ?, is_savings = ? WHERE id = ?",
                    (date, category, subcategory, description, amount, payment_status, is_savings, expense_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    # Get expense details for editing
    cursor = conn.execute("SELECT id, date, category, subcategory, description, amount, payment_status, is_savings FROM expenses WHERE id = ?", (expense_id,))
    expense = cursor.fetchone()
    
    # Get categories
    cursor = conn.execute("SELECT name FROM categories ORDER BY name")
    categories = [row[0] for row in cursor]
    
    conn.close()
    
    if not expense:
        return redirect(url_for('index'))
    
    return render_template('edit_expense.html', expense=expense, categories=categories)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    conn = sqlite3.connect('web_expenses.db')
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/get_monthly_data')
def get_monthly_data():
    # Get the selected month from query parameter
    selected_month = request.args.get('month')
    
    conn = sqlite3.connect('web_expenses.db')
    
    if selected_month:
        # If a specific month is selected, show comparison with previous months
        cursor = conn.execute("""
            SELECT strftime('%Y-%m', date) as month, SUM(amount) 
            FROM expenses 
            WHERE payment_status = 'Paid' AND is_savings = 0 
            GROUP BY strftime('%Y-%m', date) 
            ORDER BY month DESC 
            LIMIT 6
        """)
        monthly_expenses = cursor.fetchall()
        
        cursor = conn.execute("""
            SELECT strftime('%Y-%m', date) as month, SUM(amount) 
            FROM expenses 
            WHERE is_savings = 1 
            GROUP BY strftime('%Y-%m', date) 
            ORDER BY month DESC 
            LIMIT 6
        """)
        monthly_savings = cursor.fetchall()
    else:
        # Default: show last 12 months
        cursor = conn.execute("""
            SELECT strftime('%Y-%m', date) as month, SUM(amount) 
            FROM expenses 
            WHERE payment_status = 'Paid' AND is_savings = 0 
            GROUP BY strftime('%Y-%m', date) 
            ORDER BY month DESC 
            LIMIT 12
        """)
        monthly_expenses = cursor.fetchall()
        
        cursor = conn.execute("""
            SELECT strftime('%Y-%m', date) as month, SUM(amount) 
            FROM expenses 
            WHERE is_savings = 1 
            GROUP BY strftime('%Y-%m', date) 
            ORDER BY month DESC 
            LIMIT 12
        """)
        monthly_savings = cursor.fetchall()
    
    conn.close()
    
    # Convert to dictionaries for easier processing
    expenses_dict = {month: amount for month, amount in monthly_expenses}
    savings_dict = {month: amount for month, amount in monthly_savings}
    
    # Get all unique months and sort them
    all_months = sorted(set(list(expenses_dict.keys()) + list(savings_dict.keys())), reverse=True)
    if len(all_months) > 12:
        all_months = all_months[:12]
    all_months.reverse()  # Show oldest to newest
    
    # Format month names
    formatted_data = []
    for month in all_months:
        try:
            month_obj = datetime.strptime(month, '%Y-%m')
            formatted_month = month_obj.strftime('%b %Y')
            formatted_data.append({
                'month': formatted_month,
                'expenses': expenses_dict.get(month, 0),
                'savings': savings_dict.get(month, 0)
            })
        except:
            continue
    
    return jsonify(formatted_data)

@app.route('/add_subcategory', methods=['POST'])
def add_subcategory():
    category = request.form['category']
    subcategory = request.form['subcategory']
    
    if not category or not subcategory:
        return jsonify({'error': 'Category and subcategory are required'}), 400
    
    conn = sqlite3.connect('web_expenses.db')
    
    # Get category ID
    cursor = conn.execute("SELECT id FROM categories WHERE name = ?", (category,))
    cat_row = cursor.fetchone()
    
    if not cat_row:
        conn.close()
        return jsonify({'error': 'Category not found'}), 404
    
    cat_id = cat_row[0]
    
    # Check if subcategory already exists
    cursor = conn.execute("SELECT id FROM subcategories WHERE category_id = ? AND name = ?", (cat_id, subcategory))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Subcategory already exists'}), 409
    
    # Add new subcategory
    conn.execute("INSERT INTO subcategories (category_id, name) VALUES (?, ?)", (cat_id, subcategory))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Subcategory added successfully'})

@app.route('/add_lend_borrow', methods=['POST'])
def add_lend_borrow():
    date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
    name = request.form['name']
    amount = float(request.form['amount'])
    lb_type = request.form['type']
    description = request.form.get('description', '')
    status = request.form.get('status', 'Pending')
    
    conn = sqlite3.connect('web_expenses.db')
    conn.execute("INSERT INTO lends_borrows (date, name, amount, type, description, status) VALUES (?, ?, ?, ?, ?, ?)",
                (date, name, amount, lb_type, description, status))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update_lend_borrow_status', methods=['POST'])
def update_lend_borrow_status():
    lb_id = request.form['lb_id']
    status = request.form['status']
    conn = sqlite3.connect('web_expenses.db')
    conn.execute("UPDATE lends_borrows SET status = ? WHERE id = ?", (status, lb_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit_lend_borrow/<int:lb_id>', methods=['GET', 'POST'])
def edit_lend_borrow(lb_id):
    conn = sqlite3.connect('web_expenses.db')
    
    if request.method == 'POST':
        # Update lend/borrow record
        date = request.form.get('date')
        name = request.form['name']
        amount = float(request.form['amount'])
        lb_type = request.form['type']
        description = request.form.get('description', '')
        status = request.form.get('status', 'Pending')
        
        conn.execute("UPDATE lends_borrows SET date = ?, name = ?, amount = ?, type = ?, description = ?, status = ? WHERE id = ?",
                    (date, name, amount, lb_type, description, status, lb_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    # Get lend/borrow details for editing
    cursor = conn.execute("SELECT id, date, name, amount, type, description, status FROM lends_borrows WHERE id = ?", (lb_id,))
    lb_record = cursor.fetchone()
    conn.close()
    
    if not lb_record:
        return redirect(url_for('index'))
    
    return render_template('edit_lend_borrow.html', lb_record=lb_record)

@app.route('/delete_lend_borrow/<int:lb_id>', methods=['POST'])
def delete_lend_borrow(lb_id):
    conn = sqlite3.connect('web_expenses.db')
    conn.execute("DELETE FROM lends_borrows WHERE id = ?", (lb_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/send_email_report', methods=['POST'])
def send_email_report():
    # Placeholder route - returns success for now
    return jsonify({'success': True, 'message': 'Email feature not implemented yet'})

@app.route('/update_scheduler', methods=['POST'])
def update_scheduler():
    # Placeholder route - returns success for now
    return jsonify({'success': True, 'message': 'Scheduler feature not implemented yet'})

@app.route('/get_overspending_patterns')
def get_overspending_patterns():
    # Placeholder route - returns empty patterns for now
    return jsonify([])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5001)