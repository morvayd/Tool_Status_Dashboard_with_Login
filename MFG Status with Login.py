"""
MFG Tool Dashboard Application with User Authentication
Displays manufacturing tool status with user login and tool assignment
"""

import os
import sqlite3
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'  # Change this in production!

# Configuration
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'mfg_tools.db'
DEFAULT_CSV = BASE_DIR / 'sample_data.csv'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, employee_id, username, first_name, last_name, is_admin, assigned_tool_id):
        self.id = id
        self.employee_id = employee_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
        self.assigned_tool_id = assigned_tool_id
    
    @property
    def full_name(self):
        """Return full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(
            id=user_data['id'],
            employee_id=user_data['employee_id'],
            username=user_data['username'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_admin=user_data['is_admin'],
            assigned_tool_id=user_data['assigned_tool_id']
        )
    return None

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def init_database():
    """Initialize SQLite database with tools and users tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tools table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mfg_tool_name TEXT NOT NULL,
            current_status TEXT NOT NULL,
            next_action TEXT NOT NULL,
            responsible_party TEXT NOT NULL,
            eta TEXT NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            assigned_tool_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assigned_tool_id) REFERENCES tools(id)
        )
    ''')
    
    # Check if first_name and last_name columns exist, add them if not (migration)
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'first_name' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN first_name TEXT')
    if 'last_name' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN last_name TEXT')
    
    # Check if admin user exists, if not create one
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        # Create default admin user (employee_id: admin, password: admin123)
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (employee_id, username, password_hash, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'Administrator', admin_password, 1))
        print("Default admin user created - Employee ID: admin, Password: admin123")
    
    conn.commit()
    conn.close()

def load_csv_to_db(csv_path):
    """Load CSV data into SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM tools')
    
    # Read CSV and insert data
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            cursor.execute('''
                INSERT INTO tools (mfg_tool_name, current_status, next_action, 
                                   responsible_party, eta)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['MFGToolName'],
                row['CurrentStatus'],
                row['NextAction'],
                row['ResponsibleParty'],
                row['ETA']
            ))
    
    conn.commit()
    conn.close()

