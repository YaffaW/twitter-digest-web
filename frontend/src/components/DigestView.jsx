import { useState, useRef, useEffect } from 'react';
import './DigestView.css';

export default function DigestView({ digest, mode, onDownload }) {
  const [copied, setCopied] = useState(false);
  const digestRef = useRef(null);

  const handleCopy = () => {
    navigator.clipboard.writeText(digest);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    let filename = 'digest';
    let content = digest;

    if (mode === 'json') {
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
      filename += '.json';
    } else {
      element.setAttribute('href', 'data:text/markdown;charset=utf-8,' + encodeURIComponent(content));
      filename += '.md';
    }

    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  if (!digest) {
    return null;
  }

  return (
    <div className="digest-view">
      <div className="digest-header">
        <h3>Generated Digest</h3>
        <div className="digest-actions">
          <button
            className="btn-copy"
            onClick={handleCopy}
            title="Copy to clipboard"
          >
            {copied ? '✓ Copied' : '📋 Copy'}
          </button>
          <button
            className="btn-download"
            onClick={handleDownload}
            title="Download digest"
          >
            ⬇️ Download
          </button>
        </div>
      </div>

      <div
        ref={digestRef}
        className={`digest-content digest-${mode}`}
      >
        {mode === 'json' ? (
          <pre>{digest}</pre>
        ) : (
          <div className="markdown-content" dangerouslySetInnerHTML={{ __html: digest }} />
        )}
      </div>
    </div>
  );
}
