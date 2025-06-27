/**
 * Quick test to capture Docker blog with dev-tools and compare line count
 */

const { JSDOM } = require('jsdom');

// Minimal implementation to test current output
async function testDockerBlogCapture() {
  const url = 'https://www.docker.com/blog/how-to-make-ai-chatbot-from-scratch/';

  console.log('🔧 Fetching Docker blog...');
  const response = await fetch(url);
  const html = await response.text();

  console.log(`📄 HTML size: ${html.length} chars`);

  // Create DOM
  const dom = new JSDOM(html, { url });
  const { document } = dom.window;

  // Extract main content (simplified)
  let content = '';

  // Look for main content selectors
  const selectors = [
    'main',
    '[role="main"]',
    '.content',
    '.post-content',
    '.entry-content',
    '.article-content',
    'article',
    '.blog-post',
  ];

  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      content = element.innerHTML;
      console.log(`✅ Found content using selector: ${selector}`);
      break;
    }
  }

  if (!content) {
    // Fallback to body
    content = document.body.innerHTML;
    console.log('⚠️ Using fallback: document.body');
  }

  console.log(`📄 Extracted content: ${content.length} chars`);

  // Convert to markdown (basic)
  // We'll just remove HTML tags for a quick test
  let markdown = content
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  // Add frontmatter
  const frontmatter = `---
captureDate: "${new Date().toISOString()}"
tags: []
---

`;

  markdown = frontmatter + markdown;

  const lineCount = markdown.split('\n').length;

  console.log('📊 RESULTS:');
  console.log(`   Lines: ${lineCount}`);
  console.log(`   Characters: ${markdown.length}`);
  console.log(`   First 200 chars: ${markdown.substring(0, 200)}...`);

  return { markdown, lineCount, charCount: markdown.length };
}

// Run test
testDockerBlogCapture()
  .then(result => {
    console.log('✅ Test completed');
  })
  .catch(error => {
    console.error('❌ Test failed:', error);
  });
