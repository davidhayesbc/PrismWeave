// Bookmarklet Entry Point
// Simple entry point for bookmarklet execution

import { BOOKMARKLET_CONFIG } from './config';

/**
 * Generate bookmarklet loader script
 */
export function generateBookmarkletLoader(injectableUrl?: string): string {
  const baseUrl = injectableUrl || BOOKMARKLET_CONFIG.DEFAULT_INJECTABLE_BASE;

  return `javascript:(function(){
    if(window.prismweaveActive){return;}
    var s=document.createElement('script');
    s.src='${baseUrl}/content-extractor-injectable.js';
    s.onload=function(){
      if(window.prismweaveExtractAndCommit){
        window.prismweaveExtractAndCommit();
      }
    };
    document.head.appendChild(s);
    window.prismweaveActive=true;
  })();`;
}

/**
 * Execute bookmarklet in current context
 */
export function executeBookmarklet(): void {
  if (typeof window !== 'undefined') {
    const script = generateBookmarkletLoader();
    eval(script.replace('javascript:', ''));
  }
}
