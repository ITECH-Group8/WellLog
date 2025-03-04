/**
 * Community module JavaScript functions
 */

// Image loading handlers for post detail page
function handleImageLoaded(img) {
  console.log('Image loaded successfully');
  document.getElementById('loading-spinner').style.display = 'none';
  img.style.display = 'block';
}

function handleImageError(img) {
  console.error('Image loading failed');
  document.getElementById('loading-spinner').innerHTML = '<div class="text-danger"><i class="bi bi-exclamation-triangle" style="font-size: 3rem;"></i><p>Image loading failed</p></div>';
  img.style.display = 'none';
}

// Image loading handlers for post list page
function handleThumbnailLoaded(img, postId) {
  var placeholder = document.getElementById('placeholder-' + postId);
  if (placeholder) {
    placeholder.style.display = 'none';
  }
  img.style.display = 'block';
  console.log('Thumbnail loaded successfully: ' + postId);
}

function handleThumbnailError(img, postId) {
  var placeholder = document.getElementById('placeholder-' + postId);
  if (placeholder) {
    placeholder.innerHTML = '<i class="bi bi-exclamation-triangle" style="font-size: 2rem; color: #dc3545;"></i>';
  }
  img.style.display = 'none';
  console.error('Thumbnail loading failed: ' + postId);
}

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
  console.log('初始化社区页面功能');
  
  // Mobile sidebar toggle
  const menuToggle = document.querySelector('.menu-toggle');
  if (menuToggle) {
    menuToggle.addEventListener('click', function() {
      document.body.classList.toggle('sidebar-expanded');
    });
  }
  
  // 初始化卡片点赞按钮效果
  initCardLikeButtons();
  
  // Post image loading check
  const postImage = document.getElementById('post-main-image');
  const loadingSpinner = document.getElementById('loading-spinner');
  
  if (postImage && loadingSpinner) {
    // Ensure loading indicator is hidden after image loads
    postImage.onload = function() {
      console.log('Image loaded successfully');
      loadingSpinner.style.display = 'none';
      postImage.style.display = 'block';
    };
    
    // Image error handling function
    postImage.onerror = function() {
      console.error('Image loading failed');
      loadingSpinner.innerHTML = '<div class="text-danger"><i class="bi bi-exclamation-triangle" style="font-size: 3rem;"></i><p>Image loading failed</p></div>';
      postImage.style.display = 'none';
    };
    
    // If image is already loaded (from cache), manually trigger onload event
    if (postImage.complete) {
      console.log('Image loaded from cache');
      if (postImage.naturalWidth === 0) {
        // Image failed to load
        postImage.onerror();
      } else {
        // Image loaded successfully
        postImage.onload();
      }
    }
  }
  
  // Like button event handling
  const likeBtn = document.querySelector('.like-btn');
  if (likeBtn) {
    likeBtn.addEventListener('click', function() {
      const postId = this.getAttribute('data-post-id');
      const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
      
      console.log('Like button clicked, Post ID:', postId);
      
      // Send like request
      fetch('/community/posts/' + postId + '/like/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        credentials: 'same-origin'
      })
      .then(response => {
        console.log('Like request response status:', response.status);
        if (!response.ok) {
          throw new Error('Like request failed, status code: ' + response.status);
        }
        return response.json();
      })
      .then(data => {
        console.log('Like request response data:', data);
        
        // Update UI
        const icon = likeBtn.querySelector('i');
        const likeText = likeBtn.querySelector('.like-text');
        const likeCount = document.getElementById('likeCount');
        
        if (data.liked) {
          likeBtn.classList.remove('btn-outline-danger');
          likeBtn.classList.add('btn-danger');
          icon.classList.remove('bi-heart');
          icon.classList.add('bi-heart-fill');
          likeText.textContent = 'Liked';
        } else {
          likeBtn.classList.add('btn-outline-danger');
          likeBtn.classList.remove('btn-danger');
          icon.classList.add('bi-heart');
          icon.classList.remove('bi-heart-fill');
          likeText.textContent = 'Like';
        }
        
        // Always update like count display regardless of whether it's 0
        if (data.like_count > 0) {
          likeCount.textContent = '(' + data.like_count + ')';
        } else {
          likeCount.textContent = '';
        }
      })
      .catch(error => {
        console.error('Like request failed:', error);
        alert('Like failed, please try again');
      });
    });
  }
  
  // Check thumbnails on list page
  const thumbnailImages = document.querySelectorAll('.post-grid img.post-image');
  thumbnailImages.forEach(img => {
    if (img.complete) {
      const postId = img.getAttribute('data-post-id');
      if (postId) {
        if (img.naturalWidth === 0) {
          handleThumbnailError(img, postId);
        } else {
          handleThumbnailLoaded(img, postId);
        }
      }
    }
  });
  
  // 初始化点赞功能
  initLikeButtons();
  
  // 初始化图片加载处理
  initImageLoading();
  
  // 初始化分享功能
  initShareButtons();
  
  // 初始化评论功能
  initCommentForms();
});

