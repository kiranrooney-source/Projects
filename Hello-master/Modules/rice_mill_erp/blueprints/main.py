from flask import Blueprint, render_template
from .. import load_data
from ..decorators import login_required, role_required
from datetime import datetime

main_bp = Blueprint('main', __name__, template_folder='../../templates')

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    sales = load_data('sales.json')
    inventory = load_data('inventory.json')
    production = load_data('production.json')
    purchases = load_data('purchases.json')
    item_masters = load_data('item_master.json')

    # Example stats - you can make these more complex
    stats = {
        'inventory_items': len(inventory),
        'total_sales': len(sales),
        'production_batches': len(production),
        'total_purchases': len(purchases),
        'pending_orders': sum(1 for s in sales.values() if s.get('status') == 'Pending'),
        'item_masters': len(item_masters),
        'total_revenue': sum(float(s.get('total', 0)) for s in sales.values()),
        'rice_varieties': len(load_data('rice_varieties.json'))
    }
    return render_template('dashboard.html', stats=stats)

@main_bp.route('/sales')
@login_required
@role_required(['Admin', 'Manager'])
def sales():
    # These are just placeholders for now to make the template render
    all_data = {
        'sales': load_data('sales.json'),
        'delivery_notes': load_data('delivery_notes.json'),
        'sales_invoices': load_data('sales_invoices.json'),
        'gate_passes': load_data('gate_passes.json'),
        'bag_receipts': load_data('bag_receipts.json'),
        'bag_issues': load_data('bag_issues.json'),
        'data': {
            'accounts': load_data('accounts.json'),
            'item_masters': load_data('item_master.json'),
            'units': load_data('units.json'),
            'rice_varieties': load_data('rice_varieties.json'),
        },
        'fiscal_year': datetime.now().strftime('%Y'),
        'today': datetime.now().strftime('%Y-%m-%d')
    }
    return render_template('sales.html', **all_data)

@main_bp.route('/purchases')
@login_required
@role_required(['Admin', 'Manager'])
def purchases():
    all_data = {
        'purchases': load_data('purchases.json'),
        'mrns': load_data('mrns.json'),
        'vouchers': load_data('purchase_vouchers.json'),
        'gate_passes': load_data('gate_passes.json'),
        'data': {
            'companies': load_data('companies.json'),
            'accounts': load_data('accounts.json'),
            'agents': load_data('agents.json'),
            'item_masters': load_data('item_master.json'),
            'units': load_data('units.json'),
            'rice_varieties': load_data('rice_varieties.json'),
        },
        'fiscal_year': datetime.now().strftime('%Y'),
        'today': datetime.now().strftime('%Y-%m-%d')
    }
    return render_template('purchases.html', **all_data)

@main_bp.route('/inventory')
@login_required
@role_required(['Admin', 'Manager'])
def inventory():
    # Placeholder for inventory page
    return render_template('inventory.html')

@main_bp.route('/production')
@login_required
@role_required(['Admin', 'Manager'])
def production():
    # Placeholder for production page
    return render_template('production.html')

@main_bp.route('/view_document')
@login_required
def view_document():
    # Placeholder for viewing documents
    all_data = {
        'rice_varieties': load_data('rice_varieties.json')
    }
    return render_template('view_document.html', data=all_data)
