// Service Worker specific module converter
// Removes all ES6 imports/exports and ensures global assignments work correctly

const fs = require('fs');
const path = require('path');

function convertForServiceWorker(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`File not found: ${filePath}`);
    return;
  }
  
  let content = fs.readFileSync(filePath, 'utf8');
  
  console.log(`Converting for service worker: ${path.relative(process.cwd(), filePath)}`);
    // Track exported classes for global assignments
  const exportedClasses = [];
  
  // Find export class declarations
  const exportedClassMatches = content.matchAll(/^export\s+class\s+(\w+)/gm);
  for (const match of exportedClassMatches) {
    exportedClasses.push(match[1]);
  }
  
  // Find export { ClassName } declarations
  const exportBracesMatches = content.matchAll(/^export\s*{\s*([^}]+)\s*}/gm);
  for (const match of exportBracesMatches) {
    const exports = match[1].split(',').map(exp => exp.trim());
    exportedClasses.push(...exports);
  }
  
  // Find class declarations (to determine what classes exist for global assignment)
  const classMatches = content.matchAll(/^class\s+(\w+)/gm);
  const availableClasses = [];
  for (const match of classMatches) {
    availableClasses.push(match[1]);
  }
  
  // Remove all ES6 import statements
  content = content.replace(/^import\s+.*?from\s+.*?;?\s*$/gm, '// Removed import for service worker compatibility');
  
  // Remove all ES6 export statements (including export class, export interface, etc.)
  content = content.replace(/^export\s*{\s*[^}]*\s*};\s*$/gm, '// Removed ES6 export for service worker compatibility');
  content = content.replace(/^export\s+type\s*{\s*[^}]*\s*};\s*$/gm, '// Removed type export for service worker compatibility');
  content = content.replace(/^export\s+interface\s+.*?$/gm, '// Removed interface export for service worker compatibility');
  content = content.replace(/^export\s+class\s+/gm, 'class ');
  content = content.replace(/^export\s+const\s+/gm, 'const ');
  content = content.replace(/^export\s+function\s+/gm, 'function ');
  content = content.replace(/^export\s+enum\s+/gm, 'enum ');
  content = content.replace(/^export\s+/gm, '// export ');
  
  // Handle any remaining broken class declarations
  content = content.replace(/^\/\/\s*export\s+class\s+(\w+)\s*\{$/gm, 'class $1 {');
  content = content.replace(/^\/\/\s*(\w+)\s*\{$/gm, 'class $1 {');
  
  // Fix any broken constructor or method declarations
  content = content.replace(/^\s*constructor\(\)/gm, '    constructor()');
  content = content.replace(/^\s*(\w+)\s*\(/gm, '    $1(');
  
  // Remove any leftover comment artifacts that might break syntax
  content = content.replace(/^\/\/\s*export\s*$/gm, '');
    // Add global assignments for exported classes
  // Filter to only include classes that actually exist in the file
  const classesToExport = exportedClasses.filter(className => availableClasses.includes(className));
  
  if (classesToExport.length > 0) {
    const sourcemapMatch = content.match(/\/\/# sourceMappingURL=.*$/m);
    if (sourcemapMatch) {
      content = content.replace(/\/\/# sourceMappingURL=.*$/m, '');
    }
      content += '\n\n// Make available globally for service worker importScripts compatibility\n';
    content += 'if (typeof globalThis !== \'undefined\') {\n';
    for (const className of classesToExport) {
      content += `    globalThis.${className} = ${className};\n`;
    }
    content += '} else if (typeof self !== \'undefined\') {\n';
    for (const className of classesToExport) {
      content += `    self.${className} = ${className};\n`;
    }
    content += '} else if (typeof window !== \'undefined\') {\n';
    for (const className of classesToExport) {
      content += `    window.${className} = ${className};\n`;
    }
    content += '}';
    
    if (sourcemapMatch) {
      content += '\n' + sourcemapMatch[0];
    }
  } else {
    // Ensure sourcemap comment is at the end
    const sourcemapMatch = content.match(/\/\/# sourceMappingURL=.*$/m);
    if (sourcemapMatch) {
      content = content.replace(/\/\/# sourceMappingURL=.*$/m, '');
      content = content.trim() + '\n' + sourcemapMatch[0];
    }
  }
  
  fs.writeFileSync(filePath, content, 'utf8');
  console.log(`✓ Service worker compatible: ${path.relative(process.cwd(), filePath)}`);
}

function convertAllUtilsForServiceWorker(distDir) {
  console.log('Converting utility files for service worker compatibility...');
  
  const utilsDir = path.join(distDir, 'utils');
  if (fs.existsSync(utilsDir)) {
    const files = fs.readdirSync(utilsDir);
    files.forEach(file => {
      if (file.endsWith('.js') && !file.includes('.min.')) {
        convertForServiceWorker(path.join(utilsDir, file));
      }
    });
  }
  
  console.log('✓ Service worker conversion completed!');
}

// Run the conversion
const distPath = path.join(__dirname, '..', 'dist');
convertAllUtilsForServiceWorker(distPath);
