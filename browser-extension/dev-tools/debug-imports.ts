#!/usr/bin/env node

console.log('🔧 Script starting...');

console.log('🔧 Chalk imported');

console.log('🔧 fs-extra imported');

import { NodeMarkdownConverter } from './markdown-converter-node.ts';
console.log('🔧 path imported');

console.log('🔧 About to import NodeMarkdownConverter...');
console.log('🔧 NodeMarkdownConverter imported successfully');

console.log('🔧 Creating instance...');
const converter = new NodeMarkdownConverter();
console.log('🔧 Instance created successfully');

console.log('🔧 All imports successful, script would continue...');
