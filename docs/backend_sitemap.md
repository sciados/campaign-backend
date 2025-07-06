# CampaignForge Backend Sitemap

## 📁 Project Structure

```plaintext
campaignforge-backend/
└── src/
    ├── __init__.py
    ├── main.py
    │
    ├── 🔐 admin/
    │   ├── routes.py
    │   └── schemas.py
    │
    ├── 📊 analytics/
    │   └── routes.py
    │
    ├── 🔑 auth/
    │   ├── __init__.py
    │   ├── dependencies.py
    │   └── routes.py
    │
    ├── 🎯 campaigns/
    │   └── routes.py
    │
    ├── ⚙️ core/
    │   ├── config.py
    │   ├── credits.py
    │   ├── database.py
    │   └── security.py
    │
    ├── 📈 dashboard/
    │   ├── __init__.py
    │   └── routes.py
    │
    ├── 🧠 intelligence/
    │   ├── __init__.py
    │   ├── analyzers.py
    │   ├── routes.py
    │   │
    │   ├── 🚀 amplifier/
    │   │   ├── __init__.py
    │   │   ├── ai_providers.py
    │   │   ├── core.py
    │   │   ├── enhancement.py
    │   │   ├── fallbacks.py
    │   │   ├── service.py
    │   │   ├── sources.py
    │   │   ├── utils.py
    │   │   │
    │   │   └── 🔬 enhancements/
    │   │       ├── __init__.py
    │   │       ├── authority_enhancer.py
    │   │       ├── content_enhancer.py
    │   │       ├── credibility_enhancer.py
    │   │       ├── emotional_enhancer.py
    │   │       ├── market_enhancer.py
    │   │       └── scientific_enhancer.py
    │   │
    │   ├── 🤖 automation/
    │   │   └── niche_monitor.py
    │   │
    │   ├── 💾 cache/
    │   │   ├── affiliate_optimized_cache.py
    │   │   ├── global_cache.py
    │   │   └── shared_intelligence.py
    │   │
    │   ├── 🔍 extractors/
    │   │   ├── __init__.py
    │   │   └── product_extractor.py
    │   │
    │   ├── 🎨 generators/
    │   │   ├── __init__.py
    │   │   ├── ad_copy_generator.py
    │   │   ├── base_generator.py
    │   │   ├── blog_post_generator.py
    │   │   ├── email_generator.py
    │   │   ├── factory.py
    │   │   ├── image_generator.py
    │   │   ├── social_media_generator.py
    │   │   ├── video_script_generator.py
    │   │   │
    │   │   └── 🌐 landing_page/
    │   │       ├── __init__.py
    │   │       ├── routes.py
    │   │       │
    │   │       ├── 📊 analytics/
    │   │       │   ├── __init__.py
    │   │       │   ├── events.py
    │   │       │   ├── performance.py
    │   │       │   └── tracking.py
    │   │       │
    │   │       ├── 🧩 components/
    │   │       │   ├── __init__.py
    │   │       │   ├── modals.py
    │   │       │   ├── pages.py
    │   │       │   └── sections.py
    │   │       │
    │   │       ├── ⚙️ core/
    │   │       │   ├── config.py
    │   │       │   ├── generator.py
    │   │       │   └── types.py
    │   │       │
    │   │       ├── 🗄️ database/
    │   │       │   ├── __init__.py
    │   │       │   ├── models.py
    │   │       │   ├── queries.py
    │   │       │   └── storage.py
    │   │       │
    │   │       ├── 🧠 intelligence/
    │   │       │   ├── __init__.py
    │   │       │   ├── analyzer.py
    │   │       │   ├── extractor.py
    │   │       │   └── optimizer.py
    │   │       │
    │   │       ├── 📄 templates/
    │   │       │   ├── __init__.py
    │   │       │   ├── builder.py
    │   │       │   ├── defaults.py
    │   │       │   └── manager.py
    │   │       │
    │   │       ├── 🛠️ utils/
    │   │       │   ├── __init__.py
    │   │       │   ├── css.py
    │   │       │   ├── html.py
    │   │       │   └── validation.py
    │   │       │
    │   │       └── 🔄 variants/
    │   │           ├── __init__.py
    │   │           ├── generator.py
    │   │           └── hypothesis.py
    │   │
    │   ├── 🎯 handlers/
    │   │   ├── __init__.py
    │   │   ├── analysis_handler.py
    │   │   ├── content_handler.py
    │   │   └── intelligence_handler.py
    │   │
    │   ├── 🎯 niches/
    │   │   └── niche_targeting.py
    │   │
    │   ├── 🔄 proactive/
    │   │   ├── sales_page_monitor.py
    │   │   └── scheduler.py
    │   │
    │   ├── 🛣️ routers/
    │   │   ├── __init__.py
    │   │   ├── analysis_routes.py
    │   │   ├── content_routes.py
    │   │   ├── debug_routes.py
    │   │   ├── management_routes.py
    │   │   ├── proactive_analysis.py
    │   │   └── routes.py
    │   │
    │   ├── 📋 schemas/
    │   │   ├── __init__.py
    │   │   ├── requests.py
    │   │   └── responses.py
    │   │
    │   └── 🔧 utils/
    │       ├── __init__.py
    │       ├── ai_intelligence_saver.py
    │       ├── analyzer_factory.py
    │       ├── campaign_helpers.py
    │       ├── cost_optimized_ai_provider.py
    │       ├── intelligence_validation.py
    │       └── tiered_ai_provider.py
    │
    ├── 🗃️ models/
    │   ├── __init__.py
    │   ├── campaign.py
    │   ├── campaign_assets.py
    │   ├── company.py
    │   ├── intelligence.py
    │   └── user.py
    │
    └── 🔌 services/
        ├── ai_services/
        │   └── openai_service_copy.py
        └── platform_services/
            └── video_service.py
```

