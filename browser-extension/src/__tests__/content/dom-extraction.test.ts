// PrismWeave Content Script - DOM Interaction and Real-World Scenarios Tests
// Covers: DOM manipulation, content quality scoring, page structure analysis, error handling, dynamic content, real website HTML

import { PrismWeaveContent } from '../../content/content-script';

describe('PrismWeaveContent - DOM Interaction and Real-World Scenarios', () => {
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
    document.title = 'Scenario Test Page';
    document.body.innerHTML = '';
    contentScript = new PrismWeaveContent();
  });

  test('should select and manipulate DOM elements', () => {
    document.body.innerHTML = `<main><h1>Header</h1><p>Text</p></main>`;
    (contentScript as any).highlightMainContent();
    const main = document.querySelector('main');
    expect(main).not.toBeNull();
    expect((main as HTMLElement).style.outline).toContain('solid');
  });

  test('should score content quality based on word count', async () => {
    document.body.innerHTML = `<main><p>${'word '.repeat(100)}</p></main>`;
    const result = await (contentScript as any).extractContentForServiceWorker();
    expect(result.metadata.wordCount).toBeGreaterThan(90);
  });

  test('should analyze page structure with complex HTML', async () => {
    document.body.innerHTML = `
      <header>Header</header>
      <nav>Nav</nav>
      <main><article><h1>Article</h1><p>Body</p></article></main>
      <footer>Footer</footer>
    `;
    const result = await (contentScript as any).extractContentForServiceWorker();
    expect(result.html).toContain('Article');
    expect(result.html).toContain('Body');
  });

  test('should handle malformed DOM structures gracefully', async () => {
    document.body.innerHTML = `<main><p>Unclosed tag<article>Broken`; // malformed
    await expect((contentScript as any).extractContentForServiceWorker()).resolves.toBeDefined();
  });

  test('should handle dynamic content loading (simulate Docker blog)', async () => {
    // Simulate short content first, then longer after delay
    let content = '<main><div class="blog-content">Short</div></main>';
    document.body.innerHTML = content;
    setTimeout(() => {
      document.body.innerHTML =
        '<main><div class="blog-content">' + 'Long '.repeat(100) + '</div></main>';
    }, 500);
    const result = await (contentScript as any).extractAndConvertToMarkdown({});
    expect(result.success).toBe(true);
    expect(result.data.markdown.length).toBeGreaterThan(50);
  });

  test('should extract from real website-like HTML (Wikipedia)', async () => {
    document.body.innerHTML = `
      <div id="content">
        <h1 id="firstHeading">Wikipedia Title</h1>
        <div id="bodyContent">
          <p>This is a Wikipedia-style paragraph.</p>
        </div>
      </div>
    `;
    const result = await (contentScript as any).extractContentForServiceWorker();
    expect(result.html).toContain('Wikipedia Title');
    expect(result.html).toContain('Wikipedia-style paragraph');
  });

  test('should extract from real website-like HTML (Medium)', async () => {
    document.body.innerHTML = `
      <article>
        <h1>Medium Post</h1>
        <section><p>Medium content body.</p></section>
      </article>
    `;
    const result = await (contentScript as any).extractContentForServiceWorker();
    expect(result.html).toContain('Medium Post');
    expect(result.html).toContain('Medium content body');
  });
});