// 初始化点赞按钮功能
function initLikeButtons() {
  const likeButtons = document.querySelectorAll('.like-button');
  
  likeButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const postId = this.getAttribute('data-post-id');
      const likeUrl = `/community/like_toggle/${postId}/`;
      const likeCount = document.querySelector(`.like-count[data-post-id="${postId}"]`);
      const likeIcon = this.querySelector('i');
      const likeText = this.querySelector('span');
      
      // 显示加载状态
      likeIcon.className = 'fas fa-spinner fa-spin';
      
      // 发送请求到服务器
      fetch(likeUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('网络响应异常');
        }
        return response.json();
      })
      .then(data => {
        console.log('点赞响应:', data);
        
        // 更新按钮状态
        if (data.liked) {
          button.classList.add('liked');
          likeIcon.className = 'fas fa-heart text-danger';
          likeText.textContent = '已点赞';
        } else {
          button.classList.remove('liked');
          likeIcon.className = 'far fa-heart';
          likeText.textContent = '点赞';
        }
        
        // 更新点赞数量
        if (likeCount) {
          likeCount.textContent = data.likes_count;
        }
      })
      .catch(error => {
        console.error('点赞请求失败:', error);
        // 恢复原始状态
        if (button.classList.contains('liked')) {
          likeIcon.className = 'fas fa-heart text-danger';
        } else {
          likeIcon.className = 'far fa-heart';
        }
      });
    });
  });
}

// 初始化图片加载处理
function initImageLoading() {
  // 处理详情页大图
  const postImage = document.getElementById('post-image');
  if (postImage) {
    const imageLoader = document.getElementById('image-loading');
    
    // 图片加载成功处理
    postImage.addEventListener('load', function() {
      handleImageLoaded(this);
    });
    
    // 图片加载失败处理
    postImage.addEventListener('error', function() {
      handleImageError(this);
    });
    
    // 检查图片是否已从缓存加载
    if (postImage.complete) {
      if (postImage.naturalHeight === 0) {
        handleImageError(postImage);
      } else {
        handleImageLoaded(postImage);
      }
    }
  }
  
  // 处理列表页缩略图
  const thumbnails = document.querySelectorAll('.post-thumbnail');
  thumbnails.forEach(thumbnail => {
    // 图片加载成功处理
    thumbnail.addEventListener('load', function() {
      handleThumbnailLoaded(this);
    });
    
    // 图片加载失败处理
    thumbnail.addEventListener('error', function() {
      handleThumbnailError(this);
    });
    
    // 检查图片是否已从缓存加载
    if (thumbnail.complete) {
      if (thumbnail.naturalHeight === 0) {
        handleThumbnailError(thumbnail);
      } else {
        handleThumbnailLoaded(thumbnail);
      }
    }
  });
}

// 初始化分享按钮
function initShareButtons() {
  const shareButtons = document.querySelectorAll('.share-button');
  
  shareButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const postTitle = this.getAttribute('data-title');
      const postUrl = window.location.origin + this.getAttribute('data-url');
      
      // 检查是否支持原生分享API
      if (navigator.share) {
        navigator.share({
          title: postTitle,
          url: postUrl
        })
        .then(() => console.log('分享成功'))
        .catch((error) => console.log('分享失败:', error));
      } else {
        // 创建一个临时输入框复制链接
        const tempInput = document.createElement('input');
        document.body.appendChild(tempInput);
        tempInput.value = postUrl;
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        
        // 显示提示消息
        alert('链接已复制到剪贴板，可以粘贴分享给好友！');
      }
    });
  });
}

