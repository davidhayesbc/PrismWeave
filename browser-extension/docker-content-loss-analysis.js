// Docker Blog Content Loss Analysis
// Run this in the browser console to see what's happening during content extraction

(function () {
  console.log('=== Docker Blog Content Loss Analysis ===');
  console.log('URL:', window.location.href);

  // Simulate the exact extraction process
  const mainElement = document.querySelector('main');
  if (!mainElement) {
    console.log('❌ No main element found');
    return;
  }

  console.log('✅ Main element found');
  console.log('📏 Original main element text length:', mainElement.textContent?.length || 0);
  console.log('📏 Original main element HTML length:', mainElement.innerHTML?.length || 0);

  // Clone to avoid modifying original
  const cloned = mainElement.cloneNode(true);
  console.log('📋 Cloned element text length:', cloned.textContent?.length || 0);

  // Check what unwanted selectors would remove
  const unwantedSelectors = [
    'script',
    'style',
    'noscript',
    'iframe[src*="ads"]',
    'iframe[src*="advertisement"]',
    'iframe[src*="google"]',
    'embed[src*="ads"]',
    'object[data*="ads"]',
    '.ad',
    '.ads',
    '.advertisement',
    '.banner',
    '.popup',
    '.modal',
    '.overlay',
    '.social-share',
    '.share-buttons',
    '.comments-section',
    '.related-posts',
    '.sidebar',
    '.widget',
    '.newsletter-signup',
    '.subscription-box',
    '.email-signup',
    '.social-links',
    '.author-bio',
    '.author-card',
    '.breadcrumb',
    '.pagination',
    '.tag-list',
    '.category-list',
    '.metadata',
    '.post-meta',
    '.article-meta',
    '.sharing',
    '.social-sharing',
    '.follow-buttons',
    '.call-to-action',
    '.cta',
    '.promo-box',
    '.advertisement-block',
    'nav',
    'header:not(.article-header):not(.post-header)',
    'footer:not(.article-footer):not(.post-footer)',
    'aside:not(.content-aside)',
    '.navigation',
    '.nav',
    '.menu',
    '.navbar',
    '.header',
    '.footer',
    '.top-bar',
    '.bottom-bar',
    '.cookie-notice',
    '.privacy-notice',
    '.gdpr-notice',
    '.consent-banner',
  ];

  console.log('\n=== Checking Unwanted Element Removal ===');

  let totalRemovedChars = 0;
  unwantedSelectors.forEach(selector => {
    try {
      const elements = cloned.querySelectorAll(selector);
      if (elements.length > 0) {
        let selectorRemovedChars = 0;
        elements.forEach(el => {
          selectorRemovedChars += el.textContent?.length || 0;
        });

        if (selectorRemovedChars > 0) {
          console.log(`🗑️ ${selector}: ${elements.length} elements, ${selectorRemovedChars} chars`);
          totalRemovedChars += selectorRemovedChars;
        }

        elements.forEach(el => el.remove());
      }
    } catch (e) {
      console.log(`❌ Error with selector ${selector}:`, e.message);
    }
  });

  console.log(`📊 Total removed by unwanted selectors: ${totalRemovedChars} chars`);
  console.log(`📏 After unwanted removal: ${cloned.textContent?.length || 0} chars`);

  // Check empty element removal
  console.log('\n=== Checking Empty Element Removal ===');
  const emptyElements = cloned.querySelectorAll('div:empty, span:empty, p:empty, section:empty');
  console.log(`🗑️ Empty elements to remove: ${emptyElements.length}`);
  emptyElements.forEach(el => el.remove());
  console.log(`📏 After empty removal: ${cloned.textContent?.length || 0} chars`);

  // Check whitespace-only removal
  console.log('\n=== Checking Whitespace-Only Removal ===');
  const allElements = cloned.querySelectorAll('*');
  let whitespaceRemovedCount = 0;
  let whitespaceRemovedChars = 0;

  for (let i = 0; i < allElements.length; i++) {
    const el = allElements[i];
    if (el.children.length === 0 && (!el.textContent || el.textContent.trim() === '')) {
      whitespaceRemovedChars += el.textContent?.length || 0;
      whitespaceRemovedCount++;
      el.remove();
    }
  }

  console.log(
    `🗑️ Whitespace-only elements removed: ${whitespaceRemovedCount} (${whitespaceRemovedChars} chars)`
  );
  console.log(`📏 After whitespace removal: ${cloned.textContent?.length || 0} chars`);

  // Check for ad-like content removal
  console.log('\n=== Checking Ad-like Content Removal ===');
  const suspiciousElements = cloned.querySelectorAll('div, span, section, aside');
  let adRemovedCount = 0;
  let adRemovedChars = 0;

  const adKeywords = [
    'advertisement',
    'sponsored',
    'promoted',
    'ads by',
    'google ads',
    'affiliate',
    'partner content',
    'paid promotion',
    'shop now',
    'buy now',
    'get deal',
    'limited time',
    'subscribe now',
  ];

  for (let i = 0; i < suspiciousElements.length; i++) {
    const el = suspiciousElements[i];
    const text = el.textContent?.toLowerCase() || '';
    const className = el.className?.toLowerCase() || '';
    const id = el.id?.toLowerCase() || '';
    const combinedText = `${text} ${id} ${className}`.toLowerCase();

    const isAd = adKeywords.some(keyword => combinedText.includes(keyword));
    if (isAd) {
      adRemovedChars += el.textContent?.length || 0;
      adRemovedCount++;
      el.remove();
    }
  }

  console.log(`🗑️ Ad-like elements removed: ${adRemovedCount} (${adRemovedChars} chars)`);
  console.log(`📏 Final content length: ${cloned.textContent?.length || 0} chars`);
  console.log(`📄 Final HTML length: ${cloned.innerHTML?.length || 0} chars`);

  // Show the actual content that remains
  console.log('\n=== Final Content Analysis ===');
  const finalText = cloned.textContent?.trim() || '';
  console.log(`📝 First 200 chars: "${finalText.substring(0, 200)}..."`);

  // Check what major sections remain
  const remainingHeadings = cloned.querySelectorAll('h1, h2, h3, h4, h5, h6');
  const remainingParagraphs = cloned.querySelectorAll('p');
  const remainingCode = cloned.querySelectorAll('pre, code');

  console.log(`🏷️ Remaining headings: ${remainingHeadings.length}`);
  console.log(`📄 Remaining paragraphs: ${remainingParagraphs.length}`);
  console.log(`💻 Remaining code blocks: ${remainingCode.length}`);

  if (remainingHeadings.length > 0) {
    console.log('📋 Heading text samples:');
    Array.from(remainingHeadings)
      .slice(0, 3)
      .forEach((h, i) => {
        console.log(`  ${i + 1}. "${h.textContent?.trim()}"`);
      });
  }

  // Try to identify what's causing the massive content loss
  console.log('\n=== Content Loss Investigation ===');
  const originalLength = mainElement.textContent?.length || 0;
  const finalLength = cloned.textContent?.length || 0;
  const lossPercentage = (((originalLength - finalLength) / originalLength) * 100).toFixed(1);

  console.log(
    `📊 Content loss: ${originalLength} → ${finalLength} chars (${lossPercentage}% lost)`
  );

  if (lossPercentage > 80) {
    console.log('🚨 CRITICAL: Over 80% content loss detected!');
    console.log('🔍 This suggests the cleaning process is too aggressive');

    // Let's check what the .entry-content div specifically contains
    const entryContent = document.querySelector('.entry-content');
    if (entryContent) {
      console.log('\n=== Entry Content Analysis ===');
      console.log(`📏 .entry-content text length: ${entryContent.textContent?.length || 0}`);
      console.log(`📄 .entry-content HTML length: ${entryContent.innerHTML?.length || 0}`);

      const entryHeadings = entryContent.querySelectorAll('h1, h2, h3, h4, h5, h6');
      const entryParagraphs = entryContent.querySelectorAll('p');
      console.log(`🏷️ Entry headings: ${entryHeadings.length}`);
      console.log(`📄 Entry paragraphs: ${entryParagraphs.length}`);

      if (entryParagraphs.length > 0) {
        console.log('📝 First paragraph sample:');
        console.log(`"${entryParagraphs[0].textContent?.trim().substring(0, 150)}..."`);
      }
    }
  }

  // Final recommendation
  console.log('\n=== Recommendation ===');
  if (finalLength < 1000) {
    console.log('💡 Suggestion: Use .entry-content instead of main element');
    console.log('💡 The main element includes too much navigation/sidebar content');
  } else {
    console.log('✅ Content extraction appears successful');
  }
})();
