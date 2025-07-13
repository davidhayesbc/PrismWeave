// Quick test to see actual list formatting output
const TurndownService = require('turndown');

// Create TurndownService instance with same settings as our converter
const turndownService = new TurndownService({
  codeBlockStyle: 'fenced',
  fence: '```',
  bulletListMarker: '-',
  linkStyle: 'inlined',
  headingStyle: 'atx',
  hr: '---',
  strongDelimiter: '**',
  emDelimiter: '*',
});

// Test real-world scenario similar to the Leonie Monigatti blog
const html = `
<h1>37 Things I Learned About Information Retrieval</h1>

<ol>
  <li><strong>Vector similarity search</strong> is a powerful tool for finding semantically related documents</li>
  <li><strong>Term frequency</strong> alone is not enough for good search results</li>
  <li><strong>Inverse document frequency</strong> helps weight rare terms more heavily</li>
  <li><strong>Cosine similarity</strong> is scale-invariant and works well for text</li>
  <li><strong>Embedding models</strong> capture semantic meaning better than keyword matching</li>
  <li><strong>Retrieval-Augmented Generation (RAG)</strong> combines search with generation</li>
  <li><strong>Dense vectors</strong> capture semantic relationships</li>
  <li><strong>Sparse vectors</strong> preserve exact keyword matches</li>
  <li><strong>Hybrid search</strong> combines both dense and sparse approaches</li>
  <li><strong>Reranking</strong> can significantly improve initial retrieval results</li>
</ol>

<p>This demonstrates the proper list structure preservation.</p>

<h2>Nested Lists Example</h2>

<ul>
  <li>Main category 1
    <ul>
      <li>Subcategory 1.1</li>
      <li>Subcategory 1.2</li>
    </ul>
  </li>
  <li>Main category 2
    <ol>
      <li>Numbered sub-item 1</li>
      <li>Numbered sub-item 2</li>
    </ol>
  </li>
</ul>
`;

const result = turndownService.turndown(html);
console.log('Enhanced TurndownService list conversion:');
console.log('='.repeat(50));
console.log(result);
console.log('='.repeat(50));

// Test if it preserves structure
const hasOrderedList = result.includes('1.  ');
const hasUnorderedList = result.includes('-   ');
const hasFormatting = result.includes('**Vector similarity search**');

console.log('\nStructure Analysis:');
console.log('✓ Has ordered list:', hasOrderedList);
console.log('✓ Has unordered list:', hasUnorderedList);
console.log('✓ Preserves formatting:', hasFormatting);
console.log('✓ List structure preserved:', hasOrderedList && hasUnorderedList && hasFormatting);
