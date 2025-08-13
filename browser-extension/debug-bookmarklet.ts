import { BookmarkletGenerator, IBookmarkletConfig } from './src/utils/bookmarklet-generator';

const config: IBookmarkletConfig = {
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
const config2: IBookmarkletConfig = {
  ...config,
  githubRepo: 'user2/repo2',
  removeAds: false,
};

const different = BookmarkletGenerator.generateBookmarklet(config2, { minify: true });
console.log('\nDIFFERENT CONFIG:');
console.log(different);
console.log('\nSame as first?', minified === different);

console.log('\nENCODED PARAMS TEST:');
// Test the private encodeConfigAsParams method indirectly
const params = new URLSearchParams();
if (config.githubToken) params.set('token', config.githubToken);
if (config.githubRepo) params.set('repo', config.githubRepo);
if (config.defaultFolder) params.set('folder', config.defaultFolder);
if (config.commitMessageTemplate) params.set('msgTpl', config.commitMessageTemplate);

// Boolean flags as single characters to save space
if (config.captureImages === false) params.set('noImg', '1');
if (config.removeAds === true) params.set('noAds', '1');
if (config.removeNavigation === true) params.set('noNav', '1');

console.log('Expected URL params:', params.toString());
