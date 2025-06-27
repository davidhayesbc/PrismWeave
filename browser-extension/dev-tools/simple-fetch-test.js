const fetch = require('node-fetch');

async function testFetch() {
  try {
    console.log('Starting fetch...');
    const response = await fetch(
      'https://www.docker.com/blog/how-to-use-the-postgres-docker-official-image/'
    );
    console.log('Fetch completed, status:', response.status);

    const html = await response.text();
    console.log('HTML length:', html.length);
    console.log('First 200 chars:', html.substring(0, 200));
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

testFetch();
