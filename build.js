#!/usr/bin/env node

/**
 * Unified Build System for PrismWeave
 * Standard esbuild-based builder for all components
 */

const esbuild = require('esbuild');
const fs = require('fs');
const path = require('path');

class PrismWeaveBuildSystem {
  constructor() {
    this.isProduction = process.env.NODE_ENV === 'production';
    this.verbose = process.argv.includes('--verbose');
    this.config = this.getConfig();
  }

  getConfig() {
    const isInBrowserExtension = process.cwd().endsWith('browser-extension');
    const basePath = isInBrowserExtension ? './' : './browser-extension/';
    const devToolsBasePath = isInBrowserExtension ? './dev-tools/' : './browser-extension/dev-tools/';
    
    return {
      components: {
        'browser-extension': {
          name: 'Browser Extension',
          baseDir: basePath,
          targets: [
            {
              name: 'service-worker',
              entry: `${basePath}src/background/service-worker.ts`,
              outfile: `${basePath}dist/background/service-worker.js`,
              format: 'iife',
              platform: 'browser'
            },
            {
              name: 'content-script',
              entry: `${basePath}src/content/content-script.ts`,
              outfile: `${basePath}dist/content/content-script.js`,
              format: 'iife',
              platform: 'browser'
            },
            {
              name: 'popup',
              entry: `${basePath}src/popup/popup.ts`,
              outfile: `${basePath}dist/popup/popup.js`,
              format: 'iife',
              platform: 'browser'
            },
            {
              name: 'options',
              entry: `${basePath}src/options/options.ts`,
              outfile: `${basePath}dist/options/options.js`,
              format: 'iife',
              platform: 'browser'
            },
            {
              name: 'bookmarklet-options',
              entry: `${basePath}src/options/bookmarklet.ts`,
              outfile: `${basePath}dist/options/bookmarklet.js`,
              format: 'iife',
              platform: 'browser'
            }
          ],
          assets: [
            { from: `${basePath}src/popup/popup.html`, to: `${basePath}dist/popup/popup.html` },
            { from: `${basePath}src/popup/popup.css`, to: `${basePath}dist/popup/popup.css` },
            { from: `${basePath}src/options/options.html`, to: `${basePath}dist/options/options.html` },
            { from: `${basePath}src/options/options.css`, to: `${basePath}dist/options/options.css` },
            { from: `${basePath}src/options/bookmarklet.html`, to: `${basePath}dist/options/bookmarklet.html` },
            { from: `${basePath}src/styles/shared-ui.css`, to: `${basePath}dist/styles/shared-ui.css` },
            { from: `${basePath}manifest.json`, to: `${basePath}dist/manifest.json` },
            { from: `${basePath}icons`, to: `${basePath}dist/icons`, isDirectory: true }
          ]
        },
        'bookmarklet': {
          name: 'Bookmarklet',
          baseDir: basePath,
          targets: [
            {
              name: 'bookmarklet-runtime',
              entry: `${basePath}src/bookmarklet/enhanced-runtime-compatible.ts`,
              outfile: `${basePath}dist/bookmarklet/runtime.js`,
              format: 'iife',
              platform: 'browser',
              define: {
                'BOOKMARKLET_MODE': '"hosted"',
                'BOOKMARKLET_VERSION': '"2.0.0"'
              }
            },
            {
              name: 'bookmarklet-loader',
              entry: `${basePath}src/bookmarklet/hybrid-loader.ts`,
              outfile: `${basePath}dist/bookmarklet/loader.js`,
              format: 'iife',
              platform: 'browser'
            },
            {
              name: 'bookmarklet-standalone',
              entry: `${basePath}src/bookmarklet/enhanced-runtime-compatible.ts`,
              outfile: `${basePath}dist/bookmarklet/standalone.js`,
              format: 'iife',
              platform: 'browser',
              define: {
                'BOOKMARKLET_MODE': '"standalone"',
                'BOOKMARKLET_VERSION': '"2.0.0"'
              }
            }
          ],
          assets: [
            { from: `${basePath}src/bookmarklet/help.html`, to: `${basePath}dist/bookmarklet/help.html` },
            { from: `${basePath}src/bookmarklet/install.html`, to: `${basePath}dist/bookmarklet/install.html` },
            { from: `${basePath}src/bookmarklet/README.md`, to: `${basePath}dist/bookmarklet/README.md` }
          ]
        },
        'dev-tools': {
          name: 'Dev Tools',
          baseDir: devToolsBasePath,
          targets: [
            {
              name: 'capture-cli',
              entry: `${devToolsBasePath}capture-cli.ts`,
              outfile: `${devToolsBasePath}dist/capture-cli.js`,
              format: 'cjs',
              platform: 'node',
              external: ['puppeteer', 'jsdom', 'commander']
            }
          ],
          assets: [
            { from: `${devToolsBasePath}README.md`, to: `${devToolsBasePath}dist/README.md` }
          ]
        }
      }
    };
  }