// 初始化评论表单
function initCommentForms() {
  const commentForm = document.getElementById('comment-form');
  if (!commentForm) return;
  
  commentForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const commentText = document.getElementById('comment-text').value.trim();
    if (!commentText) {
      alert('请输入评论内容！');
      return;
    }
    
    const postId = this.getAttribute('data-post-id');
    const commentUrl = `/community/comment/${postId}/`;
    const submitButton = this.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    
    // 显示加载状态
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 提交中...';
    
    // 发送请求到服务器
    fetch(commentUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: `comment=${encodeURIComponent(commentText)}`,
      credentials: 'same-origin'
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('网络响应异常');
      }
      return response.json();
    })
    .then(data => {
      console.log('评论响应:', data);
      
      // 重置表单
      document.getElementById('comment-text').value = '';
      
      // 添加新评论到评论列表
      addCommentToList(data.comment);
      
      // 更新评论计数
      updateCommentCount(data.comments_count);
      
      // 恢复按钮状态
      submitButton.disabled = false;
      submitButton.textContent = originalButtonText;
    })
    .catch(error => {
      console.error('评论请求失败:', error);
      // 恢复按钮状态
      submitButton.disabled = false;
      submitButton.textContent = originalButtonText;
      // 显示错误信息
      alert('评论提交失败，请稍后重试');
    });
  });
}

// 将新评论添加到评论列表
function addCommentToList(comment) {
  const commentsList = document.getElementById('comments-list');
  if (!commentsList) return;
  
  const commentElement = document.createElement('div');
  commentElement.className = 'comment mb-3 p-3 border-bottom';
  
  commentElement.innerHTML = `
    <div class="d-flex">
      <div class="avatar me-2">
        <img src="${comment.user_avatar || '/static/images/default-avatar.png'}" class="rounded-circle" width="40" height="40" alt="${comment.username}">
      </div>
      <div class="flex-grow-1">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <h6 class="mb-0">${comment.username}</h6>
          <small class="text-muted">${comment.created_at}</small>
        </div>
        <p class="mb-1">${comment.text}</p>
      </div>
    </div>
  `;
  
  // 将新评论插入到列表顶部
  if (commentsList.firstChild) {
    commentsList.insertBefore(commentElement, commentsList.firstChild);
  } else {
    commentsList.appendChild(commentElement);
  }
  
  // 如果之前显示"暂无评论"，现在移除它
  const emptyComments = document.querySelector('.empty-comments');
  if (emptyComments) {
    emptyComments.remove();
  }
}

// 更新评论计数
function updateCommentCount(count) {
  const commentCount = document.querySelector('.comments-count');
  if (commentCount) {
    commentCount.textContent = count;
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

// 初始化卡片点赞按钮效果
function initCardLikeButtons() {
  // 获取所有帖子卡片中的点赞显示元素
  const likeDisplays = document.querySelectorAll('.like-display');
  
  likeDisplays.forEach(display => {
    const postId = display.getAttribute('data-post-id');
    const likeIcon = display.querySelector('i');
    const likeCount = display.querySelector('.post-like-count');
    
    // 为图标添加点击效果
    if (likeIcon && likeCount) {
      likeIcon.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation(); // 阻止事件冒泡，防止触发卡片点击
        
        // 如果已经在提交中，则不处理
        if (likeIcon.classList.contains('animate-pulse')) return;
        
        // 添加动画效果
        likeIcon.classList.add('animate-pulse');
        
        // 发送点赞请求
        fetch(`/community/like_toggle/${postId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
          },
          credentials: 'same-origin'
        })
        .then(response => {
          if (!response.ok) throw new Error('网络响应异常');
          return response.json();
        })
        .then(data => {
          // 移除动画效果
          likeIcon.classList.remove('animate-pulse');
          
          // 更新点赞状态和数量
          if (data.liked) {
            likeIcon.className = 'bi bi-heart-fill';
            likeIcon.classList.add('text-danger');
            
            // 添加点赞动画
            likeIcon.classList.add('scale-effect');
            setTimeout(() => likeIcon.classList.remove('scale-effect'), 300);
          } else {
            likeIcon.className = 'bi bi-heart';
            likeIcon.classList.remove('text-danger');
          }
          
          // 更新点赞数量
          likeCount.textContent = data.likes_count;
        })
        .catch(error => {
          console.error('点赞请求失败:', error);
          likeIcon.classList.remove('animate-pulse');
        });
      });
    }
  });
}

// 添加CSS动画类
document.head.insertAdjacentHTML('beforeend', `
  <style>
    .animate-pulse {
      animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
      0% {
        transform: scale(1);
      }
      50% {
        transform: scale(1.2);
      }
      100% {
        transform: scale(1);
      }
    }
    
    .scale-effect {
      animation: scale 0.3s ease-in-out;
    }
    
    @keyframes scale {
      0% {
        transform: scale(1);
      }
      50% {
        transform: scale(1.5);
      }
      100% {
        transform: scale(1);
      }
    }
  </style>
`); 