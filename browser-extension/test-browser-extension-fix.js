/**
 * Test script to verify browser extension produces same output as dev-tools
 * after the tree structure preservation fix
 */

// Test the browser extension capture on the Docker blog
async function testBrowserExtensionCapture() {
  console.log('Testing browser extension capture...');

  try {
    // Get the current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab.id) {
      throw new Error('No active tab found');
    }

    console.log('Current tab URL:', tab.url);

    // Send capture message to content script
    const response = await chrome.tabs.sendMessage(tab.id, {
      type: 'CAPTURE_PAGE',
      timestamp: Date.now(),
    });

    if (response && response.success) {
      console.log('✅ Capture successful');
      console.log('📄 Content length:', response.markdown?.length || 0);
      console.log('📊 Line count estimate:', (response.markdown?.match(/\n/g) || []).length + 1);

      // Log first few lines to verify structure
      if (response.markdown) {
        const lines = response.markdown.split('\n');
        console.log('📋 First 10 lines:');
        lines.slice(0, 10).forEach((line, i) => {
          console.log(`${i + 1}: ${line}`);
        });

        // Check for tree structure preservation
        const hasTreeStructure =
          response.markdown.includes('├──') || response.markdown.includes('└──');
        console.log('🌳 Contains tree structure:', hasTreeStructure);

        if (hasTreeStructure) {
          // Find tree structure sections
          const treeLines = lines.filter(line => line.includes('├──') || line.includes('└──'));
          console.log('🌳 Tree structure lines found:', treeLines.length);
          console.log('📋 Sample tree lines:');
          treeLines.slice(0, 5).forEach(line => console.log(`   ${line}`));
        }
      }

      return response;
    } else {
      console.error('❌ Capture failed:', response);
      return null;
    }
  } catch (error) {
    console.error('❌ Test failed:', error);
    return null;
  }
}

// Run the test
testBrowserExtensionCapture()
  .then(result => {
    if (result) {
      console.log('✅ Browser extension test completed');
    } else {
      console.log('❌ Browser extension test failed');
    }
  })
  .catch(error => {
    console.error('💥 Test error:', error);
  });
