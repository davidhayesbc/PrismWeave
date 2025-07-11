// Debug script to analyze Stack Overflow blog structure
// Run this in browser console on SO blog page to understand DOM structure

console.log('=== Stack Overflow Blog DOM Analysis ===');

// Check what content selectors exist
const selectors = [
  'article',
  'main',
  '[role="main"]',
  '.content',
  '.post',
  '.entry',
  '#content',
  '.s-prose',
  '.js-post-body',
  '.post-content',
  '.blog-post',
  '.entry-content',
  '.article-content',
];

console.log('\n--- Checking selectors ---');
selectors.forEach(selector => {
  const element = document.querySelector(selector);
  if (element) {
    const textLength = element.textContent?.trim().length || 0;
    console.log(`✓ ${selector}: ${textLength} chars`);
    console.log(`  Classes: ${element.className}`);
    console.log(`  ID: ${element.id}`);
    console.log(`  Tag: ${element.tagName}`);
    console.log(`  First 100 chars: "${element.textContent?.trim().substring(0, 100)}..."`);
    console.log('---');
  } else {
    console.log(`✗ ${selector}: not found`);
  }
});

// Check for blog-specific elements
console.log('\n--- Blog-specific elements ---');
const blogSelectors = [
  '.blog-article',
  '.blog-content',
  '.blog-post',
  '.article',
  '.post-body',
  '.content-body',
  '[data-article]',
  '[data-post]',
];

blogSelectors.forEach(selector => {
  const element = document.querySelector(selector);
  if (element) {
    console.log(`✓ ${selector}: ${element.textContent?.trim().length} chars`);
  }
});

// Check page title and meta
console.log('\n--- Page metadata ---');
console.log(`Title: ${document.title}`);
console.log(`URL: ${window.location.href}`);
console.log(`Domain: ${window.location.hostname}`);

// Find largest content block
console.log('\n--- Content analysis ---');
const allDivs = document.querySelectorAll('div');
let largestContent = { element: null, length: 0 };

allDivs.forEach(div => {
  const text = div.textContent?.trim() || '';
  if (text.length > largestContent.length) {
    largestContent = { element: div, length: text.length };
  }
});

if (largestContent.element) {
  console.log(`Largest content block: ${largestContent.length} chars`);
  console.log(`Classes: ${largestContent.element.className}`);
  console.log(`ID: ${largestContent.element.id}`);
  console.log(
    `First 200 chars: "${largestContent.element.textContent?.trim().substring(0, 200)}..."`
  );
}

// Check for navigation and promotional content
console.log('\n--- Unwanted content detection ---');
const unwantedSelectors = [
  'nav',
  '.navigation',
  '.sidebar',
  '.footer',
  '.header',
  '.promo',
  '.advertisement',
  '.social',
  '.related',
  '.comments',
];

unwantedSelectors.forEach(selector => {
  const elements = document.querySelectorAll(selector);
  if (elements.length > 0) {
    console.log(`${selector}: ${elements.length} elements found`);
  }
});

// Look for content with "Stack Overflow" promotional text
console.log('\n--- Promotional content ---');
const allText = document.body.textContent || '';
const promoPatterns = [
  'Stack Overflow for Teams',
  'Products',
  'Recent articles',
  'Latest Podcast',
  'Add to the discussion',
];

promoPatterns.forEach(pattern => {
  if (allText.includes(pattern)) {
    console.log(`Found promotional pattern: "${pattern}"`);
  }
});

console.log('\n=== Analysis Complete ===');
