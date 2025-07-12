/**
 * Complete Anthropic Content Extraction Validation Test
 *
 * This script validates the enhanced PrismWeave content extraction for Anthropic research pages.
 *
 * To use:
 * 1. Navigate to: https://www.anthropic.com/research/project-vend-1?utm_source=tldrwebdev
 * 2. Open browser console (F12)
 * 3. Paste and run this script
 * 4. Review the detailed extraction report
 */

console.log('🚀 PrismWeave Anthropic Content Extraction Validation');
console.log('===================================================');

// Test configuration
const TEST_CONFIG = {
  minContentLength: 500,
  minParagraphs: 2,
  minHeadings: 1,
  expectedResearchTerms: [
    'research',
    'study',
    'experiment',
    'project',
    'analysis',
    'claude',
    'anthropic',
  ],
  maxNavigationRatio: 0.3,
};

function runCompleteValidation() {
  console.log('📊 Starting comprehensive validation...');

  const results = {
    selectorTest: testAnthropicSelectors(),
    scoringTest: testScoringAlgorithm(),
    contentQuality: validateContentQuality(),
    extractionAccuracy: testExtractionAccuracy(),
    researchDetection: testResearchContentDetection(),
  };

  // Generate final report
  generateValidationReport(results);

  return results;
}

function testAnthropicSelectors() {
  console.log('🔍 Testing Anthropic-specific selectors...');

  const anthropicSelectors = [
    // Primary research content containers
    'main article',
    'article',
    'main',
    '[role="main"]',

    // Research-specific containers
    '.research-content',
    '.article-content',
    '.post-content',
    '.blog-content',
    '.content',
    '.main-content',

    // Next.js/React patterns
    '#__next main',
    '[data-reactroot] main',
    '#__next article',
    '[data-reactroot] article',

    // Data attributes
    '[data-testid="article"]',
    '[data-testid="content"]',
    '[data-component="article"]',

    // Container patterns
    '.container main',
    '.wrapper main',
    '.layout main',
    '.content-container',
    '.article-container',

    // Pattern-based selectors
    '[class*="research"]',
    '[class*="article"]',
    '[class*="content"]',
  ];

  const selectorResults = [];

  for (const selector of anthropicSelectors) {
    try {
      const element = document.querySelector(selector);
      if (element) {
        const contentLength = element.textContent?.length || 0;
        const isValid = contentLength >= TEST_CONFIG.minContentLength;

        selectorResults.push({
          selector,
          found: true,
          contentLength,
          isValid,
          tagName: element.tagName,
          className: element.className,
          textPreview: element.textContent?.substring(0, 100) + '...',
        });

        if (isValid) {
          console.log(`✅ ${selector}: Found valid content (${contentLength} chars)`);
        } else {
          console.log(`⚠️ ${selector}: Found but insufficient content (${contentLength} chars)`);
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
    `📈 Selector test results: ${validSelectors.length}/${selectorResults.length} selectors found valid content`
  );

  return {
    totalSelectors: selectorResults.length,
    validSelectors: validSelectors.length,
    results: selectorResults,
    success: validSelectors.length > 0,
  };
}

function testScoringAlgorithm() {
  console.log('🎯 Testing enhanced scoring algorithm...');

  const candidates = Array.from(document.querySelectorAll('div, section, article, main'))
    .map(element => ({
      element,
      score: scoreElement(element),
      tagName: element.tagName,
      className: element.className,
      contentLength: element.textContent?.length || 0,
      paragraphs: element.querySelectorAll('p').length,
      headings: element.querySelectorAll('h1, h2, h3, h4, h5, h6').length,
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 10); // Top 10 candidates

  console.log('🏆 Top scoring elements:');
  candidates.forEach((candidate, index) => {
    console.log(
      `${index + 1}. Score: ${candidate.score}, Tag: ${candidate.tagName}, Content: ${candidate.contentLength} chars, Structure: ${candidate.paragraphs}p/${candidate.headings}h`
    );
  });

  const topCandidate = candidates[0];
  const hasGoodScore = topCandidate && topCandidate.score > 500;
  const hasGoodStructure =
    topCandidate &&
    topCandidate.paragraphs >= TEST_CONFIG.minParagraphs &&
    topCandidate.headings >= TEST_CONFIG.minHeadings;

  return {
    topScore: topCandidate?.score || 0,
    topCandidate: topCandidate,
    candidates: candidates,
    hasGoodScore,
    hasGoodStructure,
    success: hasGoodScore && hasGoodStructure,
  };
}

function validateContentQuality() {
  console.log('📝 Validating content quality...');

  // Find the best content element using our logic
  const bestElement = findBestContentElement();

  if (!bestElement) {
    console.log('❌ No content element found');
    return { success: false, error: 'No content element found' };
  }

  const text = bestElement.textContent?.trim() || '';
  const className = bestElement.className.toLowerCase();

  // Quality metrics
  const metrics = {
    contentLength: text.length,
    wordCount: text.split(/\s+/).filter(word => word.length > 0).length,
    paragraphs: bestElement.querySelectorAll('p').length,
    headings: bestElement.querySelectorAll('h1, h2, h3, h4, h5, h6').length,
    links: bestElement.querySelectorAll('a').length,
    images: bestElement.querySelectorAll('img').length,
    hasResearchContent: TEST_CONFIG.expectedResearchTerms.some(term =>
      text.toLowerCase().includes(term)
    ),
    navigationRatio: calculateNavigationRatio(bestElement),
  };

  // Quality checks
  const checks = {
    sufficientLength: metrics.contentLength >= TEST_CONFIG.minContentLength,
    goodStructure:
      metrics.paragraphs >= TEST_CONFIG.minParagraphs &&
      metrics.headings >= TEST_CONFIG.minHeadings,
    researchContent: metrics.hasResearchContent,
    lowNavigationRatio: metrics.navigationRatio <= TEST_CONFIG.maxNavigationRatio,
  };

  const qualityScore = Object.values(checks).filter(Boolean).length / Object.keys(checks).length;

  console.log('📊 Content quality metrics:');
  console.log(`   Length: ${metrics.contentLength} characters`);
  console.log(`   Words: ${metrics.wordCount}`);
  console.log(`   Structure: ${metrics.paragraphs} paragraphs, ${metrics.headings} headings`);
  console.log(`   Research content: ${metrics.hasResearchContent ? 'Yes' : 'No'}`);
  console.log(`   Navigation ratio: ${(metrics.navigationRatio * 100).toFixed(1)}%`);
  console.log(`   Quality score: ${(qualityScore * 100).toFixed(1)}%`);

  return {
    element: bestElement,
    metrics,
    checks,
    qualityScore,
    success: qualityScore >= 0.75, // 75% quality threshold
  };
}

function testExtractionAccuracy() {
  console.log('🎯 Testing extraction accuracy...');

  const extractedElement = findBestContentElement();
  if (!extractedElement) {
    return { success: false, error: 'No content extracted' };
  }

  // Check if we captured the main research content
  const extractedText = extractedElement.textContent?.toLowerCase() || '';

  // Key indicators that we got the right content
  const accuracyChecks = {
    hasProjectTitle: extractedText.includes('project') || extractedText.includes('vend'),
    hasAnthropicMention: extractedText.includes('anthropic') || extractedText.includes('claude'),
    hasResearchContext: TEST_CONFIG.expectedResearchTerms.some(term =>
      extractedText.includes(term)
    ),
    hasSubstantialContent: extractedText.length > 2000,
    notNavigationOnly: !isNavigationContent(extractedElement),
  };

  const accuracyScore =
    Object.values(accuracyChecks).filter(Boolean).length / Object.keys(accuracyChecks).length;

  console.log('🎯 Extraction accuracy checks:');
  Object.entries(accuracyChecks).forEach(([check, passed]) => {
    console.log(`   ${passed ? '✅' : '❌'} ${check}`);
  });
  console.log(`   Accuracy score: ${(accuracyScore * 100).toFixed(1)}%`);

  return {
    element: extractedElement,
    checks: accuracyChecks,
    accuracyScore,
    success: accuracyScore >= 0.8, // 80% accuracy threshold
  };
}

function testResearchContentDetection() {
  console.log('🔬 Testing research content detection...');

  const pageText = document.body.textContent?.toLowerCase() || '';
  const detectedTerms = TEST_CONFIG.expectedResearchTerms.filter(term => pageText.includes(term));

  const bestElement = findBestContentElement();
  const extractedText = bestElement?.textContent?.toLowerCase() || '';
  const extractedTerms = TEST_CONFIG.expectedResearchTerms.filter(term =>
    extractedText.includes(term)
  );

  const detectionRatio = extractedTerms.length / Math.max(detectedTerms.length, 1);

  console.log('🔬 Research content detection:');
  console.log(`   Terms in page: ${detectedTerms.join(', ')}`);
  console.log(`   Terms extracted: ${extractedTerms.join(', ')}`);
  console.log(`   Detection ratio: ${(detectionRatio * 100).toFixed(1)}%`);

  return {
    pageTerms: detectedTerms,
    extractedTerms: extractedTerms,
    detectionRatio,
    success: detectionRatio >= 0.7, // 70% detection threshold
  };
}

// Helper functions

function findBestContentElement() {
  // This mirrors our enhanced extraction logic
  const candidates = Array.from(document.querySelectorAll('main, article, div, section'))
    .filter(el => {
      const text = el.textContent?.trim() || '';
      return text.length >= TEST_CONFIG.minContentLength;
    })
    .sort((a, b) => scoreElement(b) - scoreElement(a));

  return candidates.length > 0 ? candidates[0] : null;
}

function scoreElement(element) {
  let score = 0;
  const text = element.textContent?.trim() || '';
  const className = element.className.toLowerCase();

  // Base score from content length
  score += Math.min(text.length / 15, 400);

  // Anthropic-specific scoring enhancements
  if (window.location.href.includes('anthropic.com')) {
    if (className.includes('research')) score += 250;
    if (className.includes('article')) score += 200;
    if (className.includes('content')) score += 150;
    if (className.includes('main')) score += 100;

    if (element.tagName === 'MAIN' || element.tagName === 'ARTICLE') {
      score += 200;
    }

    // Research content indicators
    TEST_CONFIG.expectedResearchTerms.forEach(term => {
      if (text.toLowerCase().includes(term)) score += 50;
    });
  }

  // Structure bonuses
  score += element.querySelectorAll('p').length * 25;
  score += element.querySelectorAll('h1, h2, h3, h4, h5, h6').length * 30;

  // Navigation penalties
  const navTerms = ['nav', 'menu', 'header', 'footer', 'sidebar'];
  navTerms.forEach(term => {
    if (className.includes(term)) score -= 150;
  });

  return Math.max(0, score);
}

function calculateNavigationRatio(element) {
  const links = element.querySelectorAll('a').length;
  const paragraphs = element.querySelectorAll('p').length;
  return links / Math.max(paragraphs, 1);
}

function isNavigationContent(element) {
  const className = element.className.toLowerCase();
  const navTerms = ['nav', 'menu', 'header', 'footer', 'sidebar', 'navigation'];
  return navTerms.some(term => className.includes(term));
}

function generateValidationReport(results) {
  console.log('\n📊 VALIDATION REPORT');
  console.log('==================');

  const overallSuccess = Object.values(results).every(r => r.success);

  console.log(`🎯 Overall Status: ${overallSuccess ? '✅ PASS' : '❌ FAIL'}`);
  console.log('\n📋 Test Results:');

  Object.entries(results).forEach(([testName, result]) => {
    const status = result.success ? '✅' : '❌';
    console.log(`   ${status} ${testName}: ${result.success ? 'PASS' : 'FAIL'}`);

    if (testName === 'contentQuality' && result.qualityScore) {
      console.log(`      Quality Score: ${(result.qualityScore * 100).toFixed(1)}%`);
    }

    if (testName === 'extractionAccuracy' && result.accuracyScore) {
      console.log(`      Accuracy Score: ${(result.accuracyScore * 100).toFixed(1)}%`);
    }

    if (testName === 'researchDetection' && result.detectionRatio) {
      console.log(`      Detection Ratio: ${(result.detectionRatio * 100).toFixed(1)}%`);
    }
  });

  if (overallSuccess) {
    console.log('\n🎉 SUCCESS: Anthropic content extraction is working correctly!');
    console.log('   The enhanced PrismWeave extension should now properly extract');
    console.log('   research content from Anthropic pages.');
  } else {
    console.log('\n⚠️ Issues detected. Check individual test results above.');
  }

  console.log('\n🔗 To test with PrismWeave extension:');
  console.log('   1. Load the built extension in Chrome');
  console.log('   2. Click the extension icon on this page');
  console.log('   3. Verify content extraction works properly');

  return overallSuccess;
}

// Run the complete validation
console.log('🧪 Starting validation test...\n');
const validationResults = runCompleteValidation();

console.log('\n✨ Validation completed!');
console.log('Check the detailed report above for results.');
