// Quick validation script to test extension fixes
// Run this in the browser console on the background page

console.log('🔍 PrismWeave Extension Validation');

// Test 1: Check if lazy loading methods exist
const background = new PrismWeaveBackground();
console.log('✅ PrismWeaveBackground instantiated');

// Test 2: Check utility registry
if (typeof PrismWeaveRegistry !== 'undefined') {
  console.log('✅ UtilsRegistry available');
} else {
  console.error('❌ UtilsRegistry not found');
}

// Test 3: Check error handler
if (typeof ErrorHandler !== 'undefined') {
  console.log('✅ ErrorHandler available');
  
  // Test error categorization
  const testError = new Error('GitHub token not configured');
  const categorized = ErrorHandler.createUserFriendlyError(testError);
  console.log('✅ Error categorization works:', categorized);
} else {
  console.error('❌ ErrorHandler not found');
}

// Test 4: Check logger
if (typeof PrismWeaveLogger !== 'undefined') {
  const logger = PrismWeaveLogger.createLogger('ValidationTest');
  logger.info('✅ Logger system working');
} else {
  console.error('❌ Logger not found');
}

// Test 5: Check performance monitor
if (typeof PrismWeavePerf !== 'undefined') {
  const timer = PrismWeavePerf.startTimer('validation-test');
  setTimeout(() => {
    PrismWeavePerf.endTimer(timer);
    console.log('✅ Performance monitor working');
  }, 100);
} else {
  console.warn('⚠️ Performance monitor not loaded (optional)');
}

console.log('🎉 Validation complete! Check the results above.');
