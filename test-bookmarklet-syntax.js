// Test script to validate bookmarklet syntax
// This will check if our fix resolves the "Unexpected end of input" error

class BookmarkletSyntaxTester {
  constructor() {
    this.testData = {
      githubToken: 'github_pat_test_token_value',
      githubRepo: 'testuser/testrepo',
      defaultFolder: 'documents',
      commitMessage: 'PrismWeave: Add {title}',
      fileNaming: 'title-date'
    };
  }

  // Copy the fixed generateCompactBookmarklet method
  generateCompactBookmarklet(formData) {
    const token = formData.githubToken;
    const repo = formData.githubRepo;
    const folder = formData.defaultFolder;
    const msgTemplate = formData.commitMessage || 'PrismWeave: Add {title}';

    // Build the bookmarklet JavaScript as a simple string without template literals
    const jsCode = [
      '(function(){',
      'function extractTitle(){',
      '  var title = document.querySelector(\'[property="og:title"]\');',
      '  if(title) return title.getAttribute(\'content\').trim();',
      '  title = document.querySelector(\'h1\');',
      '  if(title) return title.textContent.trim();',
      '  return document.title || \'Untitled\';',
      '}',
      
      'function findMainContent(){',
      '  var selectors = [\'article\',\'main\',\'.content\',\'#content\'];',
      '  for(var i=0; i<selectors.length; i++){',
      '    var el = document.querySelector(selectors[i]);',
      '    if(el && el.textContent && el.textContent.trim().length > 100) return el;',
      '  }',
      '  return document.body;',
      '}',
      
      'function cleanContent(el){',
      '  var clone = el.cloneNode(true);',
      '  var removeSelectors = [\'script\',\'style\',\'nav\',\'header\',\'footer\',\'.ad\',\'.advertisement\'];',
      '  removeSelectors.forEach(function(sel){',
      '    var elements = clone.querySelectorAll(sel);',
      '    for(var i=0; i<elements.length; i++) elements[i].remove();',
      '  });',
      '  return clone;',
      '}',
      
      'function htmlToMarkdown(html){',
      '  var md = html;',
      '  md = md.replace(/<h([1-6])[^>]*>(.*?)<\\/h[1-6]>/gi, function(m,l,c){',
      '    return \'\\n\' + \'#\'.repeat(parseInt(l)) + \' \' + c.replace(/<[^>]*>/g,\'\').trim() + \'\\n\';',
      '  });',
      '  md = md.replace(/<p[^>]*>(.*?)<\\/p>/gi, \'\\n$1\\n\');',
      '  md = md.replace(/<(strong|b)[^>]*>(.*?)<\\/(strong|b)>/gi, \'**$2**\');',
      '  md = md.replace(/<(em|i)[^>]*>(.*?)<\\/(em|i)>/gi, \'*$2*\');',
      '  md = md.replace(/<a[^>]*href=["\\\']([^"\\\']*)["\\\'][^>]*>(.*?)<\\/a>/gi, \'[$2]($1)\');',
      '  md = md.replace(/<[^>]*>/g, \'\');',
      '  md = md.replace(/\\n\\s*\\n\\s*\\n/g, \'\\n\\n\').trim();',
      '  return md;',
      '}',
      
      'var title = extractTitle();',
      'var contentEl = findMainContent();',
      'var cleanedEl = cleanContent(contentEl);',
      'var markdown = htmlToMarkdown(cleanedEl.innerHTML);',
      'var wordCount = cleanedEl.textContent.split(/\\s+/).filter(function(w){return w.length>0;}).length;',
      
      'var frontmatter = \'---\\n\';',
      'frontmatter += \'title: "\' + title.replace(/"/g, \'\\\\\"\') + \'"\\n\';',
      'frontmatter += \'url: "\' + location.href + \'"\\n\';',
      'frontmatter += \'domain: "\' + location.hostname + \'"\\n\';',
      'frontmatter += \'extracted_at: "\' + new Date().toISOString() + \'"\\n\';',
      'frontmatter += \'word_count: \' + wordCount + \'\\n\';',
      'frontmatter += \'extraction_method: "bookmarklet"\\n\';',
      'frontmatter += \'---\\n\\n\';',
      
      'var fullContent = frontmatter + markdown;',
      'var filename = title.replace(/[^\\w\\s-]/g, \'\').replace(/\\s+/g, \'-\').toLowerCase().slice(0, 40) + \'-\' + new Date().toISOString().slice(0, 10) + \'.md\';',
      
      'fetch(\'https://api.github.com/repos/' + repo + '/contents/' + folder + '/\' + filename, {',
      '  method: \'PUT\',',
      '  headers: {',
      '    \'Authorization\': \'token ' + token + '\',',
      '    \'Content-Type\': \'application/json\'',
      '  },',
      '  body: JSON.stringify({',
      '    message: \'' + msgTemplate + '\'.replace(\'{title}\', title),',
      '    content: btoa(unescape(encodeURIComponent(fullContent)))',
      '  })',
      '}).then(function(r){',
      '  if(r.ok){',
      '    r.json().then(function(data){',
      '      alert(\'✅ Page captured successfully!\');',
      '    });',
      '  } else {',
      '    alert(\'❌ Capture failed (\' + r.status + \')\');',
      '  }',
      '}).catch(function(e){',
      '  alert(\'❌ Network error: \' + e.message);',
      '});',
      '})();'
    ].join('');

    return 'javascript:' + encodeURIComponent(jsCode);
  }

  testBookmarkletSyntax() {
    console.log('🧪 Testing bookmarklet syntax...');
    
    try {
      // Generate the bookmarklet
      const bookmarklet = this.generateCompactBookmarklet(this.testData);
      console.log('✅ Bookmarklet generated successfully');
      
      // Extract the JavaScript code (remove 'javascript:' prefix and decode)
      const jsCode = decodeURIComponent(bookmarklet.substring(11));
      console.log('✅ JavaScript code decoded successfully');
      
      // Test if the JavaScript code is syntactically valid
      try {
        new Function(jsCode);
        console.log('✅ JavaScript syntax is valid!');
        
        // Show a sample of the generated code
        const preview = jsCode.length > 200 ? jsCode.substring(0, 200) + '...' : jsCode;
        console.log('📝 Generated JavaScript preview:');
        console.log(preview);
        
        return {
          success: true,
          message: 'Bookmarklet syntax test passed!',
          codeLength: jsCode.length,
          bookmarkletLength: bookmarklet.length
        };
        
      } catch (syntaxError) {
        console.error('❌ JavaScript syntax error:', syntaxError.message);
        return {
          success: false,
          message: 'JavaScript syntax error: ' + syntaxError.message,
          error: syntaxError
        };
      }
      
    } catch (generationError) {
      console.error('❌ Bookmarklet generation error:', generationError.message);
      return {
        success: false,
        message: 'Generation error: ' + generationError.message,
        error: generationError
      };
    }
  }

  run() {
    console.log('🌟 PrismWeave Bookmarklet Syntax Test');
    console.log('====================================');
    
    const result = this.testBookmarkletSyntax();
    
    console.log('\n📊 Test Results:');
    console.log('Success:', result.success);
    console.log('Message:', result.message);
    
    if (result.success) {
      console.log('Code Length:', result.codeLength, 'characters');
      console.log('Bookmarklet Length:', result.bookmarkletLength, 'characters');
    }
    
    return result;
  }
}

// Run the test
const tester = new BookmarkletSyntaxTester();
const testResult = tester.run();

// Export the result for verification
if (typeof module !== 'undefined') {
  module.exports = testResult;
}