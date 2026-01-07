# Expense Tracker App

A minimal desktop application for tracking personal expenses.

## Features

- **Add Expenses**: Record expenses with category, description, and amount
- **View Expenses**: List all expenses with date/time stamps
- **Delete Expenses**: Remove selected expenses
- **Total Calculation**: Automatic calculation of total expenses
- **Categories**: Predefined categories (Food, Transport, Entertainment, Bills, Shopping, Other)
- **Local Storage**: SQLite database for data persistence

## Usage

1. Run the application:
```bash
python expense_app.py
```

2. **Add Expense**: 
   - Select category from dropdown
   - Enter description
   - Enter amount
   - Click "Add Expense"

3. **Delete Expense**:
   - Select expense from list
   - Click "Delete Selected"

4. **View Total**: Total amount is displayed at the bottom

## Database

The app creates a local SQLite database file `expenses.db` to store all expense data.