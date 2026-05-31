import { useState, useEffect } from 'react';
import SearchForm from './components/SearchForm';
import TweetList from './components/TweetList';
import DigestView from './components/DigestView';
import { searchTweets } from './services/api';
import './App.css';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (searchParams) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await searchTweets(searchParams);
      setResult({
        tweets: data.tweets,
        count: data.count,
        digest: data.digest,
        mode: searchParams.mode,
      });
    } catch (err) {
      setError(err.detail || err.message || 'An error occurred while searching. Make sure the backend is running.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🐦 Twitter Digest Generator</h1>
          <p>Zero-auth X/Twitter search and digest generation</p>
        </div>
      </header>

      <main className="app-main">
        <SearchForm onSearch={handleSearch} isLoading={loading} />

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {loading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <p>Searching tweets...</p>
          </div>
        )}

        {result && (
          <>
            {result.mode !== 'json' && result.tweets && result.tweets.length > 0 && (
              <TweetList tweets={result.tweets} />
            )}
            {result.digest && (
              <DigestView
                digest={result.digest}
                mode={result.mode}
              />
            )}
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>Twitter Digest Generator v1.0 | Powered by DuckDuckGo and fxtwitter API</p>
      </footer>
    </div>
  );
}

export default App;
