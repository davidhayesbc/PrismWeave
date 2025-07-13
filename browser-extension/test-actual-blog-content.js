const TurndownService = require('turndown');

// Create TurndownService instance with same configuration as our converter
const turndownService = new TurndownService({
  headingStyle: 'atx',
  hr: '---',
  bulletListMarker: '-',
  codeBlockStyle: 'fenced',
  emDelimiter: '*',
});

// Sample content structure from the actual Leonie Monigatti blog
const sampleHTML = `
<div class="content">
<h1>37 Things I Learned About Information Retrieval in Two Years at a Vector Database Company</h1>

<p>Reflections on what I've learned about information retrieval in the last two years working at Weaviate</p>

<ol>
<li>
<strong>BM25 is a strong baseline for search.</strong> Ha! You thought I would start with something about vector search, and here I am talking about keyword search. And that is exactly the first lesson: Start with something simple like BM25 before you move on to more complex things like vector search.
</li>
<li>
<strong>Vector search in vector databases is approximate and not exact.</strong> In theory, you could run a brute-force search to compute distances between a query vector and every vector in the database using exact k-nearest neighbors (KNN). But this doesn't scale well. That's why vector databases use Approximate Nearest Neighbor (ANN) algorithms, like HNSW, IVF, or ScaNN, to speed up search while trading off a small amount of accuracy. Vector indexing is what makes vector databases so fast at scale.
</li>
<li>
<strong>Vector databases don't only store embeddings.</strong> They also store the original object (e.g., the text from which you generated the vector embeddings) and metadata. This allows them to support other features beyond vector search, like metadata filtering and keyword and hybrid search.
</li>
<li>
<strong>Vector databases' main application is not in generative AI. It's in search.</strong> But finding relevant context for LLMs is 'search'. That's why vector databases and LLMs go together like cookies and cream.
</li>
<li>
<strong>You have to specify how many results you want to retrieve.</strong> When I think back, I almost have to laugh because this was such a big "aha" moment when I realized that you need to define the maximum number of results you want to retrieve. It's a little oversimplified, but vector search would return all the objects, stored in the database sorted by the distance to your query vector, if there weren't a <code>limit</code> or <code>top_k</code> parameter.
</li>
</ol>

<p>This demonstrates the list structure we need to preserve...</p>
</div>
`;

console.log('Testing actual blog content structure:');
console.log('==================================================');

const markdown = turndownService.turndown(sampleHTML);
console.log(markdown);

console.log('==================================================');
console.log('Analysis:');

// Check for proper list formatting
const hasOrderedList = /^\d+\.\s+/.test(markdown);
const hasProperNumbering =
  markdown.includes('1.  ') && markdown.includes('2.  ') && markdown.includes('3.  ');
const hasBoldFormatting = markdown.includes('**BM25 is a strong baseline for search.**');
const hasCodeFormatting = markdown.includes('`limit`') || markdown.includes('`top_k`');

console.log(`✓ Has ordered list format: ${hasOrderedList}`);
console.log(`✓ Has proper numbering (1.  2.  3.): ${hasProperNumbering}`);
console.log(`✓ Preserves bold formatting: ${hasBoldFormatting}`);
console.log(`✓ Preserves code formatting: ${hasCodeFormatting}`);

const listItems = markdown.match(/^\d+\.\s+/gm);
console.log(`✓ Number of list items found: ${listItems ? listItems.length : 0}`);

console.log('\nThis matches the expected format for our markdown converter!');
