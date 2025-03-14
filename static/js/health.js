// Mobile sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.querySelector('.menu-toggle');
  if (menuToggle) {
    menuToggle.addEventListener('click', function() {
      document.body.classList.toggle('sidebar-expanded');
    });
  }
  
  // Initialize tooltips if Bootstrap is available
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }

  // Fix navigation link issues - remove Bootstrap tabs attributes to make links work normally
  const navLinks = document.querySelectorAll('.nav-tabs .nav-link');
  navLinks.forEach(link => {
    // If the link points to other pages (not tab content), remove tab related attributes
    if (link.getAttribute('href') && (link.getAttribute('href').includes('/') || link.getAttribute('href').startsWith('http'))) {
      link.removeAttribute('data-bs-toggle');
      link.removeAttribute('role');
      link.removeAttribute('aria-controls');
      link.removeAttribute('aria-selected');
    }
  });
  
  // For in-page tab functionality (not links navigating to other pages), keep tab event handling
  const tabLinks = document.querySelectorAll('.nav-tabs .nav-link[data-target]');
  tabLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Only process tabs with data-target attribute (in-page tabs, not navigation links)
      if (!link.classList.contains('active') && link.getAttribute('data-target')) {
        e.preventDefault();
        
        // Remove active class from all tabs
        tabLinks.forEach(tab => tab.classList.remove('active'));
        
        // Add active class to clicked tab
        link.classList.add('active');
        
        // Show corresponding content
        const targetId = link.getAttribute('data-target');
        if (targetId) {
          document.querySelectorAll('.tab-content .tab-pane').forEach(pane => {
            pane.classList.remove('show', 'active');
          });
          document.querySelector(targetId).classList.add('show', 'active');
        }
      }
    });
  });

  // Initialize dashboard if on dashboard page
  if (document.getElementById('health-dashboard')) {
    initDashboard();
  }

  // Health card animations
  animateHealthCards();
  
  // Initialize charts (if they exist)
  initCharts();
  
  // Initialize interactions
  initInteractions();
});

// Dashboard Initialization and Data Loading
function initDashboard() {
  console.log('Initializing health dashboard');
  
  // Load latest health data
  loadLatestHealthData();
  
  // Initialize health trend charts
  initHealthTrendCharts();
  
  // Set up dashboard refresh button
  const refreshBtn = document.getElementById('refresh-dashboard');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', function() {
      loadLatestHealthData(true);
    });
  }
  
  // Set up date range selector
  const dateRangeSelector = document.getElementById('date-range-selector');
  if (dateRangeSelector) {
    dateRangeSelector.addEventListener('change', function() {
      updateDashboardDateRange(this.value);
    });
  }
}

// Load latest health data
function loadLatestHealthData(showLoader = false) {
  console.log('Loading latest health data');
  
  if (showLoader) {
    document.querySelectorAll('.health-card .card-body').forEach(card => {
      card.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Loading data...</p></div>';
    });
  }
  
  // Here should be the code to get data from API
  // For demonstration purposes, use setTimeout to simulate API request delay
  setTimeout(() => {
    // Simulated data - in actual project this should be replaced with real API calls
    const healthData = {
      steps: {
        today: 8765,
        yesterday: 7654,
        trend: 14.5,
        goal: 10000
      },
      sleep: {
        today: 7.2,
        yesterday: 6.5,
        trend: 10.8,
        goal: 8
      },
      diet: {
        today: 1850,
        yesterday: 2100,
        trend: -11.9,
        goal: 2000
      },
      running: {
        today: 5.2,
        yesterday: 4.0,
        trend: 30.0,
        goal: 5.0
      },
      mood: {
        today: 4,
        yesterday: 3,
        trend: 33.3,
        goal: 5
      }
    };
    
    // Update dashboard cards
    updateDashboardCards(healthData);
    
  }, 1000);
}

