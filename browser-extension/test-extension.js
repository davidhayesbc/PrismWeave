// Simple Extension Test Script
// Run this in the browser console to test the PrismWeave content extraction

(function () {
  console.log('=== PrismWeave Extension Test ===');

  // Check if extension is loaded
  if (typeof chrome === 'undefined' || !chrome.runtime) {
    console.error('❌ Chrome extension APIs not available');
    return;
  }

  console.log('✓ Chrome extension APIs available');
  console.log('Current URL:', window.location.href);

  // Test the content extraction by sending a message to the extension
  console.log('🚀 Sending extraction request to extension...');

  chrome.runtime.sendMessage(
    {
      type: 'EXTRACT_AND_CONVERT_TO_MARKDOWN',
      data: {
        preserveFormatting: true,
        removeAds: true,
        removeNavigation: true,
      },
    },
    function (response) {
      if (chrome.runtime.lastError) {
        console.error('❌ Extension communication error:', chrome.runtime.lastError.message);
        return;
      }

      if (!response) {
        console.error('❌ No response from extension');
        return;
      }

      console.log('📨 Extension response received:', response);

      if (response.success) {
        const data = response.data;
        console.log('✅ Content extraction successful!');
        console.log('📝 Markdown length:', data.markdown?.length || 0);
        console.log('📊 Metadata:', data.metadata);
        console.log('🏷️ Frontmatter:', data.frontmatter);

        if (data.markdown) {
          console.log('📄 First 500 characters of markdown:');
          console.log(data.markdown.substring(0, 500) + (data.markdown.length > 500 ? '...' : ''));
        }

        if (data.images && data.images.length > 0) {
          console.log('🖼️ Found', data.images.length, 'images');
        }

        // Show extraction quality metrics
        const wordCount = data.metadata?.wordCount || 0;
        const readingTime = data.metadata?.estimatedReadingTime || 0;
        console.log('📈 Quality metrics:');
        console.log('  - Word count:', wordCount);
        console.log('  - Reading time:', readingTime, 'minutes');

        if (wordCount < 100) {
          console.warn('⚠️ Low word count - content extraction might be incomplete');
        } else if (wordCount > 500) {
          console.log('✅ Good content length detected');
        }
      } else {
        console.error('❌ Content extraction failed:', response.error);
      }
    }
  );

  // Also check if we can see the content script
  setTimeout(() => {
    if (window.contentExtractor || window.prismweaveContent) {
      console.log('✓ Content script appears to be loaded');
    } else {
      console.warn('⚠️ Content script not detected in window object');
    }
  }, 1000);
})();
