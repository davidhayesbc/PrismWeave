#!/usr/bin/env node

/**
 * Direct comparison test between browser extension and dev-tools output
 * This script will help identify remaining differences
 */

const fs = require('fs');
const path = require('path');

// Docker blog URL for testing
const TEST_URL = 'https://www.docker.com/blog/how-to-make-ai-chatbot-from-scratch/';

async function runDevToolsCapture() {
  console.log('🔧 Running dev-tools capture...');

  const { execSync } = require('child_process');
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = `test-outputs/comparison-devtools-${timestamp}.md`;

  try {
    execSync(`npx ts-node url-test-cli.ts "${TEST_URL}"`, {
      cwd: path.join(__dirname, 'dev-tools'),
      stdio: 'inherit',
    });

    // Find the most recent output file
    const testOutputDir = path.join(__dirname, 'dev-tools', 'test-outputs');
    const files = fs
      .readdirSync(testOutputDir)
      .filter(f => f.endsWith('.md'))
      .sort()
      .reverse();

    if (files.length > 0) {
      const latestFile = path.join(testOutputDir, files[0]);
      const content = fs.readFileSync(latestFile, 'utf8');
      return {
        content,
        lineCount: content.split('\n').length,
        charCount: content.length,
        filePath: latestFile,
      };
    }

    return null;
  } catch (error) {
    console.error('❌ Dev-tools capture failed:', error.message);
    return null;
  }
}

function analyzeDifferences(devToolsResult, browserExtensionResult) {
  console.log('\n📊 COMPARISON ANALYSIS');
  console.log('='.repeat(50));

  if (!devToolsResult || !browserExtensionResult) {
    console.log('❌ Cannot compare - missing results');
    return;
  }

  console.log(`📄 Dev-tools: ${devToolsResult.lineCount} lines, ${devToolsResult.charCount} chars`);
  console.log(
    `🌐 Browser ext: ${browserExtensionResult.lineCount} lines, ${browserExtensionResult.charCount} chars`
  );

  const lineDiff = browserExtensionResult.lineCount - devToolsResult.lineCount;
  const charDiff = browserExtensionResult.charCount - devToolsResult.charCount;

  console.log(
    `📈 Difference: ${lineDiff > 0 ? '+' : ''}${lineDiff} lines, ${charDiff > 0 ? '+' : ''}${charDiff} chars`
  );

  // Analyze content structure
  const devLines = devToolsResult.content.split('\n');
  const browserLines = browserExtensionResult.content.split('\n');

  console.log('\n🔍 CONTENT ANALYSIS');
  console.log('-'.repeat(30));

  // Check frontmatter
  const devHasFrontmatter = devLines[0] === '---';
  const browserHasFrontmatter = browserLines[0] === '---';
  console.log(`📝 Frontmatter - Dev: ${devHasFrontmatter}, Browser: ${browserHasFrontmatter}`);

  // Check for tree structures
  const devTreeLines = devLines.filter(line => line.includes('├──') || line.includes('└──'));
  const browserTreeLines = browserLines.filter(
    line => line.includes('├──') || line.includes('└──')
  );
  console.log(
    `🌳 Tree structure lines - Dev: ${devTreeLines.length}, Browser: ${browserTreeLines.length}`
  );

  // Check for code blocks
  const devCodeBlocks = (devToolsResult.content.match(/```/g) || []).length / 2;
  const browserCodeBlocks = (browserExtensionResult.content.match(/```/g) || []).length / 2;
  console.log(`💻 Code blocks - Dev: ${devCodeBlocks}, Browser: ${browserCodeBlocks}`);

  // Check for headers
  const devHeaders = devLines.filter(line => line.startsWith('#'));
  const browserHeaders = browserLines.filter(line => line.startsWith('#'));
  console.log(`📑 Headers - Dev: ${devHeaders.length}, Browser: ${browserHeaders.length}`);

  // Find missing sections (simple approach)
  console.log('\n🔍 POTENTIAL MISSING CONTENT');
  console.log('-'.repeat(35));

  // Look for sections that appear in browser but not in dev-tools
  const devText = devToolsResult.content.toLowerCase();
  const browserText = browserExtensionResult.content.toLowerCase();

  const samplePhrases = [
    'docker model runner',
    'prometheus',
    'grafana',
    'jaeger',
    'kubernetes',
    'monitoring',
    'observability',
    'architecture',
    'prerequisites',
    'installation',
  ];

  samplePhrases.forEach(phrase => {
    const inDev = devText.includes(phrase);
    const inBrowser = browserText.includes(phrase);
    if (inBrowser && !inDev) {
      console.log(`❌ Missing in dev-tools: "${phrase}"`);
    } else if (inDev && !inBrowser) {
      console.log(`❌ Missing in browser: "${phrase}"`);
    } else if (inDev && inBrowser) {
      console.log(`✅ Both have: "${phrase}"`);
    }
  });
}

async function main() {
  console.log('🚀 Starting comparison test...');
  console.log(`🔗 Test URL: ${TEST_URL}`);

  // Run dev-tools capture
  const devToolsResult = await runDevToolsCapture();

  if (!devToolsResult) {
    console.log('❌ Cannot continue without dev-tools result');
    return;
  }

  console.log(`✅ Dev-tools result: ${devToolsResult.lineCount} lines`);

  // For browser extension, we'll need to provide instructions
  console.log('\n🌐 BROWSER EXTENSION TEST INSTRUCTIONS');
  console.log('='.repeat(50));
  console.log('1. Load the browser extension in Chrome/Edge');
  console.log('2. Navigate to:', TEST_URL);
  console.log('3. Open extension popup and click capture');
  console.log('4. Copy the markdown output and save as comparison-browser-ext.md');
  console.log('5. Run this script again to compare results');

  // Check if browser extension result exists
  const browserExtFile = path.join(__dirname, 'comparison-browser-ext.md');
  if (fs.existsSync(browserExtFile)) {
    console.log('📄 Found browser extension result file');
    const browserContent = fs.readFileSync(browserExtFile, 'utf8');
    const browserExtensionResult = {
      content: browserContent,
      lineCount: browserContent.split('\n').length,
      charCount: browserContent.length,
      filePath: browserExtFile,
    };

    analyzeDifferences(devToolsResult, browserExtensionResult);
  } else {
    console.log(
      '📋 Browser extension result not found. Please capture manually and save as comparison-browser-ext.md'
    );
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { runDevToolsCapture, analyzeDifferences };
