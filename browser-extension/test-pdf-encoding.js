// Test script to validate PDF binary encoding
const fs = require('fs');
const path = require('path');

async function testPDFEncoding() {
  try {
    console.log('🔍 Testing PDF binary encoding...');

    // Path to the corrupted PDF
    const corruptedPDFPath =
      'd:\\source\\PrismWeaveDocs\\documents\\pdfs\\2025-07-15-gptaiflow.tech-2025-01-18-pdf-1-techai-goolge-whitepaperprompt-en.pdf';

    if (!fs.existsSync(corruptedPDFPath)) {
      console.log('❌ Corrupted PDF file not found');
      return;
    }

    // Read the corrupted file
    const corruptedBuffer = fs.readFileSync(corruptedPDFPath);
    console.log(`📁 Corrupted PDF size: ${corruptedBuffer.length} bytes`);

    // Check the first few bytes (PDF header should be %PDF-)
    const header = corruptedBuffer.slice(0, 10).toString('ascii');
    console.log(`📋 File header: "${header}"`);

    if (!header.startsWith('%PDF-')) {
      console.log('❌ File does not have valid PDF header');

      // Try to decode as base64 and check if that fixes it
      try {
        const base64Content = corruptedBuffer.toString('utf8');
        console.log(`🔤 Trying to decode as base64...`);

        const decodedBuffer = Buffer.from(base64Content, 'base64');
        const decodedHeader = decodedBuffer.slice(0, 10).toString('ascii');
        console.log(`📋 Decoded header: "${decodedHeader}"`);

        if (decodedHeader.startsWith('%PDF-')) {
          console.log('✅ File appears to be base64 encoded!');

          // Save the corrected version
          const correctedPath = path.join(
            path.dirname(corruptedPDFPath),
            'corrected-' + path.basename(corruptedPDFPath)
          );
          fs.writeFileSync(correctedPath, decodedBuffer);
          console.log(`💾 Saved corrected PDF to: ${correctedPath}`);
          console.log(`📏 Corrected size: ${decodedBuffer.length} bytes`);
        } else {
          console.log('❌ Decoded content is not a valid PDF either');
        }
      } catch (decodeError) {
        console.log('❌ Failed to decode as base64:', decodeError.message);
      }
    } else {
      console.log('✅ File has valid PDF header');
    }
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

testPDFEncoding();
