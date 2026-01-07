# 💰 Modern Expense Tracker

A modern, responsive web-based expense tracking application built with Flask and SQLite.

## Features

- **Monthly Expense Tracking**: View expenses organized by month with automatic current month focus
- **Budget Management**: Set and track monthly budgets with progress indicators
- **Category & Subcategory Management**: Organize expenses with predefined and custom categories/subcategories
- **Payment Status Tracking**: Track pending and paid expenses
- **Savings Tracking**: Separate tracking for savings entries
- **Interactive Charts**: 
  - Pie chart for expense categories (month-specific)
  - Line chart for monthly trends
- **Expense Management**: Add, edit, and delete expenses with full CRUD operations
- **Responsive Design**: Modern UI that works on desktop and mobile devices
- **Indian Rupee Support**: Currency formatted for Indian users
- **Export Functionality**: Export data to Excel and PDF formats

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Icons**: Font Awesome
- **Styling**: Custom CSS with gradients and modern design

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Hello
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python web_expense_app.py
```

4. Open your browser and navigate to:
```
http://127.0.0.1:5001
```

## Usage

### Setting Up Budget
1. Enter your monthly budget in the "Set Budget" section
2. The dashboard will show your budget utilization and remaining amount

### Adding Expenses
1. Select a category from the dropdown
2. Choose or add a custom subcategory
3. Enter description and amount
4. Set payment status (Pending/Paid)
5. Click "Add Expense"

### Managing Expenses
- **Edit**: Click the "Edit" button on any expense to modify details
- **Delete**: Click the trash icon to remove an expense
- **Mark as Paid**: Click "Mark Paid" for pending expenses

### Monthly Navigation
- Use the month selector to view expenses from different months
- Click "Current Month" to return to the current month view
- Charts automatically update based on selected month

### Categories & Subcategories
- **Predefined Categories**: Food, Transport, Entertainment, Bills, Shopping, Savings, Other
- **Dynamic Subcategories**: Each category has relevant subcategories
- **Custom Subcategories**: Add new subcategories using the toggle button (+ icon)

## Database Schema

The application uses SQLite with the following main tables:
- `expenses`: Main expense records
- `categories`: Expense categories
- `subcategories`: Subcategories linked to categories
- `budget`: Monthly budget settings

## API Endpoints

- `GET /`: Main dashboard
- `POST /add_expense`: Add new expense
- `GET /edit_expense/<id>`: Edit expense form
- `POST /edit_expense/<id>`: Update expense
- `POST /delete_expense/<id>`: Delete expense
- `GET /get_subcategories/<category>`: Get subcategories for a category
- `GET /get_category_data`: Get category-wise expense data
- `GET /get_monthly_data`: Get monthly trend data
- `POST /set_budget`: Set monthly budget

## Features in Detail

### Dashboard
- Current month expense summary
- Budget vs actual spending with progress bars
- Month-over-month comparison
- Quick stats for paid, pending, and savings

### Charts
- **Category Pie Chart**: Shows expense distribution by category for selected month
- **Monthly Trends**: Line chart showing expense and savings trends over time

### Expense Management
- Date-grouped expense listing
- Real-time status updates
- Bulk operations support
- Search and filter capabilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions, please open an issue in the repository.