## 📋 Module Overview

### 🏗️ **Core Infrastructure**

- **`main.py`** - Application entry point and FastAPI configuration
- **`core/`** - Configuration, database connections, security, credits system
- **`auth/`** - JWT authentication, dependencies, user authorization
- **`models/`** - SQLAlchemy database models and Pydantic schemas

### 🧠 **Intelligence System** (Primary Feature)

- **`intelligence/analyzers.py`** - Core AI analysis engine with ultra-cheap providers (99%+ cost savings)
- **`amplifier/`** - AI enhancement system with tiered provider management
- **`enhancements/`** - 6 specialized AI modules:
  - `scientific_enhancer.py` - Research backing and clinical validation
  - `credibility_enhancer.py` - Trust signals and authority building
  - `market_enhancer.py` - Competitive positioning and market analysis
  - `content_enhancer.py` - Content optimization and messaging
  - `emotional_enhancer.py` - Psychological triggers and customer journey
  - `authority_enhancer.py` - Expertise demonstration and thought leadership
- **`extractors/`** - Product name extraction and content parsing
- **`cache/`** - Intelligence caching, shared data, affiliate optimization

### 🎨 **Content Generation**

- **`generators/`** - Multi-format content creation system:
  - `ad_copy_generator.py` - Facebook/Google ads creation
  - `email_generator.py` - Email sequence generation
  - `blog_post_generator.py` - SEO-optimized blog content
  - `social_media_generator.py` - Platform-specific social content
  - `video_script_generator.py` - VSL and promotional video scripts
  - `image_generator.py` - AI image generation integration
- **`landing_page/`** - Complete landing page generation system:
  - Full analytics and performance tracking
  - A/B testing variants and hypothesis generation
  - Component-based page building
  - Intelligence-driven optimization

### 🎯 **Campaign Management**

- **`campaigns/`** - Campaign CRUD operations and management
- **`niches/`** - Automated niche targeting and analysis
- **`handlers/`** - Request processing for analysis, content, and intelligence

### 🔄 **Automation & Monitoring**

- **`automation/`** - Automated niche monitoring and opportunity detection
- **`proactive/`** - Sales page monitoring, change detection, scheduling
- **`analytics/`** - Performance tracking, conversion analytics, ROI measurement

### 🛠️ **Utilities & Infrastructure**

- **`utils/`** - Core utilities:
  - `tiered_ai_provider.py` - Ultra-cheap AI provider management
  - `cost_optimized_ai_provider.py` - Cost optimization algorithms
  - `ai_intelligence_saver.py` - Database persistence for AI data
  - `intelligence_validation.py` - Data quality and validation
- **`routers/`** - FastAPI routing and API endpoints
- **`schemas/`** - Pydantic request/response validation
- **`services/`** - External service integrations (OpenAI, video platforms)

## 🚀 **Key Features & Capabilities**

