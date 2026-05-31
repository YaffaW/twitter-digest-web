import './TweetList.css';

export default function TweetList({ tweets }) {
  if (!tweets || tweets.length === 0) {
    return (
      <div className="tweet-list empty">
        <p>No tweets found. Try a different search.</p>
      </div>
    );
  }

  return (
    <div className="tweet-list">
      <h3>Found {tweets.length} tweets</h3>
      <div className="tweets-container">
        {tweets.map((tweet, index) => (
          <div key={tweet.id} className="tweet-card">
            <div className="tweet-header">
              <div className="tweet-author">
                <strong>@{tweet.author}</strong>
                <span className="author-name">{tweet.author_name}</span>
              </div>
              <div className="tweet-engagement">
                <span className="stat likes">❤️ {tweet.likes.toLocaleString()}</span>
                <span className="stat retweets">🔄 {tweet.retweets.toLocaleString()}</span>
                <span className="stat replies">💬 {tweet.replies.toLocaleString()}</span>
              </div>
            </div>

            <div className="tweet-text">
              {tweet.text}
            </div>

            <div className="tweet-meta">
              <span className="date">{tweet.created_at}</span>
              <a href={tweet.url} target="_blank" rel="noopener noreferrer" className="tweet-link">
                View on Twitter →
              </a>
            </div>

            {tweet.reply_texts && tweet.reply_texts.length > 0 && (
              <div className="tweet-replies">
                <details>
                  <summary>Thread replies ({tweet.reply_texts.length})</summary>
                  <div className="replies-list">
                    {tweet.reply_texts.slice(0, 5).map((reply, replyIndex) => (
                      <div key={replyIndex} className="reply-item">
                        <strong>@{reply.author}:</strong> {reply.text}
                      </div>
                    ))}
                  </div>
                </details>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
