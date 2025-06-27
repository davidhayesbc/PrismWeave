// Simple test of the core markdown converter
import TurndownService from 'turndown';
import { MarkdownConverterCore } from '../src/utils/markdown-converter-core.ts';

async function testSimpleConversion() {
  console.log('Creating MarkdownConverterCore...');

  const converter = new MarkdownConverterCore();

  console.log('Setting up TurndownService manually...');
  // Manually set up TurndownService since we're in Node.js
  (converter as any).turndownService = new TurndownService();
  (converter as any).setupTurndownService();
  (converter as any)._isInitialized = true;

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
    </div>
  `;

  console.log('Converting HTML to markdown...');
  const result = converter.convertToMarkdown(testHtml);

  console.log('Result:', result.markdown);
  console.log('Length:', result.markdown.length);
}

testSimpleConversion().catch(console.error);
