// Simple test using compiled JS files
console.log('Starting JS import test...');

import TurndownService from 'turndown';
import { MarkdownConverterCore } from './dist/src/utils/markdown-converter-core.js';

async function testSimpleConversion() {
  console.log('Creating MarkdownConverterCore from compiled JS...');

  const converter = new MarkdownConverterCore();

  console.log('Setting up TurndownService manually...');
  // Manually set up TurndownService since we're in Node.js
  converter.turndownService = new TurndownService();
  converter.setupTurndownService();
  converter._isInitialized = true;

  const testHtml = `
    <div>
      <h1>Test Title</h1>
      <p>This is a simple test.</p>
      <pre>
docker run -d \\
  --name postgres \\
  -e POSTGRES_PASSWORD=mypassword \\
  postgres:latest
      </pre>
      <pre>
├── src/
│   ├── components/
│   └── utils/
└── tests/
      </pre>
    </div>
  `;

  console.log('Converting HTML to markdown...');
  const result = converter.convertToMarkdown(testHtml);

  console.log('Result:');
  console.log(result.markdown);
  console.log('Length:', result.markdown.length);

  // Check if tree structure is preserved
  if (result.markdown.includes('├──') && result.markdown.includes('└──')) {
    console.log('✅ Tree structure preserved!');
  } else {
    console.log('❌ Tree structure NOT preserved');
  }
}

testSimpleConversion().catch(console.error);