  log(message, ...args) {
    if (this.verbose) {
      console.log(`🔧 ${message}`, ...args);
    }
  }

  error(message, ...args) {
    console.error(`❌ ${message}`, ...args);
  }

  success(message, ...args) {
    console.log(`✅ ${message}`, ...args);
  }

  async ensureDir(dirPath) {
    if (!fs.existsSync(dirPath)) {
      await fs.promises.mkdir(dirPath, { recursive: true });
      this.log(`Created directory: ${dirPath}`);
    }
  }

  async copyAsset(asset) {
    try {
      await this.ensureDir(path.dirname(asset.to));
      
      if (asset.isDirectory) {
        // Copy directory recursively
        if (fs.existsSync(asset.from)) {
          await this.copyDirectory(asset.from, asset.to);
        }
      } else {
        // Copy single file
        if (fs.existsSync(asset.from)) {
          await fs.promises.copyFile(asset.from, asset.to);
          this.log(`Copied: ${asset.from} → ${asset.to}`);
        }
      }
    } catch (error) {
      this.error(`Failed to copy ${asset.from}:`, error.message);
    }
  }

  async copyDirectory(src, dest) {
    await this.ensureDir(dest);
    const items = await fs.promises.readdir(src);
    
    for (const item of items) {
      const srcPath = path.join(src, item);
      const destPath = path.join(dest, item);
      const stat = await fs.promises.stat(srcPath);
      
      if (stat.isDirectory()) {
        await this.copyDirectory(srcPath, destPath);
      } else {
        await fs.promises.copyFile(srcPath, destPath);
        this.log(`Copied: ${srcPath} → ${destPath}`);
      }
    }
  }

  async buildTarget(target) {
    this.log(`Building target: ${target.name}`);
    
    // Ensure output directory exists
    await this.ensureDir(path.dirname(target.outfile));

    const buildOptions = {
      entryPoints: [target.entry],
      outfile: target.outfile,
      bundle: true,
      format: target.format || 'iife',
      platform: target.platform || 'browser',
      target: 'es2020',
      minify: this.isProduction && target.minify !== false,
      sourcemap: !this.isProduction && target.sourcemap !== false,
      external: target.external || [],
      define: {
        'process.env.NODE_ENV': this.isProduction ? '"production"' : '"development"',
        ...target.define
      },
      logLevel: this.verbose ? 'info' : 'warning'
    };

    try {
      const result = await esbuild.build(buildOptions);
      
      if (result.warnings.length > 0) {
        console.warn(`⚠️  Warnings for ${target.name}:`, result.warnings);
      }
      
      const stats = fs.statSync(target.outfile);
      const sizeKB = Math.round(stats.size / 1024);
      this.success(`Built ${target.name}: ${target.outfile} (${sizeKB}KB)`);
      
      return { success: true, size: stats.size };
    } catch (error) {
      this.error(`Failed to build ${target.name}:`, error.message);
      return { success: false, error: error.message };
    }
  }

