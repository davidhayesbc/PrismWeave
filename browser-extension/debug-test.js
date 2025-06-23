const { simpleMarkdownConversion } = require('./src/utils/test-utilities.ts');

const htmlInput = '<pre><code>#!/bin/bash\necho "test"\nexit</code></pre>';
const result = simpleMarkdownConversion(htmlInput, 'Test Script', 'https://example.com');

console.log('Result content:');
console.log(JSON.stringify(result.content, null, 2));
console.log('---');
console.log('Full result:');
console.log(JSON.stringify(result, null, 2));