def get_all_tools():
    """Retrieve all tools from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, mfg_tool_name, current_status, next_action, 
               responsible_party, eta, last_updated
        FROM tools
        ORDER BY id
    ''')
    
    tools = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return tools

def get_tool_by_id(tool_id):
    """Get a specific tool by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, mfg_tool_name, current_status, next_action, 
               responsible_party, eta, last_updated
        FROM tools
        WHERE id = ?
    ''', (tool_id,))
    
    tool = cursor.fetchone()
    conn.close()
    
    return dict(tool) if tool else None

def update_tool_status(tool_id, current_status, next_action, eta, responsible_party=None):
    """Update tool status in database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if responsible_party:
        cursor.execute('''
            UPDATE tools
            SET current_status = ?,
                next_action = ?,
                eta = ?,
                responsible_party = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (current_status, next_action, eta, responsible_party, tool_id))
    else:
        cursor.execute('''
            UPDATE tools
            SET current_status = ?,
                next_action = ?,
                eta = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (current_status, next_action, eta, tool_id))
    
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    tools = get_all_tools()
    return render_template('index.html', tools=tools)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin'))
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        password = request.form.get('password')
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE employee_id = ?', (employee_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(
                id=user_data['id'],
                employee_id=user_data['employee_id'],
                username=user_data['username'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_admin=user_data['is_admin'],
                assigned_tool_id=user_data['assigned_tool_id']
            )
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            
            # Redirect based on user type
            if user.is_admin:
                return redirect(url_for('admin'))
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid employee ID or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    """User dashboard for updating assigned tool"""
    if current_user.is_admin:
        return redirect(url_for('admin'))
    
    tool = None
    if current_user.assigned_tool_id:
        tool = get_tool_by_id(current_user.assigned_tool_id)
    
    return render_template('user_dashboard.html', tool=tool)

@app.route('/user/update-tool', methods=['POST'])
@login_required
def update_user_tool():
    """Update tool status by user"""
    if not current_user.assigned_tool_id:
        return jsonify({'success': False, 'message': 'No tool assigned to your account'}), 400
    
    try:
        data = request.get_json()
        current_status = data.get('current_status')
        next_action = data.get('next_action')
        eta = data.get('eta')
        
        if not all([current_status, next_action, eta]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        # Update tool status with user's full name as responsible party
        update_tool_status(
            current_user.assigned_tool_id,
            current_status,
            next_action,
            eta,
            current_user.full_name
        )
        
        return jsonify({
            'success': True,
            'message': 'Tool status updated successfully'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin')
@login_required
@admin_required
def admin():
    """Admin dashboard"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute('''
        SELECT u.*, t.mfg_tool_name
        FROM users u
        LEFT JOIN tools t ON u.assigned_tool_id = t.id
        ORDER BY u.is_admin DESC, u.username
    ''')
    users = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    tools = get_all_tools()
    
    return render_template('admin.html', users=users, tools=tools)

@app.route('/admin/create-user', methods=['POST'])
@login_required
@admin_required
def create_user():
    """Create new user"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        username = data.get('username')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        password = data.get('password')
        is_admin = data.get('is_admin', 0)
        assigned_tool_id = data.get('assigned_tool_id')
        
        if not all([employee_id, username, password]):
            return jsonify({'success': False, 'message': 'Employee ID, username, and password are required'}), 400
        
        # Check if employee_id already exists
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE employee_id = ?', (employee_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Employee ID already exists'}), 400
        
        # Create user
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (employee_id, username, first_name, last_name, password_hash, is_admin, assigned_tool_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (employee_id, username, first_name, last_name, password_hash, is_admin, assigned_tool_id if assigned_tool_id else None))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'User created successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/update-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user(user_id):
    """Update user information"""
    try:
        data = request.get_json()
        username = data.get('username')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        is_admin = data.get('is_admin', 0)
        assigned_tool_id = data.get('assigned_tool_id')
        new_password = data.get('new_password')
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if new_password:
            password_hash = generate_password_hash(new_password)
            cursor.execute('''
                UPDATE users
                SET username = ?, first_name = ?, last_name = ?, is_admin = ?, assigned_tool_id = ?, password_hash = ?
                WHERE id = ?
            ''', (username, first_name, last_name, is_admin, assigned_tool_id if assigned_tool_id else None, password_hash, user_id))
        else:
            cursor.execute('''
                UPDATE users
                SET username = ?, first_name = ?, last_name = ?, is_admin = ?, assigned_tool_id = ?
                WHERE id = ?
            ''', (username, first_name, last_name, is_admin, assigned_tool_id if assigned_tool_id else None, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'User updated successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/delete-user/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    try:
        # Prevent deleting yourself
        if user_id == current_user.id:
            return jsonify({'success': False, 'message': 'Cannot delete your own account'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """API endpoint to get all tools"""
    tools = get_all_tools()
    return jsonify(tools)

@app.route('/api/reload', methods=['POST'])
@login_required
@admin_required
def reload_data():
    """API endpoint to reload data from CSV (admin only)"""
    try:
        data = request.get_json()
        csv_path = data.get('csv_path', str(DEFAULT_CSV))
        
        if not os.path.exists(csv_path):
            return jsonify({
                'success': False,
                'message': f'CSV file not found: {csv_path}'
            }), 404
        
        load_csv_to_db(csv_path)
        tools = get_all_tools()
        
        return jsonify({
            'success': True,
            'message': f'Successfully loaded {len(tools)} tools from CSV',
            'tools': tools
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading CSV: {str(e)}'
        }), 500

@app.route('/api/upload', methods=['POST'])
@login_required
@admin_required
def upload_csv():
    """API endpoint to upload and process a new CSV file (admin only)"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'message': 'File must be a CSV'
            }), 400
        
        temp_path = BASE_DIR / 'temp_upload.csv'
        file.save(temp_path)
        
        load_csv_to_db(temp_path)
        tools = get_all_tools()
        
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'message': f'Successfully loaded {len(tools)} tools from uploaded CSV',
            'tools': tools
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing upload: {str(e)}'
        }), 500

def initialize_app():
    """Initialize the application"""
    init_database()
    
    # Load default CSV if database is empty
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM tools')
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0 and DEFAULT_CSV.exists():
        print(f"Loading default data from {DEFAULT_CSV}")
        load_csv_to_db(DEFAULT_CSV)

if __name__ == '__main__':
    initialize_app()
    print("=" * 60)
    print("MFG Tool Dashboard Application with Authentication")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Default CSV: {DEFAULT_CSV}")
    print("Default Admin - Employee ID: admin, Password: admin123")
    print("Starting server on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)