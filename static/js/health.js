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

  // Initialize tab functionality
  const tabLinks = document.querySelectorAll('.nav-tabs .nav-link');
  tabLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      if (!link.classList.contains('active') && !link.getAttribute('href').startsWith('http')) {
        e.preventDefault();
        
        // Remove active class from all tabs
        tabLinks.forEach(tab => tab.classList.remove('active'));
        
        // Add active class to clicked tab
        link.classList.add('active');
        
        // Show corresponding content (if using data attributes)
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

  // 健康卡片动画
  animateHealthCards();
  
  // 初始化图表（如果存在）
  initCharts();
  
  // 初始化交互动作
  initInteractions();
});

// Dashboard Initialization and Data Loading
function initDashboard() {
  console.log('初始化健康仪表板');
  
  // 加载最新的健康数据
  loadLatestHealthData();
  
  // 初始化健康趋势图表
  initHealthTrendCharts();
  
  // 设置仪表板刷新按钮
  const refreshBtn = document.getElementById('refresh-dashboard');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', function() {
      loadLatestHealthData(true);
    });
  }
  
  // 设置日期范围选择器
  const dateRangeSelector = document.getElementById('date-range-selector');
  if (dateRangeSelector) {
    dateRangeSelector.addEventListener('change', function() {
      updateDashboardDateRange(this.value);
    });
  }
}

// 加载最新的健康数据
function loadLatestHealthData(showLoader = false) {
  console.log('加载最新健康数据');
  
  if (showLoader) {
    document.querySelectorAll('.health-card .card-body').forEach(card => {
      card.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">加载中...</span></div><p class="mt-2">加载数据中...</p></div>';
    });
  }
  
  // 这里应该是从API获取数据的代码
  // 为演示目的，使用setTimeout模拟API请求延迟
  setTimeout(() => {
    // 模拟数据 - 实际项目中应该替换为真实的API调用
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
    
    // 更新仪表板卡片
    updateDashboardCards(healthData);
    
  }, 1000);
}

// 更新仪表板卡片
function updateDashboardCards(data) {
  console.log('更新仪表板卡片', data);
  
  // 更新步数卡片
  updateHealthCard('steps', data.steps);
  
  // 更新睡眠卡片
  updateHealthCard('sleep', data.sleep);
  
  // 更新饮食卡片
  updateHealthCard('diet', data.diet);
  
  // 更新跑步卡片
  updateHealthCard('running', data.running);
  
  // 更新心情卡片
  updateHealthCard('mood', data.mood);
}

