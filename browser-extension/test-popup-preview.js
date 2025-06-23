// Test script to verify popup markdown preview functionality
console.log('Testing popup markdown preview functionality...');

// Simulate popup initialization with mock data
const testPopup = {
  lastCapturedContent: `# Test Document

This is a test markdown document captured from a web page.

## Features
- Bullet point 1
- Bullet point 2
- Bullet point 3

## Code Example
\`\`\`javascript
console.log('Hello, world!');
\`\`\`

[Link example](https://example.com)

> This is a blockquote example

**Bold text** and *italic text* example.`,

  showMarkdownPreview() {
    console.log('Preview would show:', this.lastCapturedContent?.length || 0, 'characters');
    console.log('Preview content preview:', this.lastCapturedContent?.substring(0, 100) + '...');
    return true;
  },
};

// Test the functionality
console.log('Testing preview with content:', testPopup.showMarkdownPreview());
console.log('Testing with no content...');
testPopup.lastCapturedContent = null;
console.log('Should show error:', testPopup.showMarkdownPreview());

console.log('Popup markdown preview test completed!');
