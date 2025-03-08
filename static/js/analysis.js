/**
 * AI Health Advice JavaScript Module
 * Handles generating advice from user health data and formatting the results
 */

document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const generateBtn = document.getElementById('generateAdviceBtn');
  const advicePlaceholder = document.getElementById('advicePlaceholder');
  const adviceLoading = document.getElementById('adviceLoading');
  const adviceContent = document.getElementById('adviceContent');
  const adviceError = document.getElementById('adviceError');
  const errorMessage = document.getElementById('errorMessage');
  
  // If we're not on the AI advice page, exit early
  if (!generateBtn) return;
  
  // Add click event listener to the generate button
  generateBtn.addEventListener('click', generateAdvice);
  
  /**
   * Generate advice by calling the backend API
   */
  function generateAdvice() {
    // Show loading state
    advicePlaceholder.classList.add('d-none');
    adviceContent.classList.add('d-none');
    adviceError.classList.add('d-none');
    adviceLoading.classList.remove('d-none');
    
    // Set button to loading state
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Generating...';
    
    // Get CSRF token for the POST request
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Make API request to generate advice
    fetch('/analysis/ai-advice/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({}),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Hide loading, show content
      adviceLoading.classList.add('d-none');
      
      if (data.error) {
        // Show error if something went wrong
        errorMessage.textContent = data.error;
        adviceError.classList.remove('d-none');
      } else {
        // Format and display the advice
        adviceContent.innerHTML = formatAdvice(data.advice);
        adviceContent.classList.remove('d-none');
        
        // Add animation classes to elements
        const elements = adviceContent.querySelectorAll('h3, p, .recommendation-item, .correlation-item');
        elements.forEach((el, index) => {
          el.classList.add('animate__animated', 'animate__fadeIn');
          el.style.animationDelay = `${index * 0.1}s`;
        });
      }
    })
    .catch(error => {
      // Handle errors
      adviceLoading.classList.add('d-none');
      errorMessage.textContent = error.message || 'Failed to generate advice. Please try again.';
      adviceError.classList.remove('d-none');
      console.error('Error generating advice:', error);
    })
    .finally(() => {
      // Reset button state
      generateBtn.disabled = false;
      generateBtn.innerHTML = '<i class="bi bi-magic me-2"></i> Generate AI Advice';
    });
  }
  
  /**
   * Format the plain text advice into HTML with proper styling
   * @param {string} adviceText - The raw text response from the API
   * @return {string} Formatted HTML
   */
  function formatAdvice(adviceText) {
    // Split the text into sections
    const sections = adviceText.split(/#{1,2}\s+/);
    
    let formattedHtml = '';
    
    // Process each section
    sections.forEach((section, index) => {
      // Skip the first empty section if it exists
      if (index === 0 && !section.trim()) return;
      
      const lines = section.split('\n');
      const title = lines[0].trim();
      const content = lines.slice(1).join('\n').trim();
      
      // Add section title and format content based on section type
      if (title.toLowerCase().includes('summary') || index === 0) {
        formattedHtml += `<h3></i>${title}</h3>`;
        formattedHtml += `<div class="advice-body">${formatParagraphs(content)}</div>`;
      } 
      else if (title.toLowerCase().includes('strength')) {
        formattedHtml += `<h3><i class="bi bi-star me-2"></i>${title}</h3>`;
        formattedHtml += `<div class="advice-body">${formatParagraphs(content)}</div>`;
      }
      else if (title.toLowerCase().includes('improv')) {
        formattedHtml += `<h3><i class="bi bi-arrow-up-circle me-2"></i>${title}</h3>`;
        formattedHtml += `<div class="advice-body">${formatParagraphs(content)}</div>`;
      }
      else if (title.toLowerCase().includes('recommend')) {
        formattedHtml += `<h3><i class="bi bi-lightbulb me-2"></i>${title}</h3>`;
        formattedHtml += formatRecommendations(content);
      }
      else if (title.toLowerCase().includes('pattern') || title.toLowerCase().includes('correlation')) {
        formattedHtml += `<h3><i class="bi bi-graph-up me-2"></i>${title}</h3>`;
        formattedHtml += formatCorrelations(content);
      }
      else {
        formattedHtml += `<h3><i class="bi bi-info-circle me-2"></i>${title}</h3>`;
        formattedHtml += `<div class="advice-body">${formatParagraphs(content)}</div>`;
      }
    });
    
    return formattedHtml;
  }
  
  /**
   * Format plain text paragraphs into HTML paragraphs
   * @param {string} text - Raw text with paragraphs
   * @return {string} HTML paragraphs
   */
  function formatParagraphs(text) {
    return text.split('\n\n')
      .filter(para => para.trim() !== '')
      .map(para => `<p>${para.trim()}</p>`)
      .join('');
  }
  
  /**
   * Format numbered recommendations into styled list items
   * @param {string} text - Raw recommendations text
   * @return {string} HTML formatted recommendations
   */
  function formatRecommendations(text) {
    const recommendations = text.split(/\d+\.\s+/)
      .filter(item => item.trim() !== '')
      .map(item => `<div class="recommendation-item">${item.trim()}</div>`)
      .join('');
    
    return `<div class="recommendations mb-4">${recommendations}</div>`;
  }
  
  /**
   * Format correlation points into styled list items
   * @param {string} text - Raw correlation text
   * @return {string} HTML formatted correlations
   */
  function formatCorrelations(text) {
    const items = text.split(/[-•]\s+/)
      .filter(item => item.trim() !== '')
      .map(item => {
        return `<div class="correlation-item">
          <i class="bi bi-arrow-left-right"></i>
          <div>${item.trim()}</div>
        </div>`;
      })
      .join('');
    
    return `<div class="correlations mb-4">${items}</div>`;
  }
}); 