  async buildComponent(componentName, componentConfig) {
    console.log(`\n📦 Building component: ${componentConfig.name || componentName}`);
    
    const results = [];
    
    // Build all targets
    for (const target of componentConfig.targets || []) {
      const result = await this.buildTarget(target);
      results.push({ target: target.name, ...result });
    }

    // Copy assets
    if (componentConfig.assets) {
      for (const asset of componentConfig.assets) {
        await this.copyAsset(asset);
      }
    }

    return results;
  }

  async buildAll() {
    console.log('🚀 Starting PrismWeave unified build...\n');
    const startTime = Date.now();
    
    const allResults = {};
    let totalErrors = 0;

    for (const [componentName, componentConfig] of Object.entries(this.config.components)) {
      try {
        const results = await this.buildComponent(componentName, componentConfig);
        allResults[componentName] = results;
        
        const errors = results.filter(r => !r.success).length;
        totalErrors += errors;
      } catch (error) {
        this.error(`Failed to build component ${componentName}:`, error.message);
        totalErrors++;
      }
    }

    const duration = Date.now() - startTime;
    console.log(`\n🏁 Build completed in ${duration}ms`);
    
    if (totalErrors === 0) {
      this.success('All components built successfully!');
    } else {
      this.error(`Build completed with ${totalErrors} errors`);
      process.exit(1);
    }

    return allResults;
  }

  async buildSingleComponent(componentName) {
    const componentConfig = this.config.components[componentName];
    if (!componentConfig) {
      this.error(`Component '${componentName}' not found in configuration`);
      return;
    }

    return await this.buildComponent(componentName, componentConfig);
  }

  async clean() {
    console.log('🧹 Cleaning build outputs...');
    
    const dirsToClean = [
      './browser-extension/dist',
      './browser-extension/dev-tools/dist',
      './dist'
    ];

    for (const dir of dirsToClean) {
      if (fs.existsSync(dir)) {
        await fs.promises.rm(dir, { recursive: true, force: true });
        this.success(`Cleaned: ${dir}`);
      }
    }
  }

  async webBuild() {
    console.log('🌐 Building for web deployment...');
    
    // First build all components
    await this.buildAll();
    
    // Create web-ready structure
    const webDir = './dist/web';
    await this.ensureDir(webDir);
    
    // Copy browser extension files
    await this.copyDirectory('./browser-extension/dist', path.join(webDir, 'extension'));
    
    // Copy bookmarklet files
    if (fs.existsSync('./browser-extension/dist/bookmarklet')) {
      await this.copyDirectory('./browser-extension/dist/bookmarklet', path.join(webDir, 'bookmarklet'));
    }
    
    // Generate web index
    await this.generateWebIndex(webDir);
    
    this.success(`Web build ready at: ${webDir}`);
  }

