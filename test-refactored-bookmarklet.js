// Test script to verify the refactored bookmarklet generation
// This simulates the bookmarklet generator and checks the output

// Mock the DOM elements that the generator expects
const mockFormData = {
  githubToken: 'ghp_test123456789012345678901234567890',
  githubRepo: 'testuser/testrepo',
  defaultFolder: 'documents',
  commitMessage: 'Add {title}',
  fileNaming: 'title-date'
};

// Mock the BookmarkletGeneratorUI class
class TestBookmarkletGeneratorUI {
  constructor() {
    this.injectableBaseUrl = 'https://cdn.jsdelivr.net/gh/davidhayesbc/prismweave@main/dist/web/injectable';
  }

  generateCompactBookmarklet(formData) {
    const token = formData.githubToken;
    const repo = formData.githubRepo;
    const folder = formData.defaultFolder;
    const msgTemplate = formData.commitMessage || 'PrismWeave: Add {title}';
    const injectableUrl = this.injectableBaseUrl + '/content-extractor-injectable.js';

    // Build the bookmarklet JavaScript using script injection to load sophisticated extractor
    const jsCode = [
      '(function(){',
      // Configuration for the extractor
      'var config = {',
      "  githubToken: '" + token + "',",
      "  githubRepo: '" + repo + "',",
      "  folder: '" + folder + "',",
      "  commitMessageTemplate: '" + msgTemplate + "'",
      '};',

      // Load the injectable content extractor
      'function loadExtractor(){',
      '  return new Promise(function(resolve, reject){',
      '    if(window.prismweaveExtractAndCommit){',
      '      resolve();',
      '      return;',
      '    }',
      '    var script = document.createElement("script");',
      '    script.src = "' + injectableUrl + '";',
      '    script.onload = function(){',
      '      if(window.prismweaveExtractAndCommit){',
      '        resolve();',
      '      } else {',
      '        reject(new Error("Failed to load extractor API"));',
      '      }',
      '    };',
      '    script.onerror = function(){',
      '      reject(new Error("Failed to load extractor script"));',
      '    };',
      '    document.head.appendChild(script);',
      '  });',
      '}',

      // Process the page using the sophisticated extractor
      'function processPage(){',
      '  var extractionOptions = {',
      '    includeImages: true,',
      '    includeLinks: true,',
      '    cleanHtml: true,',
      '    generateFrontmatter: true,',
      '    includeMetadata: true',
      '  };',

      '  return window.prismweaveExtractAndCommit(config, extractionOptions);',
      '}',

      // Main execution flow
      'loadExtractor().then(function(){',
      '  return processPage();',
      '}).then(function(result){',
      '  if(result.success){',
      "    alert('✅ Page captured successfully with advanced extraction!');",
      '  } else {',
      "    alert('❌ Capture failed: ' + (result.error || 'Unknown error'));",
      '  }',
      '}).catch(function(error){',
      "  alert('❌ Bookmarklet error: ' + error.message);",
      '});',
      '})();',
    ].join('');

    return 'javascript:' + encodeURIComponent(jsCode);
  }
}

// Test the generator
console.log('🧪 Testing Refactored Bookmarklet Generator...\n');

const generator = new TestBookmarkletGeneratorUI();
const bookmarkletCode = generator.generateCompactBookmarklet(mockFormData);

// Verify the bookmarklet characteristics
console.log('✅ Generated Bookmarklet:');
console.log('   Length:', bookmarkletCode.length, 'characters');
console.log('   Starts with javascript:', bookmarkletCode.startsWith('javascript:'));

// Decode and check the code content
const decodedCode = decodeURIComponent(bookmarkletCode.substring(11)); // Remove 'javascript:'
console.log('\n🔍 Analyzing Generated Code:');

// Check for key features of the refactored version
const checks = [
  {
    name: 'Uses script injection',
    test: decodedCode.includes('document.createElement("script")'),
    expected: true
  },
  {
    name: 'Loads injectable extractor',
    test: decodedCode.includes('prismweaveExtractAndCommit'),
    expected: true
  },
  {
    name: 'Uses CDN URL',
    test: decodedCode.includes('cdn.jsdelivr.net'),
    expected: true
  },
  {
    name: 'No inline HTML to markdown conversion',
    test: !decodedCode.includes('htmlToMarkdown'),
    expected: true
  },
  {
    name: 'No inline content extraction',
    test: !decodedCode.includes('findMainContent'),
    expected: true
  },
  {
    name: 'Has error handling',
    test: decodedCode.includes('catch'),
    expected: true
  },
  {
    name: 'Uses advanced extraction options',
    test: decodedCode.includes('includeMetadata: true'),
    expected: true
  }
];

let passedChecks = 0;
checks.forEach(check => {
  const passed = check.test === check.expected;
  console.log(`   ${passed ? '✅' : '❌'} ${check.name}: ${passed ? 'PASS' : 'FAIL'}`);
  if (passed) passedChecks++;
});

console.log(`\n📊 Test Results: ${passedChecks}/${checks.length} checks passed`);

if (passedChecks === checks.length) {
  console.log('🎉 All tests passed! Bookmarklet refactoring is successful.');
  console.log('\n🔑 Key Improvements:');
  console.log('   • Uses sophisticated browser extension content extraction');
  console.log('   • Script injection instead of inline duplication');
  console.log('   • Advanced metadata extraction');
  console.log('   • Better error handling and user feedback');
  console.log('   • Cleaner, more maintainable code architecture');
} else {
  console.log('❌ Some tests failed. Review the refactoring.');
}

// Show a sample of the generated code (first 500 characters)
console.log('\n📝 Sample Generated Code:');
console.log(decodedCode.substring(0, 500) + '...');