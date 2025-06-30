// Debug script to understand the nested list processing issue

const html = `
<ul>
  <li>Parent item 1
    <ul>
      <li>Child item 1.1</li>
      <li>Child item 1.2</li>
    </ul>
  </li>
  <li>Parent item 2</li>
</ul>
`;

console.log('Original HTML:');
console.log(html);

// Simulate the processing logic
const ulRegex = /<ul[^>]*>(.*?)<\/ul>/gis;
const liRegex = /<li[^>]*>(.*?)<\/li>/gis;

const match = html.match(ulRegex);
if (match) {
  const content = match[0].replace(/<ul[^>]*>(.*?)<\/ul>/i, '$1');
  console.log('\nUL content:');
  console.log(JSON.stringify(content));

  const items = content.match(liRegex);
  console.log('\nLI items:');
  items?.forEach((item, index) => {
    console.log(`Item ${index}:`, JSON.stringify(item));

    const itemContent = item.replace(/<li[^>]*>(.*?)<\/li>/i, '$1');
    console.log(`Item ${index} content:`, JSON.stringify(itemContent));

    // Check for nested lists
    const nestedUl = itemContent.match(/<ul[^>]*>(.*?)<\/ul>/gis);
    if (nestedUl) {
      console.log(`Item ${index} has nested UL:`, JSON.stringify(nestedUl[0]));

      // Extract nested items
      const nestedContent = nestedUl[0].replace(/<ul[^>]*>(.*?)<\/ul>/i, '$1');
      console.log(`Nested content:`, JSON.stringify(nestedContent));

      const nestedItems = nestedContent.match(liRegex);
      console.log(
        `Nested items:`,
        nestedItems?.map(item => JSON.stringify(item))
      );

      // Replace nested list with empty string
      const afterReplacement = itemContent.replace(/<ul[^>]*>(.*?)<\/ul>/gis, '');
      console.log(`After replacement:`, JSON.stringify(afterReplacement));

      // Strip HTML
      const stripped = afterReplacement.replace(/<[^>]*>/g, '');
      console.log(`After stripping HTML:`, JSON.stringify(stripped));
      console.log(`Trimmed:`, JSON.stringify(stripped.trim()));
    }
  });
}
