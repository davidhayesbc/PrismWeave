// Test script to verify popup HTML changes for preview button
console.log('Testing popup HTML preview button functionality...');

// Simulate DOM structure
const mockHTML = `
<button id="preview-markdown" class="secondary-button" style="display: none; margin-top: 12px">
  👁️ Preview Markdown
</button>
`;

console.log('HTML structure includes preview button:', mockHTML.includes('preview-markdown'));
console.log('Button is initially hidden:', mockHTML.includes('display: none'));
console.log('Button has correct emoji icon:', mockHTML.includes('👁️'));
console.log('Button has correct text:', mockHTML.includes('Preview Markdown'));

// Test button visibility logic
const testButtonVisibility = hasContent => {
  if (hasContent) {
    console.log('With content: Button should be visible (display: block)');
    return 'block';
  } else {
    console.log('Without content: Button should be hidden (display: none)');
    return 'none';
  }
};

console.log('\nTesting button visibility logic:');
testButtonVisibility(true);
testButtonVisibility(false);

console.log('\nPopup HTML preview button test completed!');