### 💰 **Ultra-Cheap AI System**

- **99%+ cost savings** vs OpenAI using Groq ($0.0002), Together AI ($0.0008), Deepseek ($0.00014)
- **Automatic fallback** between providers for reliability
- **Real-time cost tracking** and optimization
- **Quality scoring** for provider selection

### 🧠 **Comprehensive Intelligence Analysis**

- **6 specialized AI enhancement modules** for complete competitive analysis
- **Scientific backing generation** for health/supplement claims
- **Market positioning** and competitive advantage identification
- **Credibility building** through trust signals and social proof
- **Emotional journey mapping** and psychological trigger analysis

### 🎨 **Multi-Format Content Generation**

- **Landing pages** with analytics and A/B testing
- **Ad copy** for Facebook, Google, and other platforms
- **Email sequences** with intelligence-driven personalization
- **Blog posts** with SEO optimization
- **Video scripts** for VSLs and promotional content
- **Social media content** across all major platforms

### 🔄 **Automation & Scaling**

- **Proactive competitor monitoring** with automated alerts
- **Niche opportunity detection** and analysis
- **Performance tracking** and conversion optimization
- **Intelligent caching** for cost reduction and speed
- **Batch processing** for high-volume analysis

### 🏗️ **Enterprise Architecture**

- **Modular design** with clear separation of concerns
- **Scalable database** with PostgreSQL and JSONB intelligence storage
- **RESTful API** with comprehensive documentation
- **Error handling** and logging throughout
- **Security** with JWT authentication and role-based access

## 📊 **Technology Stack**

### **Backend Framework**

- **FastAPI** - High-performance async API framework
- **SQLAlchemy** - Database ORM with PostgreSQL
- **Pydantic** - Data validation and serialization
- **Asyncio** - Asynchronous processing for AI calls

### **AI & Machine Learning**

- **Ultra-cheap providers**: Groq, Together AI, Deepseek
- **Premium providers**: OpenAI, Anthropic (Claude), Cohere
- **Custom enhancement modules** for specialized intelligence
- **Cost optimization algorithms** for provider selection

### **Data & Storage**

- **PostgreSQL** - Primary database with JSONB for intelligence
- **Redis** - Caching and session management
- **File storage** - For generated content and assets

### **Monitoring & Analytics**

- **Comprehensive logging** with structured data
- **Performance metrics** and cost tracking
- **Error monitoring** and alerting
- **Usage analytics** and optimization insights

## 🎯 **Use Cases**

### **For Affiliate Marketers**

- Analyze competitor sales pages for winning angles
- Generate high-converting landing pages and ads
- Monitor niche opportunities and trends
- Create complete campaign assets from single URL

### **For Digital Agencies**

- Provide clients with comprehensive competitive intelligence
- Generate content at scale with AI enhancement
- Track campaign performance and optimization opportunities
- Deliver data-driven marketing strategies

### **For E-commerce Businesses**

- Analyze competitor positioning and messaging
- Generate product landing pages and marketing copy
- Monitor market trends and opportunities
- Optimize conversion through intelligence-driven insights

### **For SaaS Companies**

- Competitive analysis and positioning
- Content marketing at scale
- Lead generation page optimization
- Market research and opportunity identification

---

## 📝 **Development Notes**

### **Recent Major Updates**

- ✅ **Ultra-cheap AI integration** - 99%+ cost savings implemented
- ✅ **Modular enhancement system** - 6 specialized AI modules
- ✅ **Tiered provider management** - Automatic fallbacks and optimization
- ✅ **Comprehensive intelligence categories** - Scientific, market, credibility, etc.
- ✅ **Landing page generator** - Complete system with analytics

### **Current Status**

- **Working perfectly** with ultra-cheap providers
- **Database integration** functioning correctly
- **All enhancement modules** operational
- **Cost optimization** achieving 99%+ savings
- **Quality intelligence** generation across all categories

### **Next Development Priorities**

1. **Rate limiting optimization** for high-volume usage
2. **JSON parsing robustness** for provider reliability
3. **Advanced caching strategies** for further cost reduction
4. **UI/UX development** for frontend interface
5. **Advanced analytics dashboard** for performance insights

---

*This sitemap represents a sophisticated competitive intelligence and content generation platform with enterprise-grade architecture, ultra-optimized AI costs, and comprehensive automation capabilities.*
