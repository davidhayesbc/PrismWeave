// Test script for Stack Overflow blog extractor
// Run this in the browser console on a stackoverflow.blog page to test the new extractor

console.log('🔍 Testing Stack Overflow Blog Extractor...');

// Check if we're on the right page
if (!window.location.href.includes('stackoverflow.blog')) {
  console.error('❌ This test should be run on a stackoverflow.blog page');
  console.log('Navigate to a blog post like: https://stackoverflow.blog/2024/...');
} else {
  console.log('✅ Detected Stack Overflow blog page');

  // Test the extractor (this simulates what the content script does)
  try {
    // Check if the StackOverflowBlogExtractor is available
    if (typeof window.StackOverflowBlogExtractor === 'undefined') {
      console.log('📦 StackOverflowBlogExtractor not available in window - this is expected');
      console.log('The extractor runs inside the content script context');
      console.log('To test manually, check the browser extension popup after capturing');
    } else {
      // If somehow available, test it
      const extractor = new window.StackOverflowBlogExtractor();
      const result = extractor.extractBlogContent();

      if (result) {
        console.log('✅ Stack Overflow extractor test successful!');
        console.log('📄 Title:', result.title);
        console.log('📝 Content length:', result.content.length, 'characters');
        console.log('👤 Author:', result.author || 'Not found');
        console.log('📅 Publish date:', result.publishDate || 'Not found');
        console.log('🏷️ Tags:', result.tags.length > 0 ? result.tags.join(', ') : 'None found');
        console.log('⏱️ Reading time:', result.readingTime || 'Not calculated', 'minutes');

        // Show a preview of the content
        console.log('\n📖 Content preview (first 300 chars):');
        console.log(result.content.substring(0, 300) + '...');

        // Check for common issues
        const issues = [];
        if (result.content.toLowerCase().includes('stack overflow for teams')) {
          issues.push('⚠️ Contains promotional content about Stack Overflow for Teams');
        }
        if (result.content.toLowerCase().includes('products')) {
          issues.push('⚠️ Contains "Products" navigation text');
        }
        if (result.content.toLowerCase().includes('recent articles')) {
          issues.push('⚠️ Contains "Recent articles" sidebar content');
        }

        if (issues.length > 0) {
          console.log('\n🚨 Potential issues detected:');
          issues.forEach(issue => console.log(issue));
        } else {
          console.log('\n✅ No obvious content quality issues detected');
        }
      } else {
        console.error('❌ Stack Overflow extractor returned null result');
      }
    }

    // Test basic DOM analysis
    console.log('\n🔍 DOM Analysis:');

    // Check for article elements
    const articles = document.querySelectorAll('article');
    console.log(`📰 Found ${articles.length} article element(s)`);

    // Check for main content
    const mainContent = document.querySelector('main');
    console.log(
      `📄 Main element:`,
      mainContent ? `${mainContent.textContent?.length} chars` : 'Not found'
    );

    // Check title
    const h1 = document.querySelector('h1');
    console.log(`📋 H1 title:`, h1 ? h1.textContent?.trim() : 'Not found');

    // Check for promotional content
    const bodyText = document.body.textContent || '';
    const promoKeywords = [
      'Stack Overflow for Teams',
      'Products',
      'Recent articles',
      'Latest Podcast',
    ];
    const foundPromo = promoKeywords.filter(keyword => bodyText.includes(keyword));
    if (foundPromo.length > 0) {
      console.log('🚨 Found promotional content:', foundPromo.join(', '));
    } else {
      console.log('✅ No obvious promotional content detected');
    }

    console.log('\n🎯 To test the full extraction:');
    console.log('1. Make sure the PrismWeave extension is loaded');
    console.log('2. Press Ctrl+Alt+S to capture this page');
    console.log('3. Check the browser console for "StackOverflowBlogExtractor" logs');
    console.log('4. Verify the captured content in your repository');
  } catch (error) {
    console.error('❌ Error during testing:', error);
  }
}

console.log('\n✨ Test completed');
