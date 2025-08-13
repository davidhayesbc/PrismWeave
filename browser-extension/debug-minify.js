const script = `(function(){
  if(window.prismweaveBookmarklet){
    window.prismweaveBookmarklet.show();
    return;
  }
  var s=document.createElement('script');
  s.src='https://davidhayesbc.github.io/PrismWeave/bookmarklet.js?v=1.0.0&token=ghp_1234567890abcdef1234567890abcdef12345678&repo=testuser%2Ftestrepo&folder=documents&msgTpl=Add+captured+content%3A+%7Btitle%7D&noAds=1&noNav=1';
  s.onload=function(){
    if(window.PrismWeaveBookmarklet){
      window.prismweaveBookmarklet=new window.PrismWeaveBookmarklet();
      window.prismweaveBookmarklet.init();
    }
  };
  document.head.appendChild(s);
})();`;

console.log('ORIGINAL:', script);

// Step by step
let step1 = script.replace(/\/\*[\s\S]*?\*\//g, ''); // Remove multi-line comments
console.log('\nSTEP 1 (remove comments):', step1);

let step2 = step1.replace(/\/\/.*$/gm, ''); // Remove single-line comments
console.log('\nSTEP 2 (remove single comments):', step2);

let step3 = step2.replace(/\s+/g, ' '); // Replace multiple whitespace with single space
console.log('\nSTEP 3 (collapse whitespace):', step3);

let step4 = step3.replace(/\s*{\s*/g, '{'); // Remove spaces around opening braces
console.log('\nSTEP 4 (opening braces):', step4);
