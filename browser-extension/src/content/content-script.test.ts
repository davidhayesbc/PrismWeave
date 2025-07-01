// PrismWeave Content Script - Real Functionality Tests
// Tests for DOM extraction, markdown conversion, Chrome message passing, and workflow

import { PrismWeaveContent } from './content-script';

describe('PrismWeaveContent - Real Content Script Functionality', () => {
  let contentScript: PrismWeaveContent;
  let originalTitle: string;
  let originalBody: string;

  beforeAll(() => {
    // Save original document state
    originalTitle = document.title;
    originalBody = document.body.innerHTML;
  });

  afterAll(() => {
    // Restore original document state
    document.title = originalTitle;
    document.body.innerHTML = originalBody;
  });

  beforeEach(() => {
    // Set up a simple HTML structure for extraction
    document.title = 'Test Page';
    document.body.innerHTML = `
      <main>
        <h1>Test Article</h1>
        <p>This is a <strong>test</strong> paragraph with <a href='https://example.com'>a link</a>.</p>
        <img src='https://example.com/image.png' alt='Test Image'>
      </main>
    `;
    contentScript = new PrismWeaveContent();
  });

  test('should extract main content and metadata', async () => {
    const result = await (contentScript as any).extractContentForServiceWorker();
    expect(result.title).toBe('Test Page');
    expect(result.url).toContain('http');
    expect(result.html).toContain('Test Article');
    expect(result.metadata).toHaveProperty('wordCount');
  });

  test('should convert extracted content to markdown', async () => {
    const extraction = await (contentScript as any).extractContentForServiceWorker();
    const markdownResult = await (contentScript as any).extractAndConvertToMarkdown();
    expect(markdownResult.success).toBe(true);
    expect(markdownResult.data.markdown).toContain('# Test Article');
    expect(markdownResult.data.markdown).toContain('[a link](https://example.com)');
    expect(markdownResult.data.images).toContain('https://example.com/image.png');
  });

  test('should handle PING message', done => {
    const message = { type: 'PING' };
    (contentScript as any).handleMessage(message, {}, (response: any) => {
      expect(response.success).toBe(true);
      expect(response.data.active).toBe(true);
      done();
    });
  });

  test('should highlight main content', () => {
    (contentScript as any).highlightMainContent();
    const main = document.querySelector('main');
    expect(main).not.toBeNull();
    // Should have outline style applied
    expect((main as HTMLElement).style.outline).toContain('solid');
  });

  test('should inject styles', () => {
    (contentScript as any).injectStyles('body { background: #eee !important; }');
    const style = document.getElementById('prismweave-injected-styles');
    expect(style).not.toBeNull();
    expect(style!.textContent).toContain('background: #eee');
  });

  test('should get page info', () => {
    const info = (contentScript as any).getPageInfo();
    expect(info.title).toBe('Test Page');
    expect(info.url).toContain('http');
    expect(info.wordCount).toBeGreaterThan(0);
  });

  test('should handle selection capture', async () => {
    // Simulate a selection
    const range = document.createRange();
    const p = document.querySelector('p');
    range.selectNodeContents(p!);
    const sel = window.getSelection();
    sel?.removeAllRanges();
    sel?.addRange(range);
    const result = await (contentScript as any).captureSelection();
    expect(result.markdown).toContain('test');
    expect(result.selectedText).toContain('test');
  });
});
