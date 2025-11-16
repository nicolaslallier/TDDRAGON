/**
 * Chart initialization functions for log viewer.
 */

/**
 * Initialize HTTP status code histogram chart.
 *
 * @param {string} canvasId - ID of the canvas element.
 * @param {Object} histogramData - Object mapping status codes to counts.
 */
function initializeHttpCodeHistogram(canvasId, histogramData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return;
    }

    // Prepare data
    const labels = Object.keys(histogramData).sort((a, b) => parseInt(a) - parseInt(b));
    const data = labels.map(code => histogramData[code]);

    // Color coding by status code range
    const backgroundColors = labels.map(code => {
        const status = parseInt(code);
        if (status >= 200 && status < 300) return 'rgba(46, 204, 113, 0.8)'; // Green
        if (status >= 300 && status < 400) return 'rgba(52, 152, 219, 0.8)'; // Blue
        if (status >= 400 && status < 500) return 'rgba(243, 156, 18, 0.8)'; // Orange
        if (status >= 500) return 'rgba(231, 76, 60, 0.8)'; // Red
        return 'rgba(149, 165, 166, 0.8)'; // Gray
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Request Count',
                data: data,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(c => c.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'HTTP Status Code Distribution'
                }
            }
        }
    });
}

/**
 * Initialize uptime timeline chart.
 *
 * @param {string} canvasId - ID of the canvas element.
 * @param {Array} timelineData - Array of objects with timestamp and status.
 */
function initializeUptimeTimelineChart(canvasId, timelineData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return;
    }

    // Prepare data
    const labels = timelineData.map(record => {
        // Handle both ISO string and Date object formats
        const timestamp = record.timestamp;
        const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
        return date.toLocaleString();
    });

    // Convert status to numeric values for charting (UP=1, DOWN=0)
    const data = timelineData.map(record => record.status === 'UP' ? 1 : 0);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Status',
                data: data,
                borderColor: 'rgba(52, 152, 219, 1)',
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return value === 1 ? 'UP' : 'DOWN';
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Uptime Timeline'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            const record = timelineData[index];
                            return `Status: ${record.status}${record.details ? ' - ' + record.details : ''}`;
                        }
                    }
                }
            }
        }
    });
}

