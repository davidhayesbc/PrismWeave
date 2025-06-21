// Asset copying script for PrismWeave browser extension
const fs = require('fs');
const path = require('path');

const distDir = path.join(__dirname, '..', 'dist');
const srcDir = path.join(__dirname, '..', 'src');
const nodeModulesDir = path.join(__dirname, '..', 'node_modules');

console.log('Copying assets and static files...');

// Create dist directory if it doesn't exist
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// Clean up test files from dist (Chrome extensions can't load directories starting with _)
console.log('Cleaning up test files...');
const testDirs = [
  path.join(distDir, '__tests__'),
  path.join(distDir, 'src', '__tests__')
];

testDirs.forEach(testDir => {
  if (fs.existsSync(testDir)) {
    fs.rmSync(testDir, { recursive: true, force: true });
    console.log('Removed test directory:', path.relative(distDir, testDir));
  }
});

// Remove any .test.js files
function removeTestFiles(dir) {
  if (!fs.existsSync(dir)) return;
  
  const items = fs.readdirSync(dir, { withFileTypes: true });
  items.forEach(item => {
    const itemPath = path.join(dir, item.name);
    if (item.isDirectory()) {
      removeTestFiles(itemPath);
      // Remove empty directories that might have contained test files
      try {
        const remainingItems = fs.readdirSync(itemPath);
        if (remainingItems.length === 0) {
          fs.rmdirSync(itemPath);
          console.log('Removed empty test directory:', path.relative(distDir, itemPath));
        }
      } catch (e) {
        // Directory not empty or doesn't exist, ignore
      }
    } else if (item.name.includes('.test.') || item.name.includes('.spec.')) {
      fs.unlinkSync(itemPath);
      console.log('Removed test file:', path.relative(distDir, itemPath));
    }
  });
}

removeTestFiles(distDir);

// Copy non-TypeScript files
console.log('Copying non-TypeScript files...');

// Copy CSS and HTML files from popup and options
const componentDirs = ['popup', 'options'];
componentDirs.forEach(component => {
  const srcComponentDir = path.join(srcDir, component);
  const distComponentDir = path.join(distDir, component);
  
  if (fs.existsSync(srcComponentDir)) {
    if (!fs.existsSync(distComponentDir)) {
      fs.mkdirSync(distComponentDir, { recursive: true });
    }
    
    const files = fs.readdirSync(srcComponentDir);
    files.forEach(file => {
      const ext = path.extname(file);
      if (['.css', '.html'].includes(ext)) {
        const srcFile = path.join(srcComponentDir, file);
        const distFile = path.join(distComponentDir, file);
        fs.copyFileSync(srcFile, distFile);
        console.log('Copied:', file);
      }
    });
  }
});

// Copy manifest.json
console.log('Copying manifest...');
const manifestSrc = path.join(__dirname, '..', 'manifest.json');
const manifestDist = path.join(distDir, 'manifest.json');
if (fs.existsSync(manifestSrc)) {
  fs.copyFileSync(manifestSrc, manifestDist);
} else {
  console.error('manifest.json not found!');
  process.exit(1);
}

// Copy icons
console.log('Copying icons...');
const iconsSrcDir = path.join(__dirname, '..', 'icons');
const iconsDistDir = path.join(distDir, 'icons');

if (fs.existsSync(iconsSrcDir)) {
  if (!fs.existsSync(iconsDistDir)) {
    fs.mkdirSync(iconsDistDir, { recursive: true });
  }
  
  const iconFiles = fs.readdirSync(iconsSrcDir);
  iconFiles.forEach(file => {
    if (file.endsWith('.png') || file.endsWith('.ico')) {
      const srcFile = path.join(iconsSrcDir, file);
      const distFile = path.join(iconsDistDir, file);
      fs.copyFileSync(srcFile, distFile);
      console.log('Copied:', file);
    }
  });
} else {
  console.warn('Icons directory not found, skipping...');
}

// Copy libs directory
console.log('Copying libs...');
const libsSrcDir = path.join(srcDir, 'libs');
const libsDistDir = path.join(distDir, 'libs');

if (fs.existsSync(libsSrcDir)) {
  if (!fs.existsSync(libsDistDir)) {
    fs.mkdirSync(libsDistDir, { recursive: true });
  }
  
  const libFiles = fs.readdirSync(libsSrcDir);
  libFiles.forEach(file => {
    const srcFile = path.join(libsSrcDir, file);
    const distFile = path.join(libsDistDir, file);
    fs.copyFileSync(srcFile, distFile);
    console.log('Copied:', file);
  });
} else {
  console.warn('Libs directory not found, skipping...');
}

// Copy third-party dependencies
console.log('Copying third-party dependencies...');
const turndownSrc = path.join(nodeModulesDir, 'turndown', 'dist', 'turndown.js');
const turndownDist = path.join(libsDistDir, 'turndown.js');

if (fs.existsSync(turndownSrc)) {
  if (!fs.existsSync(libsDistDir)) {
    fs.mkdirSync(libsDistDir, { recursive: true });
  }
  fs.copyFileSync(turndownSrc, turndownDist);
  console.log('Copied turndown.js');
} else {
  console.warn('Turndown.js not found in node_modules, skipping...');
}

// Copy Turndown.js dependency  
console.log('Copying Turndown.js dependency...');
const turndownLibSrc = path.join(nodeModulesDir, 'turndown', 'dist', 'turndown.js');
const turndownLibDist = path.join(distDir, 'libs', 'turndown.js');

if (fs.existsSync(turndownLibSrc)) {
  const libsDir = path.join(distDir, 'libs');
  if (!fs.existsSync(libsDir)) {
    fs.mkdirSync(libsDir, { recursive: true });
  }
  fs.copyFileSync(turndownLibSrc, turndownLibDist);
} else {
  console.warn('Turndown library not found, extension may not work properly');
}

console.log('Asset copying completed!');
