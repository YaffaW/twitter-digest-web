# Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.10+
- Node.js 16+
- npm

### Step 1: Clone Repository
```bash
cd twitter-digest-web
```

### Step 2: Backend Setup (30 seconds)
```bash
cd backend
pip install -r requirements.txt
python run.py
```

**Backend is ready at**: http://localhost:8000

### Step 3: Frontend Setup (in another terminal)
```bash
cd frontend
npm install
npm run dev
```

**Frontend is ready at**: http://localhost:5173

### Step 4: Open in Browser
Go to http://localhost:5173 and start searching!

---

## Using Docker (Even Faster)

```bash
docker-compose up
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## First Search

1. Enter a search query (e.g., "claude code", "AI")
2. Adjust settings if needed:
   - Min likes: 3
   - Max tweets: 30
3. Click "Search & Generate Digest"
4. View results and download!

---

## Common Issues

### Backend won't start
```bash
# Make sure Python 3.10+
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend shows "Cannot connect to API"
- Ensure backend is running at localhost:8000
- Check browser console for CORS errors
- Try accessing http://localhost:8000/api/health in browser

### Port already in use
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or use different port
python run.py --port 8001
```

---

## Next Steps

1. **Explore the interface**: Try different search queries
2. **Read API docs**: http://localhost:8000/docs
3. **Check deployment**: See DEPLOYMENT.md
4. **Contribute**: See DEVELOPMENT.md

---

**Need help?** Check README.md or DEVELOPMENT.md
