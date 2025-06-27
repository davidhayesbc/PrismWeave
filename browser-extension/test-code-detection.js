/**
 * Quick test to see if enhanced code block detection is working
 */

const { JSDOM } = require('jsdom');

async function testEnhancedCodeDetection() {
  const url = 'https://www.docker.com/blog/how-to-make-ai-chatbot-from-scratch/';

  console.log('🔧 Testing enhanced code block detection...');
  console.log('🔗 URL:', url);

  const response = await fetch(url);
  const html = await response.text();

  console.log(`📄 HTML size: ${html.length} chars`);

  // Look for code-related elements in the HTML
  const dom = new JSDOM(html);
  const { document } = dom.window;

  // Check for various code-related elements
  const preElements = document.querySelectorAll('pre');
  const codeElements = document.querySelectorAll('code');
  const codeBlocks = document.querySelectorAll('pre code');

  console.log('\n📊 CODE ELEMENTS FOUND:');
  console.log(`   <pre> elements: ${preElements.length}`);
  console.log(`   <code> elements: ${codeElements.length}`);
  console.log(`   <pre><code> combinations: ${codeBlocks.length}`);

  // Sample some code content
  console.log('\n📋 SAMPLE CODE CONTENT:');

  if (codeBlocks.length > 0) {
    console.log('🔍 First few <pre><code> blocks:');
    Array.from(codeBlocks)
      .slice(0, 3)
      .forEach((block, i) => {
        const text = block.textContent.trim();
        console.log(`   ${i + 1}. "${text.substring(0, 100)}${text.length > 100 ? '...' : ''}"`);
      });
  }

  if (preElements.length > 0) {
    console.log('\n🔍 First few <pre> (without <code>) blocks:');
    Array.from(preElements)
      .filter(pre => !pre.querySelector('code'))
      .slice(0, 3)
      .forEach((block, i) => {
        const text = block.textContent.trim();
        console.log(`   ${i + 1}. "${text.substring(0, 100)}${text.length > 100 ? '...' : ''}"`);
      });
  }

  // Look for command-like text patterns
  const commandPatterns = [
    'git clone',
    'docker model pull',
    'docker compose',
    'function App',
    'const \\[', // Escaped for regex
    'npm install',
    'cd ',
  ];

  console.log('\n🔍 COMMAND PATTERNS IN TEXT:');
  commandPatterns.forEach(pattern => {
    const count = (html.match(new RegExp(pattern, 'gi')) || []).length;
    if (count > 0) {
      console.log(`   "${pattern}": found ${count} times`);
    }
  });

  return {
    preElements: preElements.length,
    codeElements: codeElements.length,
    codeBlocks: codeBlocks.length,
  };
}

testEnhancedCodeDetection()
  .then(results => {
    console.log('\n✅ Test completed:', results);
  })
  .catch(error => {
    console.error('❌ Test failed:', error);
  });
