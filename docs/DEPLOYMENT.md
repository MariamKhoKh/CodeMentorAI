# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Git
- Azure OpenAI API access
- PostgreSQL client (optional, for direct database access)

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/your-team/codementor-ai.git
cd codementor-ai
```

### Step 2: Configure Environment Variables

```bash
# Backend
cd backend
cp .env.example .env
```

Edit `.env` with your actual values:
```bash
AZURE_OPENAI_API_KEY=your_actual_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-5-chat
SECRET_KEY=your_secure_random_string_here
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Start Backend Services

```bash
# From backend directory
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432 (mapped to 5433 externally)
- Redis on port 6379
- FastAPI backend on port 8000 (mapped to 8001 externally)

### Step 4: Verify Services

```bash
# Check container status
docker-compose ps

# Expected output:
# codementor_postgres    running (healthy)
# codementor_redis       running (healthy)
# codementor_backend     running
```

### Step 5: Run Database Migrations

```bash
docker exec -it codementor_backend alembic upgrade head
```

### Step 6: Seed Problems

```bash
docker exec -it codementor_backend python -m scripts.seed_problems
```

Expected output:
```
Successfully seeded 5 problems!
- Two Sum (easy)
- Valid Parentheses (easy)
- Merge Two Sorted Lists (easy)
- Best Time to Buy and Sell Stock (easy)
- Maximum Subarray (medium)
```

### Step 7: Setup Frontend

```bash
cd ../frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Step 8: Verify Application

Visit:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8001`
- API Docs: `http://localhost:8001/docs`

Test the health endpoint:
```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development"
}
```

## Production Deployment

### Backend Deployment (Railway/Heroku/AWS)

#### Option 1: Railway

1. **Create Railway Project**
```bash
npm i -g @railway/cli
railway login
railway init
```

2. **Configure Environment Variables**

In Railway dashboard, add:
```
DATABASE_URL=[automatically provided]
REDIS_URL=[automatically provided]
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-5-chat
SECRET_KEY=your_secret
ENVIRONMENT=production
```

3. **Deploy**
```bash
railway up
```

4. **Run Migrations**
```bash
railway run alembic upgrade head
railway run python -m scripts.seed_problems
```

#### Option 2: Docker-based Hosting

Build and push Docker image:
```bash
cd backend
docker build -t codementor-backend:latest .
docker tag codementor-backend:latest your-registry/codementor-backend:latest
docker push your-registry/codementor-backend:latest
```

Deploy to your hosting provider following their Docker deployment instructions.

### Frontend Deployment (Vercel/Netlify)

#### Option 1: Vercel

1. **Connect Repository**
- Go to vercel.com
- Import your GitHub repository
- Select `frontend` as root directory

2. **Configure Environment Variables**
```
VITE_API_URL=https://your-backend.railway.app
```

3. **Deploy**
- Vercel auto-deploys on push to main branch
- Manual deploy: `vercel --prod`

#### Option 2: Netlify

1. **Build Command**: `npm run build`
2. **Publish Directory**: `dist`
3. **Environment Variables**:
```
VITE_API_URL=https://your-backend-url.com
```

### Database Migration

For production database:
```bash
# Connect to production environment
export DATABASE_URL=your_production_db_url

# Run migrations
alembic upgrade head

# Seed problems
python -m scripts.seed_problems
```

## Configuration Management

### Environment-Specific Settings

#### Development (.env.development)
```bash
DATABASE_URL=postgresql+asyncpg://codementor:codementor_pass@localhost:5433/codementor_db
ENVIRONMENT=development
```

#### Production (.env.production)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
ENVIRONMENT=production
CODE_EXECUTION_TIMEOUT=5
```

## Monitoring and Maintenance

### Health Checks

```bash
# Backend health
curl https://your-backend.com/health

# Database connection
docker exec -it codementor_postgres pg_isready -U codementor
```

### Logs

```bash
# Backend logs
docker logs codementor_backend -f

# PostgreSQL logs
docker logs codementor_postgres -f

# Redis logs
docker logs codementor_redis -f
```

### Database Backup

```bash
# Backup
docker exec codementor_postgres pg_dump -U codementor codementor_db > backup.sql

# Restore
docker exec -i codementor_postgres psql -U codementor codementor_db < backup.sql
```

## Troubleshooting

### Issue: Backend won't start

**Check logs**:
```bash
docker logs codementor_backend
```

**Common causes**:
- Missing environment variables
- Database connection failure
- Port already in use

**Solution**:
```bash
# Verify .env file exists
ls backend/.env

# Check database is running
docker ps | grep postgres

# Try restarting
docker-compose restart backend
```

### Issue: Database connection error

**Verify database**:
```bash
docker exec -it codementor_postgres psql -U codementor -d codementor_db
```

**Check connection string**:
- Ensure host is `postgres` inside Docker network
- Verify credentials match docker-compose.yml

### Issue: AI feedback not generating

**Check Azure OpenAI**:
```bash
# Verify API key is set
docker exec codementor_backend env | grep AZURE_OPENAI
```

**Test manually**:
```bash
curl https://your-endpoint.cognitiveservices.azure.com/openai/deployments/gpt-5-chat/chat/completions \
  -H "api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

### Issue: Frontend can't connect to backend

**Check CORS**:
- Verify backend allows frontend origin
- Check `app/main.py` CORS settings

**Verify API URL**:
- Check `.env` has correct backend URL
- Test backend health endpoint directly

### Issue: Code execution timeout

**Adjust timeout**:
```bash
# In .env
CODE_EXECUTION_TIMEOUT=15
```

**Check system resources**:
```bash
docker stats codementor_backend
```

## Performance Optimization

### Database

**Connection pooling** (already configured):
```python
pool_size=10
max_overflow=20
```

**Indexes** (already created):
```sql
CREATE INDEX idx_submissions_user ON submissions(user_id);
CREATE INDEX idx_submissions_problem ON submissions(problem_id);
```

### Caching

**Redis caching** for:
- Session data (30 min TTL)
- API responses (5 min TTL)
- User authentication tokens

### Code Execution

**Optimization**:
- Reuse Python interpreter where possible
- Cache common imports
- Limit max code size

## Security Checklist

- [ ] Environment variables not committed to git
- [ ] SECRET_KEY is random and secure (32+ characters)
- [ ] Database credentials are unique per environment
- [ ] API keys rotated every 90 days
- [ ] HTTPS enabled in production
- [ ] CORS configured for specific origins only
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention via ORM
- [ ] Code execution timeouts enforced

## Rollback Procedure

If deployment fails:

1. **Identify issue**
```bash
docker logs codementor_backend
```

2. **Rollback database**
```bash
alembic downgrade -1
```

3. **Redeploy previous version**
```bash
git checkout previous-stable-tag
docker-compose down
docker-compose up -d
```

4. **Verify health**
```bash
curl http://localhost:8001/health
```