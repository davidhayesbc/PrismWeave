// Debug script to test content capture
// Run this in the browser console on any page to test capture functionality

console.log('🐛 PrismWeave Debug Script');

// Test 1: Check if content script is loaded
async function testContentScript() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'PING' });
    console.log('✅ Content script ping:', response);
    return true;
  } catch (error) {
    console.log('❌ Content script not responding:', error);
    return false;
  }
}

// Test 2: Check service worker status
async function testServiceWorker() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_STATUS' });
    console.log('✅ Service worker status:', response);
    return response.data;
  } catch (error) {
    console.log('❌ Service worker error:', error);
    return false;
  }
}

// Test 3: Check settings
async function testSettings() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_SETTINGS' });
    console.log('✅ Settings:', response);
    return response.data;
  } catch (error) {
    console.log('❌ Settings error:', error);
    return false;
  }
}

// Test 4: Test capture
async function testCapture() {
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'CAPTURE_PAGE',
      data: {
        url: window.location.href,
        title: document.title,
        source: 'debug-test',
      },
    });
    console.log('✅ Capture result:', response);
    return response;
  } catch (error) {
    console.log('❌ Capture error:', error);
    return false;
  }
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Running PrismWeave debug tests...');

  console.log('\n1. Testing content script...');
  await testContentScript();

  console.log('\n2. Testing service worker...');
  await testServiceWorker();

  console.log('\n3. Testing settings...');
  await testSettings();

  console.log('\n4. Testing capture...');
  await testCapture();

  console.log('\n🏁 Debug tests completed!');
}

// Auto-run if script is executed
if (typeof window !== 'undefined') {
  runAllTests();
}
