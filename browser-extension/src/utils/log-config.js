// PrismWeave Logging Configuration
// Edit these values to control logging behavior across the extension

// Use global scope that works in both window and service worker contexts
(typeof window !== 'undefined' ? window : self).PRISMWEAVE_LOG_CONFIG = {
  // Global logging toggle - set to false to disable all logging
  enabled: true,
  
  // Logging level - controls what messages are shown
  // 0 = ERROR only
  // 1 = ERROR + WARN
  // 2 = ERROR + WARN + INFO
  // 3 = ERROR + WARN + INFO + DEBUG
  // 4 = ERROR + WARN + INFO + DEBUG + TRACE (very verbose)
  level: 3,
  
  // Component-specific overrides
  components: {
    // Enable/disable logging for specific components
    'Popup': { enabled: true, level: 3 },
    'Background': { enabled: true, level: 3 },
    'Content': { enabled: true, level: 2 },
    'Settings': { enabled: true, level: 2 },
    'Git': { enabled: true, level: 2 },
    'FileManager': { enabled: true, level: 2 },
    'MarkdownConverter': { enabled: true, level: 2 }
  }
};

// Apply global configuration
const globalScope = typeof window !== 'undefined' ? window : self;
if (globalScope.PrismWeaveLogger) {
  globalScope.PrismWeaveLogger.Logger.setGlobalEnabled(globalScope.PRISMWEAVE_LOG_CONFIG.enabled);
  globalScope.PrismWeaveLogger.Logger.setGlobalLevel(globalScope.PRISMWEAVE_LOG_CONFIG.level);
}

console.log('%c🔧 PrismWeave Logging Configuration Loaded', 'color: #4CAF50; font-weight: bold;');
console.log('Logging enabled:', globalScope.PRISMWEAVE_LOG_CONFIG.enabled);
console.log('Global log level:', globalScope.PRISMWEAVE_LOG_CONFIG.level);

// Quick commands for console debugging:
// 
// To disable all logging:
// (typeof window !== 'undefined' ? window : self).PRISMWEAVE_LOG_CONFIG.enabled = false;
//
// To enable verbose logging:
// (typeof window !== 'undefined' ? window : self).PRISMWEAVE_LOG_CONFIG.level = 4;
//
// To disable popup logging only:
// (typeof window !== 'undefined' ? window : self).PRISMWEAVE_LOG_CONFIG.components.Popup.enabled = false;
