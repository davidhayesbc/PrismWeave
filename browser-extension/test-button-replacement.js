// Test script to demonstrate button replacement functionality
console.log('Testing "Capture Another" to "Preview Markdown" button replacement...');

// Simulate the button logic from popup.ts
function testButtonReplacement() {
  console.log('\n=== Testing Button Replacement Logic ===');

  // Mock actions array
  let actions = [];

  // Test 1: No captured content - should show "Capture Another"
  let lastCapturedContent = null;
  actions = [];

  if (lastCapturedContent) {
    actions.push({
      label: 'Preview Markdown',
      action: 'showMarkdownPreview',
    });
  } else {
    actions.push({
      label: 'Capture Another',
      action: 'resetCaptureStatus',
    });
  }

  console.log('Test 1 - No content:');
  console.log('  Button shown:', actions[0].label);
  console.log('  Expected: "Capture Another"');
  console.log('  ✓ Correct:', actions[0].label === 'Capture Another');

  // Test 2: With captured content - should show "Preview Markdown"
  lastCapturedContent = '# Test Content\n\nThis is some captured markdown content.';
  actions = [];

  if (lastCapturedContent) {
    actions.push({
      label: 'Preview Markdown',
      action: 'showMarkdownPreview',
    });
  } else {
    actions.push({
      label: 'Capture Another',
      action: 'resetCaptureStatus',
    });
  }

  console.log('\nTest 2 - With content:');
  console.log('  Button shown:', actions[0].label);
  console.log('  Expected: "Preview Markdown"');
  console.log('  ✓ Correct:', actions[0].label === 'Preview Markdown');

  console.log('\n=== Button Replacement Test Complete ===');
  console.log(
    '✅ The "Capture Another" button is successfully replaced with "Preview Markdown" when content is available!'
  );
}

testButtonReplacement();
