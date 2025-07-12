/**
 * GitHub Markdown Content Extraction Test
 *
 * This script tests the GitHub-specific content extraction functionality
 * to ensure we capture markdown file content instead of GitHub navigation.
 *
 * To use:
 * 1. Navigate to: https://github.com/davidhayesbc/PrismWeaveDocs/blob/main/documents/research/2025-07-12-anthropic-com-project-vend-can-claude-run-a-small-shop-and-why-d.md
 * 2. Open browser console (F12)
 * 3. Paste and run this script
 * 4. Review the extraction results
 */

console.log('🚀 GitHub Markdown Content Extraction Test');
console.log('=========================================');

// Test configuration for GitHub content
const GITHUB_TEST_CONFIG = {
  minContentLength: 200,
  expectedMarkdownElements: ['h1', 'h2', 'h3', 'p'],
  maxNavigationRatio: 0.2,
  expectedContentTerms: ['project', 'vend', 'claude', 'anthropic', 'research'],
};

function runGitHubExtractionTest() {
  console.log('📊 Starting GitHub extraction test...');

  const results = {
    selectorTest: testGitHubSelectors(),
    contentQuality: validateGitHubContentQuality(),
    markdownDetection: testMarkdownDetection(),
    navigationAvoidance: testNavigationAvoidance(),
  };

  generateGitHubTestReport(results);

  return results;
}

function testGitHubSelectors() {
  console.log('🔍 Testing GitHub-specific selectors...');

  const githubSelectors = [
    // Main markdown content area
    '.markdown-body',
    'article.markdown-body',
    '.repository-content .markdown-body',
    '.Box-body .markdown-body',

    // File content containers
    '.file-editor-textarea',
    '.blob-wrapper',
    '.highlight',
    '.blob-code-content',

    // Repository content area
    '.repository-content',
    '.file-navigation + .Box .Box-body',
    '.file-navigation ~ .Box .Box-body',

    // Content containers
    '.Box-body',
    '.container-lg .Box-body',
    '.application-main .Box-body',

    // Readme and markdown specific
    '#readme .markdown-body',
    '[data-testid="readme"] .markdown-body',
    '.readme .markdown-body',

    // File view content
    '.file .highlight',
    '.file .blob-wrapper',
    '.file .Box-body',

    // Generic content fallbacks
    'main .Box-body',
    '[role="main"] .Box-body',
    '.Layout-main .Box-body',
  ];

  const selectorResults = [];

  for (const selector of githubSelectors) {
    try {
      const element = document.querySelector(selector);
      if (element) {
        const contentLength = element.textContent?.length || 0;
        const isValid =
          contentLength >= GITHUB_TEST_CONFIG.minContentLength && isValidGitHubContent(element);

        selectorResults.push({
          selector,
          found: true,
          contentLength,
          isValid,
          tagName: element.tagName,
          className: element.className,
          hasMarkdownContent: hasMarkdownStructure(element),
          textPreview: element.textContent?.substring(0, 150) + '...',
        });

        if (isValid) {
          console.log(`✅ ${selector}: Valid content (${contentLength} chars)`);
        } else {
          console.log(`⚠️ ${selector}: Found but invalid (${contentLength} chars)`);
        }
      }
    } catch (error) {
      console.warn(`❌ ${selector}: Invalid selector`, error);
      selectorResults.push({
        selector,
        found: false,
        error: error.message,
      });
    }
  }

  const validSelectors = selectorResults.filter(r => r.isValid);
  console.log(
    `📈 GitHub selector results: ${validSelectors.length}/${selectorResults.length} selectors found valid content`
  );

  return {
    totalSelectors: selectorResults.length,
    validSelectors: validSelectors.length,
    results: selectorResults,
    success: validSelectors.length > 0,
  };
}

