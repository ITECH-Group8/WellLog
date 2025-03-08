/**
 * WellLog Authentication Module JavaScript File
 * Handles user authentication related functions
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Initializing authentication functionality');
  
  // Initialize login form validation
  initLoginForm();
  
  // Initialize registration form validation
  initRegisterForm();
  
  // Initialize password reset form
  initPasswordResetForm();
  
  // Initialize password confirmation form
  initPasswordConfirmForm();
  
  // Initialize social login buttons
  initSocialLogin();
});

// Initialize login form
function initLoginForm() {
  const loginForm = document.getElementById('login-form');
  if (!loginForm) return;
  
  loginForm.addEventListener('submit', function(e) {
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const errorMsg = document.getElementById('login-error');
    
    let isValid = true;
    
    // Clear previous error messages
    if (errorMsg) errorMsg.textContent = '';
    
    // Username validation
    if (!username.value.trim()) {
      showInputError(username, 'Please enter a username');
      isValid = false;
    } else {
      clearInputError(username);
    }
    
    // Password validation
    if (!password.value) {
      showInputError(password, 'Please enter a password');
      isValid = false;
    } else {
      clearInputError(password);
    }
    
    if (!isValid) {
      e.preventDefault();
    }
  });
}

// Initialize registration form
function initRegisterForm() {
  const registerForm = document.getElementById('register-form');
  if (!registerForm) return;
  
  // Username availability check
  const usernameInput = document.getElementById('username');
  if (usernameInput) {
    usernameInput.addEventListener('blur', function() {
      checkUsernameAvailability(this.value);
    });
  }
  
  // Email availability check
  const emailInput = document.getElementById('email');
  if (emailInput) {
    emailInput.addEventListener('blur', function() {
      checkEmailAvailability(this.value);
    });
  }
  
  // Password strength check
  const passwordInput = document.getElementById('password');
  if (passwordInput) {
    passwordInput.addEventListener('input', function() {
      checkPasswordStrength(this.value);
    });
  }
  
  // Confirm password match check
  const passwordConfirmInput = document.getElementById('password_confirm');
  if (passwordConfirmInput) {
    passwordConfirmInput.addEventListener('input', function() {
      checkPasswordMatch(
        document.getElementById('password').value,
        this.value
      );
    });
  }
  
  // Form submission validation
  registerForm.addEventListener('submit', function(e) {
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const passwordConfirm = document.getElementById('password_confirm');
    
    let isValid = true;
    
    // Username validation
    if (!username.value.trim()) {
      showInputError(username, 'Please enter a username');
      isValid = false;
    } else if (username.value.trim().length < 3) {
      showInputError(username, 'Username length must be at least 3 characters');
      isValid = false;
    } else {
      clearInputError(username);
    }
    
    // Email validation
    if (!email.value.trim()) {
      showInputError(email, 'Please enter an email address');
      isValid = false;
    } else if (!isValidEmail(email.value)) {
      showInputError(email, 'Please enter a valid email address');
      isValid = false;
    } else {
      clearInputError(email);
    }
    
    // Password validation
    if (!password.value) {
      showInputError(password, 'Please enter a password');
      isValid = false;
    } else if (password.value.length < 8) {
      showInputError(password, 'Password length must be at least 8 characters');
      isValid = false;
    } else {
      clearInputError(password);
    }
    
    // Confirm password validation
    if (!passwordConfirm.value) {
      showInputError(passwordConfirm, 'Please confirm password');
      isValid = false;
    } else if (password.value !== passwordConfirm.value) {
      showInputError(passwordConfirm, 'Passwords do not match');
      isValid = false;
    } else {
      clearInputError(passwordConfirm);
    }
    
    if (!isValid) {
      e.preventDefault();
    }
  });
}

// Check username availability
function checkUsernameAvailability(username) {
  const usernameInput = document.getElementById('username');
  if (!usernameInput || !username.trim()) return;
  
  // Show loading status
  const feedbackElement = getFeedbackElement(usernameInput);
  feedbackElement.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Checking...';
  feedbackElement.className = 'text-muted form-text';
  
  // Send AJAX request to check username
  fetch(`/api/auth/check-username/?username=${encodeURIComponent(username)}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network request failed');
      }
      return response.json();
    })
    .then(data => {
      if (data.available) {
        clearInputError(usernameInput);
        feedbackElement.textContent = 'Username available';
        feedbackElement.className = 'text-success form-text';
      } else {
        showInputError(usernameInput, 'Username already taken');
      }
    })
    .catch(error => {
      console.error('Username check failed:', error);
      feedbackElement.textContent = 'Username check failed, please try again';
      feedbackElement.className = 'text-danger form-text';
    });
}

// Check email availability
function checkEmailAvailability(email) {
  const emailInput = document.getElementById('email');
  if (!emailInput || !email.trim() || !isValidEmail(email)) return;
  
  // Show loading status
  const feedbackElement = getFeedbackElement(emailInput);
  feedbackElement.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Checking...';
  feedbackElement.className = 'text-muted form-text';
  
  // Send AJAX request to check email
  fetch(`/api/auth/check-email/?email=${encodeURIComponent(email)}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network request failed');
      }
      return response.json();
    })
    .then(data => {
      if (data.available) {
        clearInputError(emailInput);
        feedbackElement.textContent = 'Email available';
        feedbackElement.className = 'text-success form-text';
      } else {
        showInputError(emailInput, 'Email already registered');
      }
    })
    .catch(error => {
      console.error('Email check failed:', error);
      feedbackElement.textContent = 'Email check failed, please try again';
      feedbackElement.className = 'text-danger form-text';
    });
}

// Check password strength
function checkPasswordStrength(password) {
  const passwordInput = document.getElementById('password');
  const strengthMeter = document.getElementById('password-strength');
  if (!passwordInput || !strengthMeter) return;
  
  // Clear previous errors
  clearInputError(passwordInput);
  
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
  
  // Contains uppercase letter
  if (/[A-Z]/.test(password)) strength += 25;
  
  // Contains lowercase letter
  if (/[a-z]/.test(password)) strength += 25;
  
  // Contains number
  if (/[0-9]/.test(password)) strength += 15;
  
  // Contains special character
  if (/[^A-Za-z0-9]/.test(password)) strength += 10;
  
  // Set strength indicator
  strengthMeter.style.width = `${Math.min(100, strength)}%`;
  
  // Set color
  if (strength < 30) {
    strengthMeter.className = 'progress-bar bg-danger';
    showInputError(passwordInput, 'Weak password');
  } else if (strength < 60) {
    strengthMeter.className = 'progress-bar bg-warning';
    const feedbackElement = getFeedbackElement(passwordInput);
    feedbackElement.textContent = 'Medium password strength';
    feedbackElement.className = 'text-warning form-text';
  } else {
    strengthMeter.className = 'progress-bar bg-success';
    const feedbackElement = getFeedbackElement(passwordInput);
    feedbackElement.textContent = 'Strong password';
    feedbackElement.className = 'text-success form-text';
  }
}

// Check password match
function checkPasswordMatch(password, confirmPassword) {
  const confirmInput = document.getElementById('password_confirm');
  if (!confirmInput) return;
  
  if (!confirmPassword) {
    clearInputError(confirmInput);
    return;
  }
  
  if (password === confirmPassword) {
    clearInputError(confirmInput);
    const feedbackElement = getFeedbackElement(confirmInput);
    feedbackElement.textContent = 'Passwords match';
    feedbackElement.className = 'text-success form-text';
  } else {
    showInputError(confirmInput, 'Passwords do not match');
  }
}

// Initialize password reset form
function initPasswordResetForm() {
  const resetForm = document.getElementById('password-reset-form');
  if (!resetForm) return;
  
  resetForm.addEventListener('submit', function(e) {
    const email = document.getElementById('email');
    
    let isValid = true;
    
    // Email validation
    if (!email.value.trim()) {
      showInputError(email, 'Please enter an email address');
      isValid = false;
    } else if (!isValidEmail(email.value)) {
      showInputError(email, 'Please enter a valid email address');
      isValid = false;
    } else {
      clearInputError(email);
    }
    
    if (!isValid) {
      e.preventDefault();
    }
  });
}

// Initialize password confirmation form
function initPasswordConfirmForm() {
  const confirmForm = document.getElementById('password-confirm-form');
  if (!confirmForm) return;
  
  // Password strength check
  const passwordInput = document.getElementById('new_password');
  if (passwordInput) {
    passwordInput.addEventListener('input', function() {
      checkPasswordStrength(this.value);
    });
  }
  
  // Confirm password match check
  const passwordConfirmInput = document.getElementById('confirm_password');
  if (passwordConfirmInput) {
    passwordConfirmInput.addEventListener('input', function() {
      checkPasswordMatch(
        document.getElementById('new_password').value,
        this.value
      );
    });
  }
  
  confirmForm.addEventListener('submit', function(e) {
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    
    let isValid = true;
    
    // New password validation
    if (!newPassword.value) {
      showInputError(newPassword, 'Please enter a new password');
      isValid = false;
    } else if (newPassword.value.length < 8) {
      showInputError(newPassword, 'Password length must be at least 8 characters');
      isValid = false;
    } else {
      clearInputError(newPassword);
    }
    
    // Confirm password validation
    if (!confirmPassword.value) {
      showInputError(confirmPassword, 'Please confirm password');
      isValid = false;
    } else if (newPassword.value !== confirmPassword.value) {
      showInputError(confirmPassword, 'Passwords do not match');
      isValid = false;
    } else {
      clearInputError(confirmPassword);
    }
    
    if (!isValid) {
      e.preventDefault();
    }
  });
}

// Initialize social login buttons
function initSocialLogin() {
  const socialButtons = document.querySelectorAll('.social-login-btn');
  
  socialButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      const provider = this.getAttribute('data-provider');
      
      // Show button loading status
      this.disabled = true;
      const originalContent = this.innerHTML;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Connecting...';
      
      // In appropriate delay, restore button state (if page not redirected)
      setTimeout(() => {
        if (document.body.contains(this)) {
          this.disabled = false;
          this.innerHTML = originalContent;
        }
      }, 5000);
    });
  });
}

// Show input error
function showInputError(inputElement, message) {
  inputElement.classList.add('is-invalid');
  
  const feedbackElement = getFeedbackElement(inputElement);
  feedbackElement.textContent = message;
  feedbackElement.className = 'invalid-feedback';
}

// Clear input error
function clearInputError(inputElement) {
  inputElement.classList.remove('is-invalid');
  
  const feedbackElement = getFeedbackElement(inputElement);
  feedbackElement.textContent = '';
  feedbackElement.className = '';
}

// Get or create feedback element
function getFeedbackElement(inputElement) {
  let feedbackElement = inputElement.nextElementSibling;
  
  // If next element is not a feedback element, create one
  if (!feedbackElement || !feedbackElement.classList.contains('invalid-feedback') && !feedbackElement.classList.contains('form-text')) {
    feedbackElement = document.createElement('div');
    inputElement.insertAdjacentElement('afterend', feedbackElement);
  }
  
  return feedbackElement;
}

// Validate email format
function isValidEmail(email) {
  const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email.toLowerCase());
} 