# MFG Tool Dashboard - Authentication System Guide

## Overview

The MFG Tool Dashboard now includes a comprehensive user authentication system with role-based access control. Users can log in, update their assigned tools, and administrators can manage user accounts.

## Features

### 🔐 User Authentication
- Secure login with employee ID and password
- Password hashing using Werkzeug
- Session management with Flask-Login
- Automatic logout functionality

### 👥 User Roles

#### Regular Users
- View the main dashboard (read-only)
- Access personal dashboard to update assigned tool
- Update tool status, next action, and ETA
- Cannot upload CSV files or reload data

#### Administrators
- Full access to all features
- Manage user accounts (create, edit, delete)
- Assign tools to users
- Upload and reload CSV data
- Access admin panel for user management

## Getting Started

### Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

The new dependencies include:
- Flask==3.0.0
- Flask-Login==0.6.3

### First Time Setup

1. Start the application:
```bash
python app.py
```

2. The system will automatically create:
   - Users table in the database
   - Default admin account

### Default Admin Account

**Employee ID:** `admin`  
**Password:** `admin123`

⚠️ **IMPORTANT:** Change the admin password immediately after first login!

## User Guide

### Logging In

1. Click the **"🔐 Login"** button on the main dashboard
2. Enter your Employee ID and Password
3. Click **"Login"**

After successful login:
- **Regular users** are redirected to their personal dashboard
- **Administrators** are redirected to the admin panel

### Regular User Dashboard

#### Viewing Your Assigned Tool

Once logged in, users can see:
- Tool name
- Current status
- Next action
- ETA
- Last updated timestamp

#### Updating Tool Status

1. Navigate to your dashboard (click "My Tool" button)
2. Fill in the update form:
   - **Current Status**: Select from dropdown (Operational, Under Maintenance, Under Repair, Down, Idle)
   - **Next Action**: Describe what needs to be done next
   - **ETA**: Set the estimated completion date
3. Click **"💾 Update Tool Status"**
4. Confirmation message will appear

### Administrator Functions

#### Accessing Admin Panel

1. Log in with admin credentials
2. Click **"Admin Panel"** button in the header
3. Or navigate directly after login

#### Creating New Users

1. In the Admin Panel, click **"➕ Create New User"**
2. Fill in the form:
   - **Employee ID**: Unique identifier (required)
   - **Username**: Display name (required)
   - **Password**: Initial password (required)
   - **Assigned Tool**: Select from dropdown (optional)
   - **Admin User**: Check if user should have admin privileges
3. Click **"Create User"**

#### Editing Users

1. Find the user in the users table
2. Click **"Edit"** button
3. Modify:
   - Username
   - Password (leave blank to keep current)
   - Assigned tool
   - Admin status
4. Click **"Update User"**

#### Deleting Users

1. Find the user in the users table
2. Click **"Delete"** button
3. Confirm deletion
4. Note: You cannot delete your own account

#### Assigning Tools to Users

Tools can be assigned during user creation or editing:
1. Select a tool from the **"Assigned Tool"** dropdown
2. Each user can be assigned to one tool
3. Multiple users can be assigned to the same tool
4. Users without assigned tools will see a "No Tool Assigned" message

## Database Schema

### Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| employee_id | TEXT | Unique employee identifier |
| username | TEXT | Display name |
| password_hash | TEXT | Hashed password |
| is_admin | INTEGER | 1 for admin, 0 for regular user |
| assigned_tool_id | INTEGER | Foreign key to tools table |
| created_at | TIMESTAMP | Account creation date |

### Tools Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| mfg_tool_name | TEXT | Tool name/identifier |
| current_status | TEXT | Current operational status |
| next_action | TEXT | Next scheduled action |
| responsible_party | TEXT | Person responsible |
| eta | TEXT | Estimated completion date |
| last_updated | TIMESTAMP | Last update timestamp |

## API Endpoints

### Authentication Endpoints

#### POST /login
Login with employee ID and password
```
Form Data:
- employee_id: string
- password: string
```

