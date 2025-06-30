# Script to replace console.log statements with logger.debug in content-extractor.ts

$filePath = "D:\source\PrismWeave\browser-extension\src\utils\content-extractor.ts"
$content = Get-Content $filePath -Raw

# Define replacements as hashtable
$replacements = @{
    "console.log('ContentExtractor: Removing unwanted elements...');" = "this.logger.debug('Removing unwanted elements...');"
    "console.log('ContentExtractor: Removing', unwanted.length, 'unwanted elements');" = "this.logger.debug('Removing', unwanted.length, 'unwanted elements');"
    "console.log('ContentExtractor: Removing', excluded.length, 'excluded elements');" = "this.logger.debug('Removing', excluded.length, 'excluded elements');"
    "console.log('ContentExtractor: Removing', emptyElements.length, 'empty elements');" = "this.logger.debug('Removing', emptyElements.length, 'empty elements');"
    "console.log('ContentExtractor: Removed', removedWhitespace, 'whitespace-only elements');" = "this.logger.debug('Removed', removedWhitespace, 'whitespace-only elements');"
    "console.log('ContentExtractor: Removed', removedAds, 'ad-like elements');" = "this.logger.debug('Removed', removedAds, 'ad-like elements');"
    "console.log('ContentExtractor: Searching for largest content container...');" = "this.logger.debug('Searching for largest content container...');"
    "console.log('ContentExtractor: Found best content container with score:', bestScore);" = "this.logger.debug('Found best content container with score:', bestScore);"
    "console.log('ContentExtractor: Element tag:', bestCandidate.tagName);" = "this.logger.debug('Element tag:', bestCandidate.tagName);"
    "console.log('ContentExtractor: Element class:', bestCandidate.className);" = "this.logger.debug('Element class:', bestCandidate.className);"
    "console.log('ContentExtractor: Element id:', bestCandidate.id);" = "this.logger.debug('Element id:', bestCandidate.id);"
    "console.log('ContentExtractor: Text length:', bestCandidate.textContent?.length || 0);" = "this.logger.debug('Text length:', bestCandidate.textContent?.length || 0);"
    "console.log('ContentExtractor: No suitable content container found, trying fallback...');" = "this.logger.debug('No suitable content container found, trying fallback...');"
    "console.log('ContentExtractor: Content still loading...', currentContent, 'chars');" = "this.logger.debug('Content still loading...', currentContent, 'chars');"
    "console.log('ContentExtractor: Content appears to have finished loading');" = "this.logger.debug('Content appears to have finished loading');"
    "console.log('ContentExtractor: Finished waiting for content load');" = "this.logger.debug('Finished waiting for content load');"
    "console.log('ContentExtractor: Waiting for Docker blog specific content...');" = "this.logger.debug('Waiting for Docker blog specific content...');"
    "console.log('ContentExtractor: Docker blog content wait timeout');" = "this.logger.debug('Docker blog content wait timeout');"
}

# Apply replacements
foreach ($old in $replacements.Keys) {
    $new = $replacements[$old]
    $content = $content -replace [regex]::Escape($old), $new
}

# Handle multi-line console.log statements
$multiLinePatterns = @(
    @{
        old = "      console.log(`n        'ContentExtractor: Element rejected - likely navigation:',`n        element.tagName,`n        element.className,`n        'links:',`n        links`n      );"
        new = "      this.logger.debug(`n        'Element rejected - likely navigation:',`n        element.tagName,`n        element.className,`n        'links:',`n        links`n      );"
    },
    @{
        old = "    console.log('ContentExtractor: Element assessment:', {`n      tag: element.tagName,`n      class: element.className || 'none',`n      id: element.id || 'none',`n      textLength: text.length,`n      paragraphs,`n      links,`n      images: element.querySelectorAll('img').length,`n      textHtmlRatio: ratio,`n      decision: 'accepted'`n    });"
        new = "    this.logger.debug('Element assessment:', {`n      tag: element.tagName,`n      class: element.className || 'none',`n      id: element.id || 'none',`n      textLength: text.length,`n      paragraphs,`n      links,`n      images: element.querySelectorAll('img').length,`n      textHtmlRatio: ratio,`n      decision: 'accepted'`n    });"
    },
    @{
        old = "      console.log(`n        'ContentExtractor: Evaluating candidate:',`n        candidate.tagName,`n        'Score:',`n        score,`n        'Class:',`n        candidate.className`n      );"
        new = "      this.logger.debug(`n        'Evaluating candidate:',`n        candidate.tagName,`n        'Score:',`n        score,`n        'Class:',`n        candidate.className`n      );"
    },
    @{
        old = "        console.log(`n          'ContentExtractor: Found fallback candidate:',`n          candidate.tagName,`n          'Text length:',`n          textLength`n        );"
        new = "        this.logger.debug(`n          'Found fallback candidate:',`n          candidate.tagName,`n          'Text length:',`n          textLength`n        );"
    },
    @{
        old = "    console.log('ContentExtractor: Dynamic site check:', {`n      host: window.location.hostname,`n      hasSPA: Boolean(window.history.pushState),`n      hasReact: Boolean((window as any).React || document.querySelector('[data-reactroot]')),`n      hasVue: Boolean((window as any).Vue),`n      hasAngular: Boolean((window as any).angular),`n      hasMetaRefresh: Boolean(document.querySelector('meta[http-equiv=`"refresh`"]')),`n      hasRedirect: document.title.includes('Redirect') || document.body.textContent?.includes('redirecting') || false`n    });"
        new = "    this.logger.debug('Dynamic site check:', {`n      host: window.location.hostname,`n      hasSPA: Boolean(window.history.pushState),`n      hasReact: Boolean((window as any).React || document.querySelector('[data-reactroot]')),`n      hasVue: Boolean((window as any).Vue),`n      hasAngular: Boolean((window as any).angular),`n      hasMetaRefresh: Boolean(document.querySelector('meta[http-equiv=`"refresh`"]')),`n      hasRedirect: document.title.includes('Redirect') || document.body.textContent?.includes('redirecting') || false`n    });"
    },
    @{
        old = "            console.log(`ContentExtractor: Found Docker content via selector: `${selector}`);"
        new = "            this.logger.debug(`Found Docker content via selector: `${selector}`);"
    }
)

# Save the modified content
Set-Content -Path $filePath -Value $content -NoNewline

Write-Host "Console.log replacements completed"

# Count remaining console.log statements
$finalCount = ($content | Select-String "console\.log" -AllMatches).Matches.Count
Write-Host "Remaining console.log statements: $finalCount"
