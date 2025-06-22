// Complete PrismWeave Extension Test & Debug
// Run this after loading the updated extension to test the Docker blog extraction

(function () {
  console.log('=== PrismWeave Extension Complete Test ===');
  console.log('URL:', window.location.href);
  console.log('Time:', new Date().toISOString());

  // Check extension availability
  if (typeof chrome === 'undefined' || !chrome.runtime) {
    console.error('❌ Chrome extension APIs not available');
    return;
  }

  console.log('✅ Chrome extension APIs available');

  // First, test the extension's content extraction
  console.log('\n🚀 Testing PrismWeave content extraction...');

  chrome.runtime.sendMessage(
    {
      type: 'EXTRACT_AND_CONVERT_TO_MARKDOWN',
      data: {
        preserveFormatting: true,
        removeAds: true,
        removeNavigation: true,
      },
    },
    function (response) {
      if (chrome.runtime.lastError) {
        console.error('❌ Extension communication error:', chrome.runtime.lastError.message);
        return;
      }

      if (!response) {
        console.error('❌ No response from extension');
        return;
      }

      console.log('\n📨 Extension Response Analysis:');
      console.log('Success:', response.success);

      if (response.success && response.data) {
        const data = response.data;

        console.log('\n📊 Content Metrics:');
        console.log('  - Markdown length:', data.markdown?.length || 0);
        console.log('  - Frontmatter length:', data.frontmatter?.length || 0);
        console.log('  - Images found:', data.images?.length || 0);
        console.log('  - Word count:', data.metadata?.wordCount || 0);
        console.log('  - Reading time:', data.metadata?.estimatedReadingTime || 0, 'minutes');

        console.log('\n📄 Content Quality Check:');
        if (data.markdown) {
          const lines = data.markdown.split('\n');
          const headingLines = lines.filter(line => line.startsWith('#'));
          const contentLines = lines.filter(
            line => line.trim().length > 0 && !line.startsWith('#')
          );

          console.log('  - Total lines:', lines.length);
          console.log('  - Heading lines:', headingLines.length);
          console.log('  - Content lines:', contentLines.length);

          console.log('\n🏷️ Headings found:');
          headingLines.slice(0, 5).forEach((heading, i) => {
            console.log(`  ${i + 1}. ${heading}`);
          });

          console.log('\n📝 Content preview (first 300 chars):');
          console.log(`"${data.markdown.substring(0, 300)}..."`);

          if (data.markdown.length < 500) {
            console.warn('⚠️ WARNING: Markdown content seems very short for a blog post');
            console.log('💡 This suggests content extraction may not be working optimally');
          }

          // Check for specific Docker blog content indicators
          const dockerIndicators = ['docker', 'container', 'image', 'dockerfile', 'chatbot', 'ai'];
          const foundIndicators = dockerIndicators.filter(indicator =>
            data.markdown.toLowerCase().includes(indicator)
          );

          console.log('\n🐳 Docker Content Indicators:');
          console.log('  Found:', foundIndicators.join(', ') || 'none');
          if (foundIndicators.length === 0) {
            console.warn('⚠️ No Docker-related content found - extraction may have failed');
          }

          // Enhanced code block analysis
          console.log('\n📦 Code Block Quality Check:');
          const codeBlockMatches = data.markdown.match(/```[\s\S]*?```/g) || [];
          const inlineCodeMatches = data.markdown.match(/`[^`]+`/g) || [];

          console.log(`  - Fenced code blocks found: ${codeBlockMatches.length}`);
          console.log(`  - Inline code elements found: ${inlineCodeMatches.length}`);

          // Check for language tagging
          const languageTaggedBlocks = codeBlockMatches.filter(block => /```\w+/.test(block));
          console.log(`  - Language-tagged blocks: ${languageTaggedBlocks.length}`); // Check for shell script preservation
          const shellBlocks = codeBlockMatches.filter(
            block => /(bash|shell|zsh|#!)/.test(block) || /\$\s+/.test(block)
          );
          console.log(`  - Shell script blocks: ${shellBlocks.length}`);

          // Check for proper entity decoding
          const entityIssues = [];
          if (data.markdown.includes('&lt;')) entityIssues.push('&lt; found');
          if (data.markdown.includes('&gt;')) entityIssues.push('&gt; found');
          if (data.markdown.includes('&amp;')) entityIssues.push('&amp; found');
          if (data.markdown.includes('&quot;')) entityIssues.push('&quot; found');

          if (entityIssues.length > 0) {
            console.log(`  ⚠️ HTML entity issues: ${entityIssues.join(', ')}`);
          } else {
            console.log('  ✅ HTML entities properly decoded');
          }

          // Show examples of preserved code blocks
          if (codeBlockMatches.length > 0) {
            console.log('\n📋 Code Block Examples:');
            codeBlockMatches.slice(0, 3).forEach((block, i) => {
              const preview = block.substring(0, 200);
              console.log(`  ${i + 1}. ${preview}${block.length > 200 ? '...' : ''}`);
            });
          }
        } else {
          console.error('❌ No markdown content in response');
        }

        if (data.metadata) {
          console.log('\n📋 Metadata:');
          console.log('  - Title:', data.metadata.title);
          console.log('  - URL:', data.metadata.url);
          console.log('  - Tags:', data.metadata.tags?.join(', ') || 'none');
          console.log('  - Author:', data.metadata.author || 'not found');
        }
      } else {
        console.error('❌ Extension extraction failed:', response.error || 'Unknown error');

        // If extension failed, let's analyze the page manually
        console.log('\n🔍 Manual Page Analysis:');

        // Check what content containers are available
        const containers = [
          { name: '.entry-content', element: document.querySelector('.entry-content') },
          { name: 'main', element: document.querySelector('main') },
          { name: 'article', element: document.querySelector('article') },
          { name: '.post-content', element: document.querySelector('.post-content') },
        ];

        containers.forEach(container => {
          if (container.element) {
            const textLength = container.element.textContent?.length || 0;
            console.log(`  ${container.name}: ${textLength} characters`);

            if (textLength > 1000) {
              console.log(`    ↳ Sample: "${container.element.textContent?.substring(0, 100)}..."`);
            }
          } else {
            console.log(`  ${container.name}: not found`);
          }
        });
      }
    }
  );

  // Also run our content loss analysis after a delay
  setTimeout(() => {
    console.log('\n\n🔬 Running Content Loss Analysis...');

    // Simulate the content extraction process step by step
    const mainElement = document.querySelector('main');
    const entryContent = document.querySelector('.entry-content');

    console.log('\n📊 Element Comparison:');
    if (mainElement) {
      console.log(`Main element: ${mainElement.textContent?.length || 0} chars`);
    }
    if (entryContent) {
      console.log(`Entry content: ${entryContent.textContent?.length || 0} chars`);

      // This should be what the extension uses now with updated selectors
      console.log('💡 Entry content should be prioritized now');
    }

    // Check the actual selector that would be chosen
    const selectors = [
      '.entry-content',
      '.post-content',
      '.article-content',
      '.blog-content',
      'article',
      'main',
    ];

    console.log('\n🎯 Selector Priority Test:');
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        const textLength = element.textContent?.length || 0;
        console.log(`✅ ${selector}: ${textLength} chars (WOULD BE SELECTED)`);
        break;
      } else {
        console.log(`❌ ${selector}: not found`);
      }
    }
  }, 2000);
})();
