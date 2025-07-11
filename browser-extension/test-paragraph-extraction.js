// Quick test to verify paragraph extraction improvements
// This should be run in the browser console on a Stack Overflow blog page

(async function testParagraphExtraction() {
  console.log('🧪 Testing Stack Overflow blog paragraph extraction...');

  // Sample HTML with paragraphs that should be preserved
  const testHTML = `
    <div class="post-content">
      <p>This is the first paragraph with some important content about software development.</p>
      <p>This is the second paragraph that discusses different approaches to the problem.</p>
      <h2>Important Section</h2>
      <p>This paragraph comes after a heading and should maintain proper spacing.</p>
      <div class="content-block">
        <p>Nested paragraph content that should also be preserved properly.</p>
      </div>
    </div>
  `;

  console.log('Original HTML:', testHTML);

  // Test the preprocessing
  const preprocessHTML = html => {
    if (!html) return '';
    let cleaned = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
    cleaned = cleaned.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
    cleaned = cleaned.replace(/<!--[\s\S]*?-->/g, '');

    // NEW: Preserve paragraph structure
    cleaned = cleaned.replace(/[ \t]+/g, ' '); // Only collapse spaces and tabs
    cleaned = cleaned.replace(/\n\s*\n\s*\n/g, '\n\n'); // Limit to double line breaks
    cleaned = cleaned.trim();

    return cleaned;
  };

  const processedHTML = preprocessHTML(testHTML);
  console.log('Processed HTML:', processedHTML);

  // Check if we're on a Stack Overflow blog page
  if (window.location.hostname.includes('stackoverflow.blog')) {
    console.log('✅ On Stack Overflow blog - testing real extraction...');

    // Test the actual extractor if available
    if (window.prismweaveContentScript) {
      try {
        const result = await window.prismweaveContentScript.extractContent();
        console.log('📝 Extracted content sample:', result.markdown.substring(0, 500) + '...');

        // Count paragraphs in the result
        const paragraphCount = (result.markdown.match(/\n\n/g) || []).length;
        console.log(`📊 Found ${paragraphCount} paragraph breaks in markdown`);

        if (paragraphCount > 5) {
          console.log('✅ Paragraph structure appears to be preserved!');
        } else {
          console.log('❌ Still seeing wall of text - may need further investigation');
        }
      } catch (error) {
        console.log('❌ Error testing extractor:', error);
      }
    } else {
      console.log('⚠️ PrismWeave content script not available for testing');
    }
  } else {
    console.log('ℹ️ Not on Stack Overflow blog - run this on a SO blog page for full testing');
  }

  console.log('🏁 Test completed');
})();
