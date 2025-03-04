/**
 * WellLog 个人资料模块JavaScript文件
 * 处理用户个人资料相关功能
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('初始化个人资料功能');
  
  // 初始化资料编辑表单
  initProfileEditForm();
  
  // 初始化头像上传
  initAvatarUpload();
  
  // 初始化密码修改
  initPasswordChange();
  
  // 初始化隐私设置
  initPrivacySettings();
  
  // 初始化账号关联
  initAccountConnections();
});

// 初始化个人资料编辑表单
function initProfileEditForm() {
  const profileForm = document.getElementById('profile-edit-form');
  if (!profileForm) return;
  
  // 表单提交处理
  profileForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // 基本验证
    let isValid = true;
    
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const nickname = document.getElementById('nickname');
    
    // 用户名验证
    if (username && !username.value.trim()) {
      showInputError(username, '请输入用户名');
      isValid = false;
    }
    
    // 邮箱验证
    if (email && !email.value.trim()) {
      showInputError(email, '请输入邮箱地址');
      isValid = false;
    } else if (email && !isValidEmail(email.value)) {
      showInputError(email, '请输入有效的邮箱地址');
      isValid = false;
    }
    
    if (!isValid) {
      return;
    }
    
    // 显示提交中状态
    const submitBtn = document.querySelector('#profile-edit-form button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 保存中...';
    
    // 使用FormData收集表单数据
    const formData = new FormData(profileForm);
    
    // 发送AJAX请求
    fetch(profileForm.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('网络请求失败');
      }
      return response.json();
    })
    .then(data => {
      // 恢复按钮状态
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      if (data.success) {
        // 显示成功消息
        showAlert('个人资料已成功更新', 'success');
        
        // 更新页面上显示的用户信息
        const profileName = document.querySelector('.profile-name');
        if (profileName && nickname) {
          profileName.textContent = nickname.value;
        }
      } else {
        // 显示错误信息
        showAlert(data.error || '更新失败，请稍后重试', 'danger');
        
        // 处理字段错误
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
      console.error('更新个人资料失败:', error);
      
      // 恢复按钮状态
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      // 显示错误消息
      showAlert('更新失败，请检查网络连接后重试', 'danger');
    });
  });
}

// 初始化头像上传
function initAvatarUpload() {
  const avatarUpload = document.getElementById('avatar-upload');
  const avatarPreview = document.getElementById('avatar-preview');
  const avatarInput = document.getElementById('avatar-input');
  
  if (!avatarUpload || !avatarPreview || !avatarInput) return;
  
  // 点击头像预览触发文件选择
  avatarPreview.addEventListener('click', function() {
    avatarInput.click();
  });
  
  // 文件选择变化处理
  avatarInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
      const file = this.files[0];
      
      // 验证文件类型
      if (!file.type.match('image.*')) {
        showAlert('请选择图片文件', 'warning');
        return;
      }
      
      // 验证文件大小 (最大2MB)
      if (file.size > 2 * 1024 * 1024) {
        showAlert('图片大小不能超过2MB', 'warning');
        return;
      }
      
      // 创建预览
      const reader = new FileReader();
      reader.onload = function(e) {
        avatarPreview.src = e.target.result;
        // 显示上传按钮
        document.getElementById('avatar-upload-btn').style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  });
  
  // 上传按钮点击处理
  const uploadBtn = document.getElementById('avatar-upload-btn');
  if (uploadBtn) {
    uploadBtn.addEventListener('click', function() {
      if (!avatarInput.files || !avatarInput.files[0]) {
        return;
      }
      
      // 显示上传中状态
      this.disabled = true;
      const originalText = this.textContent;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 上传中...';
      
      // 创建FormData对象
      const formData = new FormData();
      formData.append('avatar', avatarInput.files[0]);
      
      // 发送AJAX请求
      fetch('/api/user/upload-avatar/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('网络请求失败');
        }
        return response.json();
      })
      .then(data => {
        // 恢复按钮状态
        this.disabled = false;
        this.textContent = originalText;
        
        if (data.success) {
          // 显示成功消息
          showAlert('头像已成功更新', 'success');
          
          // 隐藏上传按钮
          this.style.display = 'none';
          
          // 更新所有显示用户头像的地方
          document.querySelectorAll('.user-avatar').forEach(avatar => {
            // 添加时间戳防止缓存
            avatar.src = data.avatar_url + '?t=' + new Date().getTime();
          });
        } else {
          // 显示错误信息
          showAlert(data.error || '上传失败，请稍后重试', 'danger');
        }
      })
      .catch(error => {
        console.error('上传头像失败:', error);
        
        // 恢复按钮状态
        this.disabled = false;
        this.textContent = originalText;
        
        // 显示错误消息
        showAlert('上传失败，请检查网络连接后重试', 'danger');
      });
    });
  }
}

// 初始化密码修改
function initPasswordChange() {
  const passwordForm = document.getElementById('password-change-form');
  if (!passwordForm) return;
  
  // 密码强度检查
  const newPasswordInput = document.getElementById('new_password');
  if (newPasswordInput) {
    newPasswordInput.addEventListener('input', function() {
      checkPasswordStrength(this.value);
    });
  }
  
  // 确认密码匹配检查
  const confirmPasswordInput = document.getElementById('confirm_password');
  if (confirmPasswordInput) {
    confirmPasswordInput.addEventListener('input', function() {
      checkPasswordMatch(
        document.getElementById('new_password').value,
        this.value
      );
    });
  }
  
  // 表单提交处理
  passwordForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('current_password');
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    
    let isValid = true;
    
    // 当前密码验证
    if (!currentPassword.value) {
      showInputError(currentPassword, '请输入当前密码');
      isValid = false;
    }
    
    // 新密码验证
    if (!newPassword.value) {
      showInputError(newPassword, '请输入新密码');
      isValid = false;
    } else if (newPassword.value.length < 8) {
      showInputError(newPassword, '密码长度至少为8个字符');
      isValid = false;
    }
    
    // 确认密码验证
    if (!confirmPassword.value) {
      showInputError(confirmPassword, '请确认新密码');
      isValid = false;
    } else if (newPassword.value !== confirmPassword.value) {
      showInputError(confirmPassword, '两次输入的密码不一致');
      isValid = false;
    }
    
    if (!isValid) {
      return;
    }
    
    // 显示提交中状态
    const submitBtn = document.querySelector('#password-change-form button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 更新中...';
    
    // 准备表单数据
    const formData = new FormData(passwordForm);
    
    // 发送AJAX请求
    fetch(passwordForm.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('网络请求失败');
      }
      return response.json();
    })
    .then(data => {
      // 恢复按钮状态
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      if (data.success) {
        // 显示成功消息
        showAlert('密码已成功更新', 'success');
        
        // 清空表单
        passwordForm.reset();
        
        // 隐藏模态框（如果在模态框中）
        const modal = passwordForm.closest('.modal');
        if (modal && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
          const modalInstance = bootstrap.Modal.getInstance(modal);
          if (modalInstance) {
            modalInstance.hide();
          }
        }
      } else {
        // 显示错误信息
        if (data.error === 'current_password') {
          showInputError(currentPassword, '当前密码不正确');
        } else {
          showAlert(data.error || '更新失败，请稍后重试', 'danger');
        }
      }
    })
    .catch(error => {
      console.error('更新密码失败:', error);
      
      // 恢复按钮状态
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      // 显示错误消息
      showAlert('更新失败，请检查网络连接后重试', 'danger');
    });
  });
}

// 初始化隐私设置
function initPrivacySettings() {
  const privacyForm = document.getElementById('privacy-settings-form');
  if (!privacyForm) return;
  
  // 表单提交处理
  privacyForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // 显示提交中状态
    const submitBtn = document.querySelector('#privacy-settings-form button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 保存中...';
    
    // 收集设置状态
    const formData = new FormData(privacyForm);
    
    // 发送AJAX请求
    fetch(privacyForm.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('网络请求失败');
      }
      return response.json();
    })
    .then(data => {
      // 恢复按钮状态
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      if (data.success) {
        // 显示成功消息
        showAlert('隐私设置已保存', 'success');
      } else {
        // 显示错误信息
        showAlert(data.error || '保存失败，请稍后重试', 'danger');
      }
    })
    .catch(error => {
      console.error('保存隐私设置失败:', error);
      
      // 恢复按钮状态
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      // 显示错误消息
      showAlert('保存失败，请检查网络连接后重试', 'danger');
    });
  });
}

// 初始化账号关联
function initAccountConnections() {
  const connectButtons = document.querySelectorAll('.connect-account-btn');
  const disconnectButtons = document.querySelectorAll('.disconnect-account-btn');
  
  // 连接社交媒体账号
  connectButtons.forEach(button => {
    button.addEventListener('click', function() {
      const provider = this.getAttribute('data-provider');
      
      // 显示加载状态
      this.disabled = true;
      const originalText = this.textContent;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 连接中...';
      
      // 在5秒后恢复按钮状态（如果页面未被重定向）
      setTimeout(() => {
        if (document.body.contains(this)) {
          this.disabled = false;
          this.innerHTML = originalText;
        }
      }, 5000);
    });
  });
  
  // 断开社交媒体账号连接
  disconnectButtons.forEach(button => {
    button.addEventListener('click', function() {
      if (!confirm('确定要解除账号关联吗？')) {
        return;
      }
      
      const provider = this.getAttribute('data-provider');
      
      // 显示加载状态
      this.disabled = true;
      const originalText = this.textContent;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 解除中...';
      
      // 发送AJAX请求
      fetch(`/api/user/disconnect-account/${provider}/`, {
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
        if (data.success) {
          // 显示成功消息
          showAlert(`已成功解除${provider}账号关联`, 'success');
          
          // 更新UI
          const connectionItem = this.closest('.connection-item');
          if (connectionItem) {
            // 将"已连接"改为"未连接"
            const statusBadge = connectionItem.querySelector('.connection-status');
            if (statusBadge) {
              statusBadge.textContent = '未连接';
              statusBadge.classList.remove('bg-success');
              statusBadge.classList.add('bg-secondary');
            }
            
            // 隐藏断开按钮，显示连接按钮
            this.style.display = 'none';
            const connectBtn = connectionItem.querySelector('.connect-account-btn');
            if (connectBtn) {
              connectBtn.style.display = 'inline-block';
            }
          }
        } else {
          // 显示错误消息
          showAlert(data.error || '解除关联失败，请稍后重试', 'danger');
          
          // 恢复按钮状态
          this.disabled = false;
          this.textContent = originalText;
        }
      })
      .catch(error => {
        console.error('解除账号关联失败:', error);
        
        // 恢复按钮状态
        this.disabled = false;
        this.textContent = originalText;
        
        // 显示错误消息
        showAlert('解除关联失败，请稍后重试', 'danger');
      });
    });
  });
}

// 检查密码强度
function checkPasswordStrength(password) {
  const passwordInput = document.getElementById('new_password');
  const strengthMeter = document.getElementById('password-strength-meter');
  if (!passwordInput || !strengthMeter) return;
  
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
  
  // 设置颜色和文本
  const strengthText = document.getElementById('password-strength-text');
  
  if (strength < 30) {
    strengthMeter.className = 'progress-bar bg-danger';
    if (strengthText) strengthText.textContent = '弱';
  } else if (strength < 60) {
    strengthMeter.className = 'progress-bar bg-warning';
    if (strengthText) strengthText.textContent = '中等';
  } else {
    strengthMeter.className = 'progress-bar bg-success';
    if (strengthText) strengthText.textContent = '强';
  }
}

// 检查两次密码是否匹配
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
    matchText.textContent = '密码匹配';
    matchText.className = 'text-success';
  } else {
    matchText.textContent = '密码不匹配';
    matchText.className = 'text-danger';
  }
}

// 显示输入错误
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

// 清除输入错误
function clearInputError(inputElement) {
  inputElement.classList.remove('is-invalid');
  
  const feedbackElement = inputElement.nextElementSibling;
  if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
    feedbackElement.textContent = '';
  }
}

// 显示消息提示
function showAlert(message, type = 'info', duration = 3000) {
  // 创建警告元素
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
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
  
  // 设置自动消失
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

// 验证邮箱格式
function isValidEmail(email) {
  const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email.toLowerCase());
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