  async generateWebIndex(webDir) {
    const buildTime = new Date().toISOString();
    const version = require('./package.json').version || '1.0.0';
    
    const indexHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrismWeave - Document Capture Tools</title>
    <meta name="description" content="PrismWeave browser extension and bookmarklet for capturing web pages as clean markdown and syncing to your document repository.">
    <meta name="keywords" content="document capture, markdown, browser extension, bookmarklet, web scraping, note taking">
    <meta property="og:title" content="PrismWeave - Document Capture Tools">
    <meta property="og:description" content="Capture web pages as clean markdown with PrismWeave browser extension and bookmarklet.">
    <meta property="og:type" content="website">
    <link rel="icon" type="image/png" href="./extension/icons/icon32.png">
    <style>
        :root {
          --primary-color: #2563eb;
          --primary-hover: #1d4ed8;
          --secondary-color: #64748b;
          --success-color: #10b981;
          --background: #ffffff;
          --surface: #f8fafc;
          --border: #e2e8f0;
          --text-primary: #1e293b;
          --text-secondary: #64748b;
          --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
          line-height: 1.6; 
          color: var(--text-primary);
          background: var(--background);
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        
        header { 
          text-align: center; 
          margin-bottom: 4rem; 
          padding: 3rem 0;
          background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
          color: white;
          border-radius: 12px;
          margin: 0 -2rem 4rem -2rem;
        }
        
        .logo { font-size: 3rem; margin-bottom: 1rem; }
        h1 { font-size: 2.5rem; margin-bottom: 1rem; font-weight: 700; }
        .subtitle { font-size: 1.2rem; opacity: 0.9; max-width: 600px; margin: 0 auto; }
        
        .features {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
          margin-bottom: 4rem;
        }
        
        .feature {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 2rem;
          text-align: center;
          transition: all 0.2s ease;
        }
        
        .feature:hover {
          transform: translateY(-4px);
          box-shadow: var(--shadow);
          border-color: var(--primary-color);
        }
        
        .feature-icon { font-size: 3rem; margin-bottom: 1rem; }
        .feature h3 { font-size: 1.5rem; margin-bottom: 1rem; color: var(--text-primary); }
        .feature p { color: var(--text-secondary); margin-bottom: 1.5rem; }
        
        .component {
          background: white;
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 2rem;
          margin-bottom: 2rem;
          box-shadow: 0 2px 4px rgb(0 0 0 / 0.05);
          transition: all 0.2s ease;
        }
        
        .component:hover {
          box-shadow: var(--shadow);
          border-color: var(--primary-color);
        }
        
        .component h2 { 
          font-size: 1.5rem; 
          margin-bottom: 1rem; 
          color: var(--text-primary);
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .component-icon { font-size: 1.5rem; }
        
        .btn {
          display: inline-block;
          padding: 0.75rem 1.5rem;
          background: var(--primary-color);
          color: white;
          text-decoration: none;
          border-radius: 8px;
          font-weight: 600;
          transition: all 0.2s ease;
          margin-right: 1rem;
          margin-bottom: 0.5rem;
        }
        
        .btn:hover {
          background: var(--primary-hover);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgb(37 99 235 / 0.3);
        }
        
        .btn-secondary {
          background: var(--secondary-color);
          color: white;
        }
        
        .btn-secondary:hover {
          background: #475569;
        }
        
        .installation-steps {
          background: var(--surface);
          border-radius: 12px;
          padding: 2rem;
          margin-top: 1.5rem;
        }
        
        .installation-steps h4 {
          margin-bottom: 1rem;
          color: var(--text-primary);
        }
        
        .installation-steps ol {
          margin-left: 1.5rem;
          color: var(--text-secondary);
        }
        
        .installation-steps li {
          margin-bottom: 0.5rem;
        }
        
        .installation-steps code {
          background: #f1f5f9;
          padding: 0.2rem 0.4rem;
          border-radius: 4px;
          font-family: 'Monaco', 'Consolas', monospace;
          font-size: 0.9rem;
        }
        
        footer {
          text-align: center;
          margin-top: 4rem;
          padding: 2rem 0;
          border-top: 1px solid var(--border);
          color: var(--text-secondary);
        }
        
        .status-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          background: var(--success-color);
          color: white;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 600;
          margin-left: 1rem;
        }
        
        @media (max-width: 768px) {
          .container { padding: 1rem; }
          header { margin: 0 -1rem 3rem -1rem; padding: 2rem 1rem; }
          h1 { font-size: 2rem; }
          .features { grid-template-columns: 1fr; gap: 1rem; }
          .feature, .component { padding: 1.5rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">🌟</div>
            <h1>PrismWeave</h1>
            <p class="subtitle">Capture web pages as clean markdown and sync to your document repository. Available as a browser extension and bookmarklet.</p>
        </header>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">📝</div>
                <h3>Clean Markdown</h3>
                <p>Converts web pages to clean, readable markdown with proper formatting and structure preservation.</p>
            </div>
            
            <div class="feature">
                <div class="feature-icon">🔄</div>
                <h3>GitHub Sync</h3>
                <p>Automatically commits captured content to your GitHub repository with organized folder structure.</p>
            </div>
            
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <h3>Multiple Methods</h3>
                <p>Use the browser extension for full integration or the bookmarklet for quick, universal access.</p>
            </div>
        </div>
        
        <div class="component">
            <h2><span class="component-icon">🧩</span> Browser Extension <span class="status-badge">Recommended</span></h2>
            <p>Full-featured Chrome/Edge extension with keyboard shortcuts, context menus, and advanced settings.</p>
            
            <div style="margin: 1.5rem 0;">
                <a href="./extension/" class="btn">📁 Download Extension</a>
                <a href="./extension/options/options.html" class="btn btn-secondary">⚙️ Preview Settings</a>
            </div>
            
            <div class="installation-steps">
                <h4>📋 Installation Instructions:</h4>
                <ol>
                    <li>Download the extension files from the link above</li>
                    <li>Open Chrome/Edge and go to <code>chrome://extensions/</code></li>
                    <li>Enable "Developer mode" (toggle in top-right)</li>
                    <li>Click "Load unpacked" and select the downloaded extension folder</li>
                    <li>Configure your GitHub token and repository in the extension options</li>
                </ol>
            </div>
        </div>
        
        <div class="component">
            <h2><span class="component-icon">🔖</span> Bookmarklet</h2>
            <p>Lightweight bookmarklet for quick page capture without installing an extension. Works in any browser.</p>
            
            <div style="margin: 1.5rem 0;">
                <a href="./bookmarklet/" class="btn">📁 Get Bookmarklet</a>
                <a href="./bookmarklet/help.html" class="btn btn-secondary">📖 Instructions</a>
            </div>
            
            <div class="installation-steps">
                <h4>📋 Quick Setup:</h4>
                <ol>
                    <li>Visit the bookmarklet page above</li>
                    <li>Drag the "PrismWeave Capture" button to your bookmarks bar</li>
                    <li>Configure your GitHub settings in the setup form</li>
                    <li>Click the bookmark on any page to capture content</li>
                </ol>
            </div>
        </div>
        
        <footer>
            <p>
                <strong>PrismWeave v${version}</strong> • 
                Built on ${buildTime.split('T')[0]} • 
                <a href="https://github.com/davidhayesbc/PrismWeave" style="color: var(--primary-color);">View Source on GitHub</a>
            </p>
        </footer>
    </div>
</body>
</html>`;

    await fs.promises.writeFile(path.join(webDir, 'index.html'), indexHtml);
    this.success(`Generated web index: ${webDir}/index.html`);
  }
}

// CLI Interface
async function main() {
  const builder = new PrismWeaveBuildSystem();
  const args = process.argv.slice(2);
  const command = args[0];
  const component = args[1];

  try {
    switch (command) {
      case 'build':
        if (component) {
          await builder.buildSingleComponent(component);
        } else {
          await builder.buildAll();
        }
        break;
        
      case 'clean':
        await builder.clean();
        break;
        
      case 'web':
        await builder.webBuild();
        break;
        
      default:
        console.log(`
🔧 PrismWeave Unified Build System

Usage:
  node build.js <command> [component]

Commands:
  build [component]  - Build all components or specific component
  clean             - Clean all build outputs
  web               - Build for web deployment

Components:
  browser-extension - Chrome/Edge browser extension
  bookmarklet      - Standalone bookmarklet files
  dev-tools        - Development and testing tools

Examples:
  node build.js build                    # Build everything
  node build.js build browser-extension  # Build only extension
  node build.js build bookmarklet        # Build only bookmarklet
  node build.js web                      # Build for web deployment
  node build.js clean                    # Clean all outputs
        `);
    }
  } catch (error) {
    console.error('❌ Build failed:', error.message);
    if (process.argv.includes('--verbose')) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

// Export for programmatic use
module.exports = { PrismWeaveBuildSystem };

// Run if called directly
if (require.main === module) {
  main();
}
