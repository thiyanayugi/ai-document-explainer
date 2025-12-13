# 🚀 Deployment Guide - AI Document Explainer

This guide covers deploying your application to production using various platforms.

## 📋 Pre-Deployment Checklist

- [x] Docker image builds successfully
- [x] All features tested locally
- [x] Environment variables documented
- [x] Rate limiting implemented
- [x] R2 storage configured (optional)
- [ ] Choose deployment platform
- [ ] Set up domain name (optional)
- [ ] Configure SSL certificate

---

## 🎯 Recommended: Google Cloud Run (Easiest + Free Tier)

**Why Cloud Run?**

- ✅ Free tier: 2 million requests/month
- ✅ Auto-scaling (0 to N instances)
- ✅ Pay only for actual usage
- ✅ Managed SSL certificates
- ✅ No server management

### Step 1: Install Google Cloud CLI

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize and login
gcloud init
gcloud auth login
```

### Step 2: Set Up Project

```bash
# Create a new project (or use existing)
gcloud projects create ai-doc-explainer --name="AI Document Explainer"

# Set project
gcloud config set project ai-doc-explainer

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 3: Build and Push Docker Image

```bash
# Navigate to project directory
cd /home/yugi/ai_document_reader

# Build for Cloud Run
docker build -t gcr.io/ai-doc-explainer/ai-doc-explainer:latest .

# Configure Docker for GCR
gcloud auth configure-docker

# Push image
docker push gcr.io/ai-doc-explainer/ai-doc-explainer:latest
```

### Step 4: Deploy to Cloud Run

```bash
gcloud run deploy ai-doc-explainer \
  --image gcr.io/ai-doc-explainer/ai-doc-explainer:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="your_openai_key_here" \
  --set-env-vars ENABLE_OBJECT_STORAGE=true \
  --set-env-vars R2_ACCOUNT_ID="your_r2_account_id" \
  --set-env-vars R2_ACCESS_KEY_ID="your_r2_access_key" \
  --set-env-vars R2_SECRET_ACCESS_KEY="your_r2_secret_key" \
  --set-env-vars R2_BUCKET_NAME="ai-documents" \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 300
```

### Step 5: Get Your URL

```bash
# Your app will be available at:
# https://ai-doc-explainer-xxxxx-uc.a.run.app
```

### Optional: Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service ai-doc-explainer \
  --domain docs.yourdomain.com \
  --region us-central1
```

---

## 🐳 Alternative: Docker Compose (VPS/Self-Hosted)

For deployment on your own server (DigitalOcean, AWS EC2, etc.)

### Step 1: Create `docker-compose.yml`

```yaml
version: "3.8"

services:
  ai-doc-explainer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENABLE_OBJECT_STORAGE=${ENABLE_OBJECT_STORAGE:-false}
      - R2_ACCOUNT_ID=${R2_ACCOUNT_ID}
      - R2_ACCESS_KEY_ID=${R2_ACCESS_KEY_ID}
      - R2_SECRET_ACCESS_KEY=${R2_SECRET_ACCESS_KEY}
      - R2_BUCKET_NAME=${R2_BUCKET_NAME:-ai-documents}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Step 2: Deploy on VPS

```bash
# SSH into your server
ssh user@your-server-ip

# Clone repository
git clone <your-repo-url>
cd ai_document_reader

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_key_here
ENABLE_OBJECT_STORAGE=true
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=ai-documents
EOF

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 3: Set Up Nginx Reverse Proxy (Optional)

```nginx
# /etc/nginx/sites-available/ai-doc-explainer
server {
    listen 80;
    server_name docs.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ai-doc-explainer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d docs.yourdomain.com
```

---

## ☁️ Alternative: Heroku

### Step 1: Install Heroku CLI

```bash
curl https://cli-assets.heroku.com/install.sh | sh
heroku login
```

### Step 2: Create Heroku App

```bash
cd /home/yugi/ai_document_reader

# Create app
heroku create ai-doc-explainer

# Set environment variables
heroku config:set OPENAI_API_KEY="your_key"
heroku config:set ENABLE_OBJECT_STORAGE=true
heroku config:set R2_ACCOUNT_ID="your_account_id"
heroku config:set R2_ACCESS_KEY_ID="your_access_key"
heroku config:set R2_SECRET_ACCESS_KEY="your_secret_key"
heroku config:set R2_BUCKET_NAME="ai-documents"
```

### Step 3: Create `heroku.yml`

```yaml
build:
  docker:
    web: Dockerfile
run:
  web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Step 4: Deploy

```bash
# Set stack to container
heroku stack:set container

# Deploy
git push heroku master

# Open app
heroku open
```

---

## 🔒 Production Security Checklist

### Environment Variables

- [ ] Never commit `.env` to git
- [ ] Use secrets management (Cloud Run Secret Manager, etc.)
- [ ] Rotate API keys regularly

### Rate Limiting

- [x] IP-based rate limiting enabled
- [ ] Consider adding Cloudflare for DDoS protection
- [ ] Monitor usage patterns

### Database

- [ ] Use PostgreSQL for production (not SQLite)
- [ ] Set up automated backups
- [ ] Enable SSL connections

### Monitoring

- [ ] Set up error tracking (Sentry, etc.)
- [ ] Monitor API costs (OpenAI dashboard)
- [ ] Set up uptime monitoring (UptimeRobot, etc.)

---

## 💰 Cost Estimates

### Google Cloud Run (Recommended)

- **Free tier**: 2M requests/month
- **After free tier**: ~$0.40 per million requests
- **Estimated**: $5-20/month for moderate usage

### OpenAI API

- **GPT-4o-mini**: ~$0.01-0.05 per document
- **Estimated**: $10-50/month depending on usage

### Cloudflare R2

- **Free tier**: 10GB storage, 1M writes/month
- **No egress fees**
- **Estimated**: Free for most use cases

### Total Estimated Cost

- **Light usage** (100 docs/month): $10-20/month
- **Medium usage** (1000 docs/month): $30-80/month
- **Heavy usage** (10000 docs/month): $200-500/month

---

## 🎯 Quick Deploy Commands

### Google Cloud Run (One Command)

```bash
gcloud run deploy ai-doc-explainer \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="$OPENAI_API_KEY"
```

### Railway (Easiest)

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variables
5. Deploy! ✅

---

## 🔧 Troubleshooting

### Issue: Container crashes on startup

```bash
# Check logs
gcloud run services logs read ai-doc-explainer --limit 50

# Or for Docker
docker logs ai-doc-explainer-test
```

### Issue: Out of memory

```bash
# Increase memory allocation
gcloud run services update ai-doc-explainer --memory 2Gi
```

### Issue: Slow cold starts

```bash
# Set minimum instances
gcloud run services update ai-doc-explainer --min-instances 1
```

---

## 📊 Post-Deployment

### Monitor Your App

- OpenAI API usage: https://platform.openai.com/usage
- Cloud Run metrics: GCP Console → Cloud Run
- R2 storage: Cloudflare Dashboard → R2

### Update Your App

```bash
# Build new image
docker build -t gcr.io/ai-doc-explainer/ai-doc-explainer:latest .

# Push
docker push gcr.io/ai-doc-explainer/ai-doc-explainer:latest

# Deploy update
gcloud run deploy ai-doc-explainer \
  --image gcr.io/ai-doc-explainer/ai-doc-explainer:latest
```

---

## 🎉 You're Live!

Your AI Document Explainer is now deployed and accessible to the world!

**Next Steps:**

1. Share your URL with users
2. Monitor usage and costs
3. Gather feedback
4. Iterate and improve

**Need help?** Check the logs or open an issue on GitHub.
