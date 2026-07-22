// Chart.js initialization for Dashboard

function initDoughnutChart(canvasId, clinicalCount, autopsyCount) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Clinical', 'Autopsy'],
            datasets: [{
                data: [clinicalCount, autopsyCount],
                backgroundColor: [
                    '#818cf8', // Purple-blue for Clinical
                    '#fb7185'  // Pink-red for Autopsy
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            family: 'Inter',
                            size: 13
                        },
                        color: '#6b7280'
                    }
                },
                tooltip: {
                    backgroundColor: '#1f2937',
                    titleFont: { family: 'Inter' },
                    bodyFont: { family: 'Inter' },
                    cornerRadius: 6,
                    padding: 10
                }
            }
        }
    });
}

function initTrendChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // We'll mock the trend data with a single block for "May" (or current month) 
    // to match the specific look of the user's screenshot.
    const currentMonthStr = new Date().toLocaleString('default', { month: 'short' });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [currentMonthStr],
            datasets: [{
                label: 'Monthly Trend',
                data: [10], // Mock value to create a large block
                backgroundColor: 'rgba(129, 140, 248, 0.7)', // Match the purple-blue from doughnut
                borderRadius: 4,
                borderWidth: 1,
                borderColor: 'rgba(129, 140, 248, 1)',
                barPercentage: 1.0,
                categoryPercentage: 1.0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12, family: 'Inter' },
                        stepSize: 1
                    },
                    grid: {
                        color: '#f3f4f6',
                        drawBorder: false
                    }
                },
                x: {
                    ticks: {
                        color: '#6b7280',
                        font: { size: 13, family: 'Inter', weight: 500 }
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        }
    });
}