// Update dashboard cards
function updateDashboardCards(data) {
  console.log('Updating dashboard cards', data);
  
  // Update steps card
  updateHealthCard('steps', data.steps);
  
  // Update sleep card
  updateHealthCard('sleep', data.sleep);
  
  // Update diet card
  updateHealthCard('diet', data.diet);
  
  // Update running card
  updateHealthCard('running', data.running);
  
  // Update mood card
  updateHealthCard('mood', data.mood);
}

// Update single health card
function updateHealthCard(type, data) {
  const card = document.getElementById(`${type}-card`);
  if (!card) return;
  
  const valueElement = card.querySelector('.display-4');
  const descElement = card.querySelector('.text-muted');
  const progressElement = card.querySelector('.progress-bar');
  
  // Add animation effect for updates
  if (valueElement) {
    // Save current value
    const oldValue = parseFloat(valueElement.textContent) || 0;
    const newValue = parseFloat(data.today) || 0;
    
    // Create animation effect
    const duration = 1000; // 1 second
    const startTime = performance.now();
    
    // Set unit according to type
    let unit = '';
    switch(type) {
      case 'steps':
        unit = '';
        break;
      case 'sleep':
        unit = 'h';
        break;
      case 'diet':
        unit = '';
        break;
      case 'running':
        unit = 'km';
        break;
    }
    
    // Number increment/decrement animation
    function updateValue(timestamp) {
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Use easing function to make the animation more natural
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      
      const currentValue = oldValue + (newValue - oldValue) * easeProgress;
      valueElement.textContent = `${currentValue.toFixed(1)}${unit}`;
      
      if (progress < 1) {
        requestAnimationFrame(updateValue);
      } else {
        valueElement.textContent = `${newValue}${unit}`;
      }
    }
    
    requestAnimationFrame(updateValue);
  }
  
  if (descElement && data.description) {
    descElement.textContent = data.description;
    descElement.classList.add('animate__animated', 'animate__fadeIn');
    
    // Reset animation
    setTimeout(() => {
      descElement.classList.remove('animate__animated', 'animate__fadeIn');
    }, 1000);
  }
  
  if (progressElement) {
    let percentage = 0;
    
    switch(type) {
      case 'steps':
      case 'diet':
      case 'running':
        percentage = Math.min(100, (data.today / data.goal) * 100);
        break;
      case 'sleep':
        percentage = Math.min(100, (data.today / data.goal) * 100);
        break;
      case 'mood':
        percentage = (data.today / data.goal) * 100;
        break;
    }
    
    // Add animation effect to progress bar
    const oldWidth = parseFloat(progressElement.style.width) || 0;
    const newWidth = percentage;
    
    const duration = 1000; // 1 second
    const startTime = performance.now();
    
    function updateProgress(timestamp) {
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Use easing function
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      
      const currentWidth = oldWidth + (newWidth - oldWidth) * easeProgress;
      progressElement.style.width = `${currentWidth}%`;
      progressElement.setAttribute('aria-valuenow', currentWidth);
      
      if (progress < 1) {
        requestAnimationFrame(updateProgress);
      } else {
        progressElement.style.width = `${newWidth}%`;
        progressElement.setAttribute('aria-valuenow', newWidth);
      }
    }
    
    requestAnimationFrame(updateProgress);
  }
}

// Initialize health trend charts
function initHealthTrendCharts() {
  console.log('Initializing health trend charts');
  
  // Simulated data retrieval
  setTimeout(() => {
    // Simulated data for past 7 days
    const dates = [];
    const stepsData = [];
    const sleepData = [];
    
    // Generate dates and random data for past 7 days
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      dates.push(date.toLocaleDateString('zh-CN', {month: 'short', day: 'numeric'}));
      
      stepsData.push(Math.floor(Math.random() * 5000) + 5000); // 5000-10000 steps
      sleepData.push((Math.random() * 3) + 5); // 5-8 hours sleep
    }
    
    // Render steps trend chart
    renderTrendChart('steps-trend-chart', {
      labels: dates,
      values: stepsData
    }, {
      yAxisLabel: 'steps',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      borderColor: 'rgba(75, 192, 192, 1)'
    });
    
    // Render sleep trend chart
    renderTrendChart('sleep-trend-chart', {
      labels: dates,
      values: sleepData
    }, {
      yAxisLabel: 'hours',
      backgroundColor: 'rgba(153, 102, 255, 0.2)',
      borderColor: 'rgba(153, 102, 255, 1)'
    });
    
  }, 1500);
}

