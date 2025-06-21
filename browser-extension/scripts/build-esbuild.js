// Modern build script using esbuild for optimal browser extension builds
const esbuild = require('esbuild');
const fs = require('fs');
const path = require('path');

async function buildExtension() {
  console.log('Building PrismWeave Browser Extension with esbuild...');
  
  // Clean dist directory
  if (fs.existsSync('./dist')) {
    fs.rmSync('./dist', { recursive: true });
  }
  fs.mkdirSync('./dist', { recursive: true });

  try {
    // Build service worker (needs to be IIFE for Chrome extensions)
    await esbuild.build({
      entryPoints: ['src/background/service-worker.ts'],
      bundle: false, // Don't bundle for service worker - use importScripts
      outfile: 'dist/background/service-worker.js',
      format: 'iife',
      platform: 'browser',
      target: 'es2020',
      sourcemap: true,
      minify: false,
      define: {
        'process.env.NODE_ENV': '"production"'
      }
    });

    // Build utilities for service worker (individual files for importScripts)
    const utilFiles = fs.readdirSync('src/utils').filter(f => f.endsWith('.ts'));
    for (const file of utilFiles) {
      await esbuild.build({
        entryPoints: [`src/utils/${file}`],
        outfile: `dist/utils/${file.replace('.ts', '.js')}`,
        format: 'iife',
        platform: 'browser',
        target: 'es2020',
        sourcemap: true,
        globalName: file.replace('.ts', '').replace(/[-_](.)/g, (_, c) => c.toUpperCase()),
        minify: false
      });
    }

    // Build content scripts (can use ES modules)
    await esbuild.build({
      entryPoints: ['src/content/content-script.ts'],
      outfile: 'dist/content/content-script.js',
      format: 'iife',
      platform: 'browser',
      target: 'es2020',
      sourcemap: true,
      minify: false
    });

    // Build popup (can use ES modules)
    await esbuild.build({
      entryPoints: ['src/popup/popup.ts'],
      outfile: 'dist/popup/popup.js',
      format: 'iife',
      platform: 'browser',
      target: 'es2020',
      sourcemap: true,
      minify: false
    });

    // Build options page
    await esbuild.build({
      entryPoints: ['src/options/options.ts'],
      outfile: 'dist/options/options.js',
      format: 'iife',
      platform: 'browser',
      target: 'es2020',
      sourcemap: true,
      minify: false
    });

    console.log('✓ TypeScript compilation completed with esbuild');
    
    // Copy static files
    await copyStaticFiles();
    
    console.log('✓ Build completed successfully!');
    
  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

async function copyStaticFiles() {
  // Copy HTML files
  const htmlFiles = [
    { src: 'src/popup/popup.html', dest: 'dist/popup/popup.html' },
    { src: 'src/popup/popup.css', dest: 'dist/popup/popup.css' },
    { src: 'src/options/options.html', dest: 'dist/options/options.html' },
    { src: 'src/options/options.css', dest: 'dist/options/options.css' }
  ];

  for (const file of htmlFiles) {
    if (fs.existsSync(file.src)) {
      fs.copyFileSync(file.src, file.dest);
      console.log(`Copied: ${file.dest}`);
    }
  }

  // Copy manifest
  fs.copyFileSync('manifest.json', 'dist/manifest.json');
  
  // Copy icons
  fs.mkdirSync('dist/icons', { recursive: true });
  const iconFiles = fs.readdirSync('icons');
  for (const icon of iconFiles) {
    if (icon.endsWith('.png')) {
      fs.copyFileSync(`icons/${icon}`, `dist/icons/${icon}`);
    }
  }

  // Copy libs
  fs.mkdirSync('dist/libs', { recursive: true });
  if (fs.existsSync('src/libs')) {
    const libFiles = fs.readdirSync('src/libs');
    for (const lib of libFiles) {
      fs.copyFileSync(`src/libs/${lib}`, `dist/libs/${lib}`);
    }
  }
}

// Run the build
if (require.main === module) {
  buildExtension().catch(console.error);
}

module.exports = { buildExtension };
