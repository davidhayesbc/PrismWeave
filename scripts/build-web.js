#!/usr/bin/env node

/**
 * Simplified Web Distribution Builder for PrismWeave
 * 
 * Assembles the web distribution by copying built assets from workspace projects.
 * This replaces the complex incremental copy logic from the old build.js.
 * 
 * Prerequisites: All workspace projects must be built first
 *   - npm run build --workspace=website
 *   - npm run build --workspace=browser-extension
 *   - npm run build:bookmarklet --workspace=browser-extension
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const distWeb = path.join(rootDir, 'dist', 'web');

/**
 * Recursively copy directory contents
 */
async function copyDir(src, dest) {
  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

/**
 * Build web distribution
 */
async function buildWeb() {
  console.log('📦 Building web distribution...\n');
  
  // Clean dist/web
  console.log('🧹 Cleaning dist/web...');
  await fs.rm(distWeb, { recursive: true, force: true });
  await fs.mkdir(distWeb, { recursive: true });
  
  // Copy website
  console.log('📄 Copying website...');
  await copyDir(
    path.join(rootDir, 'website', 'dist'),
    distWeb
  );
  
  // Copy browser extension distribution
  console.log('🔌 Copying browser extension...');
  await copyDir(
    path.join(rootDir, 'browser-extension', 'dist'),
    path.join(distWeb, 'extension')
  );
  
  // Copy bookmarklet
  const bookmarkletSrc = path.join(rootDir, 'browser-extension', 'dist-bookmarklet', 'bookmarklet.js');
  console.log('🔖 Copying bookmarklet...');
  try {
    await fs.copyFile(
      bookmarkletSrc,
      path.join(distWeb, 'bookmarklet.js')
    );
  } catch (err) {
    console.warn(`⚠️  Bookmarklet not found (${bookmarkletSrc}) - run build:bookmarklet first`);
  }
  
  console.log('✅ Web distribution built successfully!\n');
  console.log(`📁 Output: ${distWeb}`);
}

// Run if executed directly
buildWeb().catch(err => {
  console.error('❌ Build failed:', err);
  process.exit(1);
});
