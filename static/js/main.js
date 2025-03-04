/**
 * WellLog 主JavaScript文件
 * 包含整个网站共享的功能
 */

// 文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
  console.log('WellLog应用初始化');
  
  // 初始化导航栏
  initNavbar();
  
  // 初始化通知系统
  initNotifications();
  
  // 初始化主题切换
  initThemeToggle();
  
  // 初始化返回顶部按钮
  initBackToTop();
  
  // 初始化工具提示
  initTooltips();
});

// 初始化导航栏
function initNavbar() {
  // 移动端导航菜单切换
  const navbarToggler = document.querySelector('.navbar-toggler');
  if (navbarToggler) {
    navbarToggler.addEventListener('click', function() {
      const target = document.querySelector(this.getAttribute('data-target'));
      if (target) {
        target.classList.toggle('show');
      }
    });
  }
  
  // 活动导航项高亮
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-nav .nav-item .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && currentPath.indexOf(href) === 0) {
      link.classList.add('active');
      // 如果在侧边栏内，确保父元素也高亮
      const parentItem = link.closest('.nav-item');
      if (parentItem) {
        parentItem.classList.add('active');
      }
    }
  });
  
  // 下拉菜单切换
  document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      const parent = this.parentElement;
      if (parent) {
        parent.classList.toggle('show');
        this.setAttribute('aria-expanded', parent.classList.contains('show'));
        const dropdown = parent.querySelector('.dropdown-menu');
        if (dropdown) {
          dropdown.classList.toggle('show');
        }
      }
    });
  });
  
  // 点击外部关闭下拉菜单
  document.addEventListener('click', function(e) {
    if (!e.target.matches('.dropdown-toggle')) {
      document.querySelectorAll('.dropdown.show').forEach(dropdown => {
        dropdown.classList.remove('show');
        const toggle = dropdown.querySelector('.dropdown-toggle');
        if (toggle) {
          toggle.setAttribute('aria-expanded', 'false');
        }
        const menu = dropdown.querySelector('.dropdown-menu');
        if (menu) {
          menu.classList.remove('show');
        }
      });
    }
  });
}

// 初始化通知系统
function initNotifications() {
  // 加载通知数量
  loadNotificationCount();
  
  // 轮询通知更新（每60秒）
  setInterval(loadNotificationCount, 60000);
  
  // 通知图标点击事件
  const notificationIcon = document.getElementById('notification-icon');
  if (notificationIcon) {
    notificationIcon.addEventListener('click', function(e) {
      e.preventDefault();
      toggleNotificationPanel();
    });
  }
  
  // 关闭通知按钮
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('notification-close')) {
      const notificationId = e.target.getAttribute('data-id');
      if (notificationId) {
        markNotificationAsRead(notificationId);
      }
    }
  });
}

// 加载通知数量
function loadNotificationCount() {
  const notificationBadge = document.getElementById('notification-badge');
  if (!notificationBadge) return;
  
  // AJAX请求获取未读通知数量
  fetch('/api/notifications/unread-count/')
    .then(response => {
      if (!response.ok) {
        throw new Error('网络请求失败');
      }
      return response.json();
    })
    .then(data => {
      // 更新通知数量
      if (data.count > 0) {
        notificationBadge.textContent = data.count > 99 ? '99+' : data.count;
        notificationBadge.style.display = 'block';
      } else {
        notificationBadge.style.display = 'none';
      }
    })
    .catch(error => {
      console.error('获取通知数量失败:', error);
    });
}

// 切换通知面板
function toggleNotificationPanel() {
  const panel = document.getElementById('notification-panel');
  if (!panel) return;
  
  if (panel.classList.contains('show')) {
    panel.classList.remove('show');
  } else {
    panel.classList.add('show');
    loadNotifications();
  }
}

