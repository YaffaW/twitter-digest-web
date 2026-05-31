# Deployment Guide

## Local Deployment

### Option 1: Direct Python & Node.js

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Option 2: Docker Compose (Recommended)

```bash
docker-compose up
```

Access at:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Production Deployment

### Option 1: Docker Container

Build:
```bash
docker build -t twitter-digest-web .
```

Run:
```bash
docker run -d \
  -p 8000:8000 \
  --name twitter-digest \
  twitter-digest-web
```

### Option 2: Traditional Server (Ubuntu/Debian)

#### Install Dependencies
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nodejs npm
```

#### Setup Backend
```bash
git clone <repo>
cd twitter-digest-web/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/twitter-digest.service
```

Add:
```ini
[Unit]
Description=Twitter Digest Backend
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/venv/bin"
ExecStart=/path/to/backend/venv/bin/python run.py

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable twitter-digest
sudo systemctl start twitter-digest
```

#### Setup Frontend
```bash
cd ../frontend
npm install
npm run build

# Copy build to backend
cp -r dist ../backend/static/dist
```

### Option 3: Cloud Deployment (Heroku, Railway, etc.)

#### Heroku

```bash
# Create Procfile
echo "web: cd backend && python run.py" > Procfile

# Deploy
heroku create twitter-digest-web
git push heroku main
```

#### Railway.app

1. Connect GitHub repo
2. Set working directory to `backend/`
3. Deploy

## Nginx Reverse Proxy Configuration

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name example.com;

    location / {
        root /var/www/twitter-digest-web/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        # ... proxy settings same as above
    }
}
```

## SSL/TLS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d api.example.com
```

## Monitoring

### Check Backend Status
```bash
curl http://localhost:8000/api/health
```

### View Logs
```bash
# Docker
docker logs -f twitter-digest

# Systemd
journalctl -u twitter-digest -f
```

## Scaling

### Load Balancing with Multiple Backend Instances

Use Docker Compose:
```yaml
backend:
  image: twitter-digest-web
  deploy:
    replicas: 3
  ports:
    - "8000-8002:8000"
```

Then use Nginx to load balance between instances.

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### CORS Issues
Update backend CORS settings in `app/__init__.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Memory Issues
Limit Docker container:
```bash
docker run -m 512m twitter-digest-web
```

## Backup & Maintenance

### Regular Backups
```bash
# Backup code
tar -czf backup-$(date +%Y%m%d).tar.gz /path/to/twitter-digest-web

# Upload to cloud storage
aws s3 cp backup-*.tar.gz s3://my-bucket/backups/
```

## Performance Optimization

1. **Enable Caching**
   - Add Redis for search result caching
   - Set appropriate TTLs based on search queries

2. **Database Optimization** (future)
   - Index frequently searched queries
   - Archive old results

3. **Frontend Optimization**
   - Already using Vite for bundling
   - Enable gzip compression in Nginx
   - Use CDN for static assets

4. **Backend Optimization**
   - Implement request rate limiting
   - Add database connection pooling
   - Use async operations for long-running searches

---

For more information, see README.md
