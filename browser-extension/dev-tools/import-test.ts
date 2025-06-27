console.log('Starting import test...');

try {
  console.log('About to import markdown-converter-core...');
  import('../src/utils/markdown-converter-core.ts')
    .then(() => {
      console.log('Import successful!');
    })
    .catch(error => {
      console.error('Import failed:', error);
    });
} catch (error) {
  console.error('Sync import error:', error);
}
