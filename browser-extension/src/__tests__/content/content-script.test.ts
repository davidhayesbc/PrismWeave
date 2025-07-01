// PrismWeave Content Script - Real Functionality Tests
// Covers: content extraction, markdown conversion, message handling, error handling

import { PrismWeaveContent } from '../../content/content-script';

describe('PrismWeaveContent - Real Functionality', () => {
  let contentScript: PrismWeaveContent;
  let originalTitle: string;
  let originalBody: string;

  beforeAll(() => {
    originalTitle = document.title;
    originalBody = document.body.innerHTML;
  });

  afterAll(() => {
    document.title = originalTitle;
    document.body.innerHTML = originalBody;
  });

  beforeEach(() => {
    document.title = 'Test Page';
    document.body.innerHTML = '';
    contentScript = new PrismWeaveContent();
  });

  test('should extract content and convert to markdown', async () => {
    document.body.innerHTML = `<main><h1>Test Title</h1><p>Test paragraph.</p></main>`;
    const result = await (contentScript as any).extractAndConvertToMarkdown({});
    expect(result.success).toBe(true);
    expect(result.data.markdown).toContain('# Test Title');
    expect(result.data.markdown).toContain('Test paragraph.');
  });

  test('should handle empty body gracefully', async () => {
    document.body.innerHTML = '';
    const result = await (contentScript as any).extractAndConvertToMarkdown({});
    expect(result.success).toBe(true);
    expect(result.data.markdown).toBe('');
  });

  test('should handle missing main content', async () => {
    document.body.innerHTML = '<div>No main content</div>';
    const result = await (contentScript as any).extractAndConvertToMarkdown({});
    expect(result.success).toBe(true);
    expect(result.data.markdown).toContain('No main content');
  });

  test('should handle message passing (PING)', async () => {
    const response = await (contentScript as any)._handleMessage({ type: 'PING' });
    expect(response.status).toBe('ready');
  });

  test('should handle message passing (EXTRACT_CONTENT)', async () => {
    document.body.innerHTML = `<main><h1>Extracted</h1></main>`;
    const response = await (contentScript as any)._handleMessage({ type: 'EXTRACT_CONTENT' });
    expect(response.title).toBe('Extracted');
  });

  test('should handle message passing (GET_PAGE_INFO)', async () => {
    document.title = 'Info Page';
    const response = await (contentScript as any)._handleMessage({ type: 'GET_PAGE_INFO' });
    expect(response.title).toBe('Info Page');
    expect(response.url).toBe(window.location.href);
  });

  test('should handle message passing (UPDATE_CONFIG)', async () => {
    const response = await (contentScript as any)._handleMessage({
      type: 'UPDATE_CONFIG',
      data: { includeImages: false },
    });
    expect(response.success).toBe(true);
  });

  test('should throw on unknown message type', async () => {
    await expect((contentScript as any)._handleMessage({ type: 'UNKNOWN_TYPE' })).rejects.toThrow(
      'Unknown message type'
    );
  });
});
