const { createCanvas } = require('canvas');
const fs = require('fs');
const path = require('path');

// Create icons directory if it doesn't exist
const iconsDir = path.join(__dirname, '..', 'icons');
if (!fs.existsSync(iconsDir)) {
    fs.mkdirSync(iconsDir, { recursive: true });
}

// Also create icons in dist directory
const distIconsDir = path.join(__dirname, '..', 'dist', 'icons');
if (!fs.existsSync(distIconsDir)) {
    fs.mkdirSync(distIconsDir, { recursive: true });
}

// Icon sizes to generate
const sizes = [16, 32, 48, 128];

function generateIcon(size) {
    const canvas = createCanvas(size, size);
    const ctx = canvas.getContext('2d');
    
    // Clear background
    ctx.fillStyle = 'transparent';
    ctx.fillRect(0, 0, size, size);
    
    // Draw document icon background
    const padding = size * 0.1;
    const docWidth = size - (padding * 2);
    const docHeight = size - (padding * 2);
    
    // Document background (white with border)
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(padding, padding, docWidth, docHeight);
    
    // Document border
    ctx.strokeStyle = '#2196F3';
    ctx.lineWidth = Math.max(1, size / 32);
    ctx.strokeRect(padding, padding, docWidth, docHeight);
    
    // Document fold (top-right corner)
    const foldSize = size * 0.15;
    ctx.beginPath();
    ctx.moveTo(size - padding - foldSize, padding);
    ctx.lineTo(size - padding, padding + foldSize);
    ctx.lineTo(size - padding, padding);
    ctx.closePath();
    ctx.fillStyle = '#e3f2fd';
    ctx.fill();
    ctx.stroke();
    
    // Document lines (content representation)
    if (size >= 32) {
        const lineY = padding + (size * 0.25);
        const lineSpacing = size * 0.08;
        const lineWidth = docWidth * 0.7;
        
        ctx.strokeStyle = '#90caf9';
        ctx.lineWidth = Math.max(1, size / 48);
        
        for (let i = 0; i < 3; i++) {
            const y = lineY + (i * lineSpacing);
            const width = i === 2 ? lineWidth * 0.6 : lineWidth; // Last line shorter
            ctx.beginPath();
            ctx.moveTo(padding + (docWidth * 0.15), y);
            ctx.lineTo(padding + (docWidth * 0.15) + width, y);
            ctx.stroke();
        }
    }
    
    // Capture arrow (download symbol)
    if (size >= 24) {
        const arrowSize = size * 0.2;
        const arrowX = size - padding - arrowSize - (size * 0.05);
        const arrowY = size - padding - arrowSize - (size * 0.05);
        
        // Arrow background circle
        ctx.fillStyle = '#4CAF50';
        ctx.beginPath();
        ctx.arc(arrowX + arrowSize/2, arrowY + arrowSize/2, arrowSize/2, 0, 2 * Math.PI);
        ctx.fill();
        
        // Arrow shape
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        const centerX = arrowX + arrowSize/2;
        const centerY = arrowY + arrowSize/2;
        const arrowWidth = arrowSize * 0.3;
        const arrowHeight = arrowSize * 0.4;
        
        // Arrow shaft
        ctx.fillRect(centerX - arrowWidth/6, centerY - arrowHeight/2, arrowWidth/3, arrowHeight * 0.6);
        
        // Arrow head
        ctx.moveTo(centerX, centerY + arrowHeight/2);
        ctx.lineTo(centerX - arrowWidth/2, centerY);
        ctx.lineTo(centerX + arrowWidth/2, centerY);
        ctx.closePath();
        ctx.fill();
    }
    
    return canvas.toBuffer('image/png');
}

// Generate all icon sizes
sizes.forEach(size => {
    console.log(`Generating ${size}x${size} icon...`);
    const iconBuffer = generateIcon(size);
    
    // Save to both locations
    const filename = `icon${size}.png`;
    fs.writeFileSync(path.join(iconsDir, filename), iconBuffer);
    fs.writeFileSync(path.join(distIconsDir, filename), iconBuffer);
    
    console.log(`✓ Created ${filename}`);
});

console.log('\n✅ All icons generated successfully!');
console.log('Icons created in:');
console.log(`  - ${iconsDir}`);
console.log(`  - ${distIconsDir}`);
