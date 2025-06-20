// PrismWeave Utilities Registry
// Centralized utility management to eliminate duplication

class UtilsRegistry {
  constructor() {
    this.utilities = new Map();
    this.logger = null;
  }

  static getInstance() {
    if (!UtilsRegistry.instance) {
      UtilsRegistry.instance = new UtilsRegistry();
    }
    return UtilsRegistry.instance;
  }

  register(name, utility) {
    this.utilities.set(name, utility);
  }

  get(name) {
    return this.utilities.get(name);
  }

  getLogger(component) {
    if (!this.logger && window.PrismWeaveLogger) {
      this.logger = window.PrismWeaveLogger;
    }
    return this.logger?.createLogger(component) || this.createFallbackLogger();
  }

  createFallbackLogger() {
    return {
      debug: console.log,
      info: console.log,
      warn: console.warn,
      error: console.error,
      group: console.group,
      groupEnd: console.groupEnd
    };
  }
}

// Global registry instance
if (typeof window !== 'undefined') {
  window.PrismWeaveRegistry = UtilsRegistry.getInstance();
} else if (typeof self !== 'undefined') {
  self.PrismWeaveRegistry = UtilsRegistry.getInstance();
}