// 更新单个健康卡片
function updateHealthCard(type, data) {
  const card = document.getElementById(`${type}-card`);
  if (!card) return;
  
  const valueElement = card.querySelector('.display-4');
  const descElement = card.querySelector('.text-muted');
  const progressElement = card.querySelector('.progress-bar');
  
  // 为更新添加动画效果
  if (valueElement) {
    // 保存当前值
    const oldValue = parseFloat(valueElement.textContent) || 0;
    const newValue = parseFloat(data.today) || 0;
    
    // 创建动画效果
    const duration = 1000; // 1秒
    const startTime = performance.now();
    
    // 根据类型设置单位
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
    
    // 数字递增/递减动画
    function updateValue(timestamp) {
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // 使用缓动函数使动画更自然
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
    
    // 重置动画
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
    
    // 为进度条添加动画效果
    const oldWidth = parseFloat(progressElement.style.width) || 0;
    const newWidth = percentage;
    
    const duration = 1000; // 1秒
    const startTime = performance.now();
    
    function updateProgress(timestamp) {
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // 使用缓动函数
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

// 初始化健康趋势图表
function initHealthTrendCharts() {
  console.log('初始化健康趋势图表');
  
  // 模拟获取历史数据
  setTimeout(() => {
    // 模拟过去7天的数据
    const dates = [];
    const stepsData = [];
    const sleepData = [];
    
    // 生成过去7天的日期和随机数据
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      dates.push(date.toLocaleDateString('zh-CN', {month: 'short', day: 'numeric'}));
      
      stepsData.push(Math.floor(Math.random() * 5000) + 5000); // 5000-10000步
      sleepData.push((Math.random() * 3) + 5); // 5-8小时睡眠
    }
    
    // 渲染步数趋势图
    renderTrendChart('steps-trend-chart', {
      labels: dates,
      values: stepsData
    }, {
      yAxisLabel: '步数',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      borderColor: 'rgba(75, 192, 192, 1)'
    });
    
    // 渲染睡眠趋势图
    renderTrendChart('sleep-trend-chart', {
      labels: dates,
      values: sleepData
    }, {
      yAxisLabel: '小时',
      backgroundColor: 'rgba(153, 102, 255, 0.2)',
      borderColor: 'rgba(153, 102, 255, 1)'
    });
    
  }, 1500);
}

// 渲染趋势图表
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
        tension: 0.3,
        fill: true
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
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  };

  // 创建图表实例并存储在window对象上，以便后续更新
  if (window[chartId]) {
    window[chartId].destroy();
  }
  
  window[chartId] = new Chart(ctx, chartConfig);
}

// 更新仪表板日期范围
function updateDashboardDateRange(range) {
  console.log('更新仪表板日期范围为:', range);
  
  document.querySelectorAll('.health-card .card-body').forEach(card => {
    card.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">加载中...</span></div><p class="mt-2">正在更新数据...</p></div>';
  });
  
  // 模拟API调用
  setTimeout(() => {
    // 根据所选范围更新数据
    loadLatestHealthData();
    
    // 更新图表数据
    updateChartsForDateRange(range);
  }, 1000);
}

// 根据日期范围更新图表
function updateChartsForDateRange(range) {
  console.log('为日期范围更新图表:', range);
  
  // 生成日期标签
  const labels = [];
  const daysCount = range === 'week' ? 7 : range === 'month' ? 30 : 90;
  
  for (let i = daysCount - 1; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    
    if (range === 'week') {
      labels.push(date.toLocaleDateString('zh-CN', {weekday: 'short'}));
    } else {
      labels.push(date.toLocaleDateString('zh-CN', {month: 'short', day: 'numeric'}));
    }
  }
  
  // 生成随机数据
  const stepsData = Array.from({length: daysCount}, () => Math.floor(Math.random() * 5000) + 5000);
  const sleepData = Array.from({length: daysCount}, () => (Math.random() * 3) + 5);
  
  // 更新图表
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
        tension: 0.1,
        fill: true
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

// 健康卡片动画函数
function animateHealthCards() {
  const cards = document.querySelectorAll('.health-card');
  
  // 使用IntersectionObserver监测卡片进入视口
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // 添加动画类
        entry.target.classList.add('animate__animated', 'animate__fadeInUp');
        // 卡片已显示，不再监测
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1  // 当卡片10%进入视口时触发
  });
  
  // 为每个卡片添加淡入动画，并设置延迟
  cards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.animationDelay = `${index * 0.1}s`;
    observer.observe(card);
  });
}

// 初始化图表函数
function initCharts() {
  // 运动图表
  if (document.getElementById('runningChart')) {
    const ctx = document.getElementById('runningChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        datasets: [{
          label: '距离 (km)',
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
            text: '本周跑步距离'
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
  
  // 步数图表
  if (document.getElementById('stepsChart')) {
    const ctx = document.getElementById('stepsChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        datasets: [{
          label: '步数',
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
            text: '本周步数统计'
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
  
  // 睡眠图表
  if (document.getElementById('sleepChart')) {
    const ctx = document.getElementById('sleepChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        datasets: [{
          label: '睡眠时长 (小时)',
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
            text: '本周睡眠统计'
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

// 初始化交互函数
function initInteractions() {
  // 为健康卡片添加点击效果
  const healthCards = document.querySelectorAll('.health-card');
  healthCards.forEach(card => {
    card.addEventListener('click', function() {
      // 添加点击动画
      this.classList.add('card-clicked');
      
      // 移除动画类（允许再次点击）
      setTimeout(() => {
        this.classList.remove('card-clicked');
      }, 300);
    });
  });
  
  // 为按钮添加波纹效果
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
  
  // 实现健康数据卡片轮播（对于移动设备）
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
        const cardWidth = cards[0].offsetWidth + 16; // 包含间距
        
        if (startX - endX > threshold) {
          // 向左滑动
          cardsContainer.scrollBy({
            left: cardWidth,
            behavior: 'smooth'
          });
        } else if (endX - startX > threshold) {
          // 向右滑动
          cardsContainer.scrollBy({
            left: -cardWidth,
            behavior: 'smooth'
          });
        }
      }
    }
  }
  
  // 实现标签页平滑过渡
  const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
  tabButtons.forEach(button => {
    button.addEventListener('shown.bs.tab', function() {
      // 切换标签时触发动画
      const targetId = this.getAttribute('data-bs-target');
      const targetPane = document.querySelector(targetId);
      
      if (targetPane) {
        const cards = targetPane.querySelectorAll('.health-card');
        cards.forEach((card, index) => {
          card.style.opacity = "0";
          card.classList.add('animate__animated', 'animate__fadeInUp');
          card.style.animationDelay = `${index * 0.1}s`;
          
          // 重置动画
          void card.offsetWidth;
          card.style.opacity = "1";
        });
      }
    });
  });
}