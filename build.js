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
    const indexHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrismWeave - Web Components</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; }
        .component { margin: 2rem 0; padding: 1.5rem; border: 1px solid #ddd; border-radius: 8px; }
        .component h2 { margin-top: 0; color: #333; }
        .component a { color: #0066cc; text-decoration: none; }
        .component a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>🌟 PrismWeave Web Components</h1>
    <p>Welcome to PrismWeave's web-deployable components.</p>
    
    <div class="component">
        <h2>Browser Extension</h2>
        <p><a href="./extension/">View Extension Files →</a></p>
        <p>Chrome/Edge browser extension for capturing web pages.</p>
    </div>
    
    <div class="component">
        <h2>Bookmarklet</h2>
        <p><a href="./bookmarklet/">View Bookmarklet →</a></p>
        <p>Standalone bookmarklet for web page capture without extension.</p>
    </div>
    
    <footer>
        <p><small>Built on ${new Date().toISOString()}</small></p>
    </footer>
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
