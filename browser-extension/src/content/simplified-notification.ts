// Simplified notification function
function showNotification(
  message: string,
  type: 'success' | 'error' | 'info' = 'info',
  duration: number = 4000,
  clickUrl?: string
): void {
  console.log('showNotification called:', { message, type, duration, clickUrl });

  // Simple guard clause
  if (!document.body) return;

  // Remove existing notification
  const existingNotification = document.getElementById('prismweave-notification');
  if (existingNotification) {
    existingNotification.remove();
  }

  // Create notification element
  const notification = document.createElement('div');
  notification.id = 'prismweave-notification';

  // Set base styles
  const colors = {
    success: '#10b981',
    error: '#ef4444',
    info: '#3b82f6',
  };

  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 2147483647;
    padding: 16px 20px;
    border-radius: 6px;
    color: white;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    max-width: 320px;
    word-wrap: break-word;
    background-color: ${colors[type]};
    opacity: 0;
    transform: translateX(100%);
    transition: all 0.3s ease;
    user-select: none;
    pointer-events: auto;
    cursor: ${clickUrl ? 'pointer' : 'default'};
  `;

  // Create notification content
  if (clickUrl) {
    const documentTitle = document.title || 'this page';
    const urlDomain = new URL(clickUrl).hostname;
    const displayText =
      documentTitle.length > 50 ? documentTitle.substring(0, 47) + '...' : documentTitle;

    notification.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 8px;">
        <div style="font-size: 13px; opacity: 0.9;">${message}</div>
        <div style="
          padding: 8px 12px;
          background: rgba(255, 255, 255, 0.15);
          border-radius: 4px;
          border: 1px solid rgba(255, 255, 255, 0.2);
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 6px;
          cursor: pointer;
        " onclick="window.open('${clickUrl}', '_blank')">
          <span style="font-size: 16px;">🔗</span>
          <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${displayText}</span>
        </div>
        <div style="font-size: 11px; opacity: 0.7; text-align: center;">
          Click to open • 
          <a href="${clickUrl}" 
             target="_blank" 
             rel="noopener noreferrer" 
             style="color: rgba(255, 255, 255, 0.9); text-decoration: underline; cursor: pointer;">
            ${urlDomain}
          </a>
        </div>
      </div>
    `;
  } else {
    notification.textContent = message;
  }

  // Add to DOM
  document.body.appendChild(notification);

  // Show notification with animation
  requestAnimationFrame(() => {
    notification.style.opacity = '1';
    notification.style.transform = 'translateX(0)';
  });

  // Auto-hide notification after specified duration
  if (duration > 0) {
    setTimeout(() => {
      hideNotification(notification);
    }, duration);
  }
}

// Helper function to hide notification
function hideNotification(notification: HTMLElement | null): void {
  if (notification && notification.parentNode) {
    // Smoothly fade out the notification
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100%)';
    notification.style.pointerEvents = 'none';

    // Remove the element after animation completes
    setTimeout(() => {
      if (notification && notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }
}
