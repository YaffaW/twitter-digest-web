# Development Guide

## Project Structure

```
twitter-digest-web/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # FastAPI app creation
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── twitter_fetcher.py  # Tweet search & fetching
│   │   │   ├── formatter.py        # Output formatting
│   │   │   └── summarizer.py       # Claude summarization
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── api.py              # API endpoints
│   ├── run.py                    # Entry point
│   ├── requirements.txt
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchForm.jsx
│   │   │   ├── TweetList.jsx
│   │   │   └── DigestView.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .gitignore
├── Dockerfile
├── Dockerfile.frontend
├── docker-compose.yml
├── README.md
├── DEPLOYMENT.md
└── DEVELOPMENT.md
```

## Backend Development

### Adding a New API Endpoint

1. **Create handler in `app/routes/api.py`:**

```python
@router.get("/tweets/{tweet_id}")
async def get_tweet_details(tweet_id: str):
    """Get details about a specific tweet."""
    # Your implementation
    return {"tweet_id": tweet_id}
```

2. **Add request/response models:**

```python
from pydantic import BaseModel

class TweetDetailsRequest(BaseModel):
    include_replies: bool = True
    include_analytics: bool = False
```

### Extending Twitter Fetcher

Add new search strategies in `app/core/twitter_fetcher.py`:

```python
def search_tweets_by_author(username: str, limit: int = 20) -> list[str]:
    """Search tweets from a specific author."""
    full_query = f"from:{username} site:x.com"
    # Implementation...
```

### Adding Output Format

Create new formatter in `app/core/formatter.py`:

```python
def format_tweets_csv(tweets: list[dict]) -> str:
    """Format tweets as CSV."""
    import csv
    from io import StringIO
    # Implementation...
```

## Frontend Development

### Creating New Component

```jsx
// frontend/src/components/NewComponent.jsx
import './NewComponent.css';

export default function NewComponent({ data }) {
  return (
    <div className="new-component">
      {/* JSX here */}
    </div>
  );
}
```

Add styling:
```css
/* frontend/src/components/NewComponent.css */
.new-component {
  /* styles */
}
```

Use in App:
```jsx
import NewComponent from './components/NewComponent';

function App() {
  return <NewComponent data={...} />;
}
```

### API Service Calls

```jsx
import { searchTweets } from './services/api';

const handleSearch = async (params) => {
  try {
    const result = await searchTweets(params);
    setData(result);
  } catch (error) {
    setError(error.message);
  }
};
```

## Testing

### Backend Testing

```bash
pip install pytest pytest-asyncio

# Run tests
pytest backend/tests/

# With coverage
pytest --cov=backend backend/tests/
```

Example test:
```python
# backend/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_search_endpoint():
    response = client.post("/api/search", json={
        "queries": ["test"],
        "mode": "json"
    })
    assert response.status_code == 200
```

### Frontend Testing

```bash
npm install --save-dev vitest @testing-library/react

# Run tests
npm run test
```

## Code Style & Linting

### Backend (Python)

```bash
# Install tools
pip install black flake8 isort

# Format code
black backend/

# Check linting
flake8 backend/

# Sort imports
isort backend/
```

### Frontend (JavaScript)

```bash
# Install ESLint
npm install --save-dev eslint eslint-plugin-react

# Create eslintrc
npx eslint --init

# Lint and fix
npx eslint src/ --fix
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/add-new-search

# Make changes and commit
git add .
git commit -m "Add advanced search filters"

# Push branch
git push origin feature/add-new-search

# Create Pull Request on GitHub
```

## Debugging

### Backend Debugging

```python
# Add print statements
import logging
logger = logging.getLogger("debug")
logger.info(f"Search query: {query}")

# Or use debugger
import pdb; pdb.set_trace()
```

### Frontend Debugging

```jsx
// Chrome DevTools
console.log("Component props:", props);

// React DevTools browser extension
// Inspect component state and props
```

### Docker Debugging

```bash
# View logs
docker-compose logs backend -f

# Enter container
docker-compose exec backend bash
```

## Performance Profiling

### Backend

```python
from time import time

start = time()
# code to profile
elapsed = time() - start
logger.info(f"Search took {elapsed}s")
```

### Frontend

```jsx
console.time("search");
// code to profile
console.timeEnd("search");
```

## Environment Variables

### Backend

```bash
# .env
LOG_LEVEL=DEBUG
MAX_WORKERS=4
CACHE_TTL=300
```

Load in code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

### Frontend

```bash
# .env.local
VITE_API_URL=http://localhost:8000
VITE_DEBUG=true
```

Use in code:
```jsx
const API_URL = import.meta.env.VITE_API_URL;
```

## Documentation

### Backend Docstrings

```python
def search_tweets(query: str, max_results: int = 20) -> list[str]:
    """
    Search for tweets matching the query.
    
    Args:
        query: DuckDuckGo search query syntax
        max_results: Maximum number of tweets to return
        
    Returns:
        List of tweet URLs
        
    Raises:
        ValueError: If query is empty
        RequestException: If search fails
    """
```

### Component Props Documentation

```jsx
/**
 * SearchForm Component
 * @component
 * @param {Object} props
 * @param {Function} props.onSearch - Callback when search is submitted
 * @param {boolean} props.isLoading - Whether search is in progress
 * @returns {ReactElement}
 */
export default function SearchForm({ onSearch, isLoading }) {
```

## Common Development Tasks

### Update Dependencies

Backend:
```bash
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

Frontend:
```bash
npm outdated
npm update
npm audit fix
```

### Clear Cache

```bash
# Backend
find . -type d -name __pycache__ -exec rm -r {} +
find . -name "*.pyc" -delete

# Frontend
rm -rf node_modules dist
npm install
```

### Restart Services

```bash
# Docker
docker-compose restart

# Manual
# Stop backend (Ctrl+C)
# Stop frontend (Ctrl+C)
# Restart both
```

## Useful Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [DuckDuckGo API](https://github.com/deedy/ddg-api)
- [fxtwitter API](https://github.com/FixTweet/FixTweet)

## Getting Help

1. Check existing issues and documentation
2. Search Stack Overflow
3. Ask in project discussions
4. Create detailed bug reports with:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment info (OS, versions)

---

Happy developing! 🚀
