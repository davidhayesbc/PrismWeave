// Test script for shell scripting code block issues on Chris Penner blog
// Run this on https://chrispenner.ca/posts/transcript-tests

(function () {
  console.log('=== PrismWeave Shell Script Code Block Test ===');
  console.log('URL:', window.location.href);
  console.log('Time:', new Date().toISOString());

  // Check extension availability
  if (typeof chrome === 'undefined' || !chrome.runtime) {
    console.error('❌ Chrome extension APIs not available');
    return;
  }

  console.log('✅ Chrome extension APIs available');

  // Analyze the page's code blocks before extraction
  console.log('\n🔍 Pre-extraction Code Block Analysis:');
  
  const codeBlocks = document.querySelectorAll('pre code, code');
  console.log(`Found ${codeBlocks.length} code elements on page`);

  codeBlocks.forEach((block, index) => {
    const isBlock = block.parentElement?.tagName === 'PRE';
    const type = isBlock ? 'Block' : 'Inline';
    const className = block.className;
    const content = block.textContent || '';
    
    console.log(`\n${index + 1}. ${type} Code:`, {
      className: className || 'no class',
      contentLength: content.length,
      contentPreview: content.substring(0, 100) + (content.length > 100 ? '...' : ''),
      hasShellCommands: /\$|#!/.test(content),
      hasBackticks: /`/.test(content),
      hasSpecialChars: /[<>&]/.test(content)
    });
  });

  // Look for potential problematic content
  const shellCodeBlocks = Array.from(codeBlocks).filter(block => {
    const content = block.textContent || '';
    return /(\$|#!|zsh|bash|shell)/.test(content);
  });

  console.log(`\n🐚 Found ${shellCodeBlocks.length} blocks with shell-like content`);

  // Test the extension's markdown conversion
  console.log('\n🚀 Testing PrismWeave markdown conversion...');

  chrome.runtime.sendMessage(
    {
      type: 'EXTRACT_AND_CONVERT_TO_MARKDOWN',
      data: {
        preserveFormatting: true,
        removeAds: true,
        removeNavigation: true,
      },
    },
    function (response) {
      if (chrome.runtime.lastError) {
        console.error('❌ Extension communication error:', chrome.runtime.lastError.message);
        return;
      }

      if (!response) {
        console.error('❌ No response from extension');
        return;
      }

      console.log('\n📊 Extension Response Analysis:');
      console.log('Success:', response.success);

      if (response.success && response.data) {
        const data = response.data;
        const markdown = data.markdown || '';

        console.log('\n📝 Markdown Analysis:');
        console.log('  - Total length:', markdown.length);
        console.log('  - Word count:', data.metadata?.wordCount || 0);

        // Analyze code block preservation
        const codeBlockMatches = markdown.match(/```[\s\S]*?```/g) || [];
        const inlineCodeMatches = markdown.match(/`[^`]+`/g) || [];

        console.log('\n📦 Code Block Preservation:');
        console.log(`  - Fenced code blocks: ${codeBlockMatches.length}`);
        console.log(`  - Inline code: ${inlineCodeMatches.length}`);

        // Check for shell script content preservation        const shellContent = codeBlockMatches.filter(block => 
          /(\$|#!|zsh|bash|shell)/.test(block)
        );

        console.log(`  - Shell script blocks: ${shellContent.length}`);

        // Check for language tagging
        const languageTaggedBlocks = codeBlockMatches.filter(block =>
          /```\w+/.test(block)
        );

        console.log(`  - Language-tagged blocks: ${languageTaggedBlocks.length}`);

        // Display some code block examples
        console.log('\n📋 Code Block Examples:');
        codeBlockMatches.slice(0, 3).forEach((block, i) => {
          console.log(`${i + 1}. ${block.substring(0, 200)}${block.length > 200 ? '...' : ''}`);
        });

        // Check for specific shell command preservation
        const bashCommands = markdown.match(/(\$|#!)[^\n]*/g) || [];
        console.log(`\n💻 Shell Commands Found: ${bashCommands.length}`);
        bashCommands.slice(0, 5).forEach((cmd, i) => {
          console.log(`  ${i + 1}. ${cmd}`);
        });

        // Look for potential issues
        const issues = [];
        
        if (codeBlockMatches.length < shellCodeBlocks.length) {
          issues.push('Some shell code blocks may not have been preserved');
        }
        
        if (markdown.includes('&lt;') || markdown.includes('&gt;') || markdown.includes('&amp;')) {
          issues.push('HTML entities not properly decoded in code');
        }
        
        if (markdown.includes('```\n```')) {
          issues.push('Empty code blocks detected');
        }

        if (issues.length > 0) {
          console.log('\n⚠️ Potential Issues:');
          issues.forEach((issue, i) => {
            console.log(`  ${i + 1}. ${issue}`);
          });
        } else {
          console.log('\n✅ No obvious code block issues detected');
        }

        // Test specific problematic content
        const problemContent = [
          'set -e',
          'source "../../transcript_helpers.sh"',
          'fetch "$unauthenticated_user"',
          '#!/usr/bin/env zsh'
        ];

        console.log('\n🔍 Checking for specific shell content:');
        problemContent.forEach(content => {
          const found = markdown.includes(content);
          console.log(`  "${content}": ${found ? '✅ Found' : '❌ Missing'}`);
        });

      } else {
        console.error('❌ Extension extraction failed:', response.error || 'Unknown error');
      }
    }
  );
})();
