// MFG Tool Dashboard JavaScript

// Global variable to track current filter
let currentFilter = 'all';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateStats();
    updateLastRefresh();
    
    // Set up event listeners (only if elements exist)
    const reloadBtn = document.getElementById('reloadBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    
    if (reloadBtn) {
        reloadBtn.addEventListener('click', reloadFromDefaultCSV);
    }
    if (uploadBtn) {
        uploadBtn.addEventListener('click', () => {
            fileInput.click();
        });
    }
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
    
    // Set up stat card click listeners for filtering
    setupStatCardFilters();
});

/**
 * Set up click handlers for stat cards to filter table
 */
function setupStatCardFilters() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            const cardClasses = this.classList;
            let filterType = 'all';
            
            if (cardClasses.contains('operational')) {
                filterType = 'operational';
            } else if (cardClasses.contains('maintenance')) {
                filterType = 'maintenance';
            } else if (cardClasses.contains('down')) {
                filterType = 'down';
            }
            
            filterTableByStatus(filterType);
        });
    });
}

/**
 * Filter table rows by status type
 */
function filterTableByStatus(filterType) {
    const rows = document.querySelectorAll('#toolsTableBody tr');
    const statCards = document.querySelectorAll('.stat-card');
    
    // Update current filter
    currentFilter = filterType;
    
    // Remove active class from all cards - next line original uncommented
    statCards.forEach(card => card.classList.remove('active'));
    
    // Add active class to clicked card
    if (filterType === 'operational') {
        document.querySelector('.stat-card.operational').classList.add('active');
    } else if (filterType === 'maintenance') {
        document.querySelector('.stat-card.maintenance').classList.add('active');
    } else if (filterType === 'down') {
        document.querySelector('.stat-card.down').classList.add('active');
    } else {
        document.querySelector('.stat-card:not(.operational):not(.maintenance):not(.down)').classList.add('active');
    }
    
    // Filter rows
    rows.forEach(row => {
        const status = row.dataset.status.toLowerCase();
        let shouldShow = false;
        
        if (filterType === 'all') {
            shouldShow = true;
        } else if (filterType === 'operational') {
            shouldShow = status === 'operational';
        } else if (filterType === 'maintenance') {
            shouldShow = status.includes('maintenance') || status.includes('repair');
        } else if (filterType === 'down') {
            shouldShow = status === 'down' || status === 'idle';
        }
        
        if (shouldShow) {
            row.style.display = '';
            row.style.animation = 'fadeIn 0.3s ease';
        } else {
            row.style.display = 'none';
        }
    });
    
    // Show message
    const filterMessages = {
        'all': 'Showing all tools',
        'operational': 'Showing operational tools only',
        'maintenance': 'Showing tools under maintenance/repair',
        'down': 'Showing down/idle tools only'
    };
    
    showMessage(filterMessages[filterType], 'info');
}

/**
 * Update statistics cards based on current table data
 */
function updateStats() {
    const rows = document.querySelectorAll('#toolsTableBody tr');
    let operational = 0;
    let maintenance = 0;
    let down = 0;
    
    rows.forEach(row => {
        const status = row.dataset.status.toLowerCase();
        if (status === 'operational') {
            operational++;
        } else if (status.includes('maintenance') || status.includes('repair')) {
            maintenance++;
        } else if (status === 'down' || status === 'idle') {
            down++;
        }
    });
    
    document.getElementById('totalTools').textContent = rows.length;
    document.getElementById('operationalTools').textContent = operational;
    document.getElementById('maintenanceTools').textContent = maintenance;
    document.getElementById('downTools').textContent = down;
}

/**
 * Update the last refresh timestamp
 */
function updateLastRefresh() {
    const now = new Date();
    const formatted = now.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('lastRefresh').textContent = formatted;
}

/**
 * Show status message to user
 */
function showMessage(message, type = 'info') {
    const messageDiv = document.getElementById('statusMessage');
    messageDiv.textContent = message;
    messageDiv.className = `status-message ${type} show`;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 5000);
}

/**
 * Reload data from default CSV file
 */
async function reloadFromDefaultCSV() {
    const btn = document.getElementById('reloadBtn');
    const originalText = btn.innerHTML;
    
    try {
        // Show loading state
        btn.disabled = true;
        btn.innerHTML = '<span class="icon">⏳</span> Loading...';
        
        const response = await fetch('/api/reload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateTable(data.tools);
            showMessage(data.message, 'success');
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Error reloading data: ' + error.message, 'error');
    } finally {
        // Restore button state
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

/**
 * Handle CSV file upload
 */
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const btn = document.getElementById('uploadBtn');
    const originalText = btn.innerHTML;
    
    try {
        // Show loading state
        btn.disabled = true;
        btn.innerHTML = '<span class="icon">⏳</span> Uploading...';
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateTable(data.tools);
            showMessage(data.message, 'success');
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Error uploading file: ' + error.message, 'error');
    } finally {
        // Restore button state
        btn.disabled = false;
        btn.innerHTML = originalText;
        // Clear file input
        event.target.value = '';
    }
}

/**
 * Update the table with new data
 */
function updateTable(tools) {
    const tbody = document.getElementById('toolsTableBody');
    tbody.innerHTML = '';
    
    tools.forEach(tool => {
        const row = document.createElement('tr');
        row.dataset.status = tool.current_status;
        
        const statusClass = tool.current_status.toLowerCase().replace(/\s+/g, '-');
        
        row.innerHTML = `
            <td>${tool.id}</td>
            <td class="tool-name">${escapeHtml(tool.mfg_tool_name)}</td>
            <td>
                <span class="status-badge status-${statusClass}">
                    ${escapeHtml(tool.current_status)}
                </span>
            </td>
            <td>${escapeHtml(tool.next_action)}</td>
            <td>${escapeHtml(tool.responsible_party)}</td>
            <td>${escapeHtml(tool.eta)}</td>
            <td class="timestamp">${escapeHtml(tool.last_updated)}</td>
        `;
        
        tbody.appendChild(row);
    });
    
    // Update stats and timestamp
    updateStats();
    updateLastRefresh();
    
    // Re-setup stat card filters
    setupStatCardFilters();
    
    // Re-apply current filter if any
    if (currentFilter !== 'all') {
        filterTableByStatus(currentFilter);
    }
    
    // Add fade-in animation
    tbody.style.animation = 'fadeIn 0.5s ease';
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Fetch and refresh data from API
 */
async function refreshData() {
    try {
        const response = await fetch('/api/tools');
        const tools = await response.json();
        updateTable(tools);
        showMessage('Data refreshed successfully', 'success');
    } catch (error) {
        showMessage('Error refreshing data: ' + error.message, 'error');
    }
}

// Optional: Auto-refresh every 5 minutes
// setInterval(refreshData, 300000);