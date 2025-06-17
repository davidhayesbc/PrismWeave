// PrismWeave Logging Utility
// Simple logging system with configurable levels and easy on/off toggle

class Logger {
  constructor(component = 'PrismWeave') {
    this.component = component;
    this.enabled = true; // Set to false to disable all logging
    this.level = Logger.LEVELS.DEBUG; // Minimum level to log
    this.styles = {
      error: 'color: #ff4444; font-weight: bold;',
      warn: 'color: #ffaa00; font-weight: bold;',
      info: 'color: #4444ff; font-weight: bold;',
      debug: 'color: #888888;',
      trace: 'color: #cccccc;'
    };
  }

  static LEVELS = {
    ERROR: 0,
    WARN: 1,
    INFO: 2,
    DEBUG: 3,
    TRACE: 4
  };

  static LEVEL_NAMES = ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'];

  _shouldLog(level) {
    return this.enabled && level <= this.level;
  }

  _formatMessage(level, message, ...args) {
    const levelName = Logger.LEVEL_NAMES[level];
    const timestamp = new Date().toISOString().substr(11, 12);
    const prefix = `[${timestamp}] [${this.component}] [${levelName}]`;
    
    if (typeof message === 'string') {
      return [`%c${prefix} ${message}`, this.styles[levelName.toLowerCase()], ...args];
    } else {
      return [`%c${prefix}`, this.styles[levelName.toLowerCase()], message, ...args];
    }
  }

  error(message, ...args) {
    if (this._shouldLog(Logger.LEVELS.ERROR)) {
      console.error(...this._formatMessage(Logger.LEVELS.ERROR, message, ...args));
    }
  }

  warn(message, ...args) {
    if (this._shouldLog(Logger.LEVELS.WARN)) {
      console.warn(...this._formatMessage(Logger.LEVELS.WARN, message, ...args));
    }
  }

  info(message, ...args) {
    if (this._shouldLog(Logger.LEVELS.INFO)) {
      console.info(...this._formatMessage(Logger.LEVELS.INFO, message, ...args));
    }
  }

  debug(message, ...args) {
    if (this._shouldLog(Logger.LEVELS.DEBUG)) {
      console.log(...this._formatMessage(Logger.LEVELS.DEBUG, message, ...args));
    }
  }

  trace(message, ...args) {
    if (this._shouldLog(Logger.LEVELS.TRACE)) {
      console.log(...this._formatMessage(Logger.LEVELS.TRACE, message, ...args));
    }
  }

  // Utility methods
  group(label, collapsed = false) {
    if (this.enabled) {
      if (collapsed) {
        console.groupCollapsed(`[${this.component}] ${label}`);
      } else {
        console.group(`[${this.component}] ${label}`);
      }
    }
  }

  groupEnd() {
    if (this.enabled) {
      console.groupEnd();
    }
  }

  table(data, columns) {
    if (this.enabled && this._shouldLog(Logger.LEVELS.DEBUG)) {
      console.table(data, columns);
    }
  }

  time(label) {
    if (this.enabled && this._shouldLog(Logger.LEVELS.DEBUG)) {
      console.time(`[${this.component}] ${label}`);
    }
  }

  timeEnd(label) {
    if (this.enabled && this._shouldLog(Logger.LEVELS.DEBUG)) {
      console.timeEnd(`[${this.component}] ${label}`);
    }
  }

  // Configuration methods
  setLevel(level) {
    this.level = level;
    this.info('Log level set to:', Logger.LEVEL_NAMES[level]);
  }

  enable() {
    this.enabled = true;
    console.log(`%c[${this.component}] Logging enabled`, this.styles.info);
  }
  disable() {
    console.log(`%c[${this.component}] Logging disabled`, this.styles.warn);
    this.enabled = false;
  }

  // Global configuration methods
  static setGlobalLevel(level) {
    const globalScope = typeof window !== 'undefined' ? window : self;
    globalScope.PRISMWEAVE_LOG_LEVEL = level;
  }

  static setGlobalEnabled(enabled) {
    const globalScope = typeof window !== 'undefined' ? window : self;
    globalScope.PRISMWEAVE_LOG_ENABLED = enabled;
  }
}

// Global logger factory
function createLogger(component) {
  const logger = new Logger(component);
  
  // Check for global overrides
  const globalScope = typeof window !== 'undefined' ? window : self;
  if (globalScope.PRISMWEAVE_LOG_ENABLED !== undefined) {
    logger.enabled = globalScope.PRISMWEAVE_LOG_ENABLED;
  }
  if (globalScope.PRISMWEAVE_LOG_LEVEL !== undefined) {
    logger.level = globalScope.PRISMWEAVE_LOG_LEVEL;
  }
  
  return logger;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { Logger, createLogger };
} else {
  // Use globalThis to work in both window and service worker contexts
  const globalScope = typeof window !== 'undefined' ? window : self;
  globalScope.PrismWeaveLogger = { Logger, createLogger };
}
