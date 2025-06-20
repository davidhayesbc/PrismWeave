// Test script for enhanced markdown conversion
// This can be run in the browser console to test the improvements

function testMarkdownConversion() {
  console.log('Testing Enhanced Markdown Conversion...');
  
  // Test HTML with various content types
  const testHtml = `
    <article>
      <header>
        <h1>Enhanced Markdown Conversion Test</h1>
        <div class="author">By John Doe</div>
        <time datetime="2025-06-19">June 19, 2025</time>
      </header>
      
      <p>This is a <strong>test article</strong> with <em>various formatting</em> to demonstrate the enhanced markdown conversion capabilities.</p>
      
      <blockquote cite="https://example.com">
        This is a quote with proper attribution.
        <cite>Famous Author</cite>
      </blockquote>
      
      <h2>Code Examples</h2>
      
      <p>Here's some inline <code>code</code> and a code block:</p>
      
      <pre><code class="language-javascript">
function example() {
  // This should be detected as JavaScript
  return "Hello, World!";
}
      </code></pre>
      
      <h3>Table Example</h3>
      
      <table>
        <thead>
          <tr>
            <th>Column 1</th>
            <th style="text-align: center">Column 2</th>
            <th style="text-align: right">Column 3</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Data 1</td>
            <td><strong>Bold data</strong></td>
            <td><a href="https://example.com">Link</a></td>
          </tr>
          <tr>
            <td>Data 2</td>
            <td><em>Italic data</em></td>
            <td><code>Code</code></td>
          </tr>
        </tbody>
      </table>
      
      <h3>Lists and Media</h3>
      
      <ul>
        <li>First item</li>
        <li>Second item with <strong>formatting</strong></li>
        <li>Third item</li>
      </ul>
      
      <ol>
        <li>Numbered item</li>
        <li>Another numbered item</li>
      </ol>
      
      <figure>
        <img src="https://via.placeholder.com/300x200" alt="Test Image" title="A test image">
        <figcaption>This is an image caption that should be preserved</figcaption>
      </figure>
      
      <div class="callout warning">
        <p>This is a warning callout that should be converted properly.</p>
      </div>
      
      <hr>
      
      <p>Text with special formatting: <sup>superscript</sup>, <sub>subscript</sub>, <mark>highlighted text</mark>, and <del>deleted text</del>.</p>
      
      <dl>
        <dt>Definition Term</dt>
        <dd>Definition description that explains the term above.</dd>
        <dt>Another Term</dt>
        <dd>Another definition with <strong>formatting</strong>.</dd>
      </dl>
    </article>
    
    <!-- This should be removed -->
    <div class="advertisement">
      <p>Buy our product!</p>
    </div>
    
    <nav class="navigation">
      <a href="/home">Home</a>
      <a href="/about">About</a>
    </nav>
  `;
  
  try {
    // Test with MarkdownConverter
    const converter = new MarkdownConverter();
    const markdown = converter.convert(testHtml);
    
    console.log('✅ Conversion successful!');
    console.log('Generated Markdown:');
    console.log('==================');
    console.log(markdown);
    console.log('==================');
    
    // Test specific features
    const tests = [
      {
        name: 'Code blocks with language detection',
        test: markdown.includes('```javascript')
      },
      {
        name: 'Blockquotes with attribution',
        test: markdown.includes('> ') && markdown.includes('*— Famous Author*')
      },
      {
        name: 'Table conversion',
        test: markdown.includes('| Column 1') && markdown.includes('| --- |')
      },
      {
        name: 'Image with caption',
        test: markdown.includes('![Test Image]') && markdown.includes('*This is an image caption*')
      },
      {
        name: 'Enhanced formatting',
        test: markdown.includes('<sup>') || markdown.includes('<sub>') || markdown.includes('==highlighted text==')
      },
      {
        name: 'Definition lists',
        test: markdown.includes('**Definition Term**') && markdown.includes(': Definition description')
      },
      {
        name: 'Callout detection',
        test: markdown.includes('> **Warning:**') || markdown.includes('> **Note:**')
      },
      {
        name: 'Unwanted content removal',
        test: !markdown.includes('Buy our product') && !markdown.includes('Home') && !markdown.includes('About')
      }
    ];
    
    console.log('\nFeature Tests:');
    console.log('=============');
    tests.forEach(test => {
      console.log(`${test.test ? '✅' : '❌'} ${test.name}`);
    });
    
    const passedTests = tests.filter(test => test.test).length;
    console.log(`\nPassed: ${passedTests}/${tests.length} tests`);
    
    return {
      success: true,
      markdown: markdown,
      testsPassedCount: passedTests,
      totalTests: tests.length,
      testResults: tests
    };
    
  } catch (error) {
    console.error('❌ Conversion failed:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Run the test if in browser context
if (typeof window !== 'undefined' && typeof MarkdownConverter !== 'undefined') {
  testMarkdownConversion();
} else {
  console.log('Test script loaded. Run testMarkdownConversion() to test the enhanced conversion.');
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { testMarkdownConversion };
}