// Render trend chart
function renderTrendChart(chartId, data, options) {
  const ctx = document.getElementById(chartId);
  if (!ctx) return;
  
  const chartConfig = {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        label: options.yAxisLabel,
        data: data.values,
        backgroundColor: options.backgroundColor,
        borderColor: options.borderColor,
        borderWidth: 2,
        tension: 0.2,
        fill: true,
        cubicInterpolationMode: 'monotone',
        borderJoinStyle: 'round',
        stepped: false,
        pointRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            drawBorder: false,
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            font: {
              size: 10
            }
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: {
              size: 10
            }
          }
        }
      },
      elements: {
        line: {
          tension: 0.2,
          borderJoinStyle: 'round',
          capBezierPoints: true
        },
        point: {
          radius: 3,
          hoverRadius: 5
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  };

  // Create chart instance and store in window object for future updates
  if (window[chartId]) {
    window[chartId].destroy();
  }
  
  window[chartId] = new Chart(ctx, chartConfig);
}

// Update dashboard date range
function updateDashboardDateRange(range) {
  console.log('Updating dashboard date range to:', range);
  
  document.querySelectorAll('.health-card .card-body').forEach(card => {
    card.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Updating data...</p></div>';
  });
  
  // Simulated API call
  setTimeout(() => {
    // Update data based on selected range
    loadLatestHealthData();
    
    // Update chart data
    updateChartsForDateRange(range);
  }, 1000);
}

// Update charts based on date range
function updateChartsForDateRange(range) {
  console.log('Updating charts for date range:', range);
  
  // Generate date labels
  const labels = [];
  const daysCount = range === 'week' ? 7 : range === 'month' ? 30 : 90;
  
  for (let i = daysCount - 1; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    
    if (range === 'week') {
      labels.push(date.toLocaleDateString('en-US', {weekday: 'short'}));
    } else {
      labels.push(date.toLocaleDateString('en-US', {month: 'short', day: 'numeric'}));
    }
  }
  
  // Generate random data
  const stepsData = Array.from({length: daysCount}, () => Math.floor(Math.random() * 5000) + 5000);
  const sleepData = Array.from({length: daysCount}, () => (Math.random() * 3) + 5);
  
  // Update charts
  if (window['steps-trend-chart']) {
    window['steps-trend-chart'].data.labels = labels;
    window['steps-trend-chart'].data.datasets[0].data = stepsData;
    window['steps-trend-chart'].update();
  }
  
  if (window['sleep-trend-chart']) {
    window['sleep-trend-chart'].data.labels = labels;
    window['sleep-trend-chart'].data.datasets[0].data = sleepData;
    window['sleep-trend-chart'].update();
  }
}

// Training history filter functionality
function applyTrainingFilters() {
  const exerciseType = document.getElementById('filter-exercise-type').value;
  const dateFrom = document.getElementById('filter-date-from').value;
  const dateTo = document.getElementById('filter-date-to').value;
  const sortBy = document.getElementById('filter-sort-by').value;
  
  const rows = document.querySelectorAll('#training-records-table tbody tr');
  
  rows.forEach(row => {
    let visible = true;
    
    // Apply exercise type filter
    if (exerciseType && exerciseType !== 'all') {
      const rowExerciseType = row.getAttribute('data-exercise-type');
      if (rowExerciseType !== exerciseType) {
        visible = false;
      }
    }
    
    // Apply date range filter
    if (dateFrom || dateTo) {
      const rowDate = new Date(row.getAttribute('data-date'));
      
      if (dateFrom) {
        const fromDate = new Date(dateFrom);
        if (rowDate < fromDate) {
          visible = false;
        }
      }
      
      if (dateTo) {
        const toDate = new Date(dateTo);
        toDate.setHours(23, 59, 59, 999); // End of day
        if (rowDate > toDate) {
          visible = false;
        }
      }
    }
    
    // Show or hide row
    row.style.display = visible ? '' : 'none';
  });
  
  // Show empty state if no visible rows
  const visibleRows = document.querySelectorAll('#training-records-table tbody tr[style=""]').length;
  const emptyState = document.getElementById('empty-state');
  if (emptyState) {
    emptyState.style.display = visibleRows === 0 ? 'block' : 'none';
  }
}

