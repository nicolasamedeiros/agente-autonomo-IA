// Gráfico de Linha
const ctxLine = document.getElementById('lineChart').getContext('2d');
const lineChart = new Chart(ctxLine, {
    type: 'line',
    data: {
        labels: ['2017', '2018', '2019', '2020', '2021', '2022', '2023'],
        datasets: [{
            label: 'Desmatamento',
            data: [120, 150, 180, 130, 170, 210, 190],
            borderColor: '#00fff7',
            backgroundColor: 'rgba(0,255,247,0.1)',
            pointBackgroundColor: '#ff00c8',
            pointBorderColor: '#fff',
            pointRadius: 6,
            tension: 0.4,
        }]
    },
    options: {
        plugins: {
            legend: {
                labels: {
                    color: '#00fff7',
                    font: { size: 16 }
                }
            }
        },
        scales: {
            x: {
                ticks: { color: '#e0e0f0' },
                grid: { color: '#23234a' }
            },
            y: {
                ticks: { color: '#e0e0f0' },
                grid: { color: '#23234a' }
            }
        }
    }
});

// Gráfico Doughnut
const ctxDoughnut = document.getElementById('doughnutChart').getContext('2d');
const doughnutChart = new Chart(ctxDoughnut, {
    type: 'doughnut',
    data: {
        labels: ['Legal', 'Ilegal'],
        datasets: [{
            data: [65, 35],
            backgroundColor: [
                'rgba(0,255,247,0.8)',
                'rgba(255,0,200,0.8)'
            ],
            borderColor: '#181828',
            borderWidth: 4
        }]
    },
    options: {
        plugins: {
            legend: {
                labels: {
                    color: '#e0e0f0',
                    font: { size: 16 }
                }
            }
        }
    }
}); 