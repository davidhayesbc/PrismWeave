// Debug the actual HTML structure that's causing the issue
const TurndownService = require('turndown');

// Based on your raw markdown output, it seems like the list items are NOT in an <ol> structure
// Let me test different HTML structures that might be causing this

console.log('=== DEBUGGING REAL HTML STRUCTURE ===\n');

// Test 1: What if the content is not in a proper <ol> structure?
const possibleHTML1 = `
<div>
<p>BM25 is a strong baseline for search. Ha! You thought I would start with something about vector search, and here I am talking about keyword search. And that is exactly the first lesson: Start with something simple like BM25 before you move on to more complex things like vector search.</p>

<p>Vector search in vector databases is approximate and not exact. In theory, you could run a brute-force search to compute distances between a query vector and every vector in the database using exact k-nearest neighbors (KNN). But this doesn't scale well. That's why vector databases use Approximate Nearest Neighbor (ANN) algorithms, like HNSW, IVF, or ScaNN, to speed up search while trading off a small amount of accuracy. Vector indexing is what makes vector databases so fast at scale.</p>

<p>Vector databases don't only store embeddings. They also store the original object (e.g., the text from which you generated the vector embeddings) and metadata. This allows them to support other features beyond vector search, like metadata filtering and keyword and hybrid search.</p>
</div>
`;

// Test 2: What if it's in a div with numbered classes but no actual list structure?
const possibleHTML2 = `
<div>
<div class="item-1">BM25 is a strong baseline for search. Ha! You thought I would start with something about vector search...</div>
<div class="item-2">Vector search in vector databases is approximate and not exact. In theory, you could run a brute-force search...</div>
<div class="item-3">Vector databases don't only store embeddings. They also store the original object...</div>
</div>
`;

// Test 3: What if it's using custom list styling that's not semantic HTML?
const possibleHTML3 = `
<div>
<p><span>1.</span> BM25 is a strong baseline for search. Ha! You thought I would start with something about vector search, and here I am talking about keyword search. And that is exactly the first lesson: Start with something simple like BM25 before you move on to more complex things like vector search.</p>

<p><span>2.</span> Vector search in vector databases is approximate and not exact. In theory, you could run a brute-force search to compute distances between a query vector and every vector in the database using exact k-nearest neighbors (KNN). But this doesn't scale well. That's why vector databases use Approximate Nearest Neighbor (ANN) algorithms, like HNSW, IVF, or ScaNN, to speed up search while trading off a small amount of accuracy. Vector indexing is what makes vector databases so fast at scale.</p>

<p><span>3.</span> Vector databases don't only store embeddings. They also store the original object (e.g., the text from which you generated the vector embeddings) and metadata. This allows them to support other features beyond vector search, like metadata filtering and keyword and hybrid search.</p>
</div>
`;

const turndown = new TurndownService({
  bulletListMarker: '-',
  strongDelimiter: '**',
  emDelimiter: '*',
});

console.log('Test 1: Plain paragraphs (no list structure)');
console.log('---');
const result1 = turndown.turndown(possibleHTML1);
console.log(result1.substring(0, 200) + '...');
console.log('Has numbered lists:', /^\d+\.\s/.test(result1));
console.log();

console.log('Test 2: Divs with classes (no semantic list)');
console.log('---');
const result2 = turndown.turndown(possibleHTML2);
console.log(result2.substring(0, 200) + '...');
console.log('Has numbered lists:', /^\d+\.\s/.test(result2));
console.log();

console.log('Test 3: Paragraphs with number spans (pseudo-list)');
console.log('---');
const result3 = turndown.turndown(possibleHTML3);
console.log(result3.substring(0, 200) + '...');
console.log('Has numbered lists:', /^\d+\.\s/.test(result3));
console.log();

console.log('=== CONCLUSION ===');
console.log('If your output looks like Test 1 or Test 2, then the webpage');
console.log('is NOT using proper HTML <ol><li> structure for the numbered list.');
console.log("This would explain why you're seeing plain paragraphs instead of numbered lists.");
console.log();
console.log('The fix would be to add custom detection and conversion');
console.log('for non-semantic list structures in the markdown converter.');