#### GET /logout
Logout current user (requires authentication)

### User Endpoints

#### GET /user/dashboard
View user's personal dashboard (requires authentication)

#### POST /user/update-tool
Update assigned tool status (requires authentication)
```json
{
  "current_status": "Operational",
  "next_action": "Scheduled Maintenance",
  "eta": "2026-01-20"
}
```

### Admin Endpoints

#### GET /admin
Admin panel (requires admin authentication)

#### POST /admin/create-user
Create new user (requires admin authentication)
```json
{
  "employee_id": "emp123",
  "username": "John Doe",
  "password": "password123",
  "is_admin": 0,
  "assigned_tool_id": 5
}
```

#### POST /admin/update-user/<user_id>
Update user information (requires admin authentication)
```json
{
  "username": "John Doe",
  "new_password": "newpassword123",
  "is_admin": 0,
  "assigned_tool_id": 5
}
```

#### DELETE /admin/delete-user/<user_id>
Delete user (requires admin authentication)

## Security Features

### Password Security
- Passwords are hashed using Werkzeug's `generate_password_hash`
- Passwords are never stored in plain text
- Password verification uses `check_password_hash`

### Session Management
- Flask-Login manages user sessions
- Sessions expire when browser closes
- Logout clears session data

### Access Control
- `@login_required` decorator protects authenticated routes
- `@admin_required` decorator protects admin-only routes
- Users cannot access other users' data
- Admins cannot delete their own accounts

### CSRF Protection
- Secret key configured for session security
- Change `SECRET_KEY` in production!

## Best Practices

### For Administrators

1. **Change Default Password**: Immediately change the admin password after first login
2. **Strong Passwords**: Enforce strong passwords for all users
3. **Regular Audits**: Review user accounts regularly
4. **Tool Assignment**: Ensure each user has the correct tool assigned
5. **Backup Database**: Regularly backup `mfg_tools.db`

### For Users

1. **Keep Password Secure**: Don't share your password
2. **Update Regularly**: Update tool status at least once per shift
3. **Accurate Information**: Provide accurate status and ETA information
4. **Logout**: Always logout when finished

## Troubleshooting

### Cannot Login

**Problem**: "Invalid employee ID or password"

**Solutions**:
- Verify employee ID is correct (case-sensitive)
- Verify password is correct
- Contact administrator to reset password
- Check if account exists in admin panel

### No Tool Assigned

**Problem**: "No tool assigned to your account"

**Solution**:
- Contact administrator to assign a tool
- Administrator can assign tool in admin panel

### Permission Denied

**Problem**: "Admin access required"

**Solution**:
- Feature requires admin privileges
- Contact administrator if you need admin access

### Database Errors

**Problem**: Database connection or query errors

**Solutions**:
- Ensure `mfg_tools.db` exists and is writable
- Check file permissions
- Restart the application
- Check application logs

## Configuration

### Secret Key

⚠️ **IMPORTANT**: Change the secret key in production!

In `app.py`, line 17:
```python
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
```

Generate a secure secret key:
```python
import secrets
print(secrets.token_hex(32))
```

### Session Configuration

Modify session settings in `app.py`:
```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
```

## Upgrading from Previous Version

If upgrading from a version without authentication:

1. **Backup Database**: 
   ```bash
   cp mfg_tools.db mfg_tools.db.backup
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**: The users table will be created automatically

4. **Login as Admin**: Use default credentials (admin/admin123)

5. **Create User Accounts**: Add accounts for all users

6. **Assign Tools**: Assign tools to users in admin panel

## Support

For issues or questions:
- Check application logs in terminal
- Review this guide
- Check database integrity
- Verify all dependencies are installed

## Version History

- **v2.0.0** (2026-01-16): Added authentication system
  - User login and session management
  - Role-based access control
  - User dashboard for tool updates
  - Admin panel for user management
  - Password hashing and security features

- **v1.0.0** (2026-01-08): Initial release
  - Basic tool dashboard
  - CSV import functionality
  - SQLite database persistence