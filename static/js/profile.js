/**
 * WellLog Profile Module JavaScript File
 * Handles user profile related functions
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Initializing profile functionality');
  
  // Initialize profile edit form
  initProfileEditForm();
  
  // Initialize avatar upload
  initAvatarUpload();
  
  // Initialize password change
  initPasswordChange();
  
  // Initialize privacy settings
  initPrivacySettings();
  
  // Initialize account connections
  initAccountConnections();
});

// Initialize profile edit form
function initProfileEditForm() {
  const profileForm = document.getElementById('profile-edit-form');
  if (!profileForm) return;
  
  // Form submission handling
  profileForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Basic validation
    let isValid = true;
    
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const nickname = document.getElementById('nickname');
    
    // Username validation
    if (username && !username.value.trim()) {
      showInputError(username, 'Please enter a username');
      isValid = false;
    }
    
    // Email validation
    if (email && !email.value.trim()) {
      showInputError(email, 'Please enter an email address');
      isValid = false;
    } else if (email && !isValidEmail(email.value)) {
      showInputError(email, 'Please enter a valid email address');
      isValid = false;
    }
    
    if (!isValid) {
      return;
    }
    
    // Show submission status
    const submitBtn = document.querySelector('#profile-edit-form button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
    
    // Use FormData to collect form data
    const formData = new FormData(profileForm);
    
    // Send AJAX request
    fetch(profileForm.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network request failed');
      }
      return response.json();
    })
    .then(data => {
      // Restore button state
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      if (data.success) {
        // Show success message
        showAlert('Profile updated successfully', 'success');
        
        // Update displayed user information
        const profileName = document.querySelector('.profile-name');
        if (profileName && nickname) {
          profileName.textContent = nickname.value;
        }
      } else {
        // Show error message
        showAlert(data.error || 'Update failed, please try again later', 'danger');
        
        // Handle field errors
        if (data.errors) {
          for (const field in data.errors) {
            const inputElement = document.getElementById(field);
            if (inputElement) {
              showInputError(inputElement, data.errors[field]);
            }
          }
        }
      }
    })
    .catch(error => {
      console.error('Update profile failed:', error);
      
      // Restore button state
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      // Show error message
      showAlert('Update failed, please check network connection and try again', 'danger');
    });
  });
}

// Initialize avatar upload
function initAvatarUpload() {
  const avatarUpload = document.getElementById('avatar-upload');
  const avatarPreview = document.getElementById('avatar-preview');
  const avatarInput = document.getElementById('avatar-input');
  
  if (!avatarUpload || !avatarPreview || !avatarInput) return;
  
  // Click avatar preview to trigger file selection
  avatarPreview.addEventListener('click', function() {
    avatarInput.click();
  });
  
  // File selection change handling
  avatarInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
      const file = this.files[0];
      
      // Verify file type
      if (!file.type.match('image.*')) {
        showAlert('Please select an image file', 'warning');
        return;
      }
      
      // Verify file size (max 2MB)
      if (file.size > 2 * 1024 * 1024) {
        showAlert('Image size cannot exceed 2MB', 'warning');
        return;
      }
      
      // Create preview
      const reader = new FileReader();
      reader.onload = function(e) {
        avatarPreview.src = e.target.result;
        // Show upload button
        document.getElementById('avatar-upload-btn').style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  });
  
  // Upload button click handling
  const uploadBtn = document.getElementById('avatar-upload-btn');
  if (uploadBtn) {
    uploadBtn.addEventListener('click', function() {
      if (!avatarInput.files || !avatarInput.files[0]) {
        return;
      }
      
      // Show upload status
      this.disabled = true;
      const originalText = this.textContent;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
      
      // Create FormData object
      const formData = new FormData();
      formData.append('avatar', avatarInput.files[0]);
      
      // Send AJAX request
      fetch('/api/user/upload-avatar/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network request failed');
        }
        return response.json();
      })
      .then(data => {
        // Restore button state
        this.disabled = false;
        this.textContent = originalText;
        
        if (data.success) {
          // Show success message
          showAlert('Avatar updated successfully', 'success');
          
          // Hide upload button
          this.style.display = 'none';
          
          // Update all displayed user avatar places
          document.querySelectorAll('.user-avatar').forEach(avatar => {
            // Add timestamp to prevent caching
            avatar.src = data.avatar_url + '?t=' + new Date().getTime();
          });
        } else {
          // Show error message
          showAlert(data.error || 'Upload failed, please try again later', 'danger');
        }
      })
      .catch(error => {
        console.error('Upload avatar failed:', error);
        
        // Restore button state
        this.disabled = false;
        this.textContent = originalText;
        
        // Show error message
        showAlert('Upload failed, please check network connection and try again', 'danger');
      });
    });
  }
}

// Initialize password change
function initPasswordChange() {
  const passwordForm = document.getElementById('password-change-form');
  if (!passwordForm) return;
  
  // Password strength check
  const newPasswordInput = document.getElementById('new_password');
  if (newPasswordInput) {
    newPasswordInput.addEventListener('input', function() {
      checkPasswordStrength(this.value);
    });
  }
  
  // Confirm password match check
  const confirmPasswordInput = document.getElementById('confirm_password');
  if (confirmPasswordInput) {
    confirmPasswordInput.addEventListener('input', function() {
      checkPasswordMatch(
        document.getElementById('new_password').value,
        this.value
      );
    });
  }
  
  // Form submission handling
  passwordForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('current_password');
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    
    let isValid = true;
    
    // Current password validation
    if (!currentPassword.value) {
      showInputError(currentPassword, 'Please enter current password');
      isValid = false;
    }
    
    // New password validation
    if (!newPassword.value) {
      showInputError(newPassword, 'Please enter new password');
      isValid = false;
    } else if (newPassword.value.length < 8) {
      showInputError(newPassword, 'Password length must be at least 8 characters');
      isValid = false;
    }
    
    // Confirm password validation
    if (!confirmPassword.value) {
      showInputError(confirmPassword, 'Please confirm new password');
      isValid = false;
    } else if (newPassword.value !== confirmPassword.value) {
      showInputError(confirmPassword, 'Two passwords do not match');
      isValid = false;
    }
    
    if (!isValid) {
      return;
    }
    
    // Show submission status
    const submitBtn = document.querySelector('#password-change-form button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
    
    // Prepare form data
    const formData = new FormData(passwordForm);
    
    // Send AJAX request
    fetch(passwordForm.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network request failed');
      }
      return response.json();
    })
    .then(data => {
      // Restore button state
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      if (data.success) {
        // Show success message
        showAlert('Password updated successfully', 'success');
        
        // Clear form
        passwordForm.reset();
        
        // Hide modal (if in modal)
        const modal = passwordForm.closest('.modal');
        if (modal && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
          const modalInstance = bootstrap.Modal.getInstance(modal);
          if (modalInstance) {
            modalInstance.hide();
          }
        }
      } else {
        // Show error message
        if (data.error === 'current_password') {
          showInputError(currentPassword, 'Current password is incorrect');
        } else {
          showAlert(data.error || 'Update failed, please try again later', 'danger');
        }
      }
    })
    .catch(error => {
      console.error('Update password failed:', error);
      
      // Restore button state
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      // Show error message
      showAlert('Update failed, please check network connection and try again', 'danger');
    });
  });
}

// Initialize privacy settings
function initPrivacySettings() {
  const privacyForm = document.getElementById('privacy-settings-form');
  if (!privacyForm) return;
  
  // Form submission handling
  privacyForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Show submission status
    const submitBtn = document.querySelector('#privacy-settings-form button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
    
    // Collect setting status
    const formData = new FormData(privacyForm);
    
    // Send AJAX request
    fetch(privacyForm.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network request failed');
      }
      return response.json();
    })
    .then(data => {
      // Restore button state
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      if (data.success) {
        // Show success message
        showAlert('Privacy settings saved', 'success');
      } else {
        // Show error message
        showAlert(data.error || 'Save failed, please try again later', 'danger');
      }
    })
    .catch(error => {
      console.error('Save privacy settings failed:', error);
      
      // Restore button state
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      // Show error message
      showAlert('Save failed, please check network connection and try again', 'danger');
    });
  });
}

// Initialize account connections
function initAccountConnections() {
  const connectButtons = document.querySelectorAll('.connect-account-btn');
  const disconnectButtons = document.querySelectorAll('.disconnect-account-btn');
  
  // Connect social media account
  connectButtons.forEach(button => {
    button.addEventListener('click', function() {
      const provider = this.getAttribute('data-provider');
      
      // Show loading status
      this.disabled = true;
      const originalText = this.textContent;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Connecting...';
      
      // Restore button state after 5 seconds (if page is not redirected)
      setTimeout(() => {
        if (document.body.contains(this)) {
          this.disabled = false;
          this.innerHTML = originalText;
        }
      }, 5000);
    });
  });
  
  // Disconnect social media account connection
  disconnectButtons.forEach(button => {
    button.addEventListener('click', function() {
      if (!confirm('Are you sure you want to disconnect this account?')) {
        return;
      }
      
      const provider = this.getAttribute('data-provider');
      
      // Show loading status
      this.disabled = true;
      const originalText = this.textContent;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Disconnecting...';
      
      // Send AJAX request
      fetch(`/api/user/disconnect-account/${provider}/`, {
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
        if (data.success) {
          // Show success message
          showAlert(`Successfully disconnected ${provider} account`, 'success');
          
          // Update UI
          const connectionItem = this.closest('.connection-item');
          if (connectionItem) {
            // Change "Connected" to "Disconnected"
            const statusBadge = connectionItem.querySelector('.connection-status');
            if (statusBadge) {
              statusBadge.textContent = 'Disconnected';
              statusBadge.classList.remove('bg-success');
              statusBadge.classList.add('bg-secondary');
            }
            
            // Hide disconnect button, show connect button
            this.style.display = 'none';
            const connectBtn = connectionItem.querySelector('.connect-account-btn');
            if (connectBtn) {
              connectBtn.style.display = 'inline-block';
            }
          }
        } else {
          // Show error message
          showAlert(data.error || 'Disconnect failed, please try again later', 'danger');
          
          // Restore button state
          this.disabled = false;
          this.textContent = originalText;
        }
      })
      .catch(error => {
        console.error('Disconnect account failed:', error);
        
        // Restore button state
        this.disabled = false;
        this.textContent = originalText;
        
        // Show error message
        showAlert('Disconnect failed, please try again later', 'danger');
      });
    });
  });
}

// Check password strength
function checkPasswordStrength(password) {
  const passwordInput = document.getElementById('new_password');
  const strengthMeter = document.getElementById('password-strength-meter');
  if (!passwordInput || !strengthMeter) return;
  
  // If password is empty
  if (!password) {
    strengthMeter.style.width = '0%';
    strengthMeter.className = 'progress-bar';
    return;
  }
  
  // Calculate password strength
  let strength = 0;
  
  // Length check
  if (password.length >= 8) strength += 25;
  
  // Include uppercase letters
  if (/[A-Z]/.test(password)) strength += 25;
  
  // Include lowercase letters
  if (/[a-z]/.test(password)) strength += 25;
  
  // Include numbers
  if (/[0-9]/.test(password)) strength += 15;
  
  // Include special characters
  if (/[^A-Za-z0-9]/.test(password)) strength += 10;
  
  // Set strength indicator
  strengthMeter.style.width = `${Math.min(100, strength)}%`;
  
  // Set color and text
  const strengthText = document.getElementById('password-strength-text');
  
  if (strength < 30) {
    strengthMeter.className = 'progress-bar bg-danger';
    if (strengthText) strengthText.textContent = 'Weak';
  } else if (strength < 60) {
    strengthMeter.className = 'progress-bar bg-warning';
    if (strengthText) strengthText.textContent = 'Medium';
  } else {
    strengthMeter.className = 'progress-bar bg-success';
    if (strengthText) strengthText.textContent = 'Strong';
  }
}

// Check if two passwords match
function checkPasswordMatch(password, confirmPassword) {
  const confirmInput = document.getElementById('confirm_password');
  const matchText = document.getElementById('password-match-text');
  if (!confirmInput || !matchText) return;
  
  if (!confirmPassword) {
    matchText.textContent = '';
    matchText.className = '';
    return;
  }
  
  if (password === confirmPassword) {
    matchText.textContent = 'Passwords match';
    matchText.className = 'text-success';
  } else {
    matchText.textContent = 'Passwords do not match';
    matchText.className = 'text-danger';
  }
}

// Show input error
function showInputError(inputElement, message) {
  inputElement.classList.add('is-invalid');
  
  let feedbackElement = inputElement.nextElementSibling;
  if (!feedbackElement || !feedbackElement.classList.contains('invalid-feedback')) {
    feedbackElement = document.createElement('div');
    feedbackElement.className = 'invalid-feedback';
    inputElement.insertAdjacentElement('afterend', feedbackElement);
  }
  
  feedbackElement.textContent = message;
}

// Clear input error
function clearInputError(inputElement) {
  inputElement.classList.remove('is-invalid');
  
  const feedbackElement = inputElement.nextElementSibling;
  if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
    feedbackElement.textContent = '';
  }
}

// Show message prompt
function showAlert(message, type = 'info', duration = 3000) {
  // Create alert element
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  // Add to page
  const alertContainer = document.getElementById('alert-container');
  if (alertContainer) {
    alertContainer.appendChild(alertDiv);
  } else {
    // If container does not exist, create one
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    container.appendChild(alertDiv);
    document.body.appendChild(container);
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
  
  return alertDiv;
}

// Verify email format
function isValidEmail(email) {
  const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email.toLowerCase());
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