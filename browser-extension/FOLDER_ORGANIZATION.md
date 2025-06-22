# Automatic Folder Organization

## Overview

PrismWeave now automatically organizes captured articles into appropriate
subfolders based on content analysis. Instead of dropping everything into the
root `documents/` folder, articles are intelligently sorted into topical
subfolders.

## How It Works

### Automatic Classification

The system analyzes three key sources to determine the best folder:

1. **Article Title** - Looks for keywords that indicate the content type
2. **URL** - Examines the domain and path for classification hints
3. **Tags** - Uses extracted metadata tags and keywords

### Available Folders

| Folder      | Description                                   | Example Keywords                                             |
| ----------- | --------------------------------------------- | ------------------------------------------------------------ |
| `tech`      | Programming, software development, technology | programming, javascript, python, react, api, github          |
| `business`  | Business strategy, marketing, finance         | marketing, startup, sales, management, finance, entrepreneur |
| `tutorial`  | How-to guides, learning content               | tutorial, guide, how-to, learn, step-by-step, course         |
| `news`      | News articles, current events                 | news, breaking, report, announcement, current, events        |
| `research`  | Academic papers, research studies             | research, study, academic, journal, analysis, data           |
| `design`    | UI/UX, visual design, creative                | design, ui, ux, css, figma, visual, typography               |
| `tools`     | Software tools, utilities, resources          | tool, utility, software, app, service, platform              |
| `personal`  | Personal blogs, opinions, experiences         | personal, blog, journal, thoughts, reflection, life          |
| `reference` | Documentation, manuals, specs                 | reference, documentation, manual, spec, docs, wiki           |
| `unsorted`  | Default for unclassified content              | (fallback category)                                          |

### File Path Structure

Articles are now saved with the following structure:

```
documents/
├── tech/
│   ├── 2025-06-22-dev-to-react-tutorial.md
│   └── 2025-06-22-github-api-guide.md
├── business/
│   ├── 2025-06-22-startup-marketing.md
│   └── 2025-06-22-sales-strategy.md
├── tutorial/
│   └── 2025-06-22-css-grid-guide.md
└── unsorted/
    └── 2025-06-22-miscellaneous-article.md
```

## Configuration

### Automatic Detection (Default)

By default, PrismWeave uses automatic folder detection. This works for most
content without any configuration.

### Manual Folder Selection

You can override automatic detection:

1. **In Popup**: Use the folder dropdown to select a specific folder for
   captures
2. **In Settings**: Set a default folder that bypasses automatic detection

### Custom Folders

You can create custom folders:

1. Go to extension options
2. Set "Default Folder" to "Custom"
3. Enter your custom folder name
4. All new captures will use this folder

## Benefits

### Better Organization

- **Topic-based Structure**: Related articles are grouped together
- **Easy Navigation**: Find articles by category rather than date
- **Scalable**: Works well with large collections of captured content

### Improved Workflow

- **Automatic Sorting**: No manual organization required
- **Consistent Naming**: Predictable folder structure
- **Repository Cleanliness**: Avoids cluttered root directory

### AI-Ready Structure

- **Topic Clustering**: Enables better AI analysis of related content
- **Content Discovery**: Easier to find articles on specific topics
- **Batch Processing**: Process entire categories at once

## Examples

### Tech Article

**Input**: "Getting Started with React Hooks"  
**URL**: `https://dev.to/react-hooks-tutorial`  
**Result**: `documents/tech/2025-06-22-dev-to-getting-started-react-hooks.md`

### Business Article

**Input**: "5 Marketing Strategies for SaaS Startups"  
**URL**: `https://business.com/saas-marketing`  
**Result**: `documents/business/2025-06-22-business-com-marketing-strategies-saas-startups.md`

### Tutorial Content

**Input**: "Complete Guide to CSS Flexbox"  
**URL**: `https://css-tricks.com/flexbox-guide`  
**Result**: `documents/tutorial/2025-06-22-css-tricks-complete-guide-css-flexbox.md`

## Migration

### Existing Content

- **No Impact**: Previously captured articles remain in their current locations
- **New Structure**: Only new captures use the folder organization
- **Manual Migration**: You can manually move old files to appropriate folders
  if desired

### Repository Compatibility

- **Git History**: Folder structure changes don't affect existing commit history
- **Sync**: Works seamlessly with existing GitHub repositories
- **Backwards Compatible**: Old file paths continue to work

## Troubleshooting

### Misclassified Articles

If an article is placed in the wrong folder:

1. **Manual Override**: Select the correct folder in the popup before capturing
2. **Move Manually**: Relocate the file in your Git repository
3. **Keyword Feedback**: Common misclassifications help improve the algorithm

### Custom Keywords

Currently, custom keywords are not supported, but this is planned for future
releases. The current keyword set covers most common content types effectively.

## Technical Implementation

The folder classification uses a keyword scoring system:

1. **Text Analysis**: Combines title, URL, and tags into searchable text
2. **Keyword Matching**: Scores each folder based on keyword frequency
3. **Best Match**: Selects the folder with the highest score
4. **Fallback**: Uses "unsorted" if no clear match is found

This approach is lightweight, fast, and works entirely within the browser
extension without requiring external AI services.
