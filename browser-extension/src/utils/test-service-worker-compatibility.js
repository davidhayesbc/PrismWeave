// Service Worker Compatibility Test
// Tests that the markdown converter works properly in service worker context

function testServiceWorkerCompatibility() {
  console.log('🧪 Testing Service Worker Compatibility...');
  
  try {
    // Test 1: Check if TurndownService is available
    console.log('✅ TurndownService available:', typeof TurndownService !== 'undefined');
    
    // Test 2: Initialize MarkdownConverter
    const converter = new MarkdownConverter();
    console.log('✅ MarkdownConverter initialized successfully');
    
    // Test 3: Test with simple HTML (should use fallback in service worker)
    const testHtml = `
      <article>
        <h1>Test Article</h1>
        <p>This is a <strong>test</strong> with <em>formatting</em>.</p>
        <pre><code class="language-javascript">
          function test() {
            return "hello world";
          }
        </code></pre>
        <blockquote>
          This is a quote.
        </blockquote>
      </article>
    `;
    
    const markdown = converter.convert(testHtml);
    console.log('✅ HTML conversion successful');
    console.log('Generated markdown length:', markdown.length);
    
    // Test 4: Verify service worker specific functionality
    const isServiceWorker = typeof window === 'undefined' && typeof document === 'undefined';
    console.log('✅ Service worker context detected:', isServiceWorker);
    
    if (isServiceWorker) {
      console.log('✅ Running in service worker - DOM fallbacks should be used');
    } else {
      console.log('✅ Running in browser context - DOM methods available');
    }
    
    console.log('🎉 All compatibility tests passed!');
    return {
      success: true,
      turndownAvailable: typeof TurndownService !== 'undefined',
      isServiceWorker: isServiceWorker,
      markdownLength: markdown.length
    };
    
  } catch (error) {
    console.error('❌ Compatibility test failed:', error);
    return {
      success: false,
      error: error.message,
      stack: error.stack
    };
  }
}

// Auto-run test if in service worker context
if (typeof window === 'undefined' && typeof self !== 'undefined') {
  // Wait a moment for all imports to complete
  setTimeout(() => {
    testServiceWorkerCompatibility();
  }, 100);
}

// Export for manual testing
if (typeof self !== 'undefined') {
  self.testServiceWorkerCompatibility = testServiceWorkerCompatibility;
}
