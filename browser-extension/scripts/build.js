// Build script for PrismWeave browser extension
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const distDir = path.join(__dirname, '..', 'dist');
const srcDir = path.join(__dirname, '..', 'src');
const nodeModulesDir = path.join(__dirname, '..', 'node_modules');

console.log('Building PrismWeave Browser Extension...');

// Clean dist directory
if (fs.existsSync(distDir)) {
  console.log('Cleaning dist directory...');
  fs.rmSync(distDir, { recursive: true, force: true });
}

// Create dist directory
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// Compile TypeScript
console.log('Compiling TypeScript...');
try {
  execSync('npx tsc', { 
    cwd: path.join(__dirname, '..'),
    stdio: 'inherit'
  });
  console.log('TypeScript compilation completed successfully');
} catch (error) {
  console.error('TypeScript compilation failed:', error.message);
  process.exit(1);
}

// Copy files function (for non-TypeScript files)
function copyFiles(src, dest, extensions = ['.html', '.css', '.json']) {
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
      copyFiles(srcPath, destPath, extensions);
    } else {
      const ext = path.extname(file.name);
      if (extensions.includes(ext)) {
        fs.copyFileSync(srcPath, destPath);
        console.log(`Copied: ${file.name}`);
      }
    }
  });
}

// Copy non-TypeScript source files to dist (HTML, CSS, etc.)
console.log('Copying non-TypeScript files...');
copyFiles(srcDir, distDir, ['.html', '.css', '.json']);

// Copy manifest
console.log('Copying manifest...');
const manifestSrc = path.join(__dirname, '..', 'manifest.json');
const manifestDest = path.join(distDir, 'manifest.json');
if (fs.existsSync(manifestSrc)) {
  // Update manifest to point to compiled JavaScript files
  const manifest = JSON.parse(fs.readFileSync(manifestSrc, 'utf8'));
  
  // Update background script path
  if (manifest.background && manifest.background.service_worker) {
    manifest.background.service_worker = manifest.background.service_worker.replace(/\.ts$/, '.js');
  }
  
  // Update content scripts paths
  if (manifest.content_scripts) {
    manifest.content_scripts.forEach(script => {
      if (script.js) {
        script.js = script.js.map(file => file.replace(/\.ts$/, '.js'));
      }
    });
  }
  
  fs.writeFileSync(manifestDest, JSON.stringify(manifest, null, 2));
} else {
  console.warn('Warning: manifest.json not found');
}

// Copy icons if they exist
const iconsDir = path.join(__dirname, '..', 'icons');
if (fs.existsSync(iconsDir)) {
  console.log('Copying icons...');
  const distIconsDir = path.join(distDir, 'icons');
  if (!fs.existsSync(distIconsDir)) {
    fs.mkdirSync(distIconsDir);
  }
  copyFiles(iconsDir, distIconsDir, ['.png', '.jpg', '.jpeg', '.svg', '.ico']);
} else {
  console.warn('Warning: Icons directory not found. Please add icons before packaging.');
}

// Copy libs directory if it exists (third-party libraries)
const libsDir = path.join(srcDir, 'libs');
if (fs.existsSync(libsDir)) {
  console.log('Copying libs...');
  const distLibsDir = path.join(distDir, 'libs');
  if (!fs.existsSync(distLibsDir)) {
    fs.mkdirSync(distLibsDir, { recursive: true });
  }
  copyFiles(libsDir, distLibsDir, ['.js', '.min.js', '.css']);
}

// Copy third-party dependencies from node_modules if needed
console.log('Copying third-party dependencies...');
const turndownSrc = path.join(nodeModulesDir, 'turndown', 'dist', 'turndown.js');
const turndownDest = path.join(distDir, 'libs', 'turndown.min.js');
if (fs.existsSync(turndownSrc)) {
  if (!fs.existsSync(path.dirname(turndownDest))) {
    fs.mkdirSync(path.dirname(turndownDest), { recursive: true });
  }
  fs.copyFileSync(turndownSrc, turndownDest);
  console.log('Copied turndown.js');
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

// Check for compiled files
const requiredFiles = [
  'background/service-worker.js',
  'content/content-script.js',
  'popup/popup.html',
  'popup/popup.js',
  'options/options.html',
  'options/options.js',
  'utils/settings-manager.js',
  'utils/error-handler.js',
  'manifest.json'
];

console.log('\nChecking compiled files:');
let allFilesPresent = true;
requiredFiles.forEach(file => {
  const filePath = path.join(distDir, file);
  if (fs.existsSync(filePath)) {
    console.log(`✓ ${file}`);
  } else {
    console.log(`✗ ${file} - MISSING`);
    allFilesPresent = false;
  }
});

if (allFilesPresent) {
  console.log('\n✓ Build completed successfully! All required files are present.');
} else {
  console.log('\n✗ Build completed with missing files. Check compilation errors.');
}
