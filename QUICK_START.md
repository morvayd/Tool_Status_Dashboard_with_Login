# Quick Start Guide - MFG Tool Dashboard

## Installation & Running

### 1. Install Flask (if not already installed)
```bash
pip install flask
```

### 2. Navigate to the application directory
```bash
cd "/Users/dan1/R/PythonWorkArea/IBM Bob - MFG Tool Dashboard"
```

### 3. Run the application
```bash
python app.py
```

### 4. Open your browser
Navigate to: **http://127.0.0.1:5000**

## What You'll See

- **Dashboard**: A table showing all manufacturing tools with their status
- **Statistics Cards**: Real-time counts of operational, maintenance, and down tools (clickable to filter!)
- **Reload Button**: Refresh data from the default CSV file
- **Upload Button**: Load data from a custom CSV file

## Quick Tips

💡 **Click any statistics card** to filter the table by that status type
💡 Click "Total Tools" card to show all tools again
💡 The active filter is highlighted with a gradient background

## Features at a Glance

✅ **Automatic Database**: SQLite database is created automatically on first run  
✅ **Sample Data**: Pre-loaded with 15 sample manufacturing tools  
✅ **CSV Import**: Load data from any CSV file with the correct format  
✅ **Persistent Storage**: All data is saved to the database  
✅ **Responsive Design**: Works on desktop and mobile devices  

## CSV File Format

Your CSV must have these exact column names:
- `MFGToolName`
- `CurrentStatus`
- `NextAction`
- `ResponsibleParty`
- `ETA`

Example:
```csv
MFGToolName,CurrentStatus,NextAction,ResponsibleParty,ETA
CNC Mill #1,Operational,Scheduled Maintenance,John Smith,2026-01-15
```

## Troubleshooting

**Port 5000 already in use?**
- Edit `app.py` and change the port number in the last line

**Flask not found?**
- Run: `pip install flask`

**Need to reset the database?**
- Delete `mfg_tools.db` and restart the app

## Next Steps

See **README.md** for complete documentation including:
- API endpoints
- Database schema
- Customization options
- Development guide