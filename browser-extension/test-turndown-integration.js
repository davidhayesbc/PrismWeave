// PrismWeave TurndownService Integration Test
// Run this in the browser console to test if TurndownService is working in the service worker

(function () {
  'use strict';

  console.log('🧪 Testing TurndownService Integration in Service Worker...');

  // Test HTML content similar to Docker blog structure
  const testHtml = `
        <article>
            <h1>Test Article Title</h1>
            <p>This is a test paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>
            <h2>Section Heading</h2>
            <p>Another paragraph with a <a href="https://example.com">link to example</a>.</p>
            <ul>
                <li>First list item</li>
                <li>Second list item with <code>inline code</code></li>
                <li>Third list item</li>
            </ul>
            <h3>Code Example</h3>
            <pre><code class="language-javascript">
function hello() {
    console.log('Hello, World!');
}
            </code></pre>
            <blockquote>
                <p>This is a blockquote with important information.</p>
            </blockquote>
            <p>Final paragraph with an image: <img src="https://example.com/image.jpg" alt="Test Image"></p>
        </article>
    `;

  // Test metadata
  const testMetadata = {
    title: 'Test Article for TurndownService',
    url: window.location.href,
    captureDate: new Date().toISOString(),
  };

  console.log('📤 Sending test HTML to service worker for conversion...');
  console.log('📄 Test HTML length:', testHtml.length);

  // Send message to service worker to test conversion
  chrome.runtime
    .sendMessage({
      type: 'TEST_MARKDOWN_CONVERSION',
      data: {
        html: testHtml,
        metadata: testMetadata,
      },
    })
    .then(response => {
      if (response && response.success) {
        console.log('✅ TurndownService test successful!');
        console.log('📊 Conversion Results:');
        console.log('  - Original HTML length:', testHtml.length);
        console.log('  - Converted Markdown length:', response.data.markdown.length);
        console.log(
          '  - Conversion ratio:',
          ((response.data.markdown.length / testHtml.length) * 100).toFixed(1) + '%'
        );
        console.log('📝 Generated Markdown:');
        console.log('---START MARKDOWN---');
        console.log(response.data.markdown);
        console.log('---END MARKDOWN---');

        // Test if markdown contains expected elements
        const markdown = response.data.markdown;
        const tests = [
          {
            name: 'YAML frontmatter',
            test: markdown.includes('---') && markdown.includes('title:'),
          },
          { name: 'H1 heading', test: markdown.includes('# Test Article Title') },
          { name: 'H2 heading', test: markdown.includes('## Section Heading') },
          { name: 'H3 heading', test: markdown.includes('### Code Example') },
          { name: 'Bold text', test: markdown.includes('**bold text**') },
          { name: 'Italic text', test: markdown.includes('*italic text*') },
          { name: 'Links', test: markdown.includes('[link to example](https://example.com)') },
          { name: 'Lists', test: markdown.includes('- First list item') },
          { name: 'Inline code', test: markdown.includes('`inline code`') },
          { name: 'Code blocks', test: markdown.includes('```') },
          { name: 'Blockquotes', test: markdown.includes('> This is a blockquote') },
          { name: 'Images', test: markdown.includes('![Test Image]') },
        ];

        console.log('🔍 Quality Tests:');
        tests.forEach(test => {
          console.log(`  ${test.test ? '✅' : '❌'} ${test.name}`);
        });

        const passedTests = tests.filter(t => t.test).length;
        const totalTests = tests.length;
        console.log(
          `📈 Overall Score: ${passedTests}/${totalTests} (${((passedTests / totalTests) * 100).toFixed(1)}%)`
        );

        if (passedTests === totalTests) {
          console.log('🎉 All tests passed! TurndownService integration is working perfectly.');
        } else if (passedTests > totalTests * 0.7) {
          console.log('⚠️ Most tests passed. TurndownService is working but may need fine-tuning.');
        } else {
          console.log('❌ Many tests failed. TurndownService integration needs debugging.');
        }
      } else {
        console.error('❌ TurndownService test failed:', response?.error || 'Unknown error');
      }
    })
    .catch(error => {
      console.error('❌ Error testing TurndownService:', error);
      console.log('💡 Make sure the extension is loaded and the service worker is running.');
    });

  // Also test a direct capture of current page
  console.log('🔄 Testing live page capture...');
  chrome.runtime
    .sendMessage({
      type: 'CAPTURE_PAGE',
    })
    .then(response => {
      if (response && response.success) {
        console.log('✅ Live page capture successful!');
        console.log('📊 Capture Results:');
        console.log('  - File:', response.data.filename);
        console.log('  - Markdown length:', response.data.markdownLength);
        console.log('  - Status:', response.data.status);
      } else {
        console.error('❌ Live page capture failed:', response?.error || 'Unknown error');
      }
    })
    .catch(error => {
      console.error('❌ Error capturing page:', error);
    });
})();
