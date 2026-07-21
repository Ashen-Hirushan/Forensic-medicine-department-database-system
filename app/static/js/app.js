document.addEventListener('DOMContentLoaded', () => {
    console.log("Forensic App Initialized");

    // Fetch alerts every 30 seconds
    fetchAlerts();
    setInterval(fetchAlerts, 30000);

    // Sidebar active state logic
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        // Simple prefix matching for active links
        const href = item.getAttribute('href');
        if(href && currentPath.startsWith(href) && href !== '/') {
            item.classList.add('active');
        } else if (currentPath === href) {
            item.classList.add('active');
        }
    });
});

async function fetchAlerts() {
    try {
        const response = await fetch('/alerts');
        if (response.ok) {
            const alerts = await response.json();
            updateBellBadge(alerts.length);
        }
    } catch (e) {
        console.error("Error fetching alerts:", e);
    }
}

function updateBellBadge(count) {
    const badge = document.getElementById('notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }
}

async function dismissAlert(alertId) {
    try {
        const formData = new FormData();
        formData.append('alert_id', alertId);
        
        await fetch('/alerts/dismiss', {
            method: 'POST',
            body: formData
        });
        fetchAlerts(); // refresh count
        
        // Remove element from DOM
        const alertEl = document.getElementById(`alert-${alertId}`);
        if(alertEl) {
            alertEl.style.display = 'none';
        }
    } catch (e) {
        console.error("Error dismissing alert", e);
    }
}
