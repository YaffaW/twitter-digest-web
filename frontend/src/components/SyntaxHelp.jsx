import './SyntaxHelp.css';

export default function SyntaxHelp({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>DuckDuckGo Search Syntax</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <section className="syntax-section">
            <h3>Basic Operators</h3>
            <div className="syntax-examples">
              <div className="example">
                <code>"exact phrase"</code>
                <p>Search for exact phrase - results must contain all words in order</p>
              </div>
              <div className="example">
                <code>word1 word2</code>
                <p>Both words must appear but not necessarily in order</p>
              </div>
              <div className="example">
                <code>-word</code>
                <p>Exclude results containing this word</p>
              </div>
            </div>
          </section>

          <section className="syntax-section">
            <h3>Boolean Operators</h3>
            <div className="syntax-examples">
              <div className="example">
                <code>word1 OR word2</code>
                <p>Results must contain word1 OR word2 (or both)</p>
              </div>
              <div className="example">
                <code>(word1 OR word2) AND word3</code>
                <p>Complex queries with grouping</p>
              </div>
              <div className="example">
                <code>word1 word2 word3</code>
                <p>AND is implicit - all words must appear</p>
              </div>
            </div>
          </section>

          <section className="syntax-section">
            <h3>Special Operators</h3>
            <div className="syntax-examples">
              <div className="example">
                <code>site:example.com</code>
                <p>Search within specific website</p>
              </div>
              <div className="example">
                <code>filetype:pdf</code>
                <p>Search for specific file types</p>
              </div>
              <div className="example">
                <code>inurl:keyword</code>
                <p>Search for keyword in URL</p>
              </div>
            </div>
          </section>

          <section className="syntax-section">
            <h3>Examples for Twitter Search</h3>
            <div className="syntax-examples">
              <div className="example">
                <code>"claude code" OR "cursor ai"</code>
                <p>Find tweets about Claude or Cursor AI</p>
              </div>
              <div className="example">
                <code>("react" OR "next.js") framework</code>
                <p>React or Next.js framework discussions</p>
              </div>
              <div className="example">
                <code>"machine learning" -spam</code>
                <p>Machine learning without spam results</p>
              </div>
              <div className="example">
                <code>python AND ("web development" OR "backend")</code>
                <p>Python web development or backend content</p>
              </div>
              <div className="example">
                <code>javascript -deprecated</code>
                <p>Modern JavaScript content (exclude deprecated)</p>
              </div>
            </div>
          </section>

          <section className="syntax-section">
            <h3>Tips</h3>
            <ul className="tips-list">
              <li>Use quotes for exact phrases: <code>"web development"</code></li>
              <li>Combine operators: <code>(A OR B) AND C -D</code></li>
              <li>Case-insensitive: queries work the same in any case</li>
              <li>Spaces between operators and keywords matter</li>
              <li>Use multiple queries for different search strategies</li>
              <li>Filter results by adjusting "Minimum Likes" setting</li>
            </ul>
          </section>
        </div>

        <div className="modal-footer">
          <button className="btn-close" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
