// Test pure TurndownService with proper ol/li structure
const TurndownService = require('turndown');

// Create HTML with proper ol/li structure like the website should have
const properOlLiHTML = `
<div>
<p>Here are some of the things I've learned and some common misconceptions I see:</p>

<ol>
<li>BM25 is a strong baseline for search. Ha! You thought I would start with something about vector search, and here I am talking about keyword search. And that is exactly the first lesson: Start with something simple like BM25 before you move on to more complex things like vector search.</li>
<li>Vector search in vector databases is approximate and not exact. In theory, you could run a brute-force search to compute distances between a query vector and every vector in the database using exact k-nearest neighbors (KNN). But this doesn't scale well.</li>
<li>Vector databases don't only store embeddings. They also store the original object (e.g., the text from which you generated the vector embeddings) and metadata.</li>
</ol>
</div>
`;

console.log('=== TESTING PURE TURNDOWN WITH PROPER OL/LI ===');
console.log('Testing with minimal configuration (no custom rules):\n');

// Test with minimal configuration - just like the core should work
const turndown = new TurndownService({
  bulletListMarker: '-',
  strongDelimiter: '**',
  emDelimiter: '*',
  headingStyle: 'atx',
  codeBlockStyle: 'fenced',
});

const result = turndown.turndown(properOlLiHTML);

console.log('Input HTML structure:');
console.log('- Contains <ol> tag');
console.log('- Contains <li> tags');
console.log('- Proper HTML list structure\n');

console.log('Result:');
console.log('---');
console.log(result);
console.log('---\n');

// Analysis
const hasNumberedList = result.includes('1.') && result.includes('2.') && result.includes('3.');
const hasProperListStructure = /^\d+\.\s+/m.test(result);

console.log('Analysis:');
console.log(`Contains numbered list items: ${hasNumberedList}`);
console.log(`Has proper markdown list structure: ${hasProperListStructure}`);
console.log(`Lines with numbered format: ${(result.match(/^\d+\.\s+/gm) || []).length}`);

if (hasNumberedList) {
  console.log('\n✅ TurndownService IS working correctly with proper ol/li structure!');
  console.log('The issue might be that the website HTML is not actually using ol/li tags.');
} else {
  console.log('\n❌ Something is wrong with TurndownService list conversion.');
}