// 加载通知列表
function loadNotifications() {
  const notificationList = document.getElementById('notification-list');
  if (!notificationList) return;
  
  // 显示加载中状态
  notificationList.innerHTML = '<div class="text-center p-3"><div class="spinner-border spinner-border-sm text-primary" role="status"></div><span class="ms-2">加载中...</span></div>';
  
  // AJAX请求获取最近通知
  fetch('/api/notifications/recent/')
    .then(response => {
      if (!response.ok) {
        throw new Error('网络请求失败');
      }
      return response.json();
    })
    .then(data => {
      // 清空列表
      notificationList.innerHTML = '';
      
      if (data.notifications && data.notifications.length > 0) {
        // 添加通知项
        data.notifications.forEach(notification => {
          const notificationItem = document.createElement('div');
          notificationItem.className = `notification-item p-3 border-bottom ${notification.read ? 'read' : 'unread'}`;
          notificationItem.innerHTML = `
            <div class="d-flex justify-content-between">
              <div>
                <strong>${notification.title}</strong>
                <p class="mb-1">${notification.message}</p>
                <small class="text-muted">${notification.created_at}</small>
              </div>
              <button class="btn btn-sm text-muted notification-close" data-id="${notification.id}">
                <i class="fas fa-times"></i>
              </button>
            </div>
          `;
          notificationList.appendChild(notificationItem);
        });
        
        // 添加"查看全部"链接
        const viewAllLink = document.createElement('div');
        viewAllLink.className = 'text-center p-2';
        viewAllLink.innerHTML = '<a href="/notifications/" class="btn btn-link">查看全部通知</a>';
        notificationList.appendChild(viewAllLink);
      } else {
        // 无通知状态
        notificationList.innerHTML = '<div class="text-center p-3 text-muted">暂无通知</div>';
      }
    })
    .catch(error => {
      console.error('获取通知失败:', error);
      notificationList.innerHTML = '<div class="text-center p-3 text-danger">加载失败，请重试</div>';
    });
}

// 标记通知为已读
function markNotificationAsRead(notificationId) {
  fetch(`/api/notifications/mark-read/${notificationId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json'
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('网络请求失败');
      }
      return response.json();
    })
    .then(data => {
      // 更新通知UI
      const notification = document.querySelector(`.notification-item[data-id="${notificationId}"]`);
      if (notification) {
        notification.classList.remove('unread');
        notification.classList.add('read');
      }
      
      // 更新通知计数
      loadNotificationCount();
    })
    .catch(error => {
      console.error('标记通知已读失败:', error);
    });
}

// 初始化主题切换
function initThemeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  if (!themeToggle) return;
  
  // 获取当前主题
  const currentTheme = localStorage.getItem('theme') || 'light';
  
  // 设置初始主题
  document.documentElement.setAttribute('data-bs-theme', currentTheme);
  
  // 更新切换按钮图标
  updateThemeIcon(currentTheme);
  
  // 切换按钮点击事件
  themeToggle.addEventListener('click', function() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // 更新主题
    document.documentElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // 更新图标
    updateThemeIcon(newTheme);
  });
}

// 更新主题图标
function updateThemeIcon(theme) {
  const themeIcon = document.getElementById('theme-icon');
  if (!themeIcon) return;
  
  if (theme === 'dark') {
    themeIcon.classList.remove('fa-moon');
    themeIcon.classList.add('fa-sun');
  } else {
    themeIcon.classList.remove('fa-sun');
    themeIcon.classList.add('fa-moon');
  }
}

// 初始化返回顶部按钮
function initBackToTop() {
  const backToTopBtn = document.getElementById('back-to-top');
  if (!backToTopBtn) return;
  
  // 滚动事件监听
  window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
      backToTopBtn.classList.add('show');
    } else {
      backToTopBtn.classList.remove('show');
    }
  });
  
  // 点击事件
  backToTopBtn.addEventListener('click', function() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
}

// 初始化工具提示
function initTooltips() {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  if (tooltipTriggerList.length > 0) {
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
      tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
      });
    }
  }
}

// 获取CSRF Cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// 显示消息提示
function showAlert(message, type = 'info', duration = 3000) {
  // 创建警告元素
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show custom-alert`;
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  // 添加到页面
  const alertContainer = document.getElementById('alert-container');
  if (alertContainer) {
    alertContainer.appendChild(alertDiv);
  } else {
    // 如果容器不存在，创建一个
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    container.appendChild(alertDiv);
    document.body.appendChild(container);
  }
  
  // 创建Bootstrap警告对象
  if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
    const bsAlert = new bootstrap.Alert(alertDiv);
    
    // 设置自动消失
    if (duration > 0) {
      setTimeout(() => {
        bsAlert.close();
      }, duration);
    }
  } else {
    // 如果Bootstrap不可用，手动实现关闭
    const closeButton = alertDiv.querySelector('.btn-close');
    if (closeButton) {
      closeButton.addEventListener('click', function() {
        alertDiv.classList.remove('show');
        setTimeout(() => {
          alertDiv.remove();
        }, 150);
      });
    }
    
    // 设置自动消失
    if (duration > 0) {
      setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => {
          alertDiv.remove();
        }, 150);
      }, duration);
    }
  }
  
  return alertDiv;
}