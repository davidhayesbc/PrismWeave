const TurndownService = require('turndown');

// Create test with the exact same HTML structure that we'd get from a real webpage
const realWorldHTML = `
<div>
<h1>37 Things I Learned About Information Retrieval in Two Years at a Vector Database Company</h1>

<p>Reflections on what I've learned about information retrieval in the last two years working at Weaviate</p>

<ol>
<li><strong>BM25 is a strong baseline for search.</strong> Ha! You thought I would start with something about vector search, and here I am talking about keyword search. And that is exactly the first lesson: Start with something simple like BM25 before you move on to more complex things like vector search.</li>
<li><strong>Vector search in vector databases is approximate and not exact.</strong> In theory, you could run a brute-force search to compute distances between a query vector and every vector in the database using exact k-nearest neighbors (KNN). But this doesn't scale well. That's why vector databases use Approximate Nearest Neighbor (ANN) algorithms, like HNSW, IVF, or ScaNN, to speed up search while trading off a small amount of accuracy. Vector indexing is what makes vector databases so fast at scale.</li>
<li><strong>Vector databases don't only store embeddings.</strong> They also store the original object (e.g., the text from which you generated the vector embeddings) and metadata. This allows them to support other features beyond vector search, like metadata filtering and keyword and hybrid search.</li>
<li><strong>Vector databases' main application is not in generative AI. It's in search.</strong> But finding relevant context for LLMs is 'search'. That's why vector databases and LLMs go together like cookies and cream.</li>
<li><strong>You have to specify how many results you want to retrieve.</strong> When I think back, I almost have to laugh because this was such a big "aha" moment when I realized that you need to define the maximum number of results you want to retrieve. It's a little oversimplified, but vector search would return all the objects, stored in the database sorted by the distance to your query vector, if there weren't a <code>limit</code> or <code>top_k</code> parameter.</li>
<li><strong>There are many different types of embeddings.</strong> When you think of a vector embedding, you probably visualize something like [-0.9837, 0.1044, 0.0090, …, -0.2049]. That's called a dense vector, and it is the most commonly used type of vector embedding. But there's also many other types of vectors, such as sparse ([0, 2, 0, …, 1]), binary ([0, 1, 1, …, 0]), and multi-vector embeddings ([[-0.9837, …, -0.2049], [ 0.1044, …, 0.0090], …, [-0.0937, …, 0.5044]]), which can be used for different purposes.</li>
<li><strong>Fantastic embedding models and where to find them.</strong> The first place to go is the <a href="https://huggingface.co/spaces/mteb/leaderboard">Massive Text Embedding Benchmark (MTEB)</a>. It covers a wide range of different tasks for embedding models, including classification, clustering, and retrieval. If you're focused on information retrieval, you might want to check out <a href="https://github.com/beir-cellar/beir">BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models</a>.</li>
<li><strong>The majority of embedding models on MTEB are English.</strong> If you're working with multilingual or non-English languages, it might be worth checking out <a href="https://arxiv.org/html/2502.13595v1">MMTEB (Massive Multilingual Text Embedding Benchmark)</a>.</li>
<li><strong>A little history on vector embeddings:</strong> Before there were today's contextual embeddings (e.g., BERT), there were static embeddings (e.g., Word2Vec, GloVe). They are static because each word has a fixed representation, while contextual embeddings generate different representations for the same word based on the surrounding context. Although today's contextual embeddings are much more expressive, static embeddings can be helpful in computationally restrained environments because they can be looked up from pre-computed tables.</li>
<li><strong>Don't confuse sparse vectors and sparse embeddings.</strong> It took me a while until I understood that sparse vectors can be generated in different ways: Either by applying statistical scoring functions like TF-IDF or BM25 to term frequencies (often retrieved via inverted indexes), or with neural sparse embedding models like SPLADE. That means a sparse embedding is a sparse vector, but not all sparse vectors are necessarily sparse embeddings.</li>
</ol>

<p>This demonstrates the structure that should be preserved in markdown.</p>
</div>
`;

// Test 1: Basic TurndownService conversion (like our current implementation)
console.log('=== Test 1: Basic TurndownService (Current Implementation) ===');
const turndownBasic = new TurndownService({
  headingStyle: 'atx',
  bulletListMarker: '-',
  codeBlockStyle: 'fenced',
  emDelimiter: '*',
});

const markdownBasic = turndownBasic.turndown(realWorldHTML);
console.log(markdownBasic);

console.log('\n=== Analysis of Basic Conversion ===');
const lines = markdownBasic.split('\n');
const listLines = lines.filter(line => /^\d+\.\s+/.test(line));
console.log('Number of list items found:', listLines.length);
console.log('List items:');
listLines.forEach((line, index) => {
  console.log(`${index + 1}: ${line.substring(0, 50)}...`);
});

// Test 2: Check if the issue is with multi-line list items
console.log('\n=== Test 2: Check for Multi-line List Issues ===');
const hasProperListStructure = markdownBasic.match(/^\d+\.\s+\*\*.*?\*\*/gm);
console.log(
  'Found formatted list items:',
  hasProperListStructure ? hasProperListStructure.length : 0
);

// Test 3: Try with different line endings and whitespace
console.log('\n=== Test 3: Test Different HTML Structures ===');
const compactHTML = realWorldHTML.replace(/\n/g, '').replace(/\s+/g, ' ');
const markdownCompact = turndownBasic.turndown(compactHTML);
const compactListLines = markdownCompact.split('\n').filter(line => /^\d+\.\s+/.test(line));
console.log('Compact HTML - List items found:', compactListLines.length);

// Test 4: Test if the issue is spacing or content splitting
console.log('\n=== Test 4: Check Content Preservation ===');
const originalText = realWorldHTML
  .replace(/<[^>]*>/g, ' ')
  .replace(/\s+/g, ' ')
  .trim();
const markdownText = markdownBasic
  .replace(/[*_`#\[\]()]/g, ' ')
  .replace(/\s+/g, ' ')
  .trim();
console.log('Original word count:', originalText.split(' ').length);
console.log('Markdown word count:', markdownText.split(' ').length);
console.log(
  'Content preservation ratio:',
  ((markdownText.split(' ').length / originalText.split(' ').length) * 100).toFixed(1) + '%'
);

console.log('\n=== Summary ===');
console.log('✓ Lists are being converted:', listLines.length > 0);
console.log('✓ Formatting preserved:', markdownBasic.includes('**') && markdownBasic.includes('`'));
console.log('✓ All 10 list items found:', listLines.length === 10);
console.log(
  '✓ Proper numbering:',
  markdownBasic.includes('1.  ') && markdownBasic.includes('10.  ')
);