// Chart rendering for record history
function renderRecordHistoryChart(chartData, recordType) {
  const ctx = document.getElementById('recordHistoryChart');
  if (!ctx) return;
  
  let yAxisLabel = '';
  let backgroundColor = 'rgba(13, 110, 253, 0.2)';
  let borderColor = 'rgba(13, 110, 253, 1)';
  
  // Set label and colors based on record type
  switch(recordType) {
    case 'steps':
      yAxisLabel = 'Steps';
      backgroundColor = 'rgba(75, 192, 192, 0.2)';
      borderColor = 'rgba(75, 192, 192, 1)';
      break;
    case 'sleep':
      yAxisLabel = 'Hours';
      backgroundColor = 'rgba(153, 102, 255, 0.2)';
      borderColor = 'rgba(153, 102, 255, 1)';
      break;
    case 'diet':
      yAxisLabel = 'Calories';
      backgroundColor = 'rgba(255, 159, 64, 0.2)';
      borderColor = 'rgba(255, 159, 64, 1)';
      break;
    case 'running':
      yAxisLabel = 'Distance (km)';
      backgroundColor = 'rgba(255, 99, 132, 0.2)';
      borderColor = 'rgba(255, 99, 132, 1)';
      break;
    case 'mood':
      yAxisLabel = 'Mood Level';
      backgroundColor = 'rgba(255, 205, 86, 0.2)';
      borderColor = 'rgba(255, 205, 86, 1)';
      break;
    case 'training':
      yAxisLabel = 'Intensity';
      backgroundColor = 'rgba(54, 162, 235, 0.2)';
      borderColor = 'rgba(54, 162, 235, 1)';
      break;
  }
  
  // Create chart configuration
  const chartConfig = {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [{
        label: recordType.charAt(0).toUpperCase() + recordType.slice(1),
        data: chartData.values,
        backgroundColor: backgroundColor,
        borderColor: borderColor,
        borderWidth: 2,
        tension: 0.2,
        fill: true,
        cubicInterpolationMode: 'monotone',
        borderJoinStyle: 'round',
        stepped: false,
        pointRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: yAxisLabel
          }
        },
        x: {
          title: {
            display: true,
            text: 'Date'
          }
        }
      },
      elements: {
        line: {
          tension: 0.2,
          borderJoinStyle: 'round',
          capBezierPoints: true
        },
        point: {
          radius: 3,
          hoverRadius: 5
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  };
  
  // Create chart
  if (window.recordChart instanceof Chart) {
    window.recordChart.destroy();
  }
  
  window.recordChart = new Chart(ctx, chartConfig);
  console.log('Chart rendered for ' + recordType);
  
  // Handle window resize
  window.addEventListener('resize', function() {
    if (window.recordChart) {
      window.recordChart.resize();
    }
  });
}

// Health card animations function
function animateHealthCards() {
  const cards = document.querySelectorAll('.health-card');
  
  // Use IntersectionObserver to monitor card visibility
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Add animation class
        entry.target.classList.add('animate__animated', 'animate__fadeInUp');
        // Card is visible, no longer monitor
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1  // Trigger when card is 10% visible
  });
  
  // Add fade-in animation to each card and set delay
  cards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.animationDelay = `${index * 0.1}s`;
    observer.observe(card);
  });
}

