const { BookmarkletGenerator } = require('./dist/utils/bookmarklet-generator');

const config = {
  githubToken: 'ghp_1234567890abcdef1234567890abcdef12345678',
  githubRepo: 'testuser/testrepo',
  defaultFolder: 'documents',
  commitMessageTemplate: 'Add captured content: {title}',
  captureImages: true,
  removeAds: true,
  removeNavigation: true,
};

console.log('=== DEBUG BOOKMARKLET GENERATION ===');

// Test with minify false to see raw output
const unminified = BookmarkletGenerator.generateBookmarklet(config, { minify: false });
console.log('UNMINIFIED:');
console.log(unminified);
console.log('\nLength:', unminified.length);

// Test with minify true
const minified = BookmarkletGenerator.generateBookmarklet(config, { minify: true });
console.log('\nMINIFIED:');
console.log(minified);
console.log('\nLength:', minified.length);

// Test different config
const config2 = {
  ...config,
  githubRepo: 'user2/repo2',
  removeAds: false,
};

const different = BookmarkletGenerator.generateBookmarklet(config2, { minify: true });
console.log('\nDIFFERENT CONFIG:');
console.log(different);
console.log('\nSame as first?', minified === different);
