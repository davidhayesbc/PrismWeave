// Post-build fix for CommonJS exports in browser extension
// This script removes or wraps CommonJS exports that cause issues in browser context

const fs = require('fs');
const path = require('path');

function fixCommonJSExports(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`File not found: ${filePath}`);
    return;
  }
  
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Check if file has CommonJS exports
  if (content.includes('Object.defineProperty(exports,') || content.includes('exports.') || content.includes('module.exports')) {
    console.log(`Fixing CommonJS exports in: ${path.relative(process.cwd(), filePath)}`);
    
    // Wrap the entire file in an IIFE that defines exports if needed
    const wrappedContent = `(function() {
  // Define exports for CommonJS compatibility if not in Node.js environment
  if (typeof exports === 'undefined') {
    var exports = {};
    var module = { exports: exports };
  }
  
${content}
  
  // Return exports for browser usage
  return typeof module !== 'undefined' ? module.exports : exports;
})();`;
    
    fs.writeFileSync(filePath, wrappedContent, 'utf8');
    console.log(`✓ Fixed: ${path.relative(process.cwd(), filePath)}`);
  }
}

function fixAllJSFiles(distDir) {
  console.log('Fixing CommonJS exports in browser extension files...');
  
  const directories = ['background', 'content', 'popup', 'options', 'utils'];
  
  directories.forEach(dir => {
    const dirPath = path.join(distDir, dir);
    if (fs.existsSync(dirPath)) {
      const files = fs.readdirSync(dirPath);
      files.forEach(file => {
        if (file.endsWith('.js')) {
          fixCommonJSExports(path.join(dirPath, file));
        }
      });
    }
  });
  
  console.log('✓ CommonJS exports fix completed!');
}

// Run the fix
const distPath = path.join(__dirname, '..', 'dist');
fixAllJSFiles(distPath);