function validateGitHubContentQuality() {
  console.log('📝 Validating GitHub content quality...');

  const bestElement = findBestGitHubContent();

  if (!bestElement) {
    console.log('❌ No GitHub content element found');
    return { success: false, error: 'No content element found' };
  }

  const text = bestElement.textContent?.trim() || '';
  const className = bestElement.className.toLowerCase();

  // Quality metrics for GitHub content
  const metrics = {
    contentLength: text.length,
    wordCount: text.split(/\s+/).filter(word => word.length > 0).length,
    headings: bestElement.querySelectorAll('h1, h2, h3, h4, h5, h6').length,
    paragraphs: bestElement.querySelectorAll('p').length,
    links: bestElement.querySelectorAll('a').length,
    hasMarkdownClass: className.includes('markdown'),
    hasExpectedTerms: GITHUB_TEST_CONFIG.expectedContentTerms.some(term =>
      text.toLowerCase().includes(term)
    ),
    navigationRatio: calculateNavigationRatio(bestElement),
    isGitHubNavigation: isGitHubNavigationContent(bestElement),
  };

  // Quality checks
  const checks = {
    sufficientLength: metrics.contentLength >= GITHUB_TEST_CONFIG.minContentLength,
    hasMarkdownStructure: metrics.headings > 0 || metrics.paragraphs > 0,
    hasExpectedContent: metrics.hasExpectedTerms,
    lowNavigationRatio: metrics.navigationRatio <= GITHUB_TEST_CONFIG.maxNavigationRatio,
    notPureNavigation: !metrics.isGitHubNavigation,
    hasMarkdownIndicators: metrics.hasMarkdownClass || hasMarkdownStructure(bestElement),
  };

  const qualityScore = Object.values(checks).filter(Boolean).length / Object.keys(checks).length;

  console.log('📊 GitHub content quality:');
  console.log(`   Length: ${metrics.contentLength} characters`);
  console.log(`   Structure: ${metrics.paragraphs} paragraphs, ${metrics.headings} headings`);
  console.log(`   Expected content: ${metrics.hasExpectedTerms ? 'Yes' : 'No'}`);
  console.log(`   Markdown indicators: ${checks.hasMarkdownIndicators ? 'Yes' : 'No'}`);
  console.log(`   Navigation ratio: ${(metrics.navigationRatio * 100).toFixed(1)}%`);
  console.log(`   Quality score: ${(qualityScore * 100).toFixed(1)}%`);

  return {
    element: bestElement,
    metrics,
    checks,
    qualityScore,
    success: qualityScore >= 0.7, // 70% quality threshold for GitHub
  };
}

function testMarkdownDetection() {
  console.log('📋 Testing markdown content detection...');

  const markdownElements = document.querySelectorAll('.markdown-body, .blob-wrapper, .highlight');
  const hasMarkdownContent = markdownElements.length > 0;

  let bestMarkdownElement = null;
  let maxContentLength = 0;

  markdownElements.forEach(element => {
    const contentLength = element.textContent?.length || 0;
    if (contentLength > maxContentLength) {
      maxContentLength = contentLength;
      bestMarkdownElement = element;
    }
  });

  const detectionResults = {
    foundMarkdownElements: markdownElements.length,
    hasMarkdownContent,
    bestContentLength: maxContentLength,
    containsExpectedTerms: bestMarkdownElement
      ? GITHUB_TEST_CONFIG.expectedContentTerms.some(term =>
          bestMarkdownElement.textContent?.toLowerCase().includes(term)
        )
      : false,
  };

  console.log('📋 Markdown detection results:');
  console.log(`   Found ${detectionResults.foundMarkdownElements} markdown elements`);
  console.log(`   Best content length: ${detectionResults.bestContentLength} chars`);
  console.log(
    `   Contains expected terms: ${detectionResults.containsExpectedTerms ? 'Yes' : 'No'}`
  );

  return {
    ...detectionResults,
    success: hasMarkdownContent && detectionResults.bestContentLength > 500,
  };
}

function testNavigationAvoidance() {
  console.log('🚫 Testing navigation content avoidance...');

  const bestContent = findBestGitHubContent();
  if (!bestContent) {
    return { success: false, error: 'No content found' };
  }

  const text = bestContent.textContent?.toLowerCase() || '';
  const className = bestContent.className.toLowerCase();

  // Check for GitHub navigation indicators
  const navigationIndicators = [
    'navigation',
    'nav',
    'menu',
    'header',
    'footer',
    'sidebar',
    'breadcrumb',
    'pagehead',
    'subnav',
    'file navigation',
    'repository navigation',
    'sign in',
    'homepage',
    'contact support',
    'github status',
    'features',
    'pricing',
    'enterprise',
  ];

  const foundNavIndicators = navigationIndicators.filter(
    indicator => text.includes(indicator) || className.includes(indicator.replace(/\s+/g, '-'))
  );

  const navContentRatio = foundNavIndicators.length / navigationIndicators.length;
  const isLikelyNavigation = navContentRatio > 0.3 || foundNavIndicators.length > 5;

  console.log('🚫 Navigation avoidance results:');
  console.log(`   Found navigation indicators: ${foundNavIndicators.length}`);
  console.log(`   Navigation indicators: ${foundNavIndicators.join(', ')}`);
  console.log(`   Navigation ratio: ${(navContentRatio * 100).toFixed(1)}%`);
  console.log(`   Likely navigation content: ${isLikelyNavigation ? 'Yes' : 'No'}`);

  return {
    foundNavIndicators,
    navContentRatio,
    isLikelyNavigation,
    success: !isLikelyNavigation,
  };
}

// Helper functions

