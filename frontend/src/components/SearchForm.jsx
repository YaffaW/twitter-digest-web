import { useState } from 'react';
import SyntaxHelp from './SyntaxHelp';
import './SearchForm.css';

export default function SearchForm({ onSearch, isLoading }) {
  const [queries, setQueries] = useState(['']);
  const [maxResultsPerQuery, setMaxResultsPerQuery] = useState(20);
  const [minLikes, setMinLikes] = useState(3);
  const [maxTweets, setMaxTweets] = useState(30);
  const [fetchReplies, setFetchReplies] = useState(true);
  const [mode, setMode] = useState('markdown');
  const [showSyntaxHelp, setShowSyntaxHelp] = useState(false);

  const handleQueryChange = (index, value) => {
    const newQueries = [...queries];
    newQueries[index] = value;
    setQueries(newQueries);
  };

  const handleAddQuery = () => {
    setQueries([...queries, '']);
  };

  const handleRemoveQuery = (index) => {
    if (queries.length > 1) {
      setQueries(queries.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const validQueries = queries.filter(q => q.trim());

    if (validQueries.length === 0) {
      alert('Please enter at least one search query');
      return;
    }

    onSearch({
      queries: validQueries,
      max_results_per_query: parseInt(maxResultsPerQuery),
      min_likes: parseInt(minLikes),
      max_tweets: parseInt(maxTweets),
      fetch_replies: fetchReplies,
      mode: mode,
    });
  };

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <div className="form-section">
        <div className="section-header">
          <h3>Search Queries</h3>
          <button
            type="button"
            className="btn-syntax-help"
            onClick={() => setShowSyntaxHelp(true)}
            title="View DuckDuckGo search syntax help"
          >
            ? Syntax Help
          </button>
        </div>
        <p className="help-text">
          DuckDuckGo syntax is supported. Examples: "claude code" OR "cursor ai", ("react" OR "next.js") framework
        </p>

        <div className="queries-list">
          {queries.map((query, index) => (
            <div key={index} className="query-input-group">
              <input
                type="text"
                placeholder={`Query ${index + 1}`}
                value={query}
                onChange={(e) => handleQueryChange(index, e.target.value)}
                disabled={isLoading}
              />
              {queries.length > 1 && (
                <button
                  type="button"
                  className="btn-remove"
                  onClick={() => handleRemoveQuery(index)}
                  disabled={isLoading}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>

        <button
          type="button"
          className="btn-add-query"
          onClick={handleAddQuery}
          disabled={isLoading}
        >
          + Add Another Query
        </button>
      </div>

      <div className="form-section">
        <h3>Settings</h3>

        <div className="form-group">
          <label htmlFor="maxResults">Max Results Per Query:</label>
          <input
            id="maxResults"
            type="number"
            min="1"
            max="100"
            value={maxResultsPerQuery}
            onChange={(e) => setMaxResultsPerQuery(e.target.value)}
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="minLikes">Minimum Likes:</label>
          <input
            id="minLikes"
            type="number"
            min="0"
            max="1000000"
            value={minLikes}
            onChange={(e) => setMinLikes(e.target.value)}
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="maxTweets">Max Tweets to Display:</label>
          <input
            id="maxTweets"
            type="number"
            min="1"
            max="100"
            value={maxTweets}
            onChange={(e) => setMaxTweets(e.target.value)}
            disabled={isLoading}
          />
        </div>

        <div className="form-group checkbox">
          <input
            id="fetchReplies"
            type="checkbox"
            checked={fetchReplies}
            onChange={(e) => setFetchReplies(e.target.checked)}
            disabled={isLoading}
          />
          <label htmlFor="fetchReplies">Fetch thread replies</label>
        </div>

        <div className="form-group">
          <label htmlFor="mode">Output Format:</label>
          <select
            id="mode"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            disabled={isLoading}
          >
            <option value="json">JSON</option>
            <option value="markdown">Markdown</option>
            <option value="claude">AI Summary (Claude)</option>
          </select>
          <p className="help-text">
            {mode === 'claude' && 'Requires Claude CLI to be installed and configured'}
          </p>
        </div>
      </div>

      <button
        type="submit"
        className="btn-search"
        disabled={isLoading}
      >
        {isLoading ? 'Searching...' : 'Search & Generate Digest'}
      </button>

      <SyntaxHelp isOpen={showSyntaxHelp} onClose={() => setShowSyntaxHelp(false)} />
    </form>
  );
}
