// TypeScript compilation script for PrismWeave browser extension
const { execSync } = require('child_process');
const path = require('path');

console.log('Compiling TypeScript components...');

try {
  // Compile UI components (popup, options, content) with CommonJS
  console.log('Compiling UI components (popup, options, content)...');
  execSync('npx tsc -p tsconfig.ui.json', { 
    cwd: path.join(__dirname, '..'),
    stdio: 'inherit'
  });
  
  // Compile service worker and utilities with CommonJS for importScripts compatibility
  console.log('Compiling service worker and utilities...');
  execSync('npx tsc -p tsconfig.service-worker.json', { 
    cwd: path.join(__dirname, '..'),
    stdio: 'inherit'
  });
  
  console.log('TypeScript compilation completed successfully');
} catch (error) {
  console.error('TypeScript compilation failed:', error.message);
  process.exit(1);
}
