# Modern Expense Tracker - Local Server Setup

## Quick Start

### Option 1: Using Batch File (Easiest)
1. Double-click `run_server.bat`
2. The server will start automatically
3. Open your browser and go to: `http://localhost:5001`

### Option 2: Using Command Line
1. Open Command Prompt or PowerShell
2. Navigate to the project folder:
   ```
   cd "c:\Users\KIRAN\Hello"
   ```
3. Run the server:
   ```
   python web_expense_app.py
   ```
4. Open your browser and go to: `http://localhost:5001`

## Features Available

✅ **Dashboard** - View budget, expenses, savings, and remaining amount
✅ **Add Expenses** - Record new expenses with categories and subcategories
✅ **Payment Status** - Track Pending/Paid status
✅ **Savings Tracking** - Separate savings category that doesn't count as expenses
✅ **Previous Month Comparison** - Compare current vs previous month
✅ **Charts** - Visual analytics with subcategory breakdown and 3D pie chart
✅ **Export** - Download Excel and PDF reports
✅ **Edit/Delete** - Modify or remove expenses
✅ **Collapsible Sections** - Hide/show different sections
✅ **Indian Rupees** - Currency displayed in ₹

## Default Categories
- Food
- Transport
- Entertainment
- Bills
- Shopping
- Savings (special category)
- Other

## Database
- Uses SQLite database (`web_expenses.db`)
- Automatically created on first run
- Stores all your expense data locally

## Stopping the Server
- Press `Ctrl+C` in the command window
- Or simply close the command window

## Accessing from Other Devices on Same Network
To access from other devices on your local network:
1. Find your computer's IP address:
   ```
   ipconfig
   ```
2. Look for "IPv4 Address" (e.g., 192.168.1.100)
3. On other devices, go to: `http://YOUR_IP:5001`
   (e.g., `http://192.168.1.100:5001`)

## Troubleshooting
- Make sure Python is installed
- Ensure all required packages are installed: `pip install -r web_requirements.txt`
- Check if port 5001 is available
- Firewall might block access from other devices

## File Structure
```
Hello/
├── web_expense_app.py          # Main Flask application
├── templates/
│   └── index.html              # Web interface
├── web_expenses.db             # SQLite database (created automatically)
├── run_server.bat              # Easy server startup
├── web_requirements.txt        # Python dependencies
└── setup_instructions.md       # This file
```