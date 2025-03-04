/**
 * WellLog 认证模块JavaScript文件
 * 处理用户认证相关功能
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('初始化认证功能');
  
  // 初始化登录表单验证
  initLoginForm();
  
  // 初始化注册表单验证
  initRegisterForm();
  
  // 初始化密码重置表单
  initPasswordResetForm();
  
  // 初始化密码确认表单
  initPasswordConfirmForm();
  
  // 初始化社交登录按钮
  initSocialLogin();
});

// 初始化登录表单
function initLoginForm() {
  const loginForm = document.getElementById('login-form');
  if (!loginForm) return;
  
  loginForm.addEventListener('submit', function(e) {
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const errorMsg = document.getElementById('login-error');
    
    let isValid = true;
    
    // 清除之前的错误消息
    if (errorMsg) errorMsg.textContent = '';
    
    // 用户名验证
    if (!username.value.trim()) {
      showInputError(username, '请输入用户名');
      isValid = false;
    } else {
      clearInputError(username);
    }
    
    // 密码验证
    if (!password.value) {
      showInputError(password, '请输入密码');
      isValid = false;
    } else {
      clearInputError(password);
    }
    
    if (!isValid) {
      e.preventDefault();
    }
  });
}

// 初始化注册表单
function initRegisterForm() {
  const registerForm = document.getElementById('register-form');
  if (!registerForm) return;
  
  // 用户名可用性检查
  const usernameInput = document.getElementById('username');
  if (usernameInput) {
    usernameInput.addEventListener('blur', function() {
      checkUsernameAvailability(this.value);
    });
  }
  
  // 邮箱可用性检查
  const emailInput = document.getElementById('email');
  if (emailInput) {
    emailInput.addEventListener('blur', function() {
      checkEmailAvailability(this.value);
    });
  }
  
  // 密码强度检查
  const passwordInput = document.getElementById('password');
  if (passwordInput) {
    passwordInput.addEventListener('input', function() {
      checkPasswordStrength(this.value);
    });
  }
  
  // 确认密码匹配检查
  const passwordConfirmInput = document.getElementById('password_confirm');
  if (passwordConfirmInput) {
    passwordConfirmInput.addEventListener('input', function() {
      checkPasswordMatch(
        document.getElementById('password').value,
        this.value
      );
    });
  }
  
  // 表单提交验证
  registerForm.addEventListener('submit', function(e) {
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const passwordConfirm = document.getElementById('password_confirm');
    
    let isValid = true;
    
    // 用户名验证
    if (!username.value.trim()) {
      showInputError(username, '请输入用户名');
      isValid = false;
    } else if (username.value.trim().length < 3) {
      showInputError(username, '用户名长度至少为3个字符');
      isValid = false;
    } else {
      clearInputError(username);
    }
    
    // 邮箱验证
    if (!email.value.trim()) {
      showInputError(email, '请输入邮箱地址');
      isValid = false;
    } else if (!isValidEmail(email.value)) {
      showInputError(email, '请输入有效的邮箱地址');
      isValid = false;
    } else {
      clearInputError(email);
    }
    
    // 密码验证
    if (!password.value) {
      showInputError(password, '请输入密码');
      isValid = false;
    } else if (password.value.length < 8) {
      showInputError(password, '密码长度至少为8个字符');
      isValid = false;
    } else {
      clearInputError(password);
    }
    
    // 确认密码验证
    if (!passwordConfirm.value) {
      showInputError(passwordConfirm, '请确认密码');
      isValid = false;
    } else if (password.value !== passwordConfirm.value) {
      showInputError(passwordConfirm, '两次输入的密码不一致');
      isValid = false;
    } else {
      clearInputError(passwordConfirm);
    }
    
    if (!isValid) {
      e.preventDefault();
    }
  });
}

// 检查用户名是否可用
function checkUsernameAvailability(username) {
  const usernameInput = document.getElementById('username');
  if (!usernameInput || !username.trim()) return;
  
  // 显示加载状态
  const feedbackElement = getFeedbackElement(usernameInput);
  feedbackElement.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 检查中...';
  feedbackElement.className = 'text-muted form-text';
  
  // 发送AJAX请求检查用户名
  fetch(`/api/auth/check-username/?username=${encodeURIComponent(username)}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('网络请求失败');
      }
      return response.json();
    })
    .then(data => {
      if (data.available) {
        clearInputError(usernameInput);
        feedbackElement.textContent = '用户名可用';
        feedbackElement.className = 'text-success form-text';
      } else {
        showInputError(usernameInput, '该用户名已被使用');
      }
    })
    .catch(error => {
      console.error('用户名检查失败:', error);
      feedbackElement.textContent = '用户名检查失败，请重试';
      feedbackElement.className = 'text-danger form-text';
    });
}

// 检查邮箱是否可用
function checkEmailAvailability(email) {
  const emailInput = document.getElementById('email');
  if (!emailInput || !email.trim() || !isValidEmail(email)) return;
  
  // 显示加载状态
  const feedbackElement = getFeedbackElement(emailInput);
  feedbackElement.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 检查中...';
  feedbackElement.className = 'text-muted form-text';
  
  // 发送AJAX请求检查邮箱
  fetch(`/api/auth/check-email/?email=${encodeURIComponent(email)}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('网络请求失败');
      }
      return response.json();
    })
    .then(data => {
      if (data.available) {
        clearInputError(emailInput);
        feedbackElement.textContent = '邮箱可用';
        feedbackElement.className = 'text-success form-text';
      } else {
        showInputError(emailInput, '该邮箱已被注册');
      }
    })
    .catch(error => {
      console.error('邮箱检查失败:', error);
      feedbackElement.textContent = '邮箱检查失败，请重试';
      feedbackElement.className = 'text-danger form-text';
    });
}

// 检查密码强度
function checkPasswordStrength(password) {
  const passwordInput = document.getElementById('password');
  const strengthMeter = document.getElementById('password-strength');
  if (!passwordInput || !strengthMeter) return;
  
  // 清除之前的错误
  clearInputError(passwordInput);
  
  // 如果密码为空
  if (!password) {
    strengthMeter.style.width = '0%';
    strengthMeter.className = 'progress-bar';
    return;
  }
  
  // 计算密码强度
  let strength = 0;
  
  // 长度检查
  if (password.length >= 8) strength += 25;
  
  // 包含大写字母
  if (/[A-Z]/.test(password)) strength += 25;
  
  // 包含小写字母
  if (/[a-z]/.test(password)) strength += 25;
  
  // 包含数字
  if (/[0-9]/.test(password)) strength += 15;
  
  // 包含特殊字符
  if (/[^A-Za-z0-9]/.test(password)) strength += 10;
  
  // 设置强度指示器
  strengthMeter.style.width = `${Math.min(100, strength)}%`;
  
  // 设置颜色
  if (strength < 30) {
    strengthMeter.className = 'progress-bar bg-danger';
    showInputError(passwordInput, '密码强度弱');
  } else if (strength < 60) {
    strengthMeter.className = 'progress-bar bg-warning';
    const feedbackElement = getFeedbackElement(passwordInput);
    feedbackElement.textContent = '密码强度中等';
    feedbackElement.className = 'text-warning form-text';
  } else {
    strengthMeter.className = 'progress-bar bg-success';
    const feedbackElement = getFeedbackElement(passwordInput);
    feedbackElement.textContent = '密码强度强';
    feedbackElement.className = 'text-success form-text';
  }
}

// 检查两次密码是否匹配
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
    feedbackElement.textContent = '密码匹配';
    feedbackElement.className = 'text-success form-text';
  } else {
    showInputError(confirmInput, '两次输入的密码不一致');
  }
}

// 初始化密码重置表单
function initPasswordResetForm() {
  const resetForm = document.getElementById('password-reset-form');
  if (!resetForm) return;
  
  resetForm.addEventListener('submit', function(e) {
    const email = document.getElementById('email');
    
    let isValid = true;
    
    // 邮箱验证
    if (!email.value.trim()) {
      showInputError(email, '请输入邮箱地址');
      isValid = false;
    } else if (!isValidEmail(email.value)) {
      showInputError(email, '请输入有效的邮箱地址');
      isValid = false;
    } else {
      clearInputError(email);
    }
    
    if (!isValid) {
      e.preventDefault();
    }
  });
}

// 初始化密码确认表单
function initPasswordConfirmForm() {
  const confirmForm = document.getElementById('password-confirm-form');
  if (!confirmForm) return;
  
  // 密码强度检查
  const passwordInput = document.getElementById('new_password');
  if (passwordInput) {
    passwordInput.addEventListener('input', function() {
      checkPasswordStrength(this.value);
    });
  }
  
  // 确认密码匹配检查
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
    
    // 新密码验证
    if (!newPassword.value) {
      showInputError(newPassword, '请输入新密码');
      isValid = false;
    } else if (newPassword.value.length < 8) {
      showInputError(newPassword, '密码长度至少为8个字符');
      isValid = false;
    } else {
      clearInputError(newPassword);
    }
    
    // 确认密码验证
    if (!confirmPassword.value) {
      showInputError(confirmPassword, '请确认密码');
      isValid = false;
    } else if (newPassword.value !== confirmPassword.value) {
      showInputError(confirmPassword, '两次输入的密码不一致');
      isValid = false;
    } else {
      clearInputError(confirmPassword);
    }
    
    if (!isValid) {
      e.preventDefault();
    }
  });
}

// 初始化社交登录按钮
function initSocialLogin() {
  const socialButtons = document.querySelectorAll('.social-login-btn');
  
  socialButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      const provider = this.getAttribute('data-provider');
      
      // 显示按钮加载状态
      this.disabled = true;
      const originalContent = this.innerHTML;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 连接中...';
      
      // 在适当的延迟后恢复按钮状态（如果页面未被重定向）
      setTimeout(() => {
        if (document.body.contains(this)) {
          this.disabled = false;
          this.innerHTML = originalContent;
        }
      }, 5000);
    });
  });
}

// 显示输入错误
function showInputError(inputElement, message) {
  inputElement.classList.add('is-invalid');
  
  const feedbackElement = getFeedbackElement(inputElement);
  feedbackElement.textContent = message;
  feedbackElement.className = 'invalid-feedback';
}

// 清除输入错误
function clearInputError(inputElement) {
  inputElement.classList.remove('is-invalid');
  
  const feedbackElement = getFeedbackElement(inputElement);
  feedbackElement.textContent = '';
  feedbackElement.className = '';
}

// 获取或创建反馈元素
function getFeedbackElement(inputElement) {
  let feedbackElement = inputElement.nextElementSibling;
  
  // 如果下一个元素不是反馈元素，创建一个
  if (!feedbackElement || !feedbackElement.classList.contains('invalid-feedback') && !feedbackElement.classList.contains('form-text')) {
    feedbackElement = document.createElement('div');
    inputElement.insertAdjacentElement('afterend', feedbackElement);
  }
  
  return feedbackElement;
}

// 验证邮箱格式
function isValidEmail(email) {
  const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email.toLowerCase());
} 