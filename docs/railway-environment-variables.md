# Railway Environment Variables Configuration

This document outlines the required environment variables for deploying CampaignForge backend on Railway.

## Database Configuration

```bash
# Primary Database
DATABASE_URL=postgresql://user:password@host:port/database

# Async Database (for SQLAlchemy async operations)
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

## Authentication & Security

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Security
API_SECRET_KEY=your-api-secret-key
CORS_ORIGINS=https://your-frontend-domain.com,http://localhost:3000
```

## AI Service Providers

```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-api-key

# Google AI
GOOGLE_AI_API_KEY=your-google-ai-api-key

# Stability AI (for image generation)
STABILITY_API_KEY=your-stability-ai-api-key

# Together AI
TOGETHER_API_KEY=your-together-ai-api-key
```

## Content Storage

```bash
# File Storage
STORAGE_PROVIDER=s3  # or 'local' for development
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
```

## Application Configuration

```bash
# Application Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Application URLs
FRONTEND_URL=https://your-frontend-domain.com
BACKEND_URL=https://your-backend-domain.up.railway.app

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_VIDEO_GENERATION=false  # Disabled for Railway deployment
ENABLE_IMAGE_GENERATION=true
```

## Intelligence System

```bash
# RAG (Retrieval Augmented Generation)
RAG_VECTOR_STORE_URL=your-vector-store-url
RAG_EMBEDDING_MODEL=text-embedding-ada-002

# Analysis Configuration
DEFAULT_ANALYSIS_MODEL=gpt-4
ANALYSIS_TIMEOUT_SECONDS=300
```

## Missing Variables Analysis

Based on Railway deployment logs, these 23 environment variables were missing and causing 500 errors:

### Critical Missing Variables:
1. `DATABASE_URL` - Primary database connection
2. `ASYNC_DATABASE_URL` - Async database connection
3. `JWT_SECRET_KEY` - JWT token signing
4. `OPENAI_API_KEY` - Primary AI provider
5. `CORS_ORIGINS` - Frontend CORS configuration

### Service-Specific Missing Variables:
6. `ANTHROPIC_API_KEY` - Claude AI service
7. `GOOGLE_AI_API_KEY` - Google AI service
8. `STABILITY_API_KEY` - Image generation
9. `TOGETHER_API_KEY` - Alternative AI provider

### Storage Missing Variables:
10. `AWS_ACCESS_KEY_ID` - File storage access
11. `AWS_SECRET_ACCESS_KEY` - File storage secret
12. `S3_BUCKET_NAME` - Storage bucket
13. `AWS_REGION` - Storage region

### Configuration Missing Variables:
14. `ENVIRONMENT` - Application environment
15. `FRONTEND_URL` - CORS and redirects
16. `BACKEND_URL` - Internal service calls
17. `JWT_ALGORITHM` - Token algorithm
18. `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry
19. `DEBUG` - Debug mode flag
20. `LOG_LEVEL` - Logging configuration
21. `RAG_VECTOR_STORE_URL` - Vector database
22. `DEFAULT_ANALYSIS_MODEL` - AI model selection
23. `ANALYSIS_TIMEOUT_SECONDS` - Request timeout

## Railway Deployment Steps

1. **Add Environment Variables**: Go to Railway project settings and add all variables above
2. **Database Setup**: Ensure PostgreSQL plugin is installed and connected
3. **Service Configuration**: Verify all AI service API keys are valid
4. **Storage Setup**: Configure AWS S3 or alternative storage provider
5. **Deploy**: Trigger new deployment after all variables are configured

## Validation Commands

After deployment, validate configuration:

```bash
# Check database connection
railway run python -c "from src.core.database import engine; print('DB Connected')"

# Verify AI services
railway run python -c "import openai; print('OpenAI OK')"

# Test storage
railway run python -c "from src.storage.services.file_service import FileService; print('Storage OK')"
```

## Environment-Specific Notes

### Production (Railway)
- Use PostgreSQL plugin for `DATABASE_URL`
- Set `DEBUG=false` and `ENVIRONMENT=production`
- Use real AI service API keys
- Configure proper CORS origins for frontend domain

### Development (Local)
- Use local PostgreSQL or Railway database
- Set `DEBUG=true` and `ENVIRONMENT=development`
- Can use test API keys for development
- CORS origins include `http://localhost:3000`

## Security Considerations

1. **API Keys**: Never commit API keys to repository
2. **JWT Secret**: Use a strong, unique secret key
3. **Database URL**: Ensure database credentials are secure
4. **CORS**: Only allow trusted frontend domains
5. **Environment**: Always set `DEBUG=false` in production