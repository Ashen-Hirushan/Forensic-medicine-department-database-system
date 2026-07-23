// Chart.js initialization for Dashboard — uses real backend data

function initDoughnutChart(canvasId, clinicalCount, autopsyCount) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // If both are 0, show a placeholder
    if (clinicalCount === 0 && autopsyCount === 0) {
        clinicalCount = 1;
        autopsyCount = 1;
    }

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
                hoverOffset: 8
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
                        font: { family: 'Inter', size: 13 },
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

function initTrendChart(canvasId, labels, clinicalData, autopsyData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Clinical',
                    data: clinicalData,
                    backgroundColor: 'rgba(129, 140, 248, 0.7)',
                    borderColor: 'rgba(129, 140, 248, 1)',
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.6,
                    categoryPercentage: 0.7
                },
                {
                    label: 'Autopsy',
                    data: autopsyData,
                    backgroundColor: 'rgba(251, 113, 133, 0.7)',
                    borderColor: 'rgba(251, 113, 133, 1)',
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.6,
                    categoryPercentage: 0.7
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 12, family: 'Inter' },
                        stepSize: 1,
                        precision: 0
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
                    position: 'top',
                    align: 'end',
                    labels: {
                        usePointStyle: true,
                        padding: 16,
                        font: { family: 'Inter', size: 12 },
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

function initCategoryChart(canvasId, labels, values) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (!labels || labels.length === 0) {
        ctx.parentElement.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#9ca3af;font-style:italic;">No category data available</div>';
        return;
    }

    const palette = ['#818cf8', '#fb7185', '#34d399', '#fbbf24', '#60a5fa', '#a78bfa'];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: palette.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 12,
                        font: { family: 'Inter', size: 11 },
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
