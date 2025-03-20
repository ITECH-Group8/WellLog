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
  console.log('Initializing community page functionality');
  
  // Mobile sidebar toggle
  const menuToggle = document.querySelector('.menu-toggle');
  if (menuToggle) {
    menuToggle.addEventListener('click', function() {
      document.body.classList.toggle('sidebar-expanded');
    });
  }
  
  // Initialize card like button effects
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
  
  // Initialize like functionality
  initLikeButtons();
  
  // Initialize image loading
  initImageLoading();
  
  // Initialize sharing functionality
  initShareButtons();
  
  // Initialize comment functionality
  initCommentForms();
});

// Initialize like button functionality
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
      
      // Show loading state
      likeIcon.className = 'fas fa-spinner fa-spin';
      
      // Send request to server
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
          throw new Error('Network response abnormal');
        }
        return response.json();
      })
      .then(data => {
        console.log('Like response:', data);
        
        // Update button status
        if (data.liked) {
          button.classList.add('liked');
          likeIcon.className = 'fas fa-heart text-danger';
          likeText.textContent = 'Liked';
        } else {
          button.classList.remove('liked');
          likeIcon.className = 'far fa-heart';
          likeText.textContent = 'Like';
        }
        
        // Update like count
        if (likeCount) {
          likeCount.textContent = data.like_count;
        }
      })
      .catch(error => {
        console.error('Like request failed:', error);
        // Restore original state
        if (button.classList.contains('liked')) {
          likeIcon.className = 'fas fa-heart text-danger';
        } else {
          likeIcon.className = 'far fa-heart';
        }
      });
    });
  });
  
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
}

// Initialize image loading
function initImageLoading() {
  // Handle detail page large image
  const postImage = document.getElementById('post-image');
  if (postImage) {
    const imageLoader = document.getElementById('image-loading');
    
    // Image load success handler
    postImage.addEventListener('load', function() {
      handleImageLoaded(this);
    });
    
    // Image load error handler
    postImage.addEventListener('error', function() {
      handleImageError(this);
    });
    
    // Check if image is already loaded from cache
    if (postImage.complete) {
      if (postImage.naturalHeight === 0) {
        handleImageError(postImage);
      } else {
        handleImageLoaded(postImage);
      }
    }
  }
  
  // Handle list page thumbnails
  const thumbnails = document.querySelectorAll('.post-thumbnail');
  thumbnails.forEach(thumbnail => {
    // Image load success handler
    thumbnail.addEventListener('load', function() {
      handleThumbnailLoaded(this);
    });
    
    // Image load error handler
    thumbnail.addEventListener('error', function() {
      handleThumbnailError(this);
    });
    
    // Check if image is already loaded from cache
    if (thumbnail.complete) {
      if (thumbnail.naturalHeight === 0) {
        handleThumbnailError(thumbnail);
      } else {
        handleThumbnailLoaded(thumbnail);
      }
    }
  });
}

// Initialize sharing functionality
function initShareButtons() {
  const shareButtons = document.querySelectorAll('.share-button');
  
  shareButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const postTitle = this.getAttribute('data-title');
      const postUrl = window.location.origin + this.getAttribute('data-url');
      
      // Check if native sharing API is supported
      if (navigator.share) {
        navigator.share({
          title: postTitle,
          url: postUrl
        })
        .then(() => console.log('Share successful'))
        .catch((error) => console.log('Share failed:', error));
      } else {
        // Create a temporary input to copy link
        const tempInput = document.createElement('input');
        document.body.appendChild(tempInput);
        tempInput.value = postUrl;
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        
        // Show notification message
        alert('Link copied to clipboard, you can paste it to share with friends!');
      }
    });
  });
}

// Initialize comment functionality
function initCommentForms() {
  const commentForm = document.getElementById('comment-form');
  if (!commentForm) return;
  
  commentForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const commentText = document.getElementById('comment-text').value.trim();
    if (!commentText) {
      alert('Please enter a comment!');
      return;
    }
    
    const postId = this.getAttribute('data-post-id');
    const commentUrl = `/community/comment/${postId}/`;
    const submitButton = this.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
    
    // Send request to server
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
        throw new Error('Network response abnormal');
      }
      return response.json();
    })
    .then(data => {
      console.log('Comment response:', data);
      
      // Reset form
      document.getElementById('comment-text').value = '';
      
      // Add new comment to comment list
      addCommentToList(data.comment);
      
      // Update comment count
      updateCommentCount(data.comments_count);
      
      // Restore button state
      submitButton.disabled = false;
      submitButton.textContent = originalButtonText;
    })
    .catch(error => {
      console.error('Comment request failed:', error);
      // Restore button state
      submitButton.disabled = false;
      submitButton.textContent = originalButtonText;
      // Show error message
      alert('Comment submission failed, please try again later');
    });
  });
}

// Add new comment to comment list
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
  
  // Insert new comment at the top of the list
  if (commentsList.firstChild) {
    commentsList.insertBefore(commentElement, commentsList.firstChild);
  } else {
    commentsList.appendChild(commentElement);
  }
  
  // Remove "no comments" message if it exists
  const emptyComments = document.querySelector('.empty-comments');
  if (emptyComments) {
    emptyComments.remove();
  }
}

// Update comment count
function updateCommentCount(count) {
  const commentCount = document.querySelector('.comments-count');
  if (commentCount) {
    commentCount.textContent = count;
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

// Initialize card like button effects
function initCardLikeButtons() {
  // Get all like display elements in post cards
  const likeDisplays = document.querySelectorAll('.like-display');
  
  likeDisplays.forEach(display => {
    const postId = display.getAttribute('data-post-id');
    const likeIcon = display.querySelector('i');
    const likeCount = display.querySelector('.post-like-count');
    
    // Add click effect to icon
    if (likeIcon && likeCount) {
      likeIcon.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation(); // Prevent event bubbling to avoid triggering card click
        
        // Do not process if already submitting
        if (likeIcon.classList.contains('animate-pulse')) return;
        
        // Add animation effect
        likeIcon.classList.add('animate-pulse');
        
        // Send like request
        fetch(`/community/like_toggle/${postId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
          },
          credentials: 'same-origin'
        })
        .then(response => {
          if (!response.ok) throw new Error('Network response abnormal');
          return response.json();
        })
        .then(data => {
          // Remove animation effect
          likeIcon.classList.remove('animate-pulse');
          
          // Update like status and count
          if (data.liked) {
            likeIcon.className = 'bi bi-heart-fill';
            likeIcon.classList.add('text-danger');
            
            // Add like animation
            likeIcon.classList.add('scale-effect');
            setTimeout(() => likeIcon.classList.remove('scale-effect'), 300);
          } else {
            likeIcon.className = 'bi bi-heart';
            likeIcon.classList.remove('text-danger');
          }
          
          // Update like count
          likeCount.textContent = data.likes_count;
        })
        .catch(error => {
          console.error('Like request failed:', error);
          likeIcon.classList.remove('animate-pulse');
        });
      });
    }
  });
}

// Add CSS animation classes
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