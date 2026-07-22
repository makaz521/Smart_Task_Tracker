// Wait for the document to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Task Completion Stats Chart
    const completionCtx = document.getElementById('completionChart').getContext('2d');
    const completionChart = new Chart(completionCtx, {
        type: 'pie', // Use pie chart for task completion
        data: {
            labels: ['Completed', 'Pending', 'In Progress'],
            datasets: [{
                label: 'Task Completion Stats',
                data: [30, 50, 20], // Replace with dynamic data
                backgroundColor: ['#4caf50', '#f44336', '#ff9800'],
                borderColor: ['#388e3c', '#c62828', '#f57c00'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            return tooltipItem.label + ': ' + tooltipItem.raw + '%';
                        }
                    }
                }
            }
        }
    });

    // Team Performance Chart
    const performanceCtx = document.getElementById('performanceChart').getContext('2d');
    const performanceChart = new Chart(performanceCtx, {
        type: 'bar', // Use bar chart for performance
        data: {
            labels: ['Team Member 1', 'Team Member 2', 'Team Member 3'],
            datasets: [{
                label: 'Performance by Team Member',
                data: [85, 75, 92], // Replace with dynamic data
                backgroundColor: '#3f51b5',
                borderColor: '#283593',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                x: {
                    ticks: {
                        autoSkip: false
                    }
                }
            }
        }
    });

    // Overdue Tasks Summary Chart
    const overdueCtx = document.getElementById('overdueChart').getContext('2d');
    const overdueChart = new Chart(overdueCtx, {
        type: 'line', // Use line chart for overdue tasks
        data: {
            labels: ['January', 'February', 'March', 'April'], // Replace with dynamic months
            datasets: [{
                label: 'Overdue Tasks',
                data: [5, 8, 3, 12], // Replace with dynamic data
                fill: false,
                borderColor: '#f44336',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });

    // Custom Date-Based Filtering Chart
    const customCtx = document.getElementById('customChart').getContext('2d');
    const customChart = new Chart(customCtx, {
        type: 'bar', // Use bar chart for custom date filter
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3'], // Replace with dynamic data
            datasets: [{
                label: 'Tasks Completed in Custom Range',
                data: [10, 20, 15], // Replace with dynamic data
                backgroundColor: '#8e24aa',
                borderColor: '#6a1b9a',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                x: {
                    ticks: {
                        autoSkip: false
                    }
                }
            }
        }
    });

    // Add event listener for filtering custom date range
    document.getElementById('startDate').addEventListener('change', function () {
        fetchCustomData();
    });

    document.getElementById('endDate').addEventListener('change', function () {
        fetchCustomData();
    });
});

// Function to fetch data for custom date range (placeholder for now)
function fetchCustomData() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    console.log('Fetching data from:', startDate, 'to', endDate);
    // You can implement an AJAX call here to get data from the server
}
