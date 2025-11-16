"use strict";
var contentextractorinjectable = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // src/injectable/content-extractor-injectable.ts
  var content_extractor_injectable_exports = {};
  __export(content_extractor_injectable_exports, {
    InjectableContentExtractor: () => InjectableContentExtractor
  });

  // src/utils/global-types.ts
  function getGlobalScope() {
    if (typeof window !== "undefined") {
      return window;
    }
    if (typeof self !== "undefined") {
      return self;
    }
    if (typeof global !== "undefined") {
      return global;
    }
    throw new Error("No global scope available");
  }

  // src/utils/logger.ts
  var _Logger = class _Logger {
    constructor(component = "PrismWeave") {
      this.enabled = false;
      this.level = 0;
      this.componentConfig = null;
      this.component = component;
      this.environment = this._detectEnvironment();
      this.componentConfig = this._getComponentConfig(component);
      this._initializeConfiguration();
      this.styles = {
        error: "color: #ff4444; font-weight: bold;",
        warn: "color: #ffaa00; font-weight: bold;",
        info: "color: #4444ff; font-weight: bold;",
        debug: "color: #888888;",
        trace: "color: #cccccc;"
      };
    }
    // Helper methods for common operations
    static isValidLevel(level) {
      return typeof level === "number" && level >= 0 && level <= 4;
    }
    static getGlobalScope() {
      return getGlobalScope();
    }
    _detectEnvironment() {
      if (this._isTestEnvironment()) {
        return "test";
      }
      if (this._isDevelopmentEnvironment()) {
        return "development";
      }
      return "production";
    }
    _isDevelopmentEnvironment() {
      try {
        return typeof process !== "undefined" && true || this._safeCheckChromeDevMode() || typeof window !== "undefined" && window.location?.hostname === "localhost" || typeof globalThis !== "undefined" && globalThis.PRISMWEAVE_DEV_MODE === true;
      } catch (error) {
        return false;
      }
    }
    _safeCheckChromeDevMode() {
      try {
        if (typeof chrome === "undefined" || !chrome.runtime) {
          return false;
        }
        if (chrome.runtime.lastError) {
          return false;
        }
        const manifest = chrome.runtime.getManifest();
        return manifest?.version?.includes("dev") || false;
      } catch (error) {
        return false;
      }
    }
    _getComponentConfig(componentName) {
      const config = _Logger.getGlobalScope().PRISMWEAVE_LOG_CONFIG;
      if (config?.components && typeof config.components === "object" && config.components[componentName]) {
        return config.components[componentName];
      }
      return null;
    }
    _initializeConfiguration() {
      const globalScope2 = _Logger.getGlobalScope();
      const globalConfig = globalScope2.PRISMWEAVE_LOG_CONFIG;
      const environmentDefaults = {
        test: { enabled: false, level: _Logger.LEVELS.ERROR },
        development: { enabled: true, level: _Logger.LEVELS.DEBUG },
        production: { enabled: true, level: _Logger.LEVELS.INFO }
      };
      const defaults = environmentDefaults[this.environment];
      this.enabled = defaults.enabled;
      this.level = defaults.level;
      this._applyGlobalConfig(globalConfig);
      this._applyComponentConfig();
      this._applyRuntimeOverrides(globalScope2);
    }
    _applyGlobalConfig(globalConfig) {
      if (globalConfig && typeof globalConfig.enabled === "boolean") {
        this.enabled = globalConfig.enabled;
      }
      if (globalConfig && _Logger.isValidLevel(globalConfig.level)) {
        this.level = globalConfig.level;
      }
    }
    _applyComponentConfig() {
      if (!this.componentConfig) return;
      if (typeof this.componentConfig.enabled === "boolean") {
        this.enabled = this.componentConfig.enabled;
      }
      if (_Logger.isValidLevel(this.componentConfig.level)) {
        this.level = this.componentConfig.level;
      }
    }
    _applyRuntimeOverrides(globalScope2) {
      if (typeof globalScope2.PRISMWEAVE_LOG_ENABLED === "boolean") {
        this.enabled = globalScope2.PRISMWEAVE_LOG_ENABLED;
      }
      if (_Logger.isValidLevel(globalScope2.PRISMWEAVE_LOG_LEVEL)) {
        this.level = globalScope2.PRISMWEAVE_LOG_LEVEL;
      }
    }
    _shouldLog(level) {
      return this.enabled && level <= this.level;
    }
    _isTestEnvironment() {
      return typeof process !== "undefined" && process.env.JEST_WORKER_ID !== void 0;
    }
    _formatMessage(level, message, ...args) {
      const levelName = _Logger.LEVEL_NAMES[level];
      const timestamp = (/* @__PURE__ */ new Date()).toISOString().substr(11, 12);
      const prefix = `[${timestamp}] [${this.component}] [${this.environment}] [${levelName}]`;
      if (typeof message === "string") {
        return [
          `%c${prefix} ${message}`,
          this.styles[levelName.toLowerCase()],
          ...args
        ];
      } else {
        return [
          `%c${prefix}`,
          this.styles[levelName.toLowerCase()],
          message,
          ...args
        ];
      }
    }
    _createStructuredLogData(level, message, ...args) {
      const context = {
        component: this.component,
        timestamp: (/* @__PURE__ */ new Date()).toISOString(),
        environment: this.environment
      };
      const levelName = _Logger.LEVEL_NAMES[level];
      let logMessage = "";
      let logData;
      let errorInfo;
      if (typeof message === "string") {
        logMessage = message;
        logData = args.length > 0 ? args : void 0;
      } else if (message instanceof Error) {
        logMessage = message.message;
        errorInfo = {
          name: message.name,
          message: message.message,
          ...message.stack && { stack: message.stack }
        };
        logData = args.length > 0 ? args : void 0;
      } else {
        logMessage = "Object logged";
        logData = [message, ...args];
      }
      const structuredData = {
        level: levelName,
        message: logMessage,
        context
      };
      if (logData) {
        structuredData.data = logData;
      }
      if (errorInfo) {
        structuredData.error = errorInfo;
      }
      return structuredData;
    }
    // Consolidated logging methods - eliminates duplication
    _log(level, consoleMethod, message, ...args) {
      if (this._shouldLog(level)) {
        const formatMethod = console[consoleMethod];
        formatMethod.apply(console, this._formatMessage(level, message, ...args));
        this._logStructured(level, message, ...args);
      }
    }
    error(message, ...args) {
      this._log(_Logger.LEVELS.ERROR, "error", message, ...args);
    }
    warn(message, ...args) {
      this._log(_Logger.LEVELS.WARN, "warn", message, ...args);
    }
    info(message, ...args) {
      this._log(_Logger.LEVELS.INFO, "info", message, ...args);
    }
    debug(message, ...args) {
      this._log(_Logger.LEVELS.DEBUG, "log", message, ...args);
    }
    trace(message, ...args) {
      this._log(_Logger.LEVELS.TRACE, "log", message, ...args);
    }
    // Structured logging methods
    _logStructured(level, message, ...args) {
      if (this.environment === "production" && this._shouldCollectStructuredLogs()) {
        const structuredData = this._createStructuredLogData(level, message, ...args);
        this._storeStructuredLog(structuredData);
      }
    }
    _shouldCollectStructuredLogs() {
      const config = _Logger.getGlobalScope().PRISMWEAVE_LOG_CONFIG;
      return config?.structuredLogging?.enabled === true;
    }
    _storeStructuredLog(data) {
      try {
        const globalScope2 = _Logger.getGlobalScope();
        if (!globalScope2.PRISMWEAVE_STRUCTURED_LOGS) {
          globalScope2.PRISMWEAVE_STRUCTURED_LOGS = [];
        }
        globalScope2.PRISMWEAVE_STRUCTURED_LOGS.push(data);
        if (globalScope2.PRISMWEAVE_STRUCTURED_LOGS.length > 100) {
          globalScope2.PRISMWEAVE_STRUCTURED_LOGS.shift();
        }
      } catch (error) {
      }
    }
    // Enhanced context logging
    withContext(contextData) {
      const contextLogger = new _Logger(this.component);
      contextLogger.enabled = this.enabled;
      contextLogger.level = this.level;
      contextLogger.environment = this.environment;
      contextLogger.componentConfig = this.componentConfig;
      contextLogger._contextData = contextData;
      return contextLogger;
    }
    // Consolidated timer methods to eliminate duplication
    _createTimerLabel(label) {
      return `[${this.component}] ${label}`;
    }
    time(label) {
      if (this.enabled && this._shouldLog(_Logger.LEVELS.DEBUG)) {
        console.time(this._createTimerLabel(label));
      }
    }
    timeEnd(label) {
      if (this.enabled && this._shouldLog(_Logger.LEVELS.DEBUG)) {
        console.timeEnd(this._createTimerLabel(label));
      }
    }
    timeWithContext(label, contextData) {
      if (this.enabled && this._shouldLog(_Logger.LEVELS.DEBUG)) {
        console.time(this._createTimerLabel(label));
        const message = `\u23F1\uFE0F Timer started: ${label}`;
        if (contextData) {
          this.debug(message, contextData);
        } else {
          this.debug(message);
        }
      }
    }
    timeEndWithContext(label, contextData) {
      if (this.enabled && this._shouldLog(_Logger.LEVELS.DEBUG)) {
        console.timeEnd(this._createTimerLabel(label));
        const message = `\u23F1\uFE0F Timer ended: ${label}`;
        if (contextData) {
          this.debug(message, contextData);
        } else {
          this.debug(message);
        }
      }
    }
    // Utility methods
    group(label, collapsed = false) {
      if (this.enabled) {
        const groupLabel = label ? `[${this.component}] ${label}` : `[${this.component}]`;
        if (collapsed) {
          console.groupCollapsed(groupLabel);
        } else {
          console.group(groupLabel);
        }
      }
    }
    groupEnd() {
      if (this.enabled) {
        console.groupEnd();
      }
    }
    table(data, columns) {
      if (this.enabled && this._shouldLog(_Logger.LEVELS.DEBUG)) {
        console.table(data, columns);
      }
    }
    // Configuration methods
    setLevel(level) {
      this.level = level;
      this.info("Log level set to:", _Logger.LEVEL_NAMES[level]);
    }
    setComponentLevel(component, level) {
      const globalScope2 = _Logger.getGlobalScope();
      if (!globalScope2.PRISMWEAVE_LOG_CONFIG) {
        globalScope2.PRISMWEAVE_LOG_CONFIG = {
          enabled: true,
          level: _Logger.LEVELS.INFO,
          components: {}
        };
      }
      if (!globalScope2.PRISMWEAVE_LOG_CONFIG.components) {
        globalScope2.PRISMWEAVE_LOG_CONFIG.components = {};
      }
      globalScope2.PRISMWEAVE_LOG_CONFIG.components[component] = {
        enabled: true,
        level
      };
      if (this.component === component) {
        this.level = level;
      }
      this.info(`Component '${component}' log level set to:`, _Logger.LEVEL_NAMES[level]);
    }
    enable() {
      this.enabled = true;
      console.log(`%c[${this.component}] [${this.environment}] Logging enabled`, this.styles.info);
    }
    disable() {
      console.log(`%c[${this.component}] [${this.environment}] Logging disabled`, this.styles.warn);
      this.enabled = false;
    }
    // Environment and configuration reporting
    getEnvironmentInfo() {
      return {
        component: this.component,
        environment: this.environment,
        enabled: this.enabled,
        level: this.level,
        levelName: _Logger.LEVEL_NAMES[this.level],
        componentConfig: this.componentConfig,
        timestamp: (/* @__PURE__ */ new Date()).toISOString()
      };
    }
    // Structured log retrieval
    static getStructuredLogs() {
      return _Logger.getGlobalScope().PRISMWEAVE_STRUCTURED_LOGS || [];
    }
    static clearStructuredLogs() {
      _Logger.getGlobalScope().PRISMWEAVE_STRUCTURED_LOGS = [];
    }
    // Global configuration methods
    static setGlobalLevel(level) {
      const globalScope2 = _Logger.getGlobalScope();
      globalScope2.PRISMWEAVE_LOG_LEVEL = level;
      console.log(
        `%cPrismWeave Global Log Level set to: ${_Logger.LEVEL_NAMES[level]}`,
        "color: #4444ff; font-weight: bold;"
      );
    }
    static setGlobalEnabled(enabled) {
      const globalScope2 = _Logger.getGlobalScope();
      globalScope2.PRISMWEAVE_LOG_ENABLED = enabled;
      console.log(
        `%cPrismWeave Global Logging ${enabled ? "enabled" : "disabled"}`,
        enabled ? "color: #44ff44; font-weight: bold;" : "color: #ff4444; font-weight: bold;"
      );
    }
    static setEnvironmentLogging(environment, enabled, level) {
      const globalScope2 = _Logger.getGlobalScope();
      if (!globalScope2.PRISMWEAVE_ENV_LOGGING) {
        globalScope2.PRISMWEAVE_ENV_LOGGING = {};
      }
      globalScope2.PRISMWEAVE_ENV_LOGGING[environment] = {
        enabled,
        level: level || _Logger.LEVELS.INFO
      };
      console.log(
        `%cEnvironment '${environment}' logging configured:`,
        "color: #8888ff; font-weight: bold;",
        {
          enabled,
          level: level ? _Logger.LEVEL_NAMES[level] : "INFO"
        }
      );
    }
    static getGlobalConfiguration() {
      const globalScope2 = _Logger.getGlobalScope();
      return {
        globalEnabled: globalScope2.PRISMWEAVE_LOG_ENABLED,
        globalLevel: globalScope2.PRISMWEAVE_LOG_LEVEL ? _Logger.LEVEL_NAMES[globalScope2.PRISMWEAVE_LOG_LEVEL] : void 0,
        config: globalScope2.PRISMWEAVE_LOG_CONFIG,
        environmentLogging: globalScope2.PRISMWEAVE_ENV_LOGGING,
        structuredLogsCount: globalScope2.PRISMWEAVE_STRUCTURED_LOGS?.length || 0
      };
    }
  };
  _Logger.LEVELS = {
    ERROR: 0,
    WARN: 1,
    INFO: 2,
    DEBUG: 3,
    TRACE: 4
  };
  _Logger.LEVEL_NAMES = ["ERROR", "WARN", "INFO", "DEBUG", "TRACE"];
  var Logger = _Logger;
  function createLogger(component) {
    const logger3 = new Logger(component);
    const globalScope2 = Logger.getGlobalScope();
    const envLogging = globalScope2.PRISMWEAVE_ENV_LOGGING?.[logger3.environment];
    if (envLogging) {
      if (typeof envLogging.enabled === "boolean") {
        logger3.enabled = envLogging.enabled;
      }
      if (Logger.isValidLevel(envLogging.level)) {
        logger3.level = envLogging.level;
      }
    }
    if (globalScope2.PRISMWEAVE_LOG_ENABLED !== void 0) {
      logger3.enabled = globalScope2.PRISMWEAVE_LOG_ENABLED;
    }
    if (globalScope2.PRISMWEAVE_LOG_LEVEL !== void 0) {
      logger3.level = globalScope2.PRISMWEAVE_LOG_LEVEL;
    }
    return logger3;
  }
  function enableDebugMode() {
    Logger.setGlobalEnabled(true);
    Logger.setGlobalLevel(Logger.LEVELS.DEBUG);
    console.log(
      "%cPrismWeave Debug Mode Enabled",
      "color: #00ff00; font-weight: bold; font-size: 14px;"
    );
    console.log("Available debug commands:", {
      "Logger.getGlobalConfiguration()": "Show current logging configuration",
      "Logger.setGlobalLevel(level)": "Set global log level (0-4)",
      "Logger.setGlobalEnabled(boolean)": "Enable/disable all logging",
      "Logger.getStructuredLogs()": "Get structured log data",
      "Logger.clearStructuredLogs()": "Clear structured log data"
    });
  }
  function disableDebugMode() {
    Logger.setGlobalEnabled(false);
    console.log("%cPrismWeave Debug Mode Disabled", "color: #ff0000; font-weight: bold;");
  }
  var globalScope = getGlobalScope();
  globalScope.PrismWeaveLogger = {
    createLogger,
    Logger,
    enableDebugMode,
    disableDebugMode
  };

  // src/utils/content-extraction-core.ts
  var ContentExtractionCore = class {
    constructor() {
      this.logger = createLogger("ContentExtractionCore");
    }
    /**
     * Extract content from the current page
     */
    async extractContent(options = {}) {
      try {
        this.logger.debug("Starting core content extraction");
        if (options.waitForDynamicContent !== false) {
          await this.waitForContent();
        }
        const metadata = this.extractMetadata();
        const mainContent = this.findMainContent(options);
        if (!mainContent) {
          throw new Error("No suitable content found on page");
        }
        const cleanedElement = this.cleanContent(mainContent, options);
        const content = cleanedElement.innerHTML;
        const cleanedContent = cleanedElement.textContent || "";
        const wordCount = this.countWords(cleanedContent);
        const readingTime = this.estimateReadingTime(wordCount);
        this.logger.debug("Content extraction completed", {
          wordCount,
          readingTime,
          contentLength: content.length
        });
        return {
          content,
          metadata: {
            ...metadata,
            wordCount,
            estimatedReadingTime: readingTime
          },
          cleanedContent,
          wordCount,
          readingTime
        };
      } catch (error) {
        this.logger.error("Content extraction failed:", error);
        throw error;
      }
    }
    /**
     * Extract page metadata with enhanced blog support
     */
    extractMetadata() {
      const wordCount = this.countWords(document.body.textContent || "");
      const metadata = {
        title: this.extractTitle(),
        url: window.location.href,
        captureDate: (/* @__PURE__ */ new Date()).toISOString(),
        tags: this.extractKeywords(),
        author: this.extractAuthor(),
        wordCount,
        estimatedReadingTime: this.estimateReadingTime(wordCount)
      };
      if (this.isBlogPage()) {
        const blogMetadata = this.extractBlogMetadata();
        if (blogMetadata.tags && blogMetadata.tags.length > 0) {
          const combinedTags = [...metadata.tags, ...blogMetadata.tags];
          metadata.tags = [...new Set(combinedTags)].slice(0, 10);
          delete blogMetadata.tags;
        }
        Object.assign(metadata, blogMetadata);
      }
      return metadata;
    }
    /**
     * Extract images from the page
     */
    extractImages() {
      const images = [];
      const imgElements = document.querySelectorAll("img");
      imgElements.forEach((img) => {
        const src = img.src || img.dataset.src;
        const alt = img.alt || "";
        if (src && !src.startsWith("data:") && src.length > 0) {
          try {
            const absoluteUrl = new URL(src, window.location.href).href;
            images.push({ src: absoluteUrl, alt });
          } catch (error) {
          }
        }
      });
      return images;
    }
    /**
     * Get page structure information
     */
    getPageStructure() {
      const headings = [];
      const headingElements = document.querySelectorAll("h1, h2, h3, h4, h5, h6");
      headingElements.forEach((heading) => {
        const level = parseInt(heading.tagName.charAt(1));
        const text = heading.textContent?.trim() || "";
        if (text) {
          headings.push({ level, text });
        }
      });
      const sections = document.querySelectorAll("section, article, main").length;
      const paragraphs = document.querySelectorAll("p").length;
      return { headings, sections, paragraphs };
    }
    /**
     * Calculate content quality score
     */
    getContentQualityScore() {
      const structure = this.getPageStructure();
      const textLength = document.body.textContent?.length || 0;
      const wordCount = this.countWords(document.body.textContent || "");
      let score = 0;
      if (textLength > 500) score += 20;
      if (textLength > 1500) score += 20;
      if (textLength > 3e3) score += 10;
      if (wordCount > 100) score += 15;
      if (wordCount > 500) score += 15;
      if (structure.headings.length > 0) score += 10;
      if (structure.headings.length > 2) score += 10;
      if (structure.paragraphs > 3) score += 10;
      const htmlLength = document.body.innerHTML?.length || 1;
      const density = textLength / htmlLength;
      score += density * 10;
      return Math.min(score, 100);
    }
    /**
     * Check if paywall is present
     */
    isPaywallPresent() {
      const paywallSelectors = [
        ".paywall",
        '[class*="paywall"]',
        ".subscription-required",
        ".premium-content",
        '[class*="subscription"]',
        '[id*="paywall"]'
      ];
      return paywallSelectors.some((selector) => document.querySelector(selector) !== null);
    }
    /**
     * Extract advanced metadata including structured data
     */
    extractAdvancedMetadata() {
      const metadata = {};
      document.querySelectorAll('[property^="og:"]').forEach((meta) => {
        const property = meta.getAttribute("property");
        const content = meta.getAttribute("content");
        if (property && content) {
          metadata[property] = content;
        }
      });
      document.querySelectorAll('[name^="twitter:"]').forEach((meta) => {
        const name = meta.getAttribute("name");
        const content = meta.getAttribute("content");
        if (name && content) {
          metadata[name] = content;
        }
      });
      const metaTags = ["description", "author", "generator", "theme-color"];
      metaTags.forEach((name) => {
        const meta = document.querySelector(`[name="${name}"]`);
        if (meta) {
          const content = meta.getAttribute("content");
          if (content) metadata[name] = content;
        }
      });
      const filteredKeywords = this.extractKeywords();
      if (filteredKeywords.length > 0) {
        metadata.keywords = filteredKeywords;
      }
      try {
        const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
        const structuredData = [];
        jsonLdScripts.forEach((script) => {
          try {
            const data = JSON.parse(script.textContent || "");
            if (data && typeof data === "object") {
              const cleanedData = { ...data };
              delete cleanedData.keywords;
              delete cleanedData.mentions;
              delete cleanedData.relatedLink;
              structuredData.push(cleanedData);
            } else {
              structuredData.push(data);
            }
          } catch (error) {
          }
        });
        if (structuredData.length > 0) {
          metadata.structuredData = structuredData;
        }
      } catch (error) {
      }
      metadata.url = window.location.href;
      metadata.domain = window.location.hostname;
      metadata.pathname = window.location.pathname;
      metadata.language = document.documentElement.lang || "en";
      metadata.extractedAt = (/* @__PURE__ */ new Date()).toISOString();
      return metadata;
    }
    // Private helper methods
    async waitForContent() {
      await new Promise((resolve) => setTimeout(resolve, 500));
      const images = Array.from(document.images);
      if (images.length > 0) {
        const imagePromises = images.map(
          (img) => new Promise((resolve) => {
            if (img.complete) {
              resolve(img);
            } else {
              img.addEventListener("load", () => resolve(img));
              img.addEventListener("error", () => resolve(img));
              setTimeout(() => resolve(img), 2e3);
            }
          })
        );
        await Promise.all(imagePromises);
      }
    }
    findMainContent(options) {
      if (options.customSelectors?.length) {
        for (const selector of options.customSelectors) {
          const element = document.querySelector(selector);
          if (element && this.hasSubstantialContent(element)) {
            return element;
          }
        }
      }
      const contentSelectors = [
        "article",
        "main",
        '[role="main"]',
        ".content",
        ".post-content",
        ".entry-content",
        ".article-content",
        "#content",
        "#main",
        ".post",
        ".entry"
      ];
      for (const selector of contentSelectors) {
        const element = document.querySelector(selector);
        if (element && this.hasSubstantialContent(element)) {
          return element;
        }
      }
      const candidates = Array.from(document.querySelectorAll("div, section, article"));
      let bestCandidate = null;
      for (const candidate of candidates) {
        if (this.hasSubstantialContent(candidate)) {
          const score = this.scoreElement(candidate);
          if (!bestCandidate || score > bestCandidate.score) {
            bestCandidate = { element: candidate, score };
          }
        }
      }
      return bestCandidate?.element || document.body;
    }
    hasSubstantialContent(element) {
      const textContent = element.textContent || "";
      const wordCount = this.countWords(textContent);
      return wordCount > 30;
    }
    scoreElement(element) {
      const text = element.textContent || "";
      const wordCount = this.countWords(text);
      let score = 0;
      score += Math.min(wordCount / 10, 50);
      const paragraphs = element.querySelectorAll("p").length;
      score += paragraphs * 2;
      const links = element.querySelectorAll("a").length;
      const linkDensity = links / Math.max(wordCount, 1);
      if (linkDensity > 0.3) score -= 20;
      const tagName = element.tagName.toLowerCase();
      if (tagName === "article") score += 15;
      if (tagName === "main") score += 10;
      const className = element.className.toLowerCase();
      if (className.includes("content")) score += 10;
      if (className.includes("post")) score += 8;
      if (className.includes("article")) score += 8;
      if (className.includes("sidebar")) score -= 10;
      if (className.includes("footer")) score -= 10;
      if (className.includes("header")) score -= 10;
      if (className.includes("nav")) score -= 15;
      return Math.max(score, 0);
    }
    cleanContent(element, options) {
      const cloned = element.cloneNode(true);
      const defaultExcludeSelectors = [
        "script",
        "style",
        "noscript",
        "iframe",
        ".advertisement",
        ".ad",
        ".ads",
        ".popup",
        ".modal",
        ".social-share",
        ".comments",
        ".related-posts",
        '[style*="display: none"]',
        '[style*="visibility: hidden"]'
      ];
      const excludeSelectors = [...defaultExcludeSelectors, ...options.excludeSelectors || []];
      excludeSelectors.forEach((selector) => {
        const elements = cloned.querySelectorAll(selector);
        elements.forEach((el) => el.remove());
      });
      if (options.removeAds !== false) {
        this.removeAds(cloned);
      }
      if (options.removeNavigation !== false) {
        this.removeNavigation(cloned);
      }
      return cloned;
    }
    removeAds(element) {
      const adSelectors = [
        '[class*="ad"]',
        '[id*="ad"]',
        '[class*="banner"]',
        '[id*="banner"]',
        '[class*="promo"]',
        '[id*="promo"]',
        '[class*="sponsor"]',
        '[id*="sponsor"]'
      ];
      adSelectors.forEach((selector) => {
        const elements = element.querySelectorAll(selector);
        elements.forEach((el) => {
          const text = el.textContent || "";
          const wordCount = this.countWords(text);
          if (wordCount < 10 || this.hasAdCharacteristics(el)) {
            el.remove();
          }
        });
      });
    }
    hasAdCharacteristics(element) {
      const className = element.className.toLowerCase();
      const id = element.id.toLowerCase();
      const adPatterns = [
        "advertisement",
        "google-ad",
        "adsense",
        "ad-banner",
        "ad-container",
        "ad-wrapper",
        "sponsored",
        "promo-box"
      ];
      return adPatterns.some((pattern) => className.includes(pattern) || id.includes(pattern));
    }
    removeNavigation(element) {
      const navSelectors = [
        "nav",
        "header",
        "footer",
        '[role="navigation"]',
        '[role="banner"]',
        '[role="contentinfo"]',
        ".navigation",
        ".nav",
        ".menu",
        ".breadcrumb"
      ];
      navSelectors.forEach((selector) => {
        const elements = element.querySelectorAll(selector);
        elements.forEach((el) => el.remove());
      });
    }
    extractTitle() {
      const titleSources = [
        () => document.querySelector('[property="og:title"]')?.getAttribute("content"),
        () => document.querySelector('[name="twitter:title"]')?.getAttribute("content"),
        () => document.querySelector("h1")?.textContent,
        () => document.title
      ];
      for (const source of titleSources) {
        const title = source();
        if (title && title.trim().length > 0) {
          return title.trim();
        }
      }
      return "Untitled";
    }
    extractDescription() {
      const descSources = [
        () => document.querySelector('[property="og:description"]')?.getAttribute("content"),
        () => document.querySelector('[name="twitter:description"]')?.getAttribute("content"),
        () => document.querySelector('[name="description"]')?.getAttribute("content")
      ];
      for (const source of descSources) {
        const desc = source();
        if (desc && desc.trim().length > 0) {
          return desc.trim();
        }
      }
      return "";
    }
    extractKeywords() {
      const keywordsMeta = document.querySelector('[name="keywords"]')?.getAttribute("content");
      if (keywordsMeta) {
        return keywordsMeta.split(/[,;|]/).map((keyword) => keyword.trim().toLowerCase()).filter((keyword) => {
          if (keyword.length < 2 || keyword.length > 30) return false;
          if (keyword.split(/\s+/).length > 4) return false;
          if (keyword.includes("http") || keyword.includes("www.")) return false;
          return true;
        }).slice(0, 10);
      }
      return [];
    }
    extractAuthor() {
      const authorSources = [
        () => document.querySelector('[property="article:author"]')?.getAttribute("content"),
        () => document.querySelector('[name="author"]')?.getAttribute("content"),
        () => document.querySelector('[rel="author"]')?.textContent,
        () => document.querySelector(".author")?.textContent,
        () => document.querySelector(".byline")?.textContent,
        () => document.querySelector('[class*="author"]')?.textContent,
        () => document.querySelector(".post-author")?.textContent
      ];
      for (const source of authorSources) {
        const author = source();
        if (author && author.trim().length > 0) {
          return author.trim();
        }
      }
      return "";
    }
    extractPublishedDate() {
      const dateSources = [
        () => document.querySelector('[property="article:published_time"]')?.getAttribute("content"),
        () => document.querySelector('[name="publish_date"]')?.getAttribute("content"),
        () => document.querySelector("time[datetime]")?.getAttribute("datetime"),
        () => document.querySelector(".publish-date")?.textContent,
        () => document.querySelector(".date")?.textContent,
        () => document.querySelector(".published")?.textContent,
        () => document.querySelector('[class*="date"]')?.textContent
      ];
      for (const source of dateSources) {
        const date = source();
        if (date && date.trim().length > 0) {
          return date.trim();
        }
      }
      return "";
    }
    extractLanguage() {
      return document.documentElement.lang || document.querySelector('[property="og:locale"]')?.getAttribute("content") || "en";
    }
    /**
     * Check if current page appears to be a blog post
     */
    isBlogPage() {
      const url = window.location.href.toLowerCase();
      const hostname = window.location.hostname.toLowerCase();
      const blogUrlPatterns = [
        /\/blog\//,
        /\/posts?\//,
        /\/\d{4}\/\d{2}\/\d{2}\//,
        /\/\d{4}\/\d{2}\//,
        /\/article\//,
        /\/news\//
      ];
      if (blogUrlPatterns.some((pattern) => pattern.test(url))) {
        return true;
      }
      const blogHostnames = [
        "blog.",
        ".blog",
        "medium.com",
        "dev.to",
        "hashnode.dev",
        "substack.com",
        "ghost.io"
      ];
      if (blogHostnames.some((host) => hostname.includes(host))) {
        return true;
      }
      const blogSelectors = [
        ".post",
        ".entry",
        ".article",
        '[class*="post"]',
        '[class*="entry"]',
        '[class*="article"]',
        ".blog-post",
        ".news-article"
      ];
      const hasBlogElements = blogSelectors.some((selector) => {
        const elements = document.querySelectorAll(selector);
        return Array.from(elements).some((el) => {
          const wordCount = this.countWords(el.textContent || "");
          return wordCount > 50;
        });
      });
      return hasBlogElements;
    }
    /**
     * Extract blog-specific metadata
     */
    extractBlogMetadata() {
      const blogMetadata = {};
      const tags = this.extractTags();
      if (tags.length > 0) {
        blogMetadata.tags = tags;
      }
      const wordCount = this.countWords(document.body.textContent || "");
      blogMetadata.estimatedReadingTime = this.estimateReadingTime(wordCount);
      return blogMetadata;
    }
    /**
     * Extract tags from blog pages
     */
    extractTags() {
      const tags = [];
      const tagSelectors = [
        ".tags a",
        ".tag",
        ".post-tags a",
        '[class*="tag"] a',
        ".categories a",
        ".category",
        '[rel="tag"]'
      ];
      tagSelectors.forEach((selector) => {
        const elements = document.querySelectorAll(selector);
        elements.forEach((el) => {
          const tagText = el.textContent?.trim().toLowerCase();
          if (tagText) {
            if (tagText.length < 2 || tagText.length > 30) return;
            if (tagText.split(/\s+/).length > 4) return;
            if (tagText.includes("http") || tagText.includes("www.")) return;
            if (tagText.includes("click to") || tagText.includes("share on")) return;
            if (tagText.match(/^\d+\s+(comment|view|share|like)/i)) return;
            if (tagText.match(/^(print|email|share|comment|#\w+)$/i)) return;
            tags.push(tagText);
          }
        });
      });
      return [...new Set(tags)].slice(0, 10);
    }
    countWords(text) {
      return text.split(/\s+/).filter((word) => word.length > 0).length;
    }
    estimateReadingTime(wordCount) {
      return Math.ceil(wordCount / 200);
    }
  };

  // ../node_modules/turndown/lib/turndown.browser.es.js
  function extend(destination) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];
      for (var key in source) {
        if (source.hasOwnProperty(key)) destination[key] = source[key];
      }
    }
    return destination;
  }
  function repeat(character, count) {
    return Array(count + 1).join(character);
  }
  function trimLeadingNewlines(string) {
    return string.replace(/^\n*/, "");
  }
  function trimTrailingNewlines(string) {
    var indexEnd = string.length;
    while (indexEnd > 0 && string[indexEnd - 1] === "\n") indexEnd--;
    return string.substring(0, indexEnd);
  }
  var blockElements = [
    "ADDRESS",
    "ARTICLE",
    "ASIDE",
    "AUDIO",
    "BLOCKQUOTE",
    "BODY",
    "CANVAS",
    "CENTER",
    "DD",
    "DIR",
    "DIV",
    "DL",
    "DT",
    "FIELDSET",
    "FIGCAPTION",
    "FIGURE",
    "FOOTER",
    "FORM",
    "FRAMESET",
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "HEADER",
    "HGROUP",
    "HR",
    "HTML",
    "ISINDEX",
    "LI",
    "MAIN",
    "MENU",
    "NAV",
    "NOFRAMES",
    "NOSCRIPT",
    "OL",
    "OUTPUT",
    "P",
    "PRE",
    "SECTION",
    "TABLE",
    "TBODY",
    "TD",
    "TFOOT",
    "TH",
    "THEAD",
    "TR",
    "UL"
  ];
  function isBlock(node) {
    return is(node, blockElements);
  }
  var voidElements = [
    "AREA",
    "BASE",
    "BR",
    "COL",
    "COMMAND",
    "EMBED",
    "HR",
    "IMG",
    "INPUT",
    "KEYGEN",
    "LINK",
    "META",
    "PARAM",
    "SOURCE",
    "TRACK",
    "WBR"
  ];
  function isVoid(node) {
    return is(node, voidElements);
  }
  function hasVoid(node) {
    return has(node, voidElements);
  }
  var meaningfulWhenBlankElements = [
    "A",
    "TABLE",
    "THEAD",
    "TBODY",
    "TFOOT",
    "TH",
    "TD",
    "IFRAME",
    "SCRIPT",
    "AUDIO",
    "VIDEO"
  ];
  function isMeaningfulWhenBlank(node) {
    return is(node, meaningfulWhenBlankElements);
  }
  function hasMeaningfulWhenBlank(node) {
    return has(node, meaningfulWhenBlankElements);
  }
  function is(node, tagNames) {
    return tagNames.indexOf(node.nodeName) >= 0;
  }
  function has(node, tagNames) {
    return node.getElementsByTagName && tagNames.some(function(tagName) {
      return node.getElementsByTagName(tagName).length;
    });
  }
  var rules = {};
  rules.paragraph = {
    filter: "p",
    replacement: function(content) {
      return "\n\n" + content + "\n\n";
    }
  };
  rules.lineBreak = {
    filter: "br",
    replacement: function(content, node, options) {
      return options.br + "\n";
    }
  };
  rules.heading = {
    filter: ["h1", "h2", "h3", "h4", "h5", "h6"],
    replacement: function(content, node, options) {
      var hLevel = Number(node.nodeName.charAt(1));
      if (options.headingStyle === "setext" && hLevel < 3) {
        var underline = repeat(hLevel === 1 ? "=" : "-", content.length);
        return "\n\n" + content + "\n" + underline + "\n\n";
      } else {
        return "\n\n" + repeat("#", hLevel) + " " + content + "\n\n";
      }
    }
  };
  rules.blockquote = {
    filter: "blockquote",
    replacement: function(content) {
      content = content.replace(/^\n+|\n+$/g, "");
      content = content.replace(/^/gm, "> ");
      return "\n\n" + content + "\n\n";
    }
  };
  rules.list = {
    filter: ["ul", "ol"],
    replacement: function(content, node) {
      var parent = node.parentNode;
      if (parent.nodeName === "LI" && parent.lastElementChild === node) {
        return "\n" + content;
      } else {
        return "\n\n" + content + "\n\n";
      }
    }
  };
  rules.listItem = {
    filter: "li",
    replacement: function(content, node, options) {
      var prefix = options.bulletListMarker + "   ";
      var parent = node.parentNode;
      if (parent.nodeName === "OL") {
        var start = parent.getAttribute("start");
        var index = Array.prototype.indexOf.call(parent.children, node);
        prefix = (start ? Number(start) + index : index + 1) + ".  ";
      }
      content = content.replace(/^\n+/, "").replace(/\n+$/, "\n").replace(/\n/gm, "\n" + " ".repeat(prefix.length));
      return prefix + content + (node.nextSibling && !/\n$/.test(content) ? "\n" : "");
    }
  };
  rules.indentedCodeBlock = {
    filter: function(node, options) {
      return options.codeBlockStyle === "indented" && node.nodeName === "PRE" && node.firstChild && node.firstChild.nodeName === "CODE";
    },
    replacement: function(content, node, options) {
      return "\n\n    " + node.firstChild.textContent.replace(/\n/g, "\n    ") + "\n\n";
    }
  };
  rules.fencedCodeBlock = {
    filter: function(node, options) {
      return options.codeBlockStyle === "fenced" && node.nodeName === "PRE" && node.firstChild && node.firstChild.nodeName === "CODE";
    },
    replacement: function(content, node, options) {
      var className = node.firstChild.getAttribute("class") || "";
      var language = (className.match(/language-(\S+)/) || [null, ""])[1];
      var code = node.firstChild.textContent;
      var fenceChar = options.fence.charAt(0);
      var fenceSize = 3;
      var fenceInCodeRegex = new RegExp("^" + fenceChar + "{3,}", "gm");
      var match;
      while (match = fenceInCodeRegex.exec(code)) {
        if (match[0].length >= fenceSize) {
          fenceSize = match[0].length + 1;
        }
      }
      var fence = repeat(fenceChar, fenceSize);
      return "\n\n" + fence + language + "\n" + code.replace(/\n$/, "") + "\n" + fence + "\n\n";
    }
  };
  rules.horizontalRule = {
    filter: "hr",
    replacement: function(content, node, options) {
      return "\n\n" + options.hr + "\n\n";
    }
  };
  rules.inlineLink = {
    filter: function(node, options) {
      return options.linkStyle === "inlined" && node.nodeName === "A" && node.getAttribute("href");
    },
    replacement: function(content, node) {
      var href = node.getAttribute("href");
      if (href) href = href.replace(/([()])/g, "\\$1");
      var title = cleanAttribute(node.getAttribute("title"));
      if (title) title = ' "' + title.replace(/"/g, '\\"') + '"';
      return "[" + content + "](" + href + title + ")";
    }
  };
  rules.referenceLink = {
    filter: function(node, options) {
      return options.linkStyle === "referenced" && node.nodeName === "A" && node.getAttribute("href");
    },
    replacement: function(content, node, options) {
      var href = node.getAttribute("href");
      var title = cleanAttribute(node.getAttribute("title"));
      if (title) title = ' "' + title + '"';
      var replacement;
      var reference;
      switch (options.linkReferenceStyle) {
        case "collapsed":
          replacement = "[" + content + "][]";
          reference = "[" + content + "]: " + href + title;
          break;
        case "shortcut":
          replacement = "[" + content + "]";
          reference = "[" + content + "]: " + href + title;
          break;
        default:
          var id = this.references.length + 1;
          replacement = "[" + content + "][" + id + "]";
          reference = "[" + id + "]: " + href + title;
      }
      this.references.push(reference);
      return replacement;
    },
    references: [],
    append: function(options) {
      var references = "";
      if (this.references.length) {
        references = "\n\n" + this.references.join("\n") + "\n\n";
        this.references = [];
      }
      return references;
    }
  };
  rules.emphasis = {
    filter: ["em", "i"],
    replacement: function(content, node, options) {
      if (!content.trim()) return "";
      return options.emDelimiter + content + options.emDelimiter;
    }
  };
  rules.strong = {
    filter: ["strong", "b"],
    replacement: function(content, node, options) {
      if (!content.trim()) return "";
      return options.strongDelimiter + content + options.strongDelimiter;
    }
  };
  rules.code = {
    filter: function(node) {
      var hasSiblings = node.previousSibling || node.nextSibling;
      var isCodeBlock = node.parentNode.nodeName === "PRE" && !hasSiblings;
      return node.nodeName === "CODE" && !isCodeBlock;
    },
    replacement: function(content) {
      if (!content) return "";
      content = content.replace(/\r?\n|\r/g, " ");
      var extraSpace = /^`|^ .*?[^ ].* $|`$/.test(content) ? " " : "";
      var delimiter = "`";
      var matches = content.match(/`+/gm) || [];
      while (matches.indexOf(delimiter) !== -1) delimiter = delimiter + "`";
      return delimiter + extraSpace + content + extraSpace + delimiter;
    }
  };
  rules.image = {
    filter: "img",
    replacement: function(content, node) {
      var alt = cleanAttribute(node.getAttribute("alt"));
      var src = node.getAttribute("src") || "";
      var title = cleanAttribute(node.getAttribute("title"));
      var titlePart = title ? ' "' + title + '"' : "";
      return src ? "![" + alt + "](" + src + titlePart + ")" : "";
    }
  };
  function cleanAttribute(attribute) {
    return attribute ? attribute.replace(/(\n+\s*)+/g, "\n") : "";
  }
  function Rules(options) {
    this.options = options;
    this._keep = [];
    this._remove = [];
    this.blankRule = {
      replacement: options.blankReplacement
    };
    this.keepReplacement = options.keepReplacement;
    this.defaultRule = {
      replacement: options.defaultReplacement
    };
    this.array = [];
    for (var key in options.rules) this.array.push(options.rules[key]);
  }
  Rules.prototype = {
    add: function(key, rule) {
      this.array.unshift(rule);
    },
    keep: function(filter) {
      this._keep.unshift({
        filter,
        replacement: this.keepReplacement
      });
    },
    remove: function(filter) {
      this._remove.unshift({
        filter,
        replacement: function() {
          return "";
        }
      });
    },
    forNode: function(node) {
      if (node.isBlank) return this.blankRule;
      var rule;
      if (rule = findRule(this.array, node, this.options)) return rule;
      if (rule = findRule(this._keep, node, this.options)) return rule;
      if (rule = findRule(this._remove, node, this.options)) return rule;
      return this.defaultRule;
    },
    forEach: function(fn) {
      for (var i = 0; i < this.array.length; i++) fn(this.array[i], i);
    }
  };
  function findRule(rules2, node, options) {
    for (var i = 0; i < rules2.length; i++) {
      var rule = rules2[i];
      if (filterValue(rule, node, options)) return rule;
    }
    return void 0;
  }
  function filterValue(rule, node, options) {
    var filter = rule.filter;
    if (typeof filter === "string") {
      if (filter === node.nodeName.toLowerCase()) return true;
    } else if (Array.isArray(filter)) {
      if (filter.indexOf(node.nodeName.toLowerCase()) > -1) return true;
    } else if (typeof filter === "function") {
      if (filter.call(rule, node, options)) return true;
    } else {
      throw new TypeError("`filter` needs to be a string, array, or function");
    }
  }
  function collapseWhitespace(options) {
    var element = options.element;
    var isBlock2 = options.isBlock;
    var isVoid2 = options.isVoid;
    var isPre = options.isPre || function(node2) {
      return node2.nodeName === "PRE";
    };
    if (!element.firstChild || isPre(element)) return;
    var prevText = null;
    var keepLeadingWs = false;
    var prev = null;
    var node = next(prev, element, isPre);
    while (node !== element) {
      if (node.nodeType === 3 || node.nodeType === 4) {
        var text = node.data.replace(/[ \r\n\t]+/g, " ");
        if ((!prevText || / $/.test(prevText.data)) && !keepLeadingWs && text[0] === " ") {
          text = text.substr(1);
        }
        if (!text) {
          node = remove(node);
          continue;
        }
        node.data = text;
        prevText = node;
      } else if (node.nodeType === 1) {
        if (isBlock2(node) || node.nodeName === "BR") {
          if (prevText) {
            prevText.data = prevText.data.replace(/ $/, "");
          }
          prevText = null;
          keepLeadingWs = false;
        } else if (isVoid2(node) || isPre(node)) {
          prevText = null;
          keepLeadingWs = true;
        } else if (prevText) {
          keepLeadingWs = false;
        }
      } else {
        node = remove(node);
        continue;
      }
      var nextNode = next(prev, node, isPre);
      prev = node;
      node = nextNode;
    }
    if (prevText) {
      prevText.data = prevText.data.replace(/ $/, "");
      if (!prevText.data) {
        remove(prevText);
      }
    }
  }
  function remove(node) {
    var next2 = node.nextSibling || node.parentNode;
    node.parentNode.removeChild(node);
    return next2;
  }
  function next(prev, current, isPre) {
    if (prev && prev.parentNode === current || isPre(current)) {
      return current.nextSibling || current.parentNode;
    }
    return current.firstChild || current.nextSibling || current.parentNode;
  }
  var root = typeof window !== "undefined" ? window : {};
  function canParseHTMLNatively() {
    var Parser = root.DOMParser;
    var canParse = false;
    try {
      if (new Parser().parseFromString("", "text/html")) {
        canParse = true;
      }
    } catch (e) {
    }
    return canParse;
  }
  function createHTMLParser() {
    var Parser = function() {
    };
    {
      if (shouldUseActiveX()) {
        Parser.prototype.parseFromString = function(string) {
          var doc = new window.ActiveXObject("htmlfile");
          doc.designMode = "on";
          doc.open();
          doc.write(string);
          doc.close();
          return doc;
        };
      } else {
        Parser.prototype.parseFromString = function(string) {
          var doc = document.implementation.createHTMLDocument("");
          doc.open();
          doc.write(string);
          doc.close();
          return doc;
        };
      }
    }
    return Parser;
  }
  function shouldUseActiveX() {
    var useActiveX = false;
    try {
      document.implementation.createHTMLDocument("").open();
    } catch (e) {
      if (root.ActiveXObject) useActiveX = true;
    }
    return useActiveX;
  }
  var HTMLParser = canParseHTMLNatively() ? root.DOMParser : createHTMLParser();
  function RootNode(input, options) {
    var root2;
    if (typeof input === "string") {
      var doc = htmlParser().parseFromString(
        // DOM parsers arrange elements in the <head> and <body>.
        // Wrapping in a custom element ensures elements are reliably arranged in
        // a single element.
        '<x-turndown id="turndown-root">' + input + "</x-turndown>",
        "text/html"
      );
      root2 = doc.getElementById("turndown-root");
    } else {
      root2 = input.cloneNode(true);
    }
    collapseWhitespace({
      element: root2,
      isBlock,
      isVoid,
      isPre: options.preformattedCode ? isPreOrCode : null
    });
    return root2;
  }
  var _htmlParser;
  function htmlParser() {
    _htmlParser = _htmlParser || new HTMLParser();
    return _htmlParser;
  }
  function isPreOrCode(node) {
    return node.nodeName === "PRE" || node.nodeName === "CODE";
  }
  function Node(node, options) {
    node.isBlock = isBlock(node);
    node.isCode = node.nodeName === "CODE" || node.parentNode.isCode;
    node.isBlank = isBlank(node);
    node.flankingWhitespace = flankingWhitespace(node, options);
    return node;
  }
  function isBlank(node) {
    return !isVoid(node) && !isMeaningfulWhenBlank(node) && /^\s*$/i.test(node.textContent) && !hasVoid(node) && !hasMeaningfulWhenBlank(node);
  }
  function flankingWhitespace(node, options) {
    if (node.isBlock || options.preformattedCode && node.isCode) {
      return { leading: "", trailing: "" };
    }
    var edges = edgeWhitespace(node.textContent);
    if (edges.leadingAscii && isFlankedByWhitespace("left", node, options)) {
      edges.leading = edges.leadingNonAscii;
    }
    if (edges.trailingAscii && isFlankedByWhitespace("right", node, options)) {
      edges.trailing = edges.trailingNonAscii;
    }
    return { leading: edges.leading, trailing: edges.trailing };
  }
  function edgeWhitespace(string) {
    var m = string.match(/^(([ \t\r\n]*)(\s*))(?:(?=\S)[\s\S]*\S)?((\s*?)([ \t\r\n]*))$/);
    return {
      leading: m[1],
      // whole string for whitespace-only strings
      leadingAscii: m[2],
      leadingNonAscii: m[3],
      trailing: m[4],
      // empty for whitespace-only strings
      trailingNonAscii: m[5],
      trailingAscii: m[6]
    };
  }
  function isFlankedByWhitespace(side, node, options) {
    var sibling;
    var regExp;
    var isFlanked;
    if (side === "left") {
      sibling = node.previousSibling;
      regExp = / $/;
    } else {
      sibling = node.nextSibling;
      regExp = /^ /;
    }
    if (sibling) {
      if (sibling.nodeType === 3) {
        isFlanked = regExp.test(sibling.nodeValue);
      } else if (options.preformattedCode && sibling.nodeName === "CODE") {
        isFlanked = false;
      } else if (sibling.nodeType === 1 && !isBlock(sibling)) {
        isFlanked = regExp.test(sibling.textContent);
      }
    }
    return isFlanked;
  }
  var reduce = Array.prototype.reduce;
  var escapes = [
    [/\\/g, "\\\\"],
    [/\*/g, "\\*"],
    [/^-/g, "\\-"],
    [/^\+ /g, "\\+ "],
    [/^(=+)/g, "\\$1"],
    [/^(#{1,6}) /g, "\\$1 "],
    [/`/g, "\\`"],
    [/^~~~/g, "\\~~~"],
    [/\[/g, "\\["],
    [/\]/g, "\\]"],
    [/^>/g, "\\>"],
    [/_/g, "\\_"],
    [/^(\d+)\. /g, "$1\\. "]
  ];
  function TurndownService(options) {
    if (!(this instanceof TurndownService)) return new TurndownService(options);
    var defaults = {
      rules,
      headingStyle: "setext",
      hr: "* * *",
      bulletListMarker: "*",
      codeBlockStyle: "indented",
      fence: "```",
      emDelimiter: "_",
      strongDelimiter: "**",
      linkStyle: "inlined",
      linkReferenceStyle: "full",
      br: "  ",
      preformattedCode: false,
      blankReplacement: function(content, node) {
        return node.isBlock ? "\n\n" : "";
      },
      keepReplacement: function(content, node) {
        return node.isBlock ? "\n\n" + node.outerHTML + "\n\n" : node.outerHTML;
      },
      defaultReplacement: function(content, node) {
        return node.isBlock ? "\n\n" + content + "\n\n" : content;
      }
    };
    this.options = extend({}, defaults, options);
    this.rules = new Rules(this.options);
  }
  TurndownService.prototype = {
    /**
     * The entry point for converting a string or DOM node to Markdown
     * @public
     * @param {String|HTMLElement} input The string or DOM node to convert
     * @returns A Markdown representation of the input
     * @type String
     */
    turndown: function(input) {
      if (!canConvert(input)) {
        throw new TypeError(
          input + " is not a string, or an element/document/fragment node."
        );
      }
      if (input === "") return "";
      var output = process2.call(this, new RootNode(input, this.options));
      return postProcess.call(this, output);
    },
    /**
     * Add one or more plugins
     * @public
     * @param {Function|Array} plugin The plugin or array of plugins to add
     * @returns The Turndown instance for chaining
     * @type Object
     */
    use: function(plugin) {
      if (Array.isArray(plugin)) {
        for (var i = 0; i < plugin.length; i++) this.use(plugin[i]);
      } else if (typeof plugin === "function") {
        plugin(this);
      } else {
        throw new TypeError("plugin must be a Function or an Array of Functions");
      }
      return this;
    },
    /**
     * Adds a rule
     * @public
     * @param {String} key The unique key of the rule
     * @param {Object} rule The rule
     * @returns The Turndown instance for chaining
     * @type Object
     */
    addRule: function(key, rule) {
      this.rules.add(key, rule);
      return this;
    },
    /**
     * Keep a node (as HTML) that matches the filter
     * @public
     * @param {String|Array|Function} filter The unique key of the rule
     * @returns The Turndown instance for chaining
     * @type Object
     */
    keep: function(filter) {
      this.rules.keep(filter);
      return this;
    },
    /**
     * Remove a node that matches the filter
     * @public
     * @param {String|Array|Function} filter The unique key of the rule
     * @returns The Turndown instance for chaining
     * @type Object
     */
    remove: function(filter) {
      this.rules.remove(filter);
      return this;
    },
    /**
     * Escapes Markdown syntax
     * @public
     * @param {String} string The string to escape
     * @returns A string with Markdown syntax escaped
     * @type String
     */
    escape: function(string) {
      return escapes.reduce(function(accumulator, escape) {
        return accumulator.replace(escape[0], escape[1]);
      }, string);
    }
  };
  function process2(parentNode) {
    var self2 = this;
    return reduce.call(parentNode.childNodes, function(output, node) {
      node = new Node(node, self2.options);
      var replacement = "";
      if (node.nodeType === 3) {
        replacement = node.isCode ? node.nodeValue : self2.escape(node.nodeValue);
      } else if (node.nodeType === 1) {
        replacement = replacementForNode.call(self2, node);
      }
      return join(output, replacement);
    }, "");
  }
  function postProcess(output) {
    var self2 = this;
    this.rules.forEach(function(rule) {
      if (typeof rule.append === "function") {
        output = join(output, rule.append(self2.options));
      }
    });
    return output.replace(/^[\t\r\n]+/, "").replace(/[\t\r\n\s]+$/, "");
  }
  function replacementForNode(node) {
    var rule = this.rules.forNode(node);
    var content = process2.call(this, node);
    var whitespace = node.flankingWhitespace;
    if (whitespace.leading || whitespace.trailing) content = content.trim();
    return whitespace.leading + rule.replacement(content, node, this.options) + whitespace.trailing;
  }
  function join(output, replacement) {
    var s1 = trimTrailingNewlines(output);
    var s2 = trimLeadingNewlines(replacement);
    var nls = Math.max(output.length - s1.length, replacement.length - s2.length);
    var separator = "\n\n".substring(0, nls);
    return s1 + separator + s2;
  }
  function canConvert(input) {
    return input != null && (typeof input === "string" || input.nodeType && (input.nodeType === 1 || input.nodeType === 9 || input.nodeType === 11));
  }
  var turndown_browser_es_default = TurndownService;

  // src/utils/markdown-converter-core.ts
  var logger = createLogger("MarkdownConverter");
  var MarkdownConverterCore = class {
    constructor() {
      this.turndownService = null;
      this._isInitialized = false;
      this.semanticSelectors = {
        callouts: [".callout", ".note", ".warning", ".info", ".alert", ".notice", '[role="note"]'],
        quotes: ["blockquote", ".quote", ".pullquote", '[role="blockquote"]'],
        highlights: [".highlight", ".featured", ".important", "mark", ".marker"],
        captions: ["figcaption", ".caption", ".image-caption", ".photo-caption"],
        metadata: [".byline", ".author", ".date", ".timestamp", ".published", ".updated"],
        codeElements: ["code", "pre", ".code", ".highlight", ".syntax"]
      };
    }
    // This method should be called by environment-specific wrappers
    setupTurndownService() {
      if (!this.turndownService) {
        throw new Error("TurndownService not initialized");
      }
      this.turndownService.remove([
        // Core unwanted elements
        "script",
        "style",
        "head",
        "noscript",
        "meta",
        "link",
        // Navigation and UI elements (but not semantic headers that contain content)
        "nav",
        "footer",
        "aside",
        // Common unwanted content (let TurndownService handle the rest)
        ".advertisement",
        ".ads",
        ".popup",
        ".modal",
        ".overlay",
        ".social-share",
        ".share-buttons",
        ".comment-form",
        ".subscription",
        ".newsletter",
        ".paywall",
        ".navigation",
        ".menu",
        ".sidebar",
        ".widget",
        // Site-specific unwanted elements (simple selectors replace complex rules)
        ".substack-nav",
        ".publication-header",
        ".subscribe-widget",
        ".recommend",
        ".like-button",
        ".related-posts"
      ]);
      this.addMinimalCustomRules();
    }
    addMinimalCustomRules() {
      if (!this.turndownService) return;
      this.turndownService.addRule("pseudoNumberedParagraphs", {
        filter: (node) => {
          if (node.nodeType !== 1 || node.tagName !== "P") return false;
          if (node.closest("ol, ul, li")) return false;
          const text = (node.textContent || "").trim();
          return /^\d+\.\s+\w/.test(text) && text.length > 20;
        },
        replacement: (content) => {
          return content.trim() ? `
${content.trim()}
` : "";
        }
      });
      this.turndownService.addRule("basicTables", {
        filter: "table",
        replacement: (content, node) => {
          const rows = [];
          const tableRows = node.querySelectorAll("tr");
          tableRows.forEach((row) => {
            const cells = [];
            const cellNodes = row.querySelectorAll("td, th");
            cellNodes.forEach((cell) => {
              cells.push((cell.textContent || "").trim());
            });
            if (cells.length > 0) {
              rows.push(cells);
            }
          });
          if (rows.length === 0) return "";
          let table = "";
          rows.forEach((row, index) => {
            table += "| " + row.join(" | ") + " |\n";
            if (index === 0) {
              table += "|" + row.map(() => "---").join("|") + "|\n";
            }
          });
          return `
${table}
`;
        }
      });
    }
    convertToMarkdown(html, options = {}) {
      if (!this._isInitialized || !this.turndownService) {
        throw new Error("MarkdownConverter not properly initialized");
      }
      try {
        let cleanedHtml = this.preprocessHtml(html);
        if ((!cleanedHtml || cleanedHtml.trim() === "") && typeof document !== "undefined" && document.body && document.body.innerHTML) {
          cleanedHtml = document.body.innerHTML;
        }
        let markdown = this.turndownService.turndown(cleanedHtml);
        if ((!markdown || markdown.trim() === "") && typeof document !== "undefined" && document.body && document.body.textContent) {
          markdown = document.body.textContent.trim();
        }
        const cleanedMarkdown = this.postprocessMarkdown(markdown);
        let wordCount = cleanedMarkdown.split(/\s+/).filter(Boolean).length;
        if (wordCount === 0 && typeof document !== "undefined" && document.body && document.body.textContent) {
          wordCount = document.body.textContent.trim().split(/\s+/).filter(Boolean).length;
        }
        const optionsUrl = options.sourceUrl || options.pageUrl;
        let pageUrl = "";
        if (optionsUrl && typeof optionsUrl === "string" && optionsUrl !== "http://localhost/") {
          pageUrl = optionsUrl;
        } else if (typeof global !== "undefined" && global.window?.location?.href) {
          const globalHref = global.window.location.href;
          if (globalHref !== "http://localhost/") {
            pageUrl = globalHref;
          }
        }
        if (!pageUrl && typeof window !== "undefined" && window.location?.href) {
          pageUrl = window.location.href;
        }
        const result = {
          markdown: cleanedMarkdown,
          frontmatter: "",
          metadata: {
            title: "",
            url: pageUrl,
            captureDate: (/* @__PURE__ */ new Date()).toISOString(),
            tags: [],
            author: "",
            wordCount,
            estimatedReadingTime: Math.ceil(wordCount / 200)
          },
          images: [],
          wordCount
        };
        return result;
      } catch (error) {
        logger.error("MarkdownConverter: Conversion failed:", error);
        throw error;
      }
    }
    preprocessHtml(html) {
      if (!html) return "";
      let cleaned = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, "");
      cleaned = cleaned.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, "");
      cleaned = cleaned.replace(/<!--[\s\S]*?-->/g, "");
      cleaned = cleaned.replace(/[ \t]+/g, " ");
      cleaned = cleaned.replace(/\n\s*\n\s*\n/g, "\n\n");
      cleaned = cleaned.trim();
      return cleaned;
    }
    postprocessMarkdown(markdown) {
      if (!markdown) return "";
      let cleaned = markdown.replace(/\n\s*\n\s*\n\s*\n/g, "\n\n\n");
      cleaned = cleaned.replace(/\n\s*\n\s*\n/g, "\n\n");
      cleaned = cleaned.replace(/\n(#{1,6}\s[^\n]+)\n/g, "\n\n$1\n\n");
      cleaned = cleaned.replace(/\n(\s*[-*+]\s[^\n]+)/g, "\n\n$1");
      cleaned = cleaned.replace(/\n(\s*\d+\.\s[^\n]+)/g, "\n\n$1");
      cleaned = cleaned.trim();
      if (cleaned && !cleaned.endsWith("\n")) {
        cleaned += "\n";
      }
      return cleaned;
    }
  };

  // src/utils/markdown-converter.ts
  var logger2 = createLogger("MarkdownConverter");
  var MarkdownConverter = class extends MarkdownConverterCore {
    constructor() {
      super();
      this.initializeTurndown();
    }
    initializeTurndown() {
      const isServiceWorker = typeof globalThis.importScripts === "function" && typeof window === "undefined";
      if (isServiceWorker) {
        if (true) {
          logger2.info("Running in service worker context, TurndownService not available");
        }
        this.turndownService = null;
        this._isInitialized = true;
        return;
      }
      if (typeof document === "undefined") {
        if (true) {
          logger2.warn("Document not available, TurndownService cannot be initialized");
        }
        this.turndownService = null;
        this._isInitialized = true;
        return;
      }
      try {
        const options = {
          headingStyle: "atx",
          bulletListMarker: "-",
          codeBlockStyle: "fenced",
          emDelimiter: "*",
          strongDelimiter: "**",
          linkStyle: "inlined",
          linkReferenceStyle: "full",
          preformattedCode: true
        };
        this.turndownService = new turndown_browser_es_default(options);
        this.setupTurndownService();
        this._isInitialized = true;
        if (true) {
          logger2.info("TurndownService initialized successfully");
        }
      } catch (error) {
        if (true) {
          logger2.warn("Failed to initialize TurndownService:", error);
        }
        this.turndownService = null;
        this._isInitialized = true;
      }
    }
  };

  // src/utils/notifications/toast-internal.ts
  var DEFAULT_DURATION = 4e3;
  var STYLE_ID = "prismweave-toast-styles";
  var activeToasts = /* @__PURE__ */ new Map();
  var CANONICAL_TOAST_CSS = `
/* PrismWeave Toast Tokens (subset) */
:root{--pw-space-3:0.75rem;--pw-space-4:1rem;--pw-space-5:1.25rem;--pw-radius-lg:0.75rem;--pw-font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;--pw-success-500:#10b981;--pw-error-500:#ef4444;--pw-primary-500:#3b82f6;--pw-warning-500:#f59e0b;--pw-shadow-lg:0 10px 15px -3px rgba(0,0,0,.1),0 4px 6px -2px rgba(0,0,0,.05);--pw-z-toast:10000}
/* Toast container (stack) */
.pw-toast-container{position:fixed;top:var(--pw-space-5);right:var(--pw-space-5);display:flex;flex-direction:column;gap:var(--pw-space-3);z-index:var(--pw-z-toast);font-family:var(--pw-font-family)}
/* Base toast */
.pw-toast{background:var(--pw-warning-500);color:#fff;padding:var(--pw-space-3) var(--pw-space-4);border-radius:var(--pw-radius-lg);box-shadow:var(--pw-shadow-lg);font-size:14px;line-height:1.35;display:flex;align-items:center;gap:var(--pw-space-3);max-width:320px;animation:pw-slideIn .3s ease;position:relative}
.pw-toast-success{background:var(--pw-success-500)}
.pw-toast-error{background:var(--pw-error-500)}
.pw-toast-info{background:var(--pw-primary-500)}
/* Close button */
.pw-toast .pw-toast-close{all:unset;cursor:pointer;margin-left:auto;color:#fff;font-weight:600;opacity:.85;line-height:1;padding:0 var(--pw-space-1)}
.pw-toast .pw-toast-close:hover{opacity:1}
/* Keyframes (reuse naming from shared-ui.css for consistency) */
@keyframes pw-slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
@keyframes pw-toast-out{from{opacity:1;transform:translateY(0)}to{opacity:0;transform:translateY(-4px)}}
`;
  function ensureStyles() {
    if (typeof document === "undefined") return;
    if (document.getElementById(STYLE_ID)) return;
    try {
      const style = document.createElement("style");
      style.id = STYLE_ID;
      style.textContent = CANONICAL_TOAST_CSS;
      document.head.appendChild(style);
    } catch (_err) {
    }
  }
  function getContainer() {
    if (typeof document === "undefined") return null;
    let el = document.querySelector(".pw-toast-container");
    if (!el) {
      el = document.createElement("div");
      el.className = "pw-toast-container";
      document.body.appendChild(el);
    }
    return el;
  }
  function dismissToasts(typeFilter) {
    if (typeof document === "undefined") return;
    const toastsToDismiss = [];
    activeToasts.forEach((toastInfo, toastElement) => {
      if (!typeFilter || toastInfo.type === typeFilter) {
        toastsToDismiss.push(toastInfo.dismiss);
      }
    });
    toastsToDismiss.forEach((dismiss) => dismiss());
  }
  function showToast(message, options = {}) {
    const {
      duration = DEFAULT_DURATION,
      type = "info",
      dismissible = true,
      clickUrl,
      linkLabel,
      openInNewTab = true,
      onClick,
      forceHighestZIndex = false
    } = options;
    if (typeof document === "undefined" || typeof window === "undefined") return;
    if (type === "success" || type === "error") {
      dismissToasts("info");
    }
    ensureStyles();
    const container = getContainer();
    if (!container) return;
    if (forceHighestZIndex) {
      container.style.zIndex = "2147483647";
    }
    const toast = document.createElement("div");
    toast.className = `pw-toast pw-toast-${type}`;
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");
    const contentWrapper = document.createElement("span");
    contentWrapper.style.display = "flex";
    contentWrapper.style.flexDirection = "column";
    contentWrapper.style.gap = "4px";
    const msgLine = document.createElement("span");
    msgLine.textContent = message;
    contentWrapper.appendChild(msgLine);
    if (clickUrl) {
      const isGitHubUrl = /https?:\/\/github\.com\//i.test(clickUrl);
      const action = document.createElement("a");
      action.href = clickUrl;
      action.textContent = linkLabel || deriveLinkLabel(clickUrl);
      action.style.color = "#fff";
      action.style.textDecoration = "underline";
      action.style.fontWeight = "600";
      action.style.cursor = "pointer";
      if (openInNewTab) {
        action.target = "_blank";
        action.rel = "noopener noreferrer";
      }
      action.addEventListener("click", (e) => {
        try {
          onClick?.();
        } catch {
        }
        e.stopPropagation();
      });
      if (isGitHubUrl) {
        const spacer = document.createTextNode(" ");
        msgLine.appendChild(spacer);
        msgLine.appendChild(action);
      } else {
        contentWrapper.appendChild(action);
      }
      toast.style.cursor = "pointer";
      toast.addEventListener("click", () => {
        try {
          onClick?.();
        } catch {
        }
        if (openInNewTab) {
          window.open(clickUrl, "_blank", "noopener");
        } else {
          window.location.href = clickUrl;
        }
      });
    }
    toast.appendChild(contentWrapper);
    if (dismissible) {
      const closeBtn = document.createElement("button");
      closeBtn.className = "pw-toast-close";
      closeBtn.type = "button";
      closeBtn.setAttribute("aria-label", "Dismiss");
      closeBtn.textContent = "\xD7";
      closeBtn.addEventListener("click", () => dismiss());
      toast.appendChild(closeBtn);
    }
    container.appendChild(toast);
    let removalTimer;
    if (duration > 0) {
      removalTimer = window.setTimeout(() => dismiss(), duration);
    }
    function dismiss() {
      if (!toast.isConnected) return;
      toast.style.animation = "pw-toast-out .25s ease forwards";
      window.setTimeout(() => {
        if (toast.parentElement) toast.parentElement.removeChild(toast);
        activeToasts.delete(toast);
      }, 240);
      if (removalTimer) window.clearTimeout(removalTimer);
    }
    activeToasts.set(toast, { type, dismiss });
  }
  function deriveLinkLabel(url) {
    try {
      const u = new URL(url);
      if (/github\.com/i.test(u.hostname)) {
        const parts = u.pathname.split("/").filter(Boolean);
        if (parts.length >= 4 && parts[2] === "commit") {
          return "View Commit";
        }
        if (parts.length >= 4 && parts[2] === "blob") {
          return "View File";
        }
        if (parts.length >= 4 && parts[2] === "tree") {
          return "View Repository";
        }
        return "View on GitHub";
      }
      return u.hostname;
    } catch {
      return "Open";
    }
  }
  if (typeof window !== "undefined") {
    window.prismweaveShowToast = showToast;
    window.prismweaveShowToastMaxZ = (message, options = {}) => {
      return showToast(message, { ...options, forceHighestZIndex: true });
    };
  }

  // src/injectable/content-extractor-injectable.ts
  var InjectableContentExtractor = class _InjectableContentExtractor {
    constructor(options = {}) {
      this._core = null;
      this._markdownConverter = null;
      this._isInitialized = false;
      this._defaultOptions = {
        cleanHtml: true,
        preserveFormatting: true,
        waitForDynamicContent: false,
        removeAds: true,
        removeNavigation: true,
        includeImages: true,
        includeLinks: true,
        customSelectors: [],
        excludeSelectors: []
      };
      this._logger = createLogger("InjectableExtractor");
      this._defaultOptions = { ...this._defaultOptions, ...options };
    }
    async initialize() {
      if (this._isInitialized) return;
      try {
        this._core = new ContentExtractionCore();
        this._markdownConverter = new MarkdownConverter();
        this._isInitialized = true;
        this._logger.info("Injectable content extractor initialized");
      } catch (error) {
        this._logger.error("Failed to initialize injectable extractor:", error);
        throw error;
      }
    }
    async extractAdvancedContent(options = {}) {
      if (!this._isInitialized || !this._core || !this._markdownConverter) {
        await this.initialize();
      }
      try {
        this._logger.info("Starting advanced content extraction");
        const finalOptions = { ...this._defaultOptions, ...options };
        const contentResult = await this._core.extractContent(finalOptions);
        const markdownResult = this._markdownConverter.convertToMarkdown(contentResult.content);
        const markdown = markdownResult.markdown;
        const advancedMetadata = this._core.extractAdvancedMetadata();
        const imageResults = this._core.extractImages();
        const images = imageResults.map((img) => img.src);
        const qualityScore = this._core.getContentQualityScore();
        const frontmatter = this._generateFrontmatter({
          title: contentResult.metadata.title,
          url: contentResult.metadata.url,
          domain: window.location.hostname,
          wordCount: contentResult.wordCount,
          extractedAt: (/* @__PURE__ */ new Date()).toISOString(),
          metadata: advancedMetadata
        });
        return {
          content: contentResult.content,
          title: contentResult.metadata.title,
          url: contentResult.metadata.url,
          domain: window.location.hostname,
          html: contentResult.content,
          markdown,
          frontmatter,
          metadata: {
            ...contentResult.metadata,
            ...advancedMetadata,
            extractedAt: (/* @__PURE__ */ new Date()).toISOString(),
            qualityScore,
            extractionMethod: "injectable-advanced"
          },
          images,
          // Already converted to string array above
          wordCount: contentResult.wordCount,
          readingTime: contentResult.readingTime,
          qualityScore,
          extractedAt: (/* @__PURE__ */ new Date()).toISOString(),
          extractionMethod: "injectable-advanced"
        };
      } catch (error) {
        this._logger.error("Advanced content extraction failed:", error);
        const errorMessage = error instanceof Error ? error.message : "Unknown error";
        throw new Error(`Advanced extraction failed: ${errorMessage}`);
      }
    }
    _generateFrontmatter(params) {
      const frontmatterLines = [
        "---",
        `title: "${params.title.replace(/"/g, '\\"')}"`,
        `url: "${params.url}"`,
        `domain: "${params.domain}"`,
        `extracted_at: "${params.extractedAt}"`,
        `word_count: ${params.wordCount}`,
        `extraction_method: "injectable-advanced"`
      ];
      if (params.metadata.author && typeof params.metadata.author === "string") {
        frontmatterLines.push(`author: "${params.metadata.author.replace(/"/g, '\\"')}"`);
      }
      if (params.metadata.description && typeof params.metadata.description === "string") {
        frontmatterLines.push(`description: "${params.metadata.description.replace(/"/g, '\\"')}"`);
      }
      if (params.metadata.keywords) {
        let keywordArray = [];
        if (typeof params.metadata.keywords === "string") {
          keywordArray = params.metadata.keywords.split(/[,;|]/).map((k) => k.trim().toLowerCase());
        } else if (Array.isArray(params.metadata.keywords)) {
          keywordArray = params.metadata.keywords.map((k) => String(k).trim().toLowerCase());
        }
        const validTags = keywordArray.filter((tag) => {
          if (tag.length < 2 || tag.length > 30) return false;
          if (tag.split(/\s+/).length > 4) return false;
          if (tag.includes("http") || tag.includes("www.") || tag.includes("click to"))
            return false;
          if (tag.match(/^(print|email|share|comment|#\w+)$/i)) return false;
          return true;
        }).slice(0, 10);
        if (validTags.length > 0) {
          const tags = validTags.map((k) => `"${k.replace(/"/g, '\\"')}"`).join(", ");
          frontmatterLines.push(`tags: [${tags}]`);
        }
      }
      frontmatterLines.push("---", "");
      return frontmatterLines.join("\n");
    }
    /**
     * Commit content directly to GitHub repository
     */
    async commitToGitHub(content, config, filename) {
      try {
        const extractionResult = await this.extractAdvancedContent();
        const finalFilename = filename || this._generateFilename(extractionResult.title);
        const folder = config.folder || "documents";
        const filePath = `${folder}/${finalFilename}`;
        const fullContent = extractionResult.frontmatter + extractionResult.markdown;
        const commitMessage = (config.commitMessage || "PrismWeave: Add {title}").replace(
          "{title}",
          extractionResult.title
        );
        let existingFileSha;
        try {
          const existingResponse = await fetch(
            `https://api.github.com/repos/${config.repository}/contents/${filePath}`,
            {
              headers: {
                Authorization: `token ${config.token}`,
                Accept: "application/vnd.github.v3+json",
                "User-Agent": "PrismWeave-Injectable/1.0"
              }
            }
          );
          if (existingResponse.ok) {
            const existingData = await existingResponse.json();
            existingFileSha = existingData.sha;
          } else if (existingResponse.status === 404) {
          } else {
            console.warn(
              `Unexpected response when checking file existence: ${existingResponse.status}`
            );
          }
        } catch (error) {
        }
        const requestBody = {
          message: commitMessage,
          content: btoa(unescape(encodeURIComponent(fullContent))),
          branch: "main"
        };
        if (existingFileSha) {
          requestBody.sha = existingFileSha;
        }
        const response = await fetch(
          `https://api.github.com/repos/${config.repository}/contents/${filePath}`,
          {
            method: "PUT",
            headers: {
              Authorization: `token ${config.token}`,
              "Content-Type": "application/json",
              Accept: "application/vnd.github.v3+json",
              "User-Agent": "PrismWeave-Injectable/1.0"
            },
            body: JSON.stringify(requestBody)
          }
        );
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            `GitHub API error: ${response.status} - ${errorData.message || "Unknown error"}`
          );
        }
        const result = await response.json();
        return {
          success: true,
          data: {
            sha: result.content.sha,
            url: result.content.url,
            html_url: result.content.html_url
          }
        };
      } catch (error) {
        this._logger.error("GitHub commit failed:", error);
        return {
          success: false,
          error: error instanceof Error ? error.message : "Unknown error"
        };
      }
    }
    _generateFilename(title) {
      const safeName = title.replace(/[^\w\s-]/g, "").replace(/\s+/g, "-").toLowerCase().slice(0, 40);
      const date = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
      return `${date}-${safeName}.md`;
    }
    // Static methods for easy access
    static async extractContent(options = {}) {
      const extractor = new _InjectableContentExtractor();
      return await extractor.extractAdvancedContent(options);
    }
    static async extractAndCommit(config, options = {}, filename) {
      const extractor = new _InjectableContentExtractor();
      await extractor.initialize();
      const extractionResult = await extractor.extractAdvancedContent(options);
      const finalFilename = filename || extractor._generateFilename(extractionResult.title);
      const folder = config.folder || "documents";
      const filePath = `${folder}/${finalFilename}`;
      const fullContent = extractionResult.frontmatter + extractionResult.markdown;
      return await extractor.commitToGitHub(fullContent, config, finalFilename);
    }
  };
  if (typeof window !== "undefined") {
    window.PrismWeaveInjectableExtractor = InjectableContentExtractor;
    window.prismweaveExtractContent = InjectableContentExtractor.extractContent;
    window.prismweaveExtractAndCommit = InjectableContentExtractor.extractAndCommit;
    window.prismweaveShowToast = showToast;
    console.log("\u{1F517} PrismWeave Injectable Content Extractor loaded successfully");
  }
  return __toCommonJS(content_extractor_injectable_exports);
})();
//# sourceMappingURL=content-extractor-injectable.js.map
