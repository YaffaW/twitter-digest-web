# Twitter Digest Web

A modern web application for zero-auth X/Twitter search and digest generation. Built with React + FastAPI.

## Features

- **🔍 Zero-Auth Search**: Search X/Twitter without API authentication using DuckDuckGo
- **📊 Multiple Output Formats**: JSON, Markdown, and AI-powered Claude summaries
- **🎯 Advanced Filtering**: Filter by minimum likes and set custom search parameters
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **🚀 Easy to Deploy**: Docker support for quick deployment
- **💾 Export Results**: Download digests as JSON or Markdown files

## Architecture

```
twitter-digest-web/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── core/           # Core business logic
│   │   │   ├── twitter_fetcher.py
│   │   │   ├── formatter.py
│   │   │   └── summarizer.py
│   │   ├── routes/         # API endpoints
│   │   │   └── api.py
│   │   └── __init__.py     # FastAPI app
│   ├── requirements.txt
│   └── run.py
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 16+
- npm or yarn

### Local Development

#### Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
```

Backend runs at `http://localhost:8000`
API docs available at `http://localhost:8000/docs`

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### Using Docker Compose

```bash
docker-compose up
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## API Endpoints

### POST `/api/search`

Search for tweets based on queries.

**Request:**
```json
{
  "queries": ["claude code", "mcp"],
  "max_results_per_query": 20,
  "min_likes": 3,
  "fetch_replies": true,
  "max_tweets": 30,
  "mode": "markdown"
}
```

**Response:**
```json
{
  "tweets": [...],
  "count": 25,
  "digest": "# Twitter Digest...",
  "status": "success"
}
```

### GET `/api/health`

Health check endpoint.

## Configuration

### Search Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| queries | array | required | DuckDuckGo search queries |
| max_results_per_query | int | 20 | Max tweets per query |
| min_likes | int | 3 | Minimum engagement threshold |
| max_tweets | int | 30 | Max tweets to return |
| fetch_replies | bool | true | Fetch thread replies |
| mode | string | markdown | Output format: json, markdown, claude |

### Output Modes

- **json**: Raw tweet data as JSON
- **markdown**: Formatted Markdown digest
- **claude**: AI-summarized digest (requires Claude CLI)

## Building for Production

### Build Frontend

```bash
cd frontend
npm run build
```

This creates optimized build in `frontend/dist/`

### Build Docker Image

```bash
docker build -t twitter-digest-web .
docker run -p 8000:8000 twitter-digest-web
```

### Deploy to Server

1. Build frontend: `npm run build` in frontend/
2. Copy `frontend/dist` to `backend/static/dist`
3. Run Docker container or Python backend
4. Frontend will be served from backend at `/`

## Environment Variables

### Backend

Create `.env` file in backend/:
```
FLASK_ENV=production
FLASK_DEBUG=False
```

### Frontend

Set `VITE_API_URL` environment variable:
```bash
export VITE_API_URL=https://api.example.com
npm run build
```

Or configure in `frontend/vite.config.js`

## Usage Examples

### Search for AI News

```
Queries: 
- "artificial intelligence" OR "AI"
- "machine learning" OR "deep learning"

Min Likes: 5
Output: Markdown
```

### Get Tech Updates

```
Queries:
- "programming" OR "coding"
- "web development" OR "frontend"

Min Likes: 2
Output: Claude (AI Summary)
```

## Advanced Features

### Claude AI Summarization

For Claude-powered summaries, ensure Claude CLI is installed:
```bash
npm install -g @anthropic-ai/claude
```

### Rate Limiting

Be respectful of DuckDuckGo and fxtwitter API rate limits. Default is 20 results per query.

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend CORS errors

Update `VITE_API_URL` in frontend config or adjust CORS settings in backend.

### No tweets found

- Verify search queries are valid
- Try with lower `min_likes` threshold
- Check internet connection and DuckDuckGo availability

## Performance Tips

- Use specific search queries for better results
- Increase `min_likes` to filter spam and low-quality posts
- Reduce `max_results_per_query` for faster searches
- Cache frequent queries on the frontend

## Limitations

- No API authentication (uses public search)
- Rate limited by DuckDuckGo and fxtwitter
- Cannot access tweets older than ~24 hours
- No support for protected/private accounts

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built upon [trawlx](https://github.com/timstark/trawlx)
- Uses [fxtwitter API](https://github.com/FixTweet/FixTweet) for tweet data
- Search powered by [DuckDuckGo](https://duckduckgo.com/)
- Frontend built with [React](https://react.dev/) and [Vite](https://vitejs.dev/)
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API documentation at `/api/docs`

## Roadmap

- [ ] User authentication and saved searches
- [ ] Search history
- [ ] Advanced filters (date range, engagement metrics)
- [ ] Multiple output export formats (PDF, CSV)
- [ ] Scheduled digest generation
- [ ] Email delivery
- [ ] Real-time search updates
- [ ] Advanced analytics dashboard

---

Made with ❤️ for Twitter/X enthusiasts
