import json
import os
from datetime import datetime
from functools import wraps
from uuid import uuid4

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from decorators import role_required

# --- App Configuration ---
app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # Change this for production

# --- Data Management ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def get_data_path(filename):
    """Constructs the full path for a data file."""
    return os.path.join(DATA_DIR, filename)

def load_data(filename):
    """Loads data from a JSON file."""
    path = get_data_path(filename)
    if not os.path.exists(path):
        # Create the data directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)
        # Create the file with an empty dictionary if it doesn't exist
        with open(path, 'w') as f:
            json.dump({}, f)
        return {}
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(filename, data):
    """Saves data to a JSON file."""
    path = get_data_path(filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

# --- Role Permissions ---
ROLE_PERMISSIONS = load_data('role_permissions.json')

# --- Authentication ---
def login_required(f):
    """Decorator to ensure a user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# @app.before_request
# def check_user_permissions():
#     if request.endpoint and request.endpoint not in ['login', 'logout', 'static']:
#         user_role = session.get('user_role')
#         if user_role and request.endpoint not in ROLE_PERMISSIONS.get(user_role, []):
#             flash('You do not have permission to access this page.', 'danger')
#             return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_data('users.json')
        
        for user_id, user_data in users.items():
            if user_data['username'] == username and check_password_hash(user_data['password'], password):
                session['user_id'] = user_id
                session['user_name'] = user_data['name']
                session['user_role'] = user_data['role']
                flash(f'Welcome back, {user_data["name"]}!', 'success')
                return redirect(url_for('dashboard'))
        
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# --- Main Application Routes ---

@app.route('/')
@app.route('/dashboard')
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

@app.route('/sales')
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

@app.route('/purchases')
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

@app.route('/inventory')
@login_required
@role_required(['Admin', 'Manager'])
def inventory():
    # Placeholder for inventory page
    return render_template('inventory.html')

@app.route('/production')
@login_required
@role_required(['Admin', 'Manager'])
def production():
    # Placeholder for production page
    return render_template('production.html')

@app.route('/view_document')
@login_required
def view_document():
    # Placeholder for viewing documents
    all_data = {
        'rice_varieties': load_data('rice_varieties.json')
    }
    return render_template('view_document.html', data=all_data)

# --- User Management Routes ---

@app.route('/users')
@login_required
@role_required(['Admin'])
def users():
    all_users = load_data('users.json')
    return render_template('users.html', users=all_users, roles=ROLE_PERMISSIONS.keys(), ROLE_PERMISSIONS=ROLE_PERMISSIONS)

@app.route('/add_user', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_user():
    users = load_data('users.json')
    user_id = str(uuid4())
    
    # Check for existing username
    if any(u['username'] == request.form['username'] for u in users.values()):
        flash(f"Username '{request.form['username']}' already exists.", 'danger')
        return redirect(url_for('users'))

    users[user_id] = {
        'username': request.form['username'],
        'password': generate_password_hash(request.form['password']),
        'name': request.form['name'],
        'email': request.form['email'],
        'role': request.form['role'],
        'status': request.form['status'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('users.json', users)
    flash('User added successfully!', 'success')
    return redirect(url_for('users'))

@app.route('/edit_user/<user_id>', methods=['POST'])
@login_required
@role_required(['Admin'])
def edit_user(user_id):
    users = load_data('users.json')
    if user_id in users:
        # Check for existing username if it's being changed
        new_username = request.form['username']
        if (users[user_id]['username'] != new_username and
                any(u['username'] == new_username for u in users.values())):
            flash(f"Username '{new_username}' already exists.", 'danger')
            return redirect(url_for('users'))

        users[user_id]['username'] = new_username
        users[user_id]['name'] = request.form['name']
        users[user_id]['email'] = request.form['email']
        users[user_id]['role'] = request.form['role']
        users[user_id]['status'] = request.form['status']
        
        # Update password only if a new one is provided
        if request.form.get('password'):
            users[user_id]['password'] = generate_password_hash(request.form['password'])

        save_data('users.json', users)
        flash('User updated successfully!', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('users'))

@app.route('/delete_user/<user_id>')
@login_required
@role_required(['Admin'])
def delete_user(user_id):
    users = load_data('users.json')
    if user_id in users:
        # Prevent deleting the logged-in user
        if user_id == session.get('user_id'):
            flash('You cannot delete your own account.', 'danger')
            return redirect(url_for('users'))
        
        del users[user_id]
        save_data('users.json', users)
        flash('User deleted successfully!', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('users'))

@app.route('/save_role_permissions', methods=['POST'])
@login_required
@role_required(['Admin'])
def save_role_permissions():
    global ROLE_PERMISSIONS
    permissions = {}
    for role in ROLE_PERMISSIONS.keys():
        permissions[role] = request.form.getlist(f'{role}_permissions')
    save_data('role_permissions.json', permissions)
    ROLE_PERMISSIONS = permissions
    flash('Role permissions updated successfully!', 'success')
    return redirect(url_for('users'))

# --- Master Data Routes ---

@app.route('/masters')
@login_required
@role_required(['Admin'])
def masters():
    all_data = {
        'item_masters': load_data('item_master.json'),
        'units': load_data('units.json'),
        'services': load_data('services.json'),
        'locations': load_data('locations.json'),
        'companies': load_data('companies.json'),
        'warehouses': load_data('warehouses.json'),
        'accounts': load_data('accounts.json'),
        'agents': load_data('agents.json'),
        'vehicles': load_data('vehicles.json'),
        'transporters': load_data('transporters.json'),
        'rice_varieties': load_data('rice_varieties.json'),
    }
    
    custom_masters = load_data('masters.json')
    custom_master_data = {}
    for master_name, master_definition in custom_masters.items():
        custom_master_data[master_name] = {
            'definition': master_definition,
            'data': load_data(f'custom_master_{master_name}.json')
        }
    
    return render_template('masters.html', data=all_data, custom_masters=custom_master_data)

@app.route('/rice_varieties')
@login_required
@role_required(['Admin'])
def rice_varieties():
    all_data = {
        'rice_varieties': load_data('rice_varieties.json')
    }
    return render_template('rice_varieties.html', **all_data)

@app.route('/add_item_master', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_item_master():
    item_masters = load_data('item_master.json')
    item_master_id = str(uuid4())
    
    item_masters[item_master_id] = {
        'code': f"IM{len(item_masters) + 1:04d}",
        'name': request.form['name'],
        'type': request.form['type'],
        'grade': request.form['grade'],
        'unit_id': request.form['unit_id'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('item_master.json', item_masters)
    flash('Item master added successfully!', 'success')
    return redirect(url_for('masters'))

@app.route('/add_unit', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_unit():
    units = load_data('units.json')
    unit_id = str(uuid4())
    
    units[unit_id] = {
        'code': f"UN{len(units) + 1:04d}",
        'name': request.form['name'],
        'symbol': request.form['symbol'],
        'conversion_factor': request.form['conversion_factor'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('units.json', units)
    flash('Unit added successfully!', 'success')
    return redirect(url_for('masters'))

@app.route('/add_vehicle', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_vehicle():
    vehicles = load_data('vehicles.json')
    vehicle_id = str(uuid4())
    
    vehicles[vehicle_id] = {
        'code': f"VE{len(vehicles) + 1:04d}",
        'vehicle_no': request.form['vehicle_no'],
        'vehicle_type': request.form['vehicle_type'],
        'capacity': request.form['capacity'],
        'unit': request.form['unit'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('vehicles.json', vehicles)
    flash('Vehicle added successfully!', 'success')
    return redirect(url_for('masters'))

@app.route('/add_transporter', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_transporter():
    transporters = load_data('transporters.json')
    transporter_id = str(uuid4())
    
    transporters[transporter_id] = {
        'code': f"TR{len(transporters) + 1:04d}",
        'name': request.form['name'],
        'vehicle_id': request.form['vehicle_id'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('transporters.json', transporters)
    flash('Transporter added successfully!', 'success')
    return redirect(url_for('masters'))

@app.route('/add_rice_variety', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_rice_variety():
    rice_varieties = load_data('rice_varieties.json')
    rice_variety_id = str(uuid4())
    
    rice_varieties[rice_variety_id] = {
        'code': f"RV{len(rice_varieties) + 1:04d}",
        'name': request.form['name'],
        'type': request.form['type'],
        'grade': request.form['grade'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('rice_varieties.json', rice_varieties)
    flash('Rice variety added successfully!', 'success')
    return redirect(url_for('rice_varieties'))

@app.route('/edit_rice_variety/<rice_variety_id>', methods=['POST'])
@login_required
@role_required(['Admin'])
def edit_rice_variety(rice_variety_id):
    rice_varieties = load_data('rice_varieties.json')
    if rice_variety_id in rice_varieties:
        rice_varieties[rice_variety_id]['name'] = request.form['name']
        rice_varieties[rice_variety_id]['type'] = request.form['type']
        rice_varieties[rice_variety_id]['grade'] = request.form['grade']
        save_data('rice_varieties.json', rice_varieties)
        flash('Rice variety updated successfully!', 'success')
    else:
        flash('Rice variety not found.', 'danger')
    return redirect(url_for('rice_varieties'))

@app.route('/delete_rice_variety/<rice_variety_id>')
@login_required
@role_required(['Admin'])
def delete_rice_variety(rice_variety_id):
    rice_varieties = load_data('rice_varieties.json')
    if rice_variety_id in rice_varieties:
        del rice_varieties[rice_variety_id]
        save_data('rice_varieties.json', rice_varieties)
        flash('Rice variety deleted successfully!', 'success')
    else:
        flash('Rice variety not found.', 'danger')
    return redirect(url_for('rice_varieties'))

@app.route('/add_purchase_gate_pass', methods=['POST'])
@login_required
@role_required(['Admin', 'Manager'])
def add_purchase_gate_pass():
    gate_passes = load_data('gate_passes.json')
    gp_id = str(uuid4())

    gate_passes[gp_id] = {
        "gp_no": request.form['gp_no'],
        "gp_date": request.form['gp_date'],
        "purchase_order_id": request.form['purchase_order_id'],
        "supplier_id": request.form['supplier_id'],
        "vehicle_no": request.form['vehicle_no'],
        "driver_name": request.form['driver_name'],
        "items": request.form['items'],
        "origin": request.form['origin'],
        "purpose": request.form['purpose'],
        "type": "Inward"
    }

    save_data('gate_passes.json', gate_passes)
    flash('Inward Gate Pass created successfully!', 'success')
    return redirect(url_for('purchases'))

@app.route('/add_service', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_service():
    services = load_data('services.json')
    service_id = str(uuid4())
    
    services[service_id] = {
        'code': f"SR{len(services) + 1:04d}",
        'name': request.form['name'],
        'rate': request.form['rate'],
        'unit': request.form['unit'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('services.json', services)
    flash('Service added successfully!', 'success')
    return redirect(url_for('masters'))

@app.route('/add_location', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_location():
    locations = load_data('locations.json')
    location_id = str(uuid4())
    
    locations[location_id] = {
        'code': f"LO{len(locations) + 1:04d}",
        'name': request.form['name'],
        'type': request.form['type'],
        'address': request.form['address'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('locations.json', locations)
    flash('Location added successfully!', 'success')
    return redirect(url_for('masters'))

@app.route('/add_company', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_company():
    companies = load_data('companies.json')
    company_id = str(uuid4())
    
    companies[company_id] = {
        'code': f"CO{len(companies) + 1:04d}",
        'name': request.form['name'],
        'type': request.form['type'],
        'contact_person': request.form['contact_person'],
        'phone': request.form['phone'],
        'address': request.form['address'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('companies.json', companies)
    flash('Company added successfully!', 'success')
    return redirect(url_for('masters'))

@app.route('/add_warehouse', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_warehouse():
    warehouses = load_data('warehouses.json')
    warehouse_id = str(uuid4())
    
    warehouses[warehouse_id] = {
        'code': f"WH{len(warehouses) + 1:04d}",
        'name': request.form['name'],
        'location_id': request.form['location_id'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('warehouses.json', warehouses)
    flash('Warehouse added successfully!', 'success')
    return redirect(url_for('masters'))

@app.route('/add_account', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_account():
    accounts = load_data('accounts.json')
    account_id = str(uuid4())
    
    accounts[account_id] = {
        'code': f"AC{len(accounts) + 1:04d}",
        'name': request.form['name'],
        'type': request.form['type'],
        'category': request.form['category'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('accounts.json', accounts)
    flash('Account added successfully!', 'success')
    return redirect(url_for('masters'))
@app.route('/add_agent', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_agent():
    agents = load_data('agents.json')
    agent_id = str(uuid4())
    
    agents[agent_id] = {
        'code': f"AG{len(agents) + 1:04d}",
        'name': request.form['name'],
        'phone': request.form['phone'],
        'email': request.form['email'],
        'commission': request.form['commission'],
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_data('agents.json', agents)
    flash('Agent added successfully!', 'success')
    return redirect(url_for('masters'))


@app.route('/manage_masters')
@login_required
@role_required(['Admin'])
def manage_masters():
    custom_masters = load_data('masters.json')
    return render_template('manage_masters.html', custom_masters=custom_masters)

@app.route('/add_master_definition', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_master_definition():
    masters = load_data('masters.json')
    master_name = request.form['master_name']
    
    if master_name in masters:
        flash(f'Master "{master_name}" already exists.', 'danger')
        return redirect(url_for('manage_masters'))

    field_names = request.form.getlist('field_name[]')
    field_types = request.form.getlist('field_type[]')
    
    fields = [{'name': 'code', 'type': 'text'}]
    fields.extend([{'name': name, 'type': type} for name, type in zip(field_names, field_types)])
    
    masters[master_name] = {
        'fields': fields
    }
    
    save_data('masters.json', masters)
    
    # Create an empty data file for the new master
    save_data(f'custom_master_{master_name}.json', {})
    
    flash(f'Master "{master_name}" created successfully.', 'success')
    return redirect(url_for('manage_masters'))

@app.route('/delete_master_definition/<master_name>')
@login_required
@role_required(['Admin'])
def delete_master_definition(master_name):
    masters = load_data('masters.json')
    
    if master_name in masters:
        del masters[master_name]
        save_data('masters.json', masters)
        
        # Delete the data file
        os.remove(get_data_path(f'custom_master_{master_name}.json'))
        
        flash(f'Master "{master_name}" deleted successfully.', 'success')
    else:
        flash(f'Master "{master_name}" not found.', 'danger')
        
    return redirect(url_for('manage_masters'))


@app.route('/add_custom_master_data/<master_name>', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_custom_master_data(master_name):
    masters = load_data('masters.json')
    if master_name not in masters:
        flash(f'Master "{master_name}" not found.', 'danger')
        return redirect(url_for('masters'))

    master_definition = masters[master_name]
    data_file = f'custom_master_{master_name}.json'
    data = load_data(data_file)
    
    item_id = str(uuid4())
    new_item = {}
    for field in master_definition['fields']:
        new_item[field['name']] = request.form[field['name']]
    
    data[item_id] = new_item
    save_data(data_file, data)
    
    flash(f'Data added to "{master_name}" successfully.', 'success')
    return redirect(url_for('masters', _anchor=master_name.lower()))

@app.route('/delete_custom_master_data/<master_name>/<item_id>')
@login_required
@role_required(['Admin'])
def delete_custom_master_data(master_name, item_id):
    masters = load_data('masters.json')
    if master_name not in masters:
        flash(f'Master "{master_name}" not found.', 'danger')
        return redirect(url_for('masters'))

    data_file = f'custom_master_{master_name}.json'
    data = load_data(data_file)
    
    if item_id in data:
        del data[item_id]
        save_data(data_file, data)
        flash('Data deleted successfully.', 'success')
    else:
        flash('Item not found.', 'danger')
        
    return redirect(url_for('masters', _anchor=master_name.lower()))

# --- Main Execution ---
if __name__ == '__main__':
    # Create a default admin user if one doesn't exist
    users_data = load_data('users.json')
    if not any(u['username'] == 'admin' for u in users_data.values()):
        admin_id = str(uuid4())
        users_data[admin_id] = {
            'username': 'admin',
            'password': generate_password_hash('admin123'),
            'name': 'Administrator',
            'email': 'admin@example.com',
            'role': 'Admin',
            'status': 'Active',
            'created_date': datetime.now().strftime('%Y-%m-%d')
        }
        save_data('users.json', users_data)
        print("Default admin user created. Username: admin, Password: admin123")

    app.run(debug=True, port=5000)