// Initialize charts function
function initCharts() {
  // Running chart
  if (document.getElementById('runningChart')) {
    const ctx = document.getElementById('runningChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        datasets: [{
          label: 'Distance (km)',
          data: [5, 3, 0, 7, 2, 8, 4],
          borderColor: '#0d6efd',
          backgroundColor: 'rgba(13, 110, 253, 0.1)',
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        animation: {
          duration: 2000,
          easing: 'easeOutQuart'
        },
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'This Week Running Distance'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
  
  // Steps chart
  if (document.getElementById('stepsChart')) {
    const ctx = document.getElementById('stepsChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        datasets: [{
          label: 'Steps',
          data: [8000, 6500, 9000, 7500, 5000, 10000, 7800],
          backgroundColor: 'rgba(40, 167, 69, 0.7)',
          borderColor: 'rgba(40, 167, 69, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        animation: {
          duration: 2000,
          easing: 'easeOutQuart'
        },
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'This Week Steps Statistics'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
  
  // Sleep chart
  if (document.getElementById('sleepChart')) {
    const ctx = document.getElementById('sleepChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        datasets: [{
          label: 'Sleep Duration (hours)',
          data: [7.5, 6, 8, 7, 6.5, 9, 8.5],
          borderColor: '#6f42c1',
          backgroundColor: 'rgba(111, 66, 193, 0.1)',
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        animation: {
          duration: 2000,
          easing: 'easeOutQuart'
        },
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'This Week Sleep Statistics'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 12
          }
        }
      }
    });
  }
}

// Initialize interactions function
function initInteractions() {
  // Add click effect to health cards
  const healthCards = document.querySelectorAll('.health-card');
  healthCards.forEach(card => {
    card.addEventListener('click', function() {
      // Add click animation
      this.classList.add('card-clicked');
      
      // Remove animation class (allow multiple clicks)
      setTimeout(() => {
        this.classList.remove('card-clicked');
      }, 300);
    });
  });
  
  // Add ripple effect to buttons
  const buttons = document.querySelectorAll('.btn');
  buttons.forEach(button => {
    button.addEventListener('mousedown', function(e) {
      const x = e.clientX - this.getBoundingClientRect().left;
      const y = e.clientY - this.getBoundingClientRect().top;
      
      const ripple = document.createElement('span');
      ripple.classList.add('ripple-effect');
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      
      this.appendChild(ripple);
      
      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  });
  
  // Implement health data card carousel (for mobile devices)
  if (window.innerWidth < 768) {
    const cardsContainer = document.querySelector('.row');
    if (cardsContainer) {
      let startX, endX;
      
      cardsContainer.addEventListener('touchstart', function(event) {
        startX = event.touches[0].clientX;
      });
      
      cardsContainer.addEventListener('touchend', function(event) {
        endX = event.changedTouches[0].clientX;
        handleSwipe();
      });
      
      function handleSwipe() {
        const threshold = 50;
        const cards = cardsContainer.querySelectorAll('.col-md-4');
        const cardWidth = cards[0].offsetWidth + 16; // Include spacing
        
        if (startX - endX > threshold) {
          // Left swipe
          cardsContainer.scrollBy({
            left: cardWidth,
            behavior: 'smooth'
          });
        } else if (endX - startX > threshold) {
          // Right swipe
          cardsContainer.scrollBy({
            left: -cardWidth,
            behavior: 'smooth'
          });
        }
      }
    }
  }
  
  // Implement tab smooth transition
  const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
  tabButtons.forEach(button => {
    button.addEventListener('shown.bs.tab', function() {
      // Animation triggered when switching tabs
      const targetId = this.getAttribute('data-bs-target');
      const targetPane = document.querySelector(targetId);
      
      if (targetPane) {
        const cards = targetPane.querySelectorAll('.health-card');
        cards.forEach((card, index) => {
          card.style.opacity = "0";
          card.classList.add('animate__animated', 'animate__fadeInUp');
          card.style.animationDelay = `${index * 0.1}s`;
          
          // Reset animation
          void card.offsetWidth;
          card.style.opacity = "1";
        });
      }
    });
  });
}