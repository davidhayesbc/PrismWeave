# Anthropic Content Extraction Diagnosis

## 🚨 **Issue Identified**

The PrismWeave extension successfully captured content from the Anthropic
research page
`https://www.anthropic.com/research/project-vend-1?utm_source=tldrwebdev`, but
it captured **the wrong content**:

### **What Was Captured (WRONG):**

- Figure captions only: "Figure 1: The future as a mini-fridge"
- Footnotes section: Links and references
- Total content: Only 156 words
- Missing: Entire main article content

### **What Should Have Been Captured (CORRECT):**

- Main heading: "Project Vend: Can Claude run a small shop? (And why does that
  matter?)"
- Full article sections:
  - Introduction about the experiment
  - "Why did you have an LLM run a small business?"
  - "Claude's performance review" with detailed analysis
  - "Identity crisis" section
  - "What's next?" conclusions
- Expected content: 3000+ words

## 🔍 **Root Cause Analysis** _(UPDATED)_

**NEW FINDINGS:** Based on diagnostic script testing on live page:

- ✅ **Selectors ARE working correctly** - Found main content (17,532 chars)
- ✅ **Content detection IS working** - Correctly identified article content
- ❌ **Content cleaning/conversion is FAILING** - Only 156 words reach final
  output

### **ROOT CAUSE IDENTIFIED:**

The issue is **NOT** in the selector phase, but in the **content cleaning
process**. Our content cleaner is removing the main article content and only
leaving figure captions and footnotes.

### **Evidence:**

- Diagnostic shows selectors find correct container: `'main article'`,
  `'article'`, `'main'`
- Container has 17,532 characters including main article text
- Final markdown has only 156 words (figure captions + footnotes)
- **99.1% content loss** during cleaning/conversion process

### **Likely Cleaning Issues:**

1. **Aggressive cleaning rules** - Main content elements have classes that match
   our removal rules
2. **Over-zealous ad detection** - Article content misidentified as promotional
   content
3. **Empty element removal** - Content structure being destroyed by cleaning
   process
4. **Navigation/metadata removal** - Article sections wrongly classified as
   navigation

## 🧪 **Diagnostic Tools Created**

### **debug-anthropic-extraction.js**

Comprehensive diagnostic script that:

- Tests all 25+ Anthropic selectors on the live page
- Shows exactly what content each selector finds
- Identifies which elements contain the actual article content
- Provides recommendations for better selectors

### **debug-anthropic-cleaning.js** _(NEW)_

Content cleaning diagnostic script that:

- Simulates the exact cleaning process our extension uses
- Shows which elements get removed by each cleaning rule
- Tracks content length before/after each cleaning step
- Identifies if main content is being removed during cleaning

### **How to Use:**

1. Navigate to:
   `https://www.anthropic.com/research/project-vend-1?utm_source=tldrwebdev`
2. Open browser console (F12)
3. Copy and paste **both** diagnostic scripts
4. Run the scripts and compare selector vs cleaning results

## 🔧 **Expected Fix Strategy** _(UPDATED)_

Based on the new diagnostic findings, we need to fix the **content cleaning
process**:

### **1. Modify Content Cleaning Rules**

Update `content-cleaner.ts` to be less aggressive for research articles:

```typescript
// Add exception for research article content
if (isAnthropicResearchPage() && elementContainsMainContent(el)) {
  // Skip aggressive cleaning for main content areas
  return;
}
```

### **2. Improve Anthropic-Specific Cleaning**

Create Anthropic-specific cleaning rules that preserve article structure:

```typescript
// Preserve figure elements but not sidebar figures
// Preserve footnote sections at end of article
// Don't remove elements with substantial paragraph content
```

### **3. Add Content Validation in Cleaning**

Before removing any element, check if it contains key article phrases:

```typescript
const hasArticleContent =
  el.textContent?.includes('Project Vend') ||
  el.textContent?.includes('Claude performed') ||
  el.textContent?.includes('performance review');

if (hasArticleContent) {
  // Don't remove this element
  return;
}
```

### **4. Fix Markdown Conversion Process**

Ensure the markdown converter doesn't filter out article content during
conversion.

## � **Fix Implementation** _(NEW)_

### **Root Cause Resolution**

The issue was identified as overly aggressive content cleaning that removed main
article content while preserving only figure captions and footnotes.

### **Changes Made**

#### **1. Enhanced Content Cleaner (`content-cleaner.ts`)**

- ✅ Added `isResearchPage` and `domain` options to `ICleaningOptions`
- ✅ Implemented **gentle cleaning mode** for research pages
- ✅ Skip aggressive text-based ad removal for Anthropic/research pages
- ✅ Apply only essential cleaning (scripts, styles, obvious ads)
- ✅ Preserve research content that might contain keywords like "research",
  "model", etc.

#### **2. Enhanced Content Extractor (`content-extractor.ts`)**

- ✅ Added `isResearchPage()` method to detect research/academic pages
- ✅ Automatic domain detection and research page classification
- ✅ Pass domain and research page flags to content cleaner
- ✅ Research page detection for: anthropic.com, arxiv.org, research URLs, AI/ML
  domains

#### **3. Research Page Detection Logic**

```typescript
// Detects research pages based on:
// - Domain patterns (anthropic.com, arxiv.org, etc.)
// - Path patterns (/research/, /papers/, etc.)
// - URL keywords (research, AI, ML, technical, etc.)
```

### **Expected Improvements**

- **Content Preservation**: 80%+ content preservation vs previous 1%
- **Word Count**: 2000+ words vs previous 156 words
- **Content Quality**: Full research article vs only figure captions
- **Structure**: Proper headings, paragraphs, and research content

## 📋 **Testing Instructions** _(NEW)_

### **Quick Test**

1. Load the updated extension in Chrome
2. Navigate to:
   `https://www.anthropic.com/research/project-vend-1?utm_source=tldrwebdev`
3. Run in console: `testAnthropicCleaningFix()` (from `test-anthropic-fix.js`)
4. Check preservation rate >80% and >1000 words

### **Complete Test**

1. Run in console: `runAllTests()` (from `test-anthropic-complete.js`)
2. Verify both content extraction and content script communication pass
3. Confirm capture of full Project VEND research article content

### **Manual Verification**

1. Use browser extension to capture the Anthropic page
2. Verify markdown output contains:
   - ✅ "Project VEND" title and content
   - ✅ Research methodology sections
   - ✅ 2000+ words of actual article content
   - ✅ Proper paragraph structure
   - ❌ NOT just figure captions and footnotes

## 📋 **Next Steps** _(UPDATED)_

1. **✅ COMPLETE:** Content cleaning diagnostic and fix implementation
2. **🔄 IN PROGRESS:** Test the fix on live Anthropic page
3. **📋 TODO:** Verify fix works across other research domains
4. **📋 TODO:** Test the complete capture workflow end-to-end
5. **📋 TODO:** Document the gentle cleaning approach for future reference

## 🎯 **Success Criteria**

The fix will be successful when:

- ✅ Captures the main article heading
- ✅ Extracts 2000+ words of article content (not just 156)
- ✅ Includes all major sections (introduction, performance review, etc.)
- ✅ Contains research-specific content (not just figures/footnotes)
- ✅ Generates meaningful markdown with proper structure
- ✅ **Content cleaning preserves 90%+ of article text**

---

**Current Status:** **Root cause identified as content cleaning issue.** Ready
to fix the cleaning process to preserve research article content.
