# MFG Tool Dashboard

A web-based dashboard application for tracking manufacturing tool status, maintenance schedules, and responsible parties.

## Features

- 📊 **Real-time Dashboard**: View all manufacturing tools in a clean, organized table
- 🔄 **CSV Import**: Load data from CSV files with automatic database persistence
- 💾 **SQLite Database**: Persistent storage with automatic initialization
- 📈 **Statistics**: Live statistics showing operational, maintenance, and down tools
- 🎨 **Modern UI**: Responsive design with status badges and color coding
- 📁 **File Upload**: Upload new CSV files directly through the web interface

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Navigate to the application directory:
```bash
cd "/Users/dan1/R/PythonWorkArea/IBM Bob - MFG Tool Dashboard"
```

2. Install required dependencies:
```bash
pip install flask
```

## Usage

### Starting the Application

Run the application:
```bash
python app.py
```

The application will:
- Initialize the SQLite database
- Load sample data from `sample_data.csv` (if database is empty)
- Start the web server on `http://127.0.0.1:5000`

### Accessing the Dashboard

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### Using the Dashboard

1. **View Tools**: All tools are displayed in the main table with their current status
2. **Filter by Status**: Click on any statistics card to filter the table by that status:
   - Click "Total Tools" to show all tools
   - Click "Operational" to show only operational tools
   - Click "Under Maintenance" to show tools under maintenance or repair
   - Click "Down/Idle" to show down or idle tools
3. **Reload Data**: Click "Reload from Default CSV" to refresh from `sample_data.csv`
4. **Upload CSV**: Click "Upload New CSV" to load data from a different CSV file
5. **Statistics**: View real-time counts of operational, maintenance, and down tools

## CSV File Format

The application expects CSV files with the following columns:

| Column Name | Description | Example |
|-------------|-------------|---------|
| MFGToolName | Name/ID of the manufacturing tool | CNC Mill #1 |
| CurrentStatus | Current operational status | Operational, Under Repair, Down, Idle |
| NextAction | Scheduled next action | Scheduled Maintenance |
| ResponsibleParty | Person responsible for the tool | John Smith |
| ETA | Estimated time of completion | 2026-01-15 |

### Example CSV Format

```csv
MFGToolName,CurrentStatus,NextAction,ResponsibleParty,ETA
CNC Mill #1,Operational,Scheduled Maintenance,John Smith,2026-01-15
Lathe #3,Under Repair,Replace Bearings,Mike Johnson,2026-01-12
Drill Press #2,Operational,Calibration Check,Sarah Williams,2026-01-20
```

## File Structure

```
IBM Bob - MFG Tool Dashboard/
├── app.py                  # Main Flask application
├── sample_data.csv         # Sample manufacturing tool data
├── mfg_tools.db           # SQLite database (auto-generated)
├── templates/
│   └── index.html         # Main dashboard HTML template
├── static/
│   ├── styles.css         # Dashboard styling
│   └── script.js          # Client-side JavaScript
└── README.md              # This file
```

## API Endpoints

### GET /
Main dashboard page

### GET /api/tools
Returns all tools as JSON
```json
[
  {
    "id": 1,
    "mfg_tool_name": "CNC Mill #1",
    "current_status": "Operational",
    "next_action": "Scheduled Maintenance",
    "responsible_party": "John Smith",
    "eta": "2026-01-15",
    "last_updated": "2026-01-08 12:00:00"
  }
]
```

### POST /api/reload
Reload data from default CSV file
```json
{
  "csv_path": "/path/to/file.csv"  // Optional, defaults to sample_data.csv
}
```

### POST /api/upload
Upload and process a new CSV file
- Content-Type: multipart/form-data
- Field name: file

## Database Schema

### tools table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| mfg_tool_name | TEXT | Tool name/identifier |
| current_status | TEXT | Current operational status |
| next_action | TEXT | Next scheduled action |
| responsible_party | TEXT | Person responsible |
| eta | TEXT | Estimated completion date |
| last_updated | TIMESTAMP | Last update timestamp |

## Status Types

The application recognizes the following status types with color coding:

- **Operational** (Green): Tool is functioning normally
- **Under Maintenance** (Yellow): Tool is undergoing scheduled maintenance
- **Under Repair** (Yellow): Tool is being repaired
- **Down** (Red): Tool is not operational
- **Idle** (Blue): Tool is not in use

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the port in `app.py`:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Change to different port
```

### Flask Not Found
Install Flask:
```bash
pip install flask
```

### CSV File Not Found
Ensure `sample_data.csv` exists in the application directory, or upload a new CSV file through the web interface.

### Database Issues
Delete `mfg_tools.db` and restart the application to recreate the database:
```bash
rm mfg_tools.db
python app.py
```

## Development

### Adding New Features

The application is built with:
- **Backend**: Flask (Python web framework)
- **Database**: SQLite3 (built-in Python database)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **No external JavaScript libraries required**

### Customization

- **Styling**: Modify `static/styles.css`
- **Behavior**: Modify `static/script.js`
- **Layout**: Modify `templates/index.html`
- **Backend Logic**: Modify `app.py`

## License

This application is provided as-is for manufacturing tool tracking purposes.

## Support

For issues or questions, refer to the application logs in the terminal where `app.py` is running.

## Version History

- **v1.0.0** (2026-01-08): Initial release
  - CSV import functionality
  - SQLite database persistence
  - Web-based dashboard
  - File upload capability
  - Real-time statistics