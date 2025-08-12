// Test the new short bookmarklet generation
const { BookmarkletGenerator } = require('./browser-extension/dist/bookmarklet/generator.js');

const testConfig = {
  githubToken: 'ghp_1234567890abcdefghijklmnopqrstuvwxyz1234',
  githubRepo: 'username/repository',
  defaultFolder: 'documents',
  commitMessageTemplate: 'Add captured content: {title}',
  captureImages: true,
  removeAds: false,
  removeNavigation: false
};

try {
  const bookmarklet = BookmarkletGenerator.generateBookmarklet(testConfig);
  
  console.log('Generated bookmarklet:');
  console.log(bookmarklet);
  console.log('\nLength:', bookmarklet.length, 'characters');
  
  if (bookmarklet.length < 500) {
    console.log('✅ SHORT: Very good length for a bookmarklet');
  } else if (bookmarklet.length < 1000) {
    console.log('✅ GOOD: Acceptable length for a bookmarklet');
  } else if (bookmarklet.length < 2000) {
    console.log('⚠️  LONG: Getting close to browser limits');
  } else {
    console.log('❌ TOO LONG: May hit browser URL length limits');
  }
  
} catch (error) {
  console.error('Error generating bookmarklet:', error.message);
}
