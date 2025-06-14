// Build script for DocTracker browser extension
const fs = require('fs');
const path = require('path');

const distDir = path.join(__dirname, '..', 'dist');
const srcDir = path.join(__dirname, '..', 'src');
const nodeModulesDir = path.join(__dirname, '..', 'node_modules');

// Create dist directory
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// Copy files function
function copyFiles(src, dest) {
  if (!fs.existsSync(src)) {
    console.warn(`Warning: Source directory does not exist: ${src}`);
    return;
  }
  
  const files = fs.readdirSync(src, { withFileTypes: true });
  
  files.forEach(file => {
    const srcPath = path.join(src, file.name);
    const destPath = path.join(dest, file.name);
    
    if (file.isDirectory()) {
      if (!fs.existsSync(destPath)) {
        fs.mkdirSync(destPath, { recursive: true });
      }
      copyFiles(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  });
}

// Copy source files to dist
console.log('Copying source files...');
copyFiles(srcDir, path.join(distDir, 'src'));

// Copy manifest
console.log('Copying manifest...');
fs.copyFileSync(
  path.join(__dirname, '..', 'manifest.json'),
  path.join(distDir, 'manifest.json')
);

// Copy icons if they exist
const iconsDir = path.join(__dirname, '..', 'icons');
if (fs.existsSync(iconsDir)) {
  console.log('Copying icons...');
  const distIconsDir = path.join(distDir, 'icons');
  if (!fs.existsSync(distIconsDir)) {
    fs.mkdirSync(distIconsDir);
  }
  copyFiles(iconsDir, distIconsDir);
} else {
  console.warn('Warning: Icons directory not found. Please add icons before packaging.');
}

// Copy Turndown.js dependency
const turndownPath = path.join(nodeModulesDir, 'turndown', 'dist', 'turndown.js');
if (fs.existsSync(turndownPath)) {
  console.log('Copying Turndown.js dependency...');
  const libDir = path.join(distDir, 'lib');
  if (!fs.existsSync(libDir)) {
    fs.mkdirSync(libDir);
  }
  fs.copyFileSync(turndownPath, path.join(libDir, 'turndown.js'));
} else {
  console.warn('Warning: Turndown.js not found. Run npm install first.');
}

console.log('Build complete!');
console.log('Extension files are in:', distDir);
console.log('\nTo test the extension:');
console.log('1. Open Chrome/Edge and go to chrome://extensions/');
console.log('2. Enable Developer mode');
console.log('3. Click "Load unpacked" and select the dist folder');

// Check for missing files
const requiredFiles = [
  'src/background/service-worker.js',
  'src/content/content-script.js',
  'src/popup/popup.html',
  'src/popup/popup.js',
  'src/options/options.html',
  'src/options/options.js',
  'src/utils/markdown-converter.js',
  'src/utils/git-operations.js',
  'src/utils/content-extractor.js',
  'src/utils/file-manager.js'
];

console.log('\nChecking required files:');
requiredFiles.forEach(file => {
  const filePath = path.join(distDir, file);
  if (fs.existsSync(filePath)) {
    console.log(`✓ ${file}`);
  } else {
    console.log(`✗ ${file} - MISSING`);
  }
});
