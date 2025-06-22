// Test script to verify folder classification logic
// Run this in the browser console to test the folder detection

// Test data simulating different types of captured content
const testCases = [
  {
    title: 'How to Build a React App with TypeScript',
    url: 'https://dev.to/programming/react-typescript-tutorial',
    tags: ['programming', 'react', 'typescript', 'tutorial'],
    expected: 'tech',
  },
  {
    title: '10 Marketing Strategies for Startups in 2024',
    url: 'https://business.com/marketing/startup-strategies',
    tags: ['marketing', 'business', 'startup'],
    expected: 'business',
  },
  {
    title: 'Complete Guide to CSS Grid Layout',
    url: 'https://css-tricks.com/grid-tutorial',
    tags: ['css', 'tutorial', 'design', 'web-development'],
    expected: 'tutorial', // Should detect tutorial over tech due to keywords
  },
  {
    title: 'Breaking: Tech Company Reports Record Earnings',
    url: 'https://news.com/tech-earnings-report',
    tags: ['news', 'earnings', 'technology'],
    expected: 'news',
  },
  {
    title: 'My Journey Learning Python',
    url: 'https://myblog.com/personal/python-journey',
    tags: ['personal', 'blog', 'programming'],
    expected: 'personal', // Should detect personal over tech
  },
  {
    title: 'API Documentation - REST Endpoints',
    url: 'https://docs.example.com/api/reference',
    tags: ['api', 'documentation', 'reference'],
    expected: 'reference',
  },
];

// Simulate the folder detection logic
function testFolderClassification() {
  console.log('🧪 Testing Folder Classification Logic\n');

  const FOLDER_MAPPING = {
    tech: [
      'programming',
      'software',
      'coding',
      'development',
      'technology',
      'tech',
      'javascript',
      'python',
      'react',
      'node',
      'github',
      'stackoverflow',
      'dev.to',
      'css',
      'html',
      'typescript',
      'api',
      'framework',
      'library',
    ],
    business: [
      'business',
      'marketing',
      'finance',
      'startup',
      'entrepreneur',
      'sales',
      'management',
      'strategy',
      'linkedin',
      'enterprise',
      'corporate',
      'economics',
      'market',
      'revenue',
      'profit',
    ],
    tutorial: [
      'tutorial',
      'guide',
      'how-to',
      'learn',
      'course',
      'lesson',
      'walkthrough',
      'step-by-step',
      'instructions',
      'tips',
      'howto',
      'example',
    ],
    news: [
      'news',
      'article',
      'blog',
      'opinion',
      'analysis',
      'update',
      'announcement',
      'breaking',
      'report',
      'current',
      'events',
    ],
    research: [
      'research',
      'study',
      'paper',
      'academic',
      'journal',
      'thesis',
      'analysis',
      'data',
      'science',
      'experiment',
      'findings',
      'methodology',
    ],
    design: [
      'design',
      'ui',
      'ux',
      'css',
      'figma',
      'adobe',
      'creative',
      'visual',
      'art',
      'layout',
      'typography',
      'color',
      'interface',
    ],
    tools: [
      'tool',
      'utility',
      'software',
      'app',
      'service',
      'platform',
      'extension',
      'plugin',
      'resource',
      'toolkit',
    ],
    personal: [
      'personal',
      'diary',
      'journal',
      'thoughts',
      'reflection',
      'life',
      'experience',
      'blog',
      'opinion',
    ],
    reference: [
      'reference',
      'documentation',
      'manual',
      'spec',
      'api',
      'docs',
      'wiki',
      'handbook',
      'guide',
    ],
  };

  function autoDetectFolder(metadata) {
    const searchText = [
      metadata.title.toLowerCase(),
      metadata.url.toLowerCase(),
      ...metadata.tags.map(tag => tag.toLowerCase()),
    ].join(' ');

    // Score each folder based on keyword matches
    const folderScores = {};

    Object.entries(FOLDER_MAPPING).forEach(([folder, keywords]) => {
      let score = 0;
      keywords.forEach(keyword => {
        const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
        const matches = searchText.match(regex);
        if (matches) {
          score += matches.length;
        }
      });

      if (score > 0) {
        folderScores[folder] = score;
      }
    });

    // Return folder with highest score
    const bestFolder = Object.entries(folderScores).sort(([, a], [, b]) => b - a)[0];

    return bestFolder ? bestFolder[0] : 'unsorted';
  }

  let passed = 0;
  let failed = 0;

  testCases.forEach((testCase, index) => {
    const detected = autoDetectFolder({
      title: testCase.title,
      url: testCase.url,
      tags: testCase.tags,
      captureDate: new Date().toISOString(),
    });

    const success = detected === testCase.expected;

    console.log(`Test ${index + 1}: ${success ? '✅' : '❌'}`);
    console.log(`  Title: ${testCase.title}`);
    console.log(`  Expected: ${testCase.expected}`);
    console.log(`  Detected: ${detected}`);

    if (!success) {
      failed++;
      console.log(`  🔍 Analysis needed: Check keyword weights and folder priority`);
    } else {
      passed++;
    }
    console.log('');
  });

  console.log(`📊 Results: ${passed} passed, ${failed} failed`);

  if (failed > 0) {
    console.log('\n💡 Tips for improving classification:');
    console.log('- Add more specific keywords to folders');
    console.log('- Adjust keyword weights based on importance');
    console.log('- Consider URL domain patterns');
  }
}

// Run the test
testFolderClassification();
