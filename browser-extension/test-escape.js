// Test escapeHtml mock
const escapeDiv = {
  innerHTML: '',
  _textContent: '',
  set textContent(value) {
    console.log('Setting textContent:', value);
    this._textContent = value;
    this.innerHTML = value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
    console.log('Result innerHTML:', this.innerHTML);
  },
  get textContent() {
    return this._textContent || '';
  },
};

// Test the escape
escapeDiv.textContent = 'Hello <script>world</script>';
console.log('Final innerHTML:', escapeDiv.innerHTML);

escapeDiv.textContent = 'Extracting content...';
console.log('Simple message innerHTML:', escapeDiv.innerHTML);
