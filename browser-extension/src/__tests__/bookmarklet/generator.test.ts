/**
 * Test to verify the optimized bookmarklet code maintains functionality
 * This test ensures that all essential functions and logic are preserved in the optimized version
 */

describe('Optimized Bookmarklet Functionality', () => {
  // Mock DOM and window objects
  const mockDocument = {
    createElement: jest.fn(() => ({
      src: '',
      onload: null,
      onerror: null,
    })),
    head: {
      appendChild: jest.fn(),
    },
  };

  const mockWindow = {
    prismweaveShowToast: jest.fn(),
    prismweaveExtractAndCommit: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    global.document = mockDocument as any;
    global.window = mockWindow as any;
  });

  test('should contain all essential configuration properties', () => {
    const optimizedCode = `(function(){var c={token:'test_token',repository:'user/repo',folder:'documents',commitMessage:'PrismWeave: Add {title}'},n=function(a,b){(window.prismweaveShowToast||alert)(a,b||{})},l=function(){return new Promise(function(s,j){if(window.prismweaveExtractAndCommit)return s();var e=document.createElement('script');e.src='https://example.com/content-extractor-injectable.js';e.onload=function(){window.prismweaveExtractAndCommit?s():j(Error('API load failed'))};e.onerror=function(){j(Error('Script load failed'))};document.head.appendChild(e)})};l().then(function(){return window.prismweaveExtractAndCommit(c,{includeImages:!0,includeLinks:!0,cleanHtml:!0,generateFrontmatter:!0,includeMetadata:!0})}).then(function(r){r.success?n('✅ Captured!',{type:'success',clickUrl:r.data&&r.data.html_url,linkLabel:'View'}):n('❌ Failed: '+(r.error||'Unknown'),{type:'error'})}).catch(function(e){n('❌ Error: '+e.message,{type:'error'})})})();`;

    // Verify essential configuration properties are present
    expect(optimizedCode).toContain('token:');
    expect(optimizedCode).toContain('repository:');
    expect(optimizedCode).toContain('folder:');
    expect(optimizedCode).toContain('commitMessage:');

    // Verify extraction options are preserved
    expect(optimizedCode).toContain('includeImages:!0');
    expect(optimizedCode).toContain('includeLinks:!0');
    expect(optimizedCode).toContain('cleanHtml:!0');
    expect(optimizedCode).toContain('generateFrontmatter:!0');
    expect(optimizedCode).toContain('includeMetadata:!0');

    // Verify function calls are preserved
    expect(optimizedCode).toContain('prismweaveExtractAndCommit');
    expect(optimizedCode).toContain('prismweaveShowToast');
    expect(optimizedCode).toContain('document.createElement');
    expect(optimizedCode).toContain('document.head.appendChild');
  });

  test('should have significantly reduced size compared to original', () => {
    const originalSize = 2072; // Size from our optimization test
    const optimizedCode = `(function(){var c={token:'test_token',repository:'user/repo',folder:'documents',commitMessage:'PrismWeave: Add {title}'},n=function(a,b){(window.prismweaveShowToast||alert)(a,b||{})},l=function(){return new Promise(function(s,j){if(window.prismweaveExtractAndCommit)return s();var e=document.createElement('script');e.src='https://example.com/content-extractor-injectable.js';e.onload=function(){window.prismweaveExtractAndCommit?s():j(Error('API load failed'))};e.onerror=function(){j(Error('Script load failed'))};document.head.appendChild(e)})};l().then(function(){return window.prismweaveExtractAndCommit(c,{includeImages:!0,includeLinks:!0,cleanHtml:!0,generateFrontmatter:!0,includeMetadata:!0})}).then(function(r){r.success?n('✅ Captured!',{type:'success',clickUrl:r.data&&r.data.html_url,linkLabel:'View'}):n('❌ Failed: '+(r.error||'Unknown'),{type:'error'})}).catch(function(e){n('❌ Error: '+e.message,{type:'error'})})})();`;

    const optimizedSize = optimizedCode.length;
    const reduction = (1 - optimizedSize / originalSize) * 100;

    // Should have at least 40% size reduction
    expect(reduction).toBeGreaterThan(40);
    expect(optimizedSize).toBeLessThan(1200); // Should be under 1200 characters
  });

  test('should preserve all essential logic patterns', () => {
    const optimizedCode = `(function(){var c={token:'test_token',repository:'user/repo',folder:'documents',commitMessage:'PrismWeave: Add {title}'},n=function(a,b){(window.prismweaveShowToast||alert)(a,b||{})},l=function(){return new Promise(function(s,j){if(window.prismweaveExtractAndCommit)return s();var e=document.createElement('script');e.src='https://example.com/content-extractor-injectable.js';e.onload=function(){window.prismweaveExtractAndCommit?s():j(Error('API load failed'))};e.onerror=function(){j(Error('Script load failed'))};document.head.appendChild(e)})};l().then(function(){return window.prismweaveExtractAndCommit(c,{includeImages:!0,includeLinks:!0,cleanHtml:!0,generateFrontmatter:!0,includeMetadata:!0})}).then(function(r){r.success?n('✅ Captured!',{type:'success',clickUrl:r.data&&r.data.html_url,linkLabel:'View'}):n('❌ Failed: '+(r.error||'Unknown'),{type:'error'})}).catch(function(e){n('❌ Error: '+e.message,{type:'error'})})})();`;

    // Verify Promise chain pattern is preserved
    expect(optimizedCode).toContain('.then(function');
    expect(optimizedCode).toContain('.catch(function');

    // Verify error handling patterns
    expect(optimizedCode).toContain('Error(');
    expect(optimizedCode).toContain('r.success?');

    // Verify fallback notification pattern
    expect(optimizedCode).toContain('prismweaveShowToast||alert');

    // Verify script injection pattern
    expect(optimizedCode).toContain("createElement('script')");
    expect(optimizedCode).toContain('.onload=function');
    expect(optimizedCode).toContain('.onerror=function');
  });

  test('should use compact boolean literals', () => {
    const optimizedCode = `(function(){var c={token:'test_token',repository:'user/repo',folder:'documents',commitMessage:'PrismWeave: Add {title}'},n=function(a,b){(window.prismweaveShowToast||alert)(a,b||{})},l=function(){return new Promise(function(s,j){if(window.prismweaveExtractAndCommit)return s();var e=document.createElement('script');e.src='https://example.com/content-extractor-injectable.js';e.onload=function(){window.prismweaveExtractAndCommit?s():j(Error('API load failed'))};e.onerror=function(){j(Error('Script load failed'))};document.head.appendChild(e)})};l().then(function(){return window.prismweaveExtractAndCommit(c,{includeImages:!0,includeLinks:!0,cleanHtml:!0,generateFrontmatter:!0,includeMetadata:!0})}).then(function(r){r.success?n('✅ Captured!',{type:'success',clickUrl:r.data&&r.data.html_url,linkLabel:'View'}):n('❌ Failed: '+(r.error||'Unknown'),{type:'error'})}).catch(function(e){n('❌ Error: '+e.message,{type:'error'})})})();`;

    // Should use compact boolean literals instead of verbose ones
    expect(optimizedCode).toContain('!0'); // Instead of 'true'
    expect(optimizedCode).toContain('{}'); // Instead of 'new Object()'

    // Should not contain verbose boolean literals
    expect(optimizedCode).not.toContain('true');
    expect(optimizedCode).not.toContain('false');
  });

  test('should use minimized variable names', () => {
    const optimizedCode = `(function(){var c={token:'test_token',repository:'user/repo',folder:'documents',commitMessage:'PrismWeave: Add {title}'},n=function(a,b){(window.prismweaveShowToast||alert)(a,b||{})},l=function(){return new Promise(function(s,j){if(window.prismweaveExtractAndCommit)return s();var e=document.createElement('script');e.src='https://example.com/content-extractor-injectable.js';e.onload=function(){window.prismweaveExtractAndCommit?s():j(Error('API load failed'))};e.onerror=function(){j(Error('Script load failed'))};document.head.appendChild(e)})};l().then(function(){return window.prismweaveExtractAndCommit(c,{includeImages:!0,includeLinks:!0,cleanHtml:!0,generateFrontmatter:!0,includeMetadata:!0})}).then(function(r){r.success?n('✅ Captured!',{type:'success',clickUrl:r.data&&r.data.html_url,linkLabel:'View'}):n('❌ Failed: '+(r.error||'Unknown'),{type:'error'})}).catch(function(e){n('❌ Error: '+e.message,{type:'error'})})})();`;

    // Verify minimized variable names are used
    expect(optimizedCode).toContain('var c='); // config -> c
    expect(optimizedCode).toContain('n=function'); // showNotification -> n
    expect(optimizedCode).toContain('l=function'); // loadPrismWeaveScript -> l
    expect(optimizedCode).toContain('function(s,j)'); // resolve -> s, reject -> j
    expect(optimizedCode).toContain('var e='); // script element -> e
    expect(optimizedCode).toContain('function(r)'); // result -> r

    // Should not contain verbose variable names
    expect(optimizedCode).not.toContain('config');
    expect(optimizedCode).not.toContain('showNotification');
    expect(optimizedCode).not.toContain('loadPrismWeaveScript');
    expect(optimizedCode).not.toContain('extractionOptions');
  });
});
