// TurndownService import for browser extension
// This file ensures TurndownService is available in the extension context

// Load TurndownService for browser extension use
(function() {
  if (typeof window !== 'undefined' && !window.TurndownService) {
    // For content scripts and popup context - use local file
    const script = document.createElement('script');
    script.src = chrome.runtime.getURL('src/libs/turndown.min.js');
    script.async = false; // Load synchronously to ensure availability
    document.head.appendChild(script);
  } else if (typeof self !== 'undefined' && typeof importScripts !== 'undefined' && !self.TurndownService) {
    // For service worker context - import local file
    try {
      importScripts('./libs/turndown.min.js');
    } catch (error) {
      console.warn('Could not load TurndownService in service worker:', error);
      // Service worker will fall back to enhanced conversion
    }
  }
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  try {
    module.exports = require('turndown');
  } catch (e) {
    // Fallback if turndown package not available
    module.exports = null;
  }
}
