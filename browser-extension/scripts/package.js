// Package script for PrismWeave browser extension
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const distDir = path.join(__dirname, '..', 'dist');
const packagePath = path.join(__dirname, '..', 'prismweave-extension.zip');

// Check if dist directory exists
if (!fs.existsSync(distDir)) {
  console.error('Error: dist directory not found. Run "npm run build" first.');
  process.exit(1);
}

// Remove existing package
if (fs.existsSync(packagePath)) {
  fs.unlinkSync(packagePath);
  console.log('Removed existing package');
}

try {
  // Use built-in zip functionality (requires PowerShell on Windows)
  if (process.platform === 'win32') {
    // Windows PowerShell command
    const command = `Compress-Archive -Path "${distDir}\\*" -DestinationPath "${packagePath}"`;
    execSync(`powershell -Command "${command}"`, { stdio: 'inherit' });
  } else {
    // Unix-like systems
    execSync(`cd "${distDir}" && zip -r "${packagePath}" .`, { stdio: 'inherit' });
  }
  
  console.log('✓ Extension packaged successfully!');
  console.log(`Package location: ${packagePath}`);
  
  // Get package size
  const stats = fs.statSync(packagePath);
  const fileSizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
  console.log(`Package size: ${fileSizeInMB} MB`);
  
} catch (error) {
  console.error('Error creating package:', error.message);
  console.log('\nAlternative: Manually zip the contents of the dist folder');
  process.exit(1);
}

// Verify package contents
console.log('\nPackage created! To install:');
console.log('1. Open Chrome/Edge extensions page (chrome://extensions/)');
console.log('2. Enable Developer mode');
console.log('3. Drag and drop the .zip file or use "Load unpacked" with the dist folder');
