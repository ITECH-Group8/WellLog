/**
 * WellLog Main JavaScript File
 * Contains functionality shared across the entire website
 */

// Execute after document is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('WellLog application initialization');
  
  // Initialize navigation bar
  initNavbar();
  
  // Initialize notification system
  initNotifications();
  
  // Initialize theme toggle
  initThemeToggle();
  
  // Initialize back to top button
  initBackToTop();
  
  // Initialize tooltips
  initTooltips();
});

// Initialize navigation bar
function initNavbar() {
  // Mobile navigation menu toggle
  const navbarToggler = document.querySelector('.navbar-toggler');
  if (navbarToggler) {
    navbarToggler.addEventListener('click', function() {
      const target = document.querySelector(this.getAttribute('data-target'));
      if (target) {
        target.classList.toggle('show');
      }
    });
  }
  
  // Active navigation item highlight
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-nav .nav-item .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && currentPath.indexOf(href) === 0) {
      link.classList.add('active');
      // If in sidebar, ensure parent element is also highlighted
      const parentItem = link.closest('.nav-item');
      if (parentItem) {
        parentItem.classList.add('active');
      }
    }
  });
  
  // Dropdown menu toggle
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
  
  // Click outside to close dropdown menu
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

// Initialize notification system
function initNotifications() {
  // Load notification count
  loadNotificationCount();
  
  // Polling notification updates (every 60 seconds)
  setInterval(loadNotificationCount, 60000);
  
  // Notification icon click event
  const notificationIcon = document.getElementById('notification-icon');
  if (notificationIcon) {
    notificationIcon.addEventListener('click', function(e) {
      e.preventDefault();
      toggleNotificationPanel();
    });
  }
  
  // Close notification button
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('notification-close')) {
      const notificationId = e.target.getAttribute('data-id');
      if (notificationId) {
        markNotificationAsRead(notificationId);
      }
    }
  });
}

// Load notification count
function loadNotificationCount() {
  const notificationBadge = document.getElementById('notification-badge');
  if (!notificationBadge) return;
  
  // AJAX request to get unread notification count
  fetch('/api/notifications/unread-count/')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network request failed');
      }
      return response.json();
    })
    .then(data => {
      // Update notification count
      if (data.count > 0) {
        notificationBadge.textContent = data.count > 99 ? '99+' : data.count;
        notificationBadge.style.display = 'block';
      } else {
        notificationBadge.style.display = 'none';
      }
    })
    .catch(error => {
      console.error('Failed to get notification count:', error);
    });
}

// Toggle notification panel
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

// Load notification list
function loadNotifications() {
  const notificationList = document.getElementById('notification-list');
  if (!notificationList) return;
  
  // Show loading status
  notificationList.innerHTML = '<div class="text-center p-3"><div class="spinner-border spinner-border-sm text-primary" role="status"></div><span class="ms-2">Loading...</span></div>';
  
  // AJAX request to get recent notifications
  fetch('/api/notifications/recent/')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network request failed');
      }
      return response.json();
    })
    .then(data => {
      // Clear list
      notificationList.innerHTML = '';
      
      if (data.notifications && data.notifications.length > 0) {
        // Add notification item
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
        
        // Add "View All" link
        const viewAllLink = document.createElement('div');
        viewAllLink.className = 'text-center p-2';
        viewAllLink.innerHTML = '<a href="/notifications/" class="btn btn-link">View All Notifications</a>';
        notificationList.appendChild(viewAllLink);
      } else {
        // No notifications state
        notificationList.innerHTML = '<div class="text-center p-3 text-muted">No notifications</div>';
      }
    })
    .catch(error => {
      console.error('Failed to get notifications:', error);
      notificationList.innerHTML = '<div class="text-center p-3 text-danger">Load failed, please try again</div>';
    });
}

// Mark notification as read
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
        throw new Error('Network request failed');
      }
      return response.json();
    })
    .then(data => {
      // Update notification UI
      const notification = document.querySelector(`.notification-item[data-id="${notificationId}"]`);
      if (notification) {
        notification.classList.remove('unread');
        notification.classList.add('read');
      }
      
      // Update notification count
      loadNotificationCount();
    })
    .catch(error => {
      console.error('Failed to mark notification as read:', error);
    });
}

// Initialize theme toggle
function initThemeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  if (!themeToggle) return;
  
  // Get current theme
  const currentTheme = localStorage.getItem('theme') || 'light';
  
  // Set initial theme
  document.documentElement.setAttribute('data-bs-theme', currentTheme);
  
  // Update toggle button icon
  updateThemeIcon(currentTheme);
  
  // Toggle button click event
  themeToggle.addEventListener('click', function() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Update theme
    document.documentElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update icon
    updateThemeIcon(newTheme);
  });
}

// Update theme icon
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

// Initialize back to top button
function initBackToTop() {
  const backToTopBtn = document.getElementById('back-to-top');
  if (!backToTopBtn) return;
  
  // Scroll event listener
  window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
      backToTopBtn.classList.add('show');
    } else {
      backToTopBtn.classList.remove('show');
    }
  });
  
  // Click event
  backToTopBtn.addEventListener('click', function() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
}

// Initialize tooltips
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

// Get CSRF Cookie
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

// Show message prompt
function showAlert(message, type = 'info', duration = 3000) {
  // Create warning element
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show custom-alert`;
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  // Add to page
  const alertContainer = document.getElementById('alert-container');
  if (alertContainer) {
    alertContainer.appendChild(alertDiv);
  } else {
    // If container doesn't exist, create one
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    container.appendChild(alertDiv);
    document.body.appendChild(container);
  }
  
  // Create Bootstrap warning object
  if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
    const bsAlert = new bootstrap.Alert(alertDiv);
    
    // Set auto disappear
    if (duration > 0) {
      setTimeout(() => {
        bsAlert.close();
      }, duration);
    }
  } else {
    // If Bootstrap is not available, manually implement close
    const closeButton = alertDiv.querySelector('.btn-close');
    if (closeButton) {
      closeButton.addEventListener('click', function() {
        alertDiv.classList.remove('show');
        setTimeout(() => {
          alertDiv.remove();
        }, 150);
      });
    }
    
    // Set auto disappear
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