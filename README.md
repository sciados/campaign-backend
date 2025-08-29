# CampaignForge AI - Backend

Multimedia Campaign Creation Platform - FastAPI Backend

## Quick Start

1. **Create virtual environment:**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment:**

```bash
copy .env.template .env
# Edit .env with your configuration
```

4. **Run with Docker (Recommended):**

```bash
docker-compose up -d
```

5. **Or run locally:**

```bash
# Start PostgreSQL and Redis first
uvicorn src.main:app --reload
```

6. **Access API documentation:**

```
# http://localhost:8000/docs  # Swagger UI
# http://localhost:8000/redoc # ReDoc
```

## Project Structure

```
src/
├── api/v1/              # API endpoints
│   ├── campaigns/       # Campaign management
│   ├── content/         # Content processing
│   ├── users/           # User management
│   ├── analytics/       # Analytics and reporting
│   └── billing/         # Subscription and billing
├── core/                # Core configuration
├── services/            # Business logic services
│   ├── ai_services/     # AI integrations
│   └── platform_services/ # Video platform integrations
├── models/              # Database models
├── utils/               # Utility functions
└── tasks/               # Background tasks
```

## Tech Stack

- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with AsyncPG
- **Cache**: Redis
- **Queue**: Celery
- **AI Services**: OpenAI, Anthropic, Stability AI
- **Video Processing**: yt-dlp, FFmpeg
- **Storage**: Cloudflare R2 (S3-compatible)
- **Monitoring**: Sentry, Structured Logging

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn src.main:app --reload

# Run with Docker
docker-compose up --build

# Database migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Code formatting
black src/
isort src/

# Type checking
mypy src/

# Run tests
pytest tests/
```

## Environment Variables

Copy `.env.template` to `.env` and configure:

- **DATABASE_URL**: PostgreSQL connection string
- **SECRET_KEY**: JWT secret key
- **OPENAI_API_KEY**: OpenAI API key
- **ANTHROPIC_API_KEY**: Anthropic API key
- **CLOUDFLARE_R2_***: R2 storage configuration
- **REDIS_URL**: Redis connection string

## Deployment

### Railway (Recommended)

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

### Docker

```bash
docker build -t campaignforge-backend .
docker run -p 8000:8000 campaignforge-backend
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token

### Campaigns

- `GET /api/v1/campaigns/` - List campaigns
- `POST /api/v1/campaigns/` - Create campaign
- `GET /api/v1/campaigns/{id}` - Get campaign
- `PUT /api/v1/campaigns/{id}` - Update campaign

### Content Processing

- `POST /api/v1/content/process-video` - Process video URL
- `POST /api/v1/content/upload-file` - Upload document
- `POST /api/v1/content/generate` - Generate content

### AI Generation

- `POST /api/v1/content/generate-text` - Generate text content
- `POST /api/v1/content/generate-image` - Generate images
- `POST /api/v1/content/generate-video` - Generate videos

## License

Private - CampaignForge AI Platform
