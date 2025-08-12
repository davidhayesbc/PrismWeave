// Direct test of bookmarklet generation
const baseUrl = 'https://davidhayesbc.github.io/PrismWeave';
const version = '1.0.0';

// Sample config encoded as params
const configParams = 'token=ghp_1234567890abcdefghijklmnopqrstuvwxyz1234&repo=username%2Frepository&folder=documents&msgTpl=Add+captured+content%3A+%7Btitle%7D';

const loaderScript = `
(function(){
  if(window.prismweaveBookmarklet){
    window.prismweaveBookmarklet.show();
    return;
  }
  var s=document.createElement('script');
  s.src='${baseUrl}/bookmarklet.js?v=${version}&${configParams}';
  s.onload=function(){
    if(window.PrismWeaveBookmarklet){
      window.prismweaveBookmarklet=new window.PrismWeaveBookmarklet();
      window.prismweaveBookmarklet.init();
    }
  };
  document.head.appendChild(s);
})()`;

// Basic minification (remove comments, extra whitespace)
const minifiedScript = loaderScript
  .replace(/\/\*[\s\S]*?\*\//g, '') // Remove multi-line comments
  .replace(/\/\/.*$/gm, '') // Remove single-line comments
  .replace(/\s+/g, ' ') // Replace multiple whitespace with single space
  .replace(/;\s*}/g, '}') // Remove semicolons before closing braces
  .replace(/\s*{\s*/g, '{') // Remove spaces around opening braces
  .replace(/\s*}\s*/g, '}') // Remove spaces around closing braces
  .replace(/\s*;\s*/g, ';') // Remove spaces around semicolons
  .replace(/\s*,\s*/g, ',') // Remove spaces around commas
  .trim();

const bookmarklet = `javascript:${minifiedScript}`;

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

console.log('\nComparison with old approach:');
console.log('Old approach: ~15,000+ characters (with full runtime embedded)');
console.log('New approach:', bookmarklet.length, 'characters');
console.log('Reduction:', Math.round((1 - bookmarklet.length/15000) * 100) + '%');
