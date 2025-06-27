/**
 * Test the enhanced PRE element handling
 */

const { JSDOM } = require('jsdom');

async function testPreElementHandling() {
  const url = 'https://www.docker.com/blog/how-to-make-ai-chatbot-from-scratch/';

  console.log('🔧 Testing enhanced PRE element handling...');

  const response = await fetch(url);
  const html = await response.text();

  const dom = new JSDOM(html);
  const { document } = dom.window;

  // Get all PRE elements
  const preElements = Array.from(document.querySelectorAll('pre'));

  console.log(`📊 Found ${preElements.length} <pre> elements`);

  // Test our isCodeLikeContent logic on each PRE element
  preElements.slice(0, 5).forEach((pre, index) => {
    const text = pre.textContent.trim();
    console.log(`\n📋 PRE Element ${index + 1}:`);
    console.log(
      `   Content (first 100 chars): "${text.substring(0, 100)}${text.length > 100 ? '...' : ''}"`
    );

    // Test our detection logic
    const hasTreeStructure = text.includes('├──') || text.includes('└──') || text.includes('│');
    const hasGitCommand = /^git\s+/m.test(text);
    const hasDockerCommand = /^docker\s+/m.test(text);
    const hasFunctionPattern = /function\s+\w+\s*\(/.test(text);
    const hasMultipleLines = text.split('\n').length > 1;

    console.log(`   Tree structure: ${hasTreeStructure}`);
    console.log(`   Git command: ${hasGitCommand}`);
    console.log(`   Docker command: ${hasDockerCommand}`);
    console.log(`   Function pattern: ${hasFunctionPattern}`);
    console.log(`   Multiple lines: ${hasMultipleLines}`);

    // What language would be detected?
    let detectedLanguage = '';
    if (hasGitCommand || hasDockerCommand || text.match(/^\$\s+/m)) {
      detectedLanguage = 'bash';
    } else if (text.match(/(?:function|const|let|var|=>|\.then|async|await|import.*from|export)/)) {
      detectedLanguage = text.match(/interface|type\s+\w+|:\s*\w+\[\]|<\w+>/)
        ? 'typescript'
        : 'javascript';
    }

    console.log(`   Detected language: "${detectedLanguage}"`);
    console.log(
      `   Would be formatted as code block: ${hasTreeStructure || hasGitCommand || hasDockerCommand || hasFunctionPattern || hasMultipleLines}`
    );
  });
}

testPreElementHandling()
  .then(() => {
    console.log('\n✅ PRE element analysis completed');
  })
  .catch(error => {
    console.error('❌ Test failed:', error);
  });
