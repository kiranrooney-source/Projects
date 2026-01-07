import sqlite3
import pandas as pd
import os

def restore_data():
    """Restore data from CSV files to the SQLite database"""
    
    # Connect to database
    conn = sqlite3.connect('web_expenses.db')
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        conn.execute("DELETE FROM expenses")
        conn.execute("DELETE FROM budget")
        conn.execute("DELETE FROM categories")
        conn.execute("DELETE FROM subcategories")
        
        # Create lends_borrows table if it doesn't exist
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
        conn.execute("DELETE FROM lends_borrows")
        
        # Create scheduler_settings table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scheduler_settings (
                id INTEGER PRIMARY KEY,
                email_hour INTEGER,
                email_minute INTEGER
            )
        ''')
        conn.execute("DELETE FROM scheduler_settings")
        
        # Restore budget data
        print("Restoring budget data...")
        budget_df = pd.read_csv('recovered_data/budget.csv')
        for _, row in budget_df.iterrows():
            conn.execute("INSERT INTO budget (total_budget) VALUES (?)", (row['total_budget'],))
        
        # Restore categories data
        print("Restoring categories data...")
        categories_df = pd.read_csv('recovered_data/categories.csv')
        for _, row in categories_df.iterrows():
            conn.execute("INSERT INTO categories (id, name) VALUES (?, ?)", (row['id'], row['name']))
        
        # Restore subcategories data
        print("Restoring subcategories data...")
        subcategories_df = pd.read_csv('recovered_data/subcategories.csv')
        for _, row in subcategories_df.iterrows():
            conn.execute("INSERT INTO subcategories (id, category_id, name) VALUES (?, ?, ?)", 
                        (row['id'], row['category_id'], row['name']))
        
        # Restore expenses data
        print("Restoring expenses data...")
        expenses_df = pd.read_csv('recovered_data/expenses.csv')
        for _, row in expenses_df.iterrows():
            # Handle date format - extract just the date part if it contains time
            date_str = str(row['date'])
            if ' ' in date_str:
                date_str = date_str.split(' ')[0]
            
            conn.execute("""INSERT INTO expenses (id, date, category, subcategory, description, amount, payment_status, is_savings) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                        (row['id'], date_str, row['category'], row['subcategory'], 
                         row['description'], row['amount'], row['payment_status'], row['is_savings']))
        
        # Restore lends_borrows data
        print("Restoring lends & borrows data...")
        lends_borrows_df = pd.read_csv('recovered_data/lends_borrows.csv')
        for _, row in lends_borrows_df.iterrows():
            conn.execute("""INSERT INTO lends_borrows (id, date, name, amount, type, description, status) 
                           VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                        (row['id'], row['date'], row['name'], row['amount'], 
                         row['type'], row['description'], row['status']))
        
        # Set default scheduler settings
        print("Setting default scheduler settings...")
        conn.execute("INSERT INTO scheduler_settings (email_hour, email_minute) VALUES (?, ?)", (9, 0))
        
        # Commit all changes
        conn.commit()
        print("Data restoration completed successfully!")
        
        # Show summary
        cursor = conn.execute("SELECT COUNT(*) FROM expenses")
        expense_count = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM subcategories")
        subcategory_count = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM lends_borrows")
        lends_borrows_count = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT total_budget FROM budget LIMIT 1")
        budget_row = cursor.fetchone()
        budget = budget_row[0] if budget_row else 0
        
        print(f"\nRestoration Summary:")
        print(f"   • Expenses: {expense_count} records")
        print(f"   • Categories: {category_count} records")
        print(f"   • Subcategories: {subcategory_count} records")
        print(f"   • Lends & Borrows: {lends_borrows_count} records")
        print(f"   • Budget: Rs.{budget:.2f}")
        
    except Exception as e:
        print(f"Error during restoration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    # Check if recovered_data directory exists
    if not os.path.exists('recovered_data'):
        print("recovered_data directory not found!")
        exit(1)
    
    # Check if all required CSV files exist
    required_files = ['budget.csv', 'categories.csv', 'subcategories.csv', 'expenses.csv', 'lends_borrows.csv']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(f'recovered_data/{file}'):
            missing_files.append(file)
    
    if missing_files:
        print(f"Missing CSV files: {', '.join(missing_files)}")
        exit(1)
    
    print("Starting data restoration...")
    restore_data()