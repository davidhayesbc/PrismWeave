// PrismWeave UI Utilities
// Common UI patterns and DOM manipulation helpers

class UIUtils {
  static STATUS_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error', 
    WARNING: 'warning',
    INFO: 'info'
  };

  // Status/notification management
  static showStatus(message, type = UIUtils.STATUS_TYPES.SUCCESS, duration = 5000) {
    const statusElement = document.getElementById('status') || UIUtils.createStatusElement();
    const statusText = statusElement.querySelector('.status-text') || statusElement;
    
    statusText.textContent = message;
    statusElement.className = `status ${type}`;
    statusElement.style.display = 'block';
    
    if (duration > 0) {
      setTimeout(() => {
        UIUtils.hideStatus();
      }, duration);
    }
  }

  static hideStatus() {
    const statusElement = document.getElementById('status');
    if (statusElement) {
      statusElement.style.display = 'none';
    }
  }

  static createStatusElement() {
    const statusElement = document.createElement('div');
    statusElement.id = 'status';
    statusElement.className = 'status';
    statusElement.innerHTML = '<span class="status-text"></span>';
    
    // Add basic styling if no CSS is present
    Object.assign(statusElement.style, {
      position: 'fixed',
      top: '10px',
      right: '10px',
      padding: '10px 15px',
      borderRadius: '4px',
      color: 'white',
      fontFamily: 'system-ui, sans-serif',
      fontSize: '14px',
      zIndex: '10000',
      display: 'none'
    });
    
    document.body.appendChild(statusElement);
    return statusElement;
  }

  // Loading state management
  static showLoading(show = true, targetId = 'main-content') {
    const loadingElement = document.getElementById('loading') || UIUtils.createLoadingElement();
    const mainContent = document.getElementById(targetId);
    
    if (show) {
      loadingElement.style.display = 'flex';
      if (mainContent) mainContent.style.display = 'none';
    } else {
      loadingElement.style.display = 'none';
      if (mainContent) mainContent.style.display = 'block';
    }
  }

  static createLoadingElement() {
    const loadingElement = document.createElement('div');
    loadingElement.id = 'loading';
    loadingElement.innerHTML = `
      <div class="loading-spinner"></div>
      <span class="loading-text">Processing...</span>
    `;
    
    // Add basic styling
    Object.assign(loadingElement.style, {
      position: 'fixed',
      top: '0',
      left: '0',
      width: '100%',
      height: '100%',
      display: 'none',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      zIndex: '9999'
    });
    
    document.body.appendChild(loadingElement);
    return loadingElement;
  }

  // Form utilities
  static populateForm(settings, fieldMapping = {}) {
    Object.entries(settings).forEach(([key, value]) => {
      const fieldId = fieldMapping[key] || UIUtils.kebabCase(key);
      const element = document.getElementById(fieldId);
      
      if (!element) return;
      
      switch (element.type) {
        case 'checkbox':
          element.checked = Boolean(value);
          break;
        case 'radio':
          if (element.value === value) {
            element.checked = true;
          }
          break;
        case 'select-one':
        case 'select-multiple':
          element.value = value;
          break;
        default:
          element.value = value || '';
      }
    });
  }

  static collectFormData(fieldMapping = {}, containerSelector = 'body') {
    const container = document.querySelector(containerSelector);
    const formData = {};
    
    // Collect all form inputs
    const inputs = container.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
      if (!input.id) return;
      
      const key = UIUtils.findKeyByValue(fieldMapping, input.id) || UIUtils.camelCase(input.id);
      
      switch (input.type) {
        case 'checkbox':
          formData[key] = input.checked;
          break;
        case 'radio':
          if (input.checked) {
            formData[key] = input.value;
          }
          break;
        case 'number':
          formData[key] = input.value ? Number(input.value) : null;
          break;
        default:
          formData[key] = input.value?.trim() || '';
      }
    });
    
    return formData;
  }

  // Input validation helpers
  static validateField(fieldId, value, validationRules = {}) {
    const element = document.getElementById(fieldId);
    const errors = [];
    
    // Required validation
    if (validationRules.required && (!value || value === '')) {
      errors.push('This field is required');
    }
    
    // Pattern validation
    if (validationRules.pattern && value && !validationRules.pattern.test(value)) {
      errors.push('Invalid format');
    }
    
    // Length validation
    if (validationRules.minLength && value.length < validationRules.minLength) {
      errors.push(`Minimum length is ${validationRules.minLength}`);
    }
    
    if (validationRules.maxLength && value.length > validationRules.maxLength) {
      errors.push(`Maximum length is ${validationRules.maxLength}`);
    }
    
    // Range validation for numbers
    if (validationRules.min !== undefined && Number(value) < validationRules.min) {
      errors.push(`Minimum value is ${validationRules.min}`);
    }
    
    if (validationRules.max !== undefined && Number(value) > validationRules.max) {
      errors.push(`Maximum value is ${validationRules.max}`);
    }
    
    // Update field styling
    if (element) {
      UIUtils.setFieldValidation(element, errors.length === 0, errors[0]);
    }
    
    return errors;
  }

  static setFieldValidation(element, isValid, message = '') {
    if (isValid) {
      element.style.borderColor = '#ddd';
      element.title = '';
    } else {
      element.style.borderColor = '#f44336';
      element.title = message;
    }
    
    // Remove existing validation message
    const existingMessage = element.parentNode.querySelector('.validation-message');
    if (existingMessage) {
      existingMessage.remove();
    }
    
    // Add validation message if invalid
    if (!isValid && message) {
      const messageElement = document.createElement('div');
      messageElement.className = 'validation-message';
      messageElement.textContent = message;
      messageElement.style.color = '#f44336';
      messageElement.style.fontSize = '12px';
      messageElement.style.marginTop = '4px';
      
      element.parentNode.appendChild(messageElement);
    }
  }

  // Button state management
  static setButtonState(buttonId, disabled = false, text = null) {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    button.disabled = disabled;
    if (text) {
      button.textContent = text;
    }
    
    if (disabled) {
      button.style.opacity = '0.6';
      button.style.cursor = 'not-allowed';
    } else {
      button.style.opacity = '1';
      button.style.cursor = 'pointer';
    }
  }

  // Event listener helpers
  static addEventListeners(listeners) {
    listeners.forEach(({ selector, event, handler, options = {} }) => {
      const elements = typeof selector === 'string' 
        ? document.querySelectorAll(selector)
        : [selector];
        
      elements.forEach(element => {
        if (element) {
          element.addEventListener(event, handler, options);
        }
      });
    });
  }

  static debounce(func, delay = 300) {
    let timeoutId;
    return function (...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  }

  // Modal/dialog helpers
  static showConfirmDialog(message, title = 'Confirm') {
    return new Promise((resolve) => {
      const confirmed = confirm(`${title}\n\n${message}`);
      resolve(confirmed);
    });
  }

  static createModal(content, options = {}) {
    const modal = document.createElement('div');
    modal.className = 'prismweave-modal';
    modal.innerHTML = `
      <div class="modal-backdrop" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000;"></div>
      <div class="modal-content" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; z-index: 10001; max-width: 500px; width: 90%;">
        ${options.title ? `<h3>${options.title}</h3>` : ''}
        <div class="modal-body">${content}</div>
        <div class="modal-actions" style="text-align: right; margin-top: 20px;">
          <button class="modal-close" style="padding: 8px 16px; margin-left: 8px;">Close</button>
        </div>
      </div>
    `;
    
    // Close handlers
    modal.querySelector('.modal-backdrop').addEventListener('click', () => {
      UIUtils.closeModal(modal);
    });
    
    modal.querySelector('.modal-close').addEventListener('click', () => {
      UIUtils.closeModal(modal);
    });
    
    document.body.appendChild(modal);
    return modal;
  }

  static closeModal(modal) {
    if (modal && modal.parentNode) {
      modal.parentNode.removeChild(modal);
    }
  }

  // Utility string functions
  static kebabCase(str) {
    return str.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
  }

  static camelCase(str) {
    return str.replace(/-([a-z])/g, (match, letter) => letter.toUpperCase());
  }

  static findKeyByValue(obj, value) {
    return Object.keys(obj).find(key => obj[key] === value);
  }

  // File download helper
  static downloadFile(content, filename, mimeType = 'text/plain') {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    
    URL.revokeObjectURL(url);
  }

  // Copy to clipboard
  static async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      UIUtils.showStatus('Copied to clipboard', UIUtils.STATUS_TYPES.SUCCESS, 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      UIUtils.showStatus('Failed to copy to clipboard', UIUtils.STATUS_TYPES.ERROR);
    }
  }

  // CSS helper to add status styling if not present
  static addStatusStyling() {
    if (document.getElementById('prismweave-ui-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'prismweave-ui-styles';
    style.textContent = `
      .status {
        border-radius: 4px;
        padding: 10px 15px;
        margin: 10px 0;
        font-family: system-ui, sans-serif;
        font-size: 14px;
      }
      .status.success {
        background-color: #4CAF50;
        color: white;
      }
      .status.error {
        background-color: #f44336;
        color: white;
      }
      .status.warning {
        background-color: #FF9800;
        color: white;
      }
      .status.info {
        background-color: #2196F3;
        color: white;
      }
      .validation-message {
        font-size: 12px;
        color: #f44336;
        margin-top: 4px;
      }
      .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #2196F3;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin-bottom: 10px;
      }
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `;
    
    document.head.appendChild(style);
  }
}

// Auto-add styling when loaded
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', UIUtils.addStatusStyling);
  } else {
    UIUtils.addStatusStyling();
  }
}

// Export for different contexts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = UIUtils;
}

if (typeof window !== 'undefined') {
  window.UIUtils = UIUtils;
}
