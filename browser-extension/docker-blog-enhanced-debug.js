// Enhanced Docker Blog Content Analysis Tool
// Run this in the browser console on Docker blog pages to analyze the content structure

(function () {
  console.log('=== Docker Blog Content Analysis ===');
  console.log('URL:', window.location.href);
  console.log('Document ready state:', document.readyState);

  // Wait for any dynamic content to load
  setTimeout(() => {
    console.log('\n=== DOM Structure Analysis (after 2 seconds) ===');

    // Check for various container types
    const containerSelectors = [
      'article',
      'main',
      '[role="main"]',
      '.content',
      '.post-content',
      '.entry-content',
      '.article-content',
      '.blog-content',
      '.container',
      '.single-post',
      '.post',
      '.blog-post',
      '.article-body',
      '.post-body',
      '.main-content',
      '.content-wrapper',
      '.page-content',
      '.prose',
      // Docker-specific
      '.DockerBlogPost',
      '.blog-article',
      '.article-wrapper',
      '.documentation-content',
      '.tutorial-content',
      '.guide-content',
      // Generic patterns
      '[data-testid*="content"]',
      '[data-testid*="post"]',
      'div[class*="content"]',
      'div[class*="post"]',
      'div[class*="article"]',
      'section',
      'div',
      '.row',
      '.col',
    ];

    console.log('\n--- Checking All Container Selectors ---');
    const foundContainers = [];

    containerSelectors.forEach(selector => {
      try {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
          elements.forEach((el, index) => {
            const textLength = el.textContent?.trim().length || 0;
            const hasContent = textLength > 200;

            if (hasContent) {
              foundContainers.push({
                selector,
                index,
                element: el,
                textLength,
                className: el.className,
                id: el.id,
                tagName: el.tagName,
              });

              console.log(
                `✓ ${selector}[${index}]: ${textLength} chars, class="${el.className}", id="${el.id}"`
              );
            }
          });
        }
      } catch (e) {
        console.log(`✗ Error with selector "${selector}":`, e.message);
      }
    });

    console.log(`\nFound ${foundContainers.length} potential content containers`);

    // Sort by content length and show top candidates
    foundContainers.sort((a, b) => b.textLength - a.textLength);

    console.log('\n--- Top 5 Content Candidates ---');
    foundContainers.slice(0, 5).forEach((container, index) => {
      console.log(`${index + 1}. ${container.selector} (${container.textLength} chars)`);
      console.log(
        `   Tag: ${container.tagName}, Class: "${container.className}", ID: "${container.id}"`
      );

      // Show structure
      const headings = container.element.querySelectorAll('h1, h2, h3, h4, h5, h6').length;
      const paragraphs = container.element.querySelectorAll('p').length;
      const links = container.element.querySelectorAll('a').length;
      const codeBlocks = container.element.querySelectorAll('pre, code').length;

      console.log(
        `   Structure: ${headings} headings, ${paragraphs} paragraphs, ${links} links, ${codeBlocks} code blocks`
      );

      // Show a sample of the content
      const sample = container.element.textContent?.trim().substring(0, 200) + '...';
      console.log(`   Sample: "${sample}"`);
      console.log('   Element:', container.element);
      console.log('');
    });

    // Check for specific Docker blog patterns
    console.log('\n--- Docker-Specific Analysis ---');

    // Look for JSON-LD structured data
    const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
    console.log(`JSON-LD scripts found: ${jsonLdScripts.length}`);

    jsonLdScripts.forEach((script, index) => {
      try {
        const data = JSON.parse(script.textContent || '');
        console.log(`JSON-LD ${index}:`, data);
      } catch (e) {
        console.log(`JSON-LD ${index}: Parse error`);
      }
    });

    // Check meta tags
    console.log('\n--- Meta Information ---');
    const metaTags = [
      'og:title',
      'og:description',
      'og:type',
      'og:url',
      'twitter:title',
      'twitter:description',
      'twitter:card',
      'article:author',
      'article:published_time',
      'article:modified_time',
      'description',
      'keywords',
      'author',
    ];

    metaTags.forEach(tag => {
      const element = document.querySelector(`meta[property="${tag}"], meta[name="${tag}"]`);
      if (element) {
        console.log(`${tag}: "${element.getAttribute('content')}"`);
      }
    });

    // Check for any elements that might contain the full article
    console.log('\n--- Looking for Full Article Content ---');

    // Try various article-specific selectors
    const articleSelectors = [
      'article[itemtype*="Article"]',
      '[itemtype*="BlogPosting"]',
      '[itemtype*="Article"]',
      '.post-content .content',
      '.article-body .content',
      '[data-article-body]',
      '[data-content-body]',
    ];

    articleSelectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      if (elements.length > 0) {
        elements.forEach((el, index) => {
          const textLength = el.textContent?.trim().length || 0;
          console.log(`${selector}[${index}]: ${textLength} chars`);
          if (textLength > 1000) {
            console.log('   ↳ This looks like the main article content!');
            console.log('   ↳ Element:', el);
          }
        });
      }
    });

    // Final recommendation
    if (foundContainers.length > 0) {
      const best = foundContainers[0];
      console.log(
        `\n🎯 RECOMMENDATION: Use "${best.selector}" - it has ${best.textLength} characters of content`
      );
      console.log('Element for testing:', best.element);

      // Show what TurndownService would produce
      if (typeof TurndownService !== 'undefined') {
        const turndownService = new TurndownService({
          headingStyle: 'atx',
          codeBlockStyle: 'fenced',
        });
        const markdown = turndownService.turndown(best.element.innerHTML);
        console.log('\n--- Sample Markdown Output ---');
        console.log(markdown.substring(0, 500) + (markdown.length > 500 ? '...' : ''));
      }
    } else {
      console.log('\n❌ NO SUITABLE CONTENT CONTAINERS FOUND');
      console.log('This page might use unusual structure or heavy JavaScript rendering');
    }
  }, 2000);

  // Also check immediately for comparison
  console.log('\n=== Immediate Check (before dynamic loading) ===');
  const immediateArticles = document.querySelectorAll('article');
  const immediateMains = document.querySelectorAll('main');
  const immediateContent = document.querySelectorAll('.content, .post-content, .article-content');

  console.log(`Articles: ${immediateArticles.length}`);
  console.log(`Main elements: ${immediateMains.length}`);
  console.log(`Content containers: ${immediateContent.length}`);

  if (immediateArticles.length > 0) {
    const article = immediateArticles[0];
    console.log(`First article: ${article.textContent?.trim().length || 0} chars`);
  }
})();
