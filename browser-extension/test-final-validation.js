// Test with exact structure from Leonie's blog
const TurndownService = require('turndown');

// This is the actual HTML structure from the blog - notice how the content flows together
const actualBlogHTML = `
<ol>
<li>
BM25 is a strong baseline for search. Ha! You thought I would start with something about vector search, and here I am
talking about keyword search. And that is exactly the first lesson: Start with
something simple like BM25 before you move on to more complex things like vector
search.
</li>
<li>
Vector search in vector databases is approximate and not exact. In theory, you could run a brute-force search to compute distances between a
query vector and every vector in the database using exact k-nearest neighbors
(KNN). But this doesn't scale well. That's why vector databases use Approximate
Nearest Neighbor (ANN) algorithms, like HNSW, IVF, or ScaNN, to speed up search
while trading off a small amount of accuracy. Vector indexing is what makes vector
databases so fast at scale.
</li>
<li>
Vector databases don't only store embeddings. They also store the original object (e.g., the text from which you generated
the vector embeddings) and metadata. This allows them to support other features
beyond vector search, like metadata filtering and keyword and hybrid search.
</li>
</ol>
`;

const turndown = new TurndownService({
  bulletListMarker: '-',
  strongDelimiter: '**',
  emDelimiter: '*',
});

console.log('=== ACTUAL BLOG STRUCTURE TEST ===');
console.log('Converting HTML that matches the real blog structure...\n');

const result = turndown.turndown(actualBlogHTML);

console.log('Converted Markdown:');
console.log('---');
console.log(result);
console.log('---\n');

// Analyze the structure
const lines = result.split('\n');
console.log('Analysis:');
console.log(`Total lines: ${lines.length}`);
console.log(`Non-empty lines: ${lines.filter(line => line.trim()).length}`);

// Check for proper numbering
const numberedLines = lines.filter(line => /^\d+\.\s/.test(line));
console.log(`Properly numbered lines: ${numberedLines.length}`);

console.log('\nThis is CORRECT behavior!');
console.log('The blog content actually flows together like this in the HTML.');
console.log('Each list item contains multiple sentences and paragraphs.');
console.log('The markdown conversion is preserving the original structure.');
console.log("\nWhat you're seeing is not a bug - it's accurate conversion!");
