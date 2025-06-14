# PrismWeave Extension Icons

This directory contains the following icon files:

- `icon16.png` - 16x16 pixels (for toolbar) ✅ Generated
- `icon32.png` - 32x32 pixels (for extension management) ✅ Generated
- `icon48.png` - 48x48 pixels (for extension management) ✅ Generated
- `icon128.png` - 128x128 pixels (for Chrome Web Store) ✅ Generated

## Design Guidelines

The PrismWeave icon represents:
- Document capture/collection with a clean document icon
- Modern flat design with PrismWeave brand colors
- Blue (#2196F3) for the document border and primary elements
- Green (#4CAF50) for the capture/download indicator
- Simple geometric shapes that scale well across all sizes

## Generated Icons

The current icons are generated programmatically using the `scripts/generate-icons.js` script. They feature:
- A document with a folded corner (representing web pages)
- Horizontal lines indicating content
- A green circular arrow icon in the bottom-right (representing capture/download)
- Clean, scalable design that works at all sizes

## Regenerating Icons

To regenerate the icons (if you want to modify the design):

```bash
npm run generate-icons
```

Or run directly:
```bash
node scripts/generate-icons.js
```

## Icon Concepts

1. **Document with Arrow**: A document icon with a downward arrow indicating capture
2. **Folder with Plus**: A folder icon with a plus sign indicating document collection
3. **Page with Bookmark**: A page icon with a bookmark corner indicating saved content

## Creating Icons

Use tools like:
- Adobe Illustrator/Photoshop
- Figma
- GIMP (free)
- Online icon generators

Export as PNG files with transparent backgrounds.

## Temporary Solution

For development/testing purposes, you can use placeholder icons or generate simple colored squares using online tools until proper icons are designed.
