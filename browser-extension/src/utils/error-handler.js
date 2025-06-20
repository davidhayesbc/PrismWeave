// PrismWeave Error Handler
// Centralized error handling with user-friendly messages

class ErrorHandler {
  static ERROR_TYPES = {
    NETWORK: 'network',
    AUTH: 'auth',
    PERMISSION: 'permission',
    CONTENT: 'content',
    STORAGE: 'storage',
    GITHUB: 'github'
  };

  static createUserFriendlyError(error, context = '') {
    const errorInfo = this.categorizeError(error);
    
    return {
      type: errorInfo.type,
      message: errorInfo.userMessage,
      details: error.message,
      solution: errorInfo.solution,
      context,
      originalError: error
    };
  }

  static categorizeError(error) {
    const message = error.message.toLowerCase();
    
    if (message.includes('token') || message.includes('unauthorized') || message.includes('401')) {
      return {
        type: this.ERROR_TYPES.AUTH,
        userMessage: 'Authentication failed. Please check your GitHub token.',
        solution: 'Go to Settings and verify your GitHub token is valid and has the necessary permissions.'
      };
    }
    
    if (message.includes('repository') || message.includes('repo')) {
      return {
        type: this.ERROR_TYPES.GITHUB,
        userMessage: 'Repository access failed.',
        solution: 'Verify the repository exists and you have write access. Check the repository name format (owner/repo).'
      };
    }
    
    if (message.includes('network') || message.includes('fetch') || message.includes('cors')) {
      return {
        type: this.ERROR_TYPES.NETWORK,
        userMessage: 'Network connection failed.',
        solution: 'Check your internet connection and try again.'
      };
    }
    
    if (message.includes('cannot access') || message.includes('permission')) {
      return {
        type: this.ERROR_TYPES.PERMISSION,
        userMessage: 'Cannot access this page.',
        solution: 'This page may be restricted. Try refreshing the page or navigating to a different website.'
      };
    }
    
    if (message.includes('extract') || message.includes('content')) {
      return {
        type: this.ERROR_TYPES.CONTENT,
        userMessage: 'Failed to extract page content.',
        solution: 'The page may not be fully loaded. Try refreshing and waiting for the page to load completely.'
      };
    }
    
    return {
      type: 'unknown',
      userMessage: 'An unexpected error occurred.',
      solution: 'Please try again. If the problem persists, check the extension settings.'
    };
  }

  static logError(error, context = '', logger = console) {
    const errorInfo = this.createUserFriendlyError(error, context);
    
    logger.error(`Error in ${context}:`, {
      type: errorInfo.type,
      message: errorInfo.message,
      details: errorInfo.details,
      solution: errorInfo.solution
    });
    
    return errorInfo;
  }
}

// Export for both browser and service worker contexts
if (typeof window !== 'undefined') {
  window.ErrorHandler = ErrorHandler;
} else if (typeof self !== 'undefined') {
  self.ErrorHandler = ErrorHandler;
}
