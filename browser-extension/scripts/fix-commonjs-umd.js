// Post-build fix using proper UMD (Universal Module Definition) pattern
// This is the industry standard for cross-environment compatibility

const fs = require('fs');
const path = require('path');

function convertToUMD(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`File not found: ${filePath}`);
    return;
  }
  
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Check if file has CommonJS exports
  if (content.includes('Object.defineProperty(exports,') || content.includes('exports.') || content.includes('module.exports')) {
    console.log(`Converting to UMD: ${path.relative(process.cwd(), filePath)}`);
    
    // Extract the module name from file path for global registration
    const fileName = path.basename(filePath, '.js');
    const moduleName = fileName.split('-').map(part => 
      part.charAt(0).toUpperCase() + part.slice(1)
    ).join('');
    
    // Wrap in proper UMD pattern
    const umdContent = `(function (root, factory) {
  if (typeof exports === 'object' && typeof module !== 'undefined') {
    // CommonJS (Node.js)
    factory(exports);
  } else if (typeof define === 'function' && define.amd) {
    // AMD (RequireJS)
    define(['exports'], factory);
  } else {
    // Browser globals
    var exp = {};
    factory(exp);
    root.${moduleName} = exp;
    
    // Also expose individual exports as globals for service worker compatibility
    if (exp.Logger) root.Logger = exp.Logger;
    if (exp.createLogger) root.createLogger = exp.createLogger;
    if (exp.SettingsManager) root.SettingsManager = exp.SettingsManager;
    if (exp.ErrorHandler) root.ErrorHandler = exp.ErrorHandler;
    if (exp.GitOperations) root.GitOperations = exp.GitOperations;
    if (exp.FileManager) root.FileManager = exp.FileManager;
    if (exp.ContentExtractor) root.ContentExtractor = exp.ContentExtractor;
    if (exp.MarkdownConverter) root.MarkdownConverter = exp.MarkdownConverter;
    if (exp.PerformanceMonitor) root.PerformanceMonitor = exp.PerformanceMonitor;
    if (exp.SharedUtils) root.SharedUtils = exp.SharedUtils;
    if (exp.TurndownService) root.TurndownService = exp.TurndownService;
    if (exp.UIUtils) root.UIUtils = exp.UIUtils;
    if (exp.UIEnhancer) root.UIEnhancer = exp.UIEnhancer;
    if (exp.UtilsRegistry) root.UtilsRegistry = exp.UtilsRegistry;
    if (exp.LogConfig) root.LogConfig = exp.LogConfig;
  }
}(typeof self !== 'undefined' ? self : this, function (exports) {
${content.replace(/^"use strict";?\s*\n?/m, '')}
}));`;
    
    fs.writeFileSync(filePath, umdContent, 'utf8');
    console.log(`✓ Converted to UMD: ${path.relative(process.cwd(), filePath)}`);
  }
}

function convertAllToUMD(distDir) {
  console.log('Converting browser extension files to UMD format...');
  
  const directories = ['background', 'content', 'popup', 'options', 'utils'];
  
  directories.forEach(dir => {
    const dirPath = path.join(distDir, dir);
    if (fs.existsSync(dirPath)) {
      const files = fs.readdirSync(dirPath);
      files.forEach(file => {
        if (file.endsWith('.js') && !file.includes('.min.')) {
          convertToUMD(path.join(dirPath, file));
        }
      });
    }
  });
  
  console.log('✓ UMD conversion completed!');
}

// Run the conversion
const distPath = path.join(__dirname, '..', 'dist');
convertAllToUMD(distPath);
