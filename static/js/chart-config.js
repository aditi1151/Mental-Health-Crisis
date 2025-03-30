/**
 * Chart configuration for mood tracking visualization
 */

// Function to initialize and render mood chart
function initMoodChart(chartId, labels, values, options = {}) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    // Default chart options
    const defaultOptions = {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Mood Score',
          data: values,
          backgroundColor: 'rgba(78, 115, 223, 0.2)',
          borderColor: 'rgba(78, 115, 223, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(78, 115, 223, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(78, 115, 223, 1)',
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: 0,
            max: 10,
            ticks: {
              stepSize: 1
            },
            title: {
              display: true,
              text: 'Mood Score (1-10)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Date'
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            bodyFont: {
              size: 14
            },
            callbacks: {
              title: function(tooltipItems) {
                return tooltipItems[0].label;
              },
              label: function(context) {
                let label = `Mood: ${context.parsed.y}`;
                return label;
              }
            }
          }
        }
      }
    };
    
    // Merge custom options with defaults
    const chartOptions = {
      ...defaultOptions,
      options: { ...defaultOptions.options, ...options }
    };
    
    // Create and return the chart
    return new Chart(ctx, chartOptions);
  }
  
  // Function to update existing chart data
  function updateMoodChart(chart, labels, values) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = values;
    chart.update();
  }
  
  // Function to fetch mood data from API
  function fetchMoodData(days = 30) {
    return fetch(`/mood/data?days=${days}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .catch(error => {
        console.error('Error fetching mood data:', error);
        return { labels: [], values: [] };
      });
  }
  
  // Function to initialize mood range chart
  function initMoodRangeChart(chartId, data) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    const ranges = [
      { min: 1, max: 3, label: 'Low', color: 'rgba(231, 74, 59, 0.2)', border: 'rgba(231, 74, 59, 1)' },
      { min: 4, max: 7, label: 'Moderate', color: 'rgba(246, 194, 62, 0.2)', border: 'rgba(246, 194, 62, 1)' },
      { min: 8, max: 10, label: 'High', color: 'rgba(28, 200, 138, 0.2)', border: 'rgba(28, 200, 138, 1)' }
    ];
    
    // Count occurrences in each range
    const rangeCounts = ranges.map(range => {
      return data.values.filter(value => value >= range.min && value <= range.max).length;
    });
    
    const rangeChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ranges.map(r => r.label),
        datasets: [{
          label: 'Mood Distribution',
          data: rangeCounts,
          backgroundColor: ranges.map(r => r.color),
          borderColor: ranges.map(r => r.border),
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Number of Days'
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return `${context.parsed.y} day(s)`;
              }
            }
          }
        }
      }
    });
    
    return rangeChart;
  }
  