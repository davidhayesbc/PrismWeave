// Test script to verify service worker loads without errors
// Run this in browser console after loading extension

console.log('Testing service worker compatibility...');

// Test that service worker registration is successful
chrome.runtime.getBackgroundPage(function(background) {
  if (chrome.runtime.lastError) {
    console.error('Service worker registration failed:', chrome.runtime.lastError);
  } else {
    console.log('Service worker registration successful');
    
    // Test markdown conversion in service worker context
    if (background && background.MarkdownConverter) {
      const converter = new background.MarkdownConverter();
      const testHtml = '<h1>Test</h1><p>This is a <strong>test</strong> paragraph.</p>';
      const result = converter.convert(testHtml);
      console.log('Service worker markdown conversion test result:', result);
      
      if (result.includes('# Test') && result.includes('**test**')) {
        console.log('✅ Service worker markdown conversion working correctly');
      } else {
        console.warn('⚠️ Service worker markdown conversion may have issues');
      }
    } else {
      console.warn('MarkdownConverter not available in service worker');
    }
  }
});

console.log('Service worker compatibility test completed');
