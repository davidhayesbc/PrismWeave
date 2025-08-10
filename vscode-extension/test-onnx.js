// Test ONNX Runtime availability
// Run with: node test-onnx.js

console.log('Testing ONNX Runtime availability...');

try {
    const ort = require('onnxruntime-node');
    console.log('✅ ONNX Runtime loaded successfully');
    
    // Try to get available providers
    try {
        const providers = ort.InferenceSession.getAvailableProviders();
        console.log('✅ Available execution providers:', providers);
    } catch (error) {
        console.log('⚠️  Could not get execution providers:', error.message);
    }
    
} catch (error) {
    console.log('❌ ONNX Runtime not available:', error.message);
    process.exit(1);
}

console.log('✅ ONNX Runtime test completed successfully');
