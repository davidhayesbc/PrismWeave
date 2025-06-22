// Quick test script for Docker blog content extraction
// Run this in the browser console on https://www.docker.com/blog/how-to-make-ai-chatbot-from-scratch/

console.log('=== Docker Blog Content Extraction Test ===');
console.log('Current URL:', window.location.href);
console.log('Document ready state:', document.readyState);

// Test various selectors
const selectors = [
  'article',
  'main',
  '.content',
  '.post-content',
  '.entry-content',
  '.article-content',
  '.blog-content',
  '.container',
  '.single-post',
  '.post',
  '.blog-post',
  'div[class*="content"]',
  'div[class*="post"]',
  'div[class*="article"]',
  'section',
  '.row',
  '[role="main"]'
];

console.log('\n=== Testing Content Selectors ===');
selectors.forEach(selector => {
  try {
    const elements = document.querySelectorAll(selector);
    if (elements.length > 0) {
      console.log(`${selector}: Found ${elements.length} element(s)`);
      elements.forEach((el, i) => {
        if (i < 2) { // Only show first 2
          const textLen = el.textContent?.trim().length || 0;
          const htmlLen = el.innerHTML?.length || 0;
          console.log(`  [${i}] ${el.tagName}.${el.className} - Text: ${textLen}, HTML: ${htmlLen}`);
          if (textLen > 1000) {
            console.log(`    ✓ GOOD CANDIDATE - Has substantial text content`);
          }
        }
      });
    }
  } catch (e) {
    console.warn(`Error with selector ${selector}:`, e);
  }
});

// Find the element with the most text content
console.log('\n=== Finding Best Content Element ===');
const allElements = document.querySelectorAll('*');
let bestElement = null;
let maxTextLength = 0;

Array.from(allElements).forEach(el => {
  const textLength = el.textContent?.trim().length || 0;
  if (textLength > maxTextLength && textLength > 500) {
    // Make sure it's not body or html
    if (el.tagName !== 'BODY' && el.tagName !== 'HTML') {
      bestElement = el;
      maxTextLength = textLength;
    }
  }
});

if (bestElement) {
  console.log('Best content element found:');
  console.log(`Tag: ${bestElement.tagName}`);
  console.log(`Class: ${bestElement.className}`);
  console.log(`ID: ${bestElement.id}`);
  console.log(`Text length: ${maxTextLength}`);
  console.log(`HTML length: ${bestElement.innerHTML?.length || 0}`);
  console.log('Element:', bestElement);
} else {
  console.log('No good content element found');
}

// Test specific Docker selectors
console.log('\n=== Testing Docker-Specific Patterns ===');
const dockerSelectors = [
  '.DockerBlogPost',
  '.blog-article',
  '.article-wrapper',
  '[data-testid*="content"]',
  '[data-testid*="post"]',
  'div[class*="blog"]',
  'section[class*="content"]'
];

dockerSelectors.forEach(selector => {
  const elements = document.querySelectorAll(selector);
  if (elements.length > 0) {
    console.log(`Docker selector "${selector}": Found ${elements.length} elements`);
  }
});

console.log('\n=== Quick Extraction Test ===');
// Try a quick manual extraction
const candidates = [
  document.querySelector('main'),
  document.querySelector('article'),
  document.querySelector('.content'),
  document.querySelector('.post-content'),
  document.querySelector('.container')
].filter(Boolean);

candidates.forEach((el, i) => {
  if (el) {
    const text = el.textContent?.trim() || '';
    console.log(`Candidate ${i + 1}: ${el.tagName}.${el.className} - ${text.length} chars`);
    if (text.length > 500) {
      console.log(`  Preview: ${text.substring(0, 100)}...`);
    }
  }
});