function findBestGitHubContent() {
  // Try GitHub-specific selectors first
  const githubSelectors = [
    '.markdown-body',
    '.repository-content .markdown-body',
    '.Box-body .markdown-body',
    '.blob-wrapper',
    '.highlight',
    '.repository-content',
    '.Box-body',
  ];

  for (const selector of githubSelectors) {
    const element = document.querySelector(selector);
    if (element && isValidGitHubContent(element)) {
      return element;
    }
  }

  // Fallback to structure analysis
  const candidates = Array.from(document.querySelectorAll('div, section, article, main'))
    .filter(el => {
      const text = el.textContent?.trim() || '';
      return text.length >= GITHUB_TEST_CONFIG.minContentLength;
    })
    .sort((a, b) => scoreGitHubElement(b) - scoreGitHubElement(a));

  return candidates.length > 0 ? candidates[0] : null;
}

function isValidGitHubContent(element) {
  const text = element.textContent?.trim() || '';
  const className = element.className.toLowerCase();

  if (text.length < GITHUB_TEST_CONFIG.minContentLength) return false;

  const hasMarkdownIndicators =
    className.includes('markdown') ||
    className.includes('blob') ||
    className.includes('highlight') ||
    className.includes('file') ||
    className.includes('readme');

  const navTerms = ['header', 'footer', 'nav', 'menu', 'sidebar', 'breadcrumb', 'pagehead'];
  const isNavContent = navTerms.some(term => className.includes(term));

  if (isNavContent && !hasMarkdownIndicators) return false;

  return hasMarkdownIndicators || text.length > 500;
}

function hasMarkdownStructure(element) {
  const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6').length;
  const paragraphs = element.querySelectorAll('p').length;
  const codeBlocks = element.querySelectorAll('pre, code').length;

  return headings > 0 || paragraphs > 2 || codeBlocks > 0;
}

function scoreGitHubElement(element) {
  let score = 0;
  const text = element.textContent?.trim() || '';
  const className = element.className.toLowerCase();

  // Base score from text length
  score += Math.min(text.length / 10, 300);

  // GitHub-specific bonuses
  const contentBonuses = [
    { term: 'markdown-body', bonus: 300 },
    { term: 'blob-wrapper', bonus: 250 },
    { term: 'highlight', bonus: 200 },
    { term: 'repository-content', bonus: 180 },
    { term: 'box-body', bonus: 150 },
  ];

  contentBonuses.forEach(({ term, bonus }) => {
    if (className.includes(term)) score += bonus;
  });

  // Structure bonuses
  score += element.querySelectorAll('h1, h2, h3, h4, h5, h6').length * 25;
  score += element.querySelectorAll('p').length * 15;

  return Math.max(0, score);
}

function calculateNavigationRatio(element) {
  const links = element.querySelectorAll('a').length;
  const paragraphs = Math.max(element.querySelectorAll('p').length, 1);
  return links / paragraphs;
}

function isGitHubNavigationContent(element) {
  const text = element.textContent?.toLowerCase() || '';
  const className = element.className.toLowerCase();

  const strongNavIndicators = [
    'sign in',
    'homepage',
    'contact support',
    'github status',
    'skip to content',
    'site-wide links',
    'navigation menu',
  ];

  return (
    strongNavIndicators.some(indicator => text.includes(indicator)) ||
    className.includes('header') ||
    className.includes('navigation') ||
    className.includes('pagehead')
  );
}

function generateGitHubTestReport(results) {
  console.log('\n📊 GITHUB EXTRACTION TEST REPORT');
  console.log('================================');

  const overallSuccess = Object.values(results).every(r => r.success);

  console.log(`🎯 Overall Status: ${overallSuccess ? '✅ PASS' : '❌ FAIL'}`);
  console.log('\n📋 Test Results:');

  Object.entries(results).forEach(([testName, result]) => {
    const status = result.success ? '✅' : '❌';
    console.log(`   ${status} ${testName}: ${result.success ? 'PASS' : 'FAIL'}`);

    if (testName === 'contentQuality' && result.qualityScore) {
      console.log(`      Quality Score: ${(result.qualityScore * 100).toFixed(1)}%`);
    }

    if (testName === 'navigationAvoidance' && result.navContentRatio !== undefined) {
      console.log(`      Navigation Ratio: ${(result.navContentRatio * 100).toFixed(1)}%`);
    }
  });

  if (overallSuccess) {
    console.log('\n🎉 SUCCESS: GitHub markdown extraction is working correctly!');
    console.log('   The PrismWeave extension should now properly extract');
    console.log('   markdown file content from GitHub instead of navigation.');
  } else {
    console.log('\n⚠️ Issues detected. Check individual test results above.');
    console.log('   The extension may still be capturing GitHub navigation');
    console.log('   instead of the actual markdown file content.');
  }

  console.log('\n🔗 To test with PrismWeave extension:');
  console.log('   1. Load the updated extension in Chrome');
  console.log('   2. Click the extension icon on this GitHub page');
  console.log('   3. Verify it extracts the markdown content, not navigation');

  return overallSuccess;
}

// Run the test
console.log('🧪 Starting GitHub extraction test...\n');
const testResults = runGitHubExtractionTest();

console.log('\n✨ GitHub test completed!');
console.log('Check the detailed report above for results.');
