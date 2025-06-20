const path = require('path');
const FileManager = require('./src/utils/file-manager.js');

// Mock settings
const mockSettings = {
  capture: {
    filenamePattern: '{title}_{domain}_{timestamp}',
    includeImages: true,
    includeStyles: false
  }
};

// Mock content
const pageContent = {
  title: 'JavaScript Tutorial for Beginners',
  content: 'Learn programming with JavaScript frameworks and Node.js',
  url: 'https://tutorial.example.com',
  domain: 'example.com',
  timestamp: new Date().toISOString(),
  wordCount: 10,
  readingTime: 1,
  quality: 8,
  images: [],
  links: [],
  textContent: 'Learn programming with JavaScript frameworks and Node.js'
};

const fileManager = new FileManager();
const metadata = fileManager.generateMetadata(pageContent, mockSettings);

console.log('Generated tags:', metadata.tags);
console.log('Content:', pageContent.content);
console.log('Title:', pageContent.title);
console.log('Text to analyze:', `${pageContent.title || ''} ${pageContent.content || ''}`.toLowerCase());
