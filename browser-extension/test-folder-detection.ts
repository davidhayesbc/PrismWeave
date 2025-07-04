// Quick verification script for folder detection
import { UnifiedFileManager } from './src/utils/unified-file-manager.js';
import { IDocumentMetadata } from './src/types/index.js';

const manager = new UnifiedFileManager();

// Test cases from real-world scenarios
const testCases: IDocumentMetadata[] = [
  {
    title: 'Building Industrial Strength Software without Unit Tests',
    url: 'https://chrispenner.ca/posts/transcript-tests',
    captureDate: '2025-07-03T12:00:00Z',
    tags: ['programming', 'haskell', 'testing'],
    wordCount: 100,
    estimatedReadingTime: 2,
  },
  {
    title: 'JavaScript Best Practices',
    url: 'https://developer.mozilla.org/js-guide',
    captureDate: '2025-07-03T12:00:00Z',
    tags: ['javascript', 'programming'],
    wordCount: 100,
    estimatedReadingTime: 2,
  },
  {
    title: 'How to Build a REST API with Node.js',
    url: 'https://tutorial.com/nodejs-api',
    captureDate: '2025-07-03T12:00:00Z',
    tags: ['tutorial', 'guide', 'how-to'],
    wordCount: 100,
    estimatedReadingTime: 2,
  },
  {
    title: 'Breaking: New AI Breakthrough Announced',
    url: 'https://news.com/ai-breakthrough',
    captureDate: '2025-07-03T12:00:00Z',
    tags: ['news', 'ai', 'announcement'],
    wordCount: 100,
    estimatedReadingTime: 2,
  },
  {
    title: 'Random Content About Cats',
    url: 'https://example.com/cats',
    captureDate: '2025-07-03T12:00:00Z',
    tags: ['cats', 'pets', 'animals'],
    wordCount: 100,
    estimatedReadingTime: 2,
  },
];

console.log('Testing folder detection...\n');

testCases.forEach((metadata, index) => {
  const folder = manager.determineFolder(metadata);
  const fileName = manager.generateFilename(metadata);
  const fullPath = manager.generateFilePath(metadata);
  
  console.log(`Test ${index + 1}:`);
  console.log(`  Title: ${metadata.title}`);
  console.log(`  URL: ${metadata.url}`);
  console.log(`  Tags: [${metadata.tags.join(', ')}]`);
  console.log(`  Detected folder: ${folder}`);
  console.log(`  Generated filename: ${fileName}`);
  console.log(`  Full path: ${fullPath}`);
  console.log('');
});

console.log('Available folders:', manager.getAvailableFolders());
console.log('Tech keywords:', manager.getFolderKeywords('tech').slice(0, 10), '...');
