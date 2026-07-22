document.addEventListener('DOMContentLoaded', () => {
    // Fetch alerts on load and every 30 seconds
    fetchAlerts();
    setInterval(fetchAlerts, 30000);

    // Set active sidebar item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(item => {
        const href = item.getAttribute('href');
        if (href && href !== '/' && currentPath.startsWith(href)) {
            item.classList.add('active');
        }
    });

    // Bell Dropdown Toggle
    const bellContainer = document.getElementById('bell-container');
    const bellDropdown = document.getElementById('bell-dropdown');
    
    if (bellContainer && bellDropdown) {
        bellContainer.addEventListener('click', (e) => {
            // Prevent toggling when clicking inside the dropdown (like clicking a dismiss button)
            if (e.target.closest('.bell-dropdown')) return;
            bellDropdown.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!bellContainer.contains(e.target)) {
                bellDropdown.classList.remove('show');
            }
        });
    }
});

async function fetchAlerts() {
    try {
        const response = await fetch('/alerts');
        if (response.ok) {
            const data = await response.json();
            const count = Array.isArray(data) ? data.length : 0;
            updateBellBadge(count);
            populateAlertDropdown(data);

            // Update dashboard alert count if element exists
            const alertCountEl = document.getElementById('alert-count-display');
            if (alertCountEl) {
                alertCountEl.textContent = count;
            }
        }
    } catch (e) {
        // Silently fail — alerts are non-critical
    }
}

function updateBellBadge(count) {
    const badge = document.getElementById('notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
}

function populateAlertDropdown(alerts) {
    const list = document.getElementById('dropdown-list');
    if (!list) return;

    if (!Array.isArray(alerts) || alerts.length === 0) {
        list.innerHTML = '<div class="dropdown-empty">No active alerts 🎉</div>';
        return;
    }

    list.innerHTML = '';
    alerts.forEach(alert => {
        const item = document.createElement('div');
        item.className = 'dropdown-item';
        item.id = 'alert-item-' + alert.alert_id;
        
        item.innerHTML = `
            <div class="alert-message-text">${alert.message}</div>
            <button onclick="dismissAlert(${alert.alert_id})" class="btn btn-secondary btn-sm" style="padding: 2px 6px; font-size: 10px;">✕</button>
        `;
        list.appendChild(item);
    });
}

async function dismissAlert(alertId) {
    try {
        const formData = new FormData();
        formData.append('alert_id', alertId);
        await fetch('/alerts/dismiss', { method: 'POST', body: formData });
        fetchAlerts();
        const el = document.getElementById('alert-' + alertId);
        if (el) el.remove();
    } catch (e) {
        console.error('Error dismissing alert:', e);
    }
}
