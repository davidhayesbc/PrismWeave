#!/usr/bin/env node

/**
 * Simplified Build System for PrismWeave
 * 
 * This simplified build system delegates most work to npm workspaces while retaining
 * brand asset generation (converting SVG logo to various icon sizes).
 * 
 * Workflow:
 *   npm run build          → builds all components via workspaces
 *   npm run build:web      → runs scripts/build-web.js (web distribution)
 *   npm run clean          → cleans all build artifacts
 * 
 * This file now focuses on:
 *   - Brand asset generation (logo.svg → various PNG icons)
 *   - Clean operations
 *   - CLI orchestration
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class PrismWeaveBuildSystem {
  constructor() {
    this.projectRoot = __dirname;
    this.isProduction = process.env.NODE_ENV === 'production';
  }

  /**
   * Main build entry point
   */
  async build(target = 'all') {
    console.log(`🔨 Building PrismWeave - Target: ${target}`);
    console.log(`📦 Environment: ${this.isProduction ? 'Production' : 'Development'}`);

    try {
      switch (target) {
        case 'all':
        case 'build':
          await this.buildAll();
          break;
        case 'browser-extension':
          await this.buildComponent('browser-extension');
          break;
        case 'cli':
          await this.buildComponent('cli');
          break;
        case 'web':
          await this.buildWeb();
          break;
        case 'clean':
          await this.clean();
          break;
        case 'brand-assets':
          await this.generateBrandAssets();
          break;
        default:
          console.error(`❌ Unknown build target: ${target}`);
          console.log('Available targets: all, browser-extension, cli, web, clean, brand-assets');
          process.exit(1);
      }

      console.log('✅ Build completed successfully!');
    } catch (error) {
      console.error('❌ Build failed:', error.message);
      process.exit(1);
    }
  }

  /**
   * Build all components using npm workspaces
   */
  async buildAll() {
    console.log('🏗️ Building all components...\n');

    // Generate brand assets first so they're available for builds
    await this.generateBrandAssets().catch((e) =>
      console.warn('⚠️  Brand asset generation skipped:', e.message),
    );

    // Build all workspace projects
    console.log('📦 Building workspace projects...');
    execSync('npm run build --workspaces --if-present', {
      cwd: this.projectRoot,
      stdio: 'inherit',
    });

    console.log('\n✅ All components built successfully');
  }

  /**
   * Build a specific component by workspace name
   */
  async buildComponent(component) {
    console.log(`📦 Building ${component}...`);

    // Generate brand assets for browser extension (needs icons)
    if (component === 'browser-extension') {
      await this.generateBrandAssets().catch((e) =>
        console.warn('⚠️  Brand asset generation skipped:', e.message),
      );
    }

    execSync(`npm run build --workspace=${component}`, {
      cwd: this.projectRoot,
      stdio: 'inherit',
    });

    console.log(`✅ ${component} built successfully`);
  }

  /**
   * Build web distribution
   */
  async buildWeb() {
    console.log('🌐 Building web distribution...');

    // Generate brand assets
    await this.generateBrandAssets().catch((e) =>
      console.warn('⚠️  Brand asset generation skipped:', e.message),
    );

    // Build website and browser extension (required for web dist)
    console.log('📦 Building dependencies...');
    execSync('npm run build --workspace=website', {
      cwd: this.projectRoot,
      stdio: 'inherit',
    });
    execSync('npm run build --workspace=browser-extension', {
      cwd: this.projectRoot,
      stdio: 'inherit',
    });

    // Assemble web distribution
    console.log('📦 Assembling web distribution...');
    execSync('node scripts/build-web.js', {
      cwd: this.projectRoot,
      stdio: 'inherit',
    });

    console.log('✅ Web distribution built successfully');
  }

  /**
   * Clean all build artifacts
   */
  async clean() {
    console.log('🧹 Cleaning build artifacts...');

    const dirsToClean = [
      path.join(this.projectRoot, 'dist'),
      path.join(this.projectRoot, '.build-cache'),
    ];

    for (const dir of dirsToClean) {
      if (fs.existsSync(dir)) {
        fs.rmSync(dir, { recursive: true, force: true });
        console.log(`  🗑️  Removed ${path.relative(this.projectRoot, dir)}`);
      }
    }

    // Clean workspace projects
    console.log('🧹 Cleaning workspace projects...');
    try {
      execSync('npm run clean --workspaces --if-present', {
        cwd: this.projectRoot,
        stdio: 'inherit',
      });
    } catch (error) {
      console.warn('⚠️  Some workspace clean operations failed (this is usually ok)');
    }

    console.log('✅ Clean completed');
  }

  /**
   * Generate brand assets (logo.svg → various PNG icons)
   * This is the only complex function retained from the original build system
   */
  async generateBrandAssets() {
    console.log('🎨 Generating brand assets...');

    const logoSvgPath = path.join(this.projectRoot, 'logo.svg');
    if (!fs.existsSync(logoSvgPath)) {
      console.warn('⚠️  logo.svg not found, skipping brand asset generation');
      return;
    }

    // Load sharp for SVG rasterization
    let sharp;
    try {
      sharp = require('sharp');
    } catch (e) {
      console.warn(
        '⚠️  sharp is not installed; skipping icon generation. Install with: npm install -D sharp',
      );
      return;
    }

    const svgContent = fs.readFileSync(logoSvgPath, 'utf8');

    // Extract the logo-mark symbol for compact icon rendering
    const markMatch = svgContent.match(
      /<symbol[^>]*id=["']logo-mark["'][^>]*>([\s\S]*?)<\/symbol>/i,
    );
    const markInner = markMatch ? markMatch[1] : null;

    // Create minimal SVG wrapper for the mark (fallback to full SVG if no mark)
    const markSvg = markInner
      ? `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" style="color:#111">\n  ${markInner}\n</svg>`
      : svgContent;

    // Define output paths
    const rootLogoPng = path.join(this.projectRoot, 'logo.png');
    const extIconsDir = path.join(this.projectRoot, 'browser-extension', 'icons');
    const websiteAssetsDir = path.join(this.projectRoot, 'website', 'assets');

    this.ensureDirectory(extIconsDir);
    this.ensureDirectory(websiteAssetsDir);

    // 1. Generate root logo.png at high resolution
    await sharp(Buffer.from(svgContent))
      .resize(1024, 1024, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png()
      .toFile(rootLogoPng);
    console.log('  ✓ Generated logo.png');

    // 2. Generate browser extension icons from compact mark
    const iconSizes = [16, 32, 48, 64, 128];
    for (const size of iconSizes) {
      const outPath = path.join(extIconsDir, `icon${size}.png`);
      await sharp(Buffer.from(markSvg))
        .resize(size, size, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
        .png()
        .toFile(outPath);
    }
    console.log('  ✓ Generated browser extension icons (16, 32, 48, 64, 128)');

    // 3. Generate website assets
    fs.copyFileSync(logoSvgPath, path.join(websiteAssetsDir, 'logo.svg'));
    
    await sharp(Buffer.from(svgContent))
      .resize(512, 512, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png()
      .toFile(path.join(websiteAssetsDir, 'logo.png'));

    // Generate PWA icons
    const pwaIcons = [192, 384, 512];
    for (const size of pwaIcons) {
      const outPath = path.join(websiteAssetsDir, `icon-${size}.png`);
      await sharp(Buffer.from(svgContent))
        .resize(size, size, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 1 } })
        .png()
        .toFile(outPath);
    }
    console.log('  ✓ Generated website assets (logo.svg, logo.png, PWA icons)');
    
    console.log('✅ Brand assets generated successfully');
  }

  /**
   * Ensure directory exists
   */
  ensureDirectory(dir) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }
}

// CLI entry point
if (require.main === module) {
  const target = process.argv[2] || 'all';
  const builder = new PrismWeaveBuildSystem();
  builder.build(target);
}

module.exports = PrismWeaveBuildSystem;
