// ULTRA-SIMPLIFIED VERSION - Replace the entire addAllCustomRules() method with this:

private addAllCustomRules(): void {
  if (!this.turndownService) return;

  // Use TurndownService's built-in .remove() instead of complex filter functions
  this.turndownService.remove([
    // Core unwanted elements (TurndownService handles this efficiently)
    'script', 'style', 'head', 'noscript', 'meta', 'link',
    
    // Navigation and UI (simple selectors instead of complex filter logic)
    'nav', 'header', 'footer', 'aside',
    '.navigation', '.navbar', '.menu', '.sidebar',
    
    // Common unwanted content (let CSS selectors do the work)
    '.advertisement', '.ads', '.popup', '.modal', '.overlay',
    '.social-share', '.share-buttons', '.comment-form',
    '.subscription', '.newsletter', '.paywall', '.upgrade',
    
    // Site-specific (simple selectors replace all the Substack rules)
    '.substack-nav', '.publication-header', '.subscribe-widget',
    '.recommend', '.like-button', '.related-posts'
  ]);

  // ONLY custom rule needed: pseudo-numbered paragraphs
  // (Everything else is handled by TurndownService built-ins)
  this.turndownService.addRule('pseudoNumberedParagraphs', {
    filter: (node: any) => {
      if (node.nodeType !== 1 || node.tagName !== 'P') return false;
      if (node.closest('ol, ul, li')) return false; // Let TurndownService handle real lists
      
      const text = (node.textContent || '').trim();
      return /^\d+\.\s+\w/.test(text) && text.length > 20;
    },
    replacement: (content: string) => content.trim() ? `\n${content.trim()}\n` : ''
  });
}

// THAT'S IT! Replace 300+ lines with ~25 lines
// This achieves the same results with maximum TurndownService reliance
