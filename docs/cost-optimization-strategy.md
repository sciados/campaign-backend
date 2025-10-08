# Cost Optimization & User Tier Strategy

## Vision
Deliver maximum value at each tier by intelligently routing content generation to the optimal AI provider based on quality requirements, user tier, and cost constraints.

---

## Current AI Provider Costs (Per 1M Tokens)

### Text Generation

| Provider | Input Cost | Output Cost | Quality | Speed | Best For |
|----------|-----------|-------------|---------|-------|----------|
| **Claude Sonnet 3.5** | $3.00 | $15.00 | ⭐⭐⭐⭐⭐ | Fast | Premium content, complex tasks |
| **GPT-4o** | $2.50 | $10.00 | ⭐⭐⭐⭐⭐ | Fast | Premium content, creative |
| **GPT-4o Mini** | $0.15 | $0.60 | ⭐⭐⭐⭐ | Very Fast | Standard content, high volume |
| **Claude Haiku** | $0.25 | $1.25 | ⭐⭐⭐⭐ | Very Fast | Standard content, speed critical |
| **DeepSeek V3** | $0.14 | $0.28 | ⭐⭐⭐⭐ | Medium | Budget content, bulk generation |
| **Gemini Flash** | $0.075 | $0.30 | ⭐⭐⭐ | Very Fast | High volume, simple tasks |

### Image Generation

| Provider | Cost Per Image | Quality | Speed | Best For |
|----------|---------------|---------|-------|----------|
| **DALL-E 3 (HD)** | $0.080 | ⭐⭐⭐⭐⭐ | Medium | Premium images, hero shots |
| **DALL-E 3 (Standard)** | $0.040 | ⭐⭐⭐⭐ | Medium | Standard marketing images |
| **Flux Pro** | $0.055 | ⭐⭐⭐⭐⭐ | Slow | Premium artistic images |
| **Flux Schnell** | $0.003 | ⭐⭐⭐⭐ | Fast | Bulk images, social media |
| **SDXL** | $0.0055 | ⭐⭐⭐ | Medium | Budget images, variations |

---

## User Tier Structure

### **FREE Tier** - $0/month
**Monthly Quota:** 50 credits
**AI Budget:** $0.50 total ($0.01 per credit)

**Strategy:** Ultra-cheap providers only
- Text: Gemini Flash, DeepSeek V3
- Images: Flux Schnell, SDXL
- Video Scripts: Gemini Flash

**Limits:**
- 25 text generations (emails, social posts, short blog posts)
- 15 images (social media quality)
- 10 video scripts
- Max 500 words per text generation
- Max 1024x1024 images only

### **STARTER Tier** - $29/month
**Monthly Quota:** 500 credits
**AI Budget:** $15 total ($0.03 per credit)

**Strategy:** Balanced mix of cheap and standard providers
- Text: GPT-4o Mini (70%), DeepSeek V3 (30%)
- Images: Flux Schnell (70%), DALL-E 3 Standard (30%)
- Video Scripts: GPT-4o Mini

**Limits:**
- 200 text generations
- 150 images
- 150 video scripts
- Max 1500 words per text generation
- Up to 1792x1024 images

### **PROFESSIONAL Tier** - $79/month
**Monthly Quota:** 2000 credits
**AI Budget:** $80 total ($0.04 per credit)

**Strategy:** Quality-focused with smart routing
- Text: GPT-4o (60%), Claude Haiku (30%), GPT-4o Mini (10%)
- Images: DALL-E 3 HD (50%), Flux Schnell (40%), DALL-E 3 Std (10%)
- Video Scripts: GPT-4o, Claude Haiku

**Limits:**
- 1000 text generations
- 500 images
- 500 video scripts
- Max 3000 words per text generation
- All image sizes available
- Priority generation queue

### **AGENCY Tier** - $199/month
**Monthly Quota:** 10000 credits
**AI Budget:** $400 total ($0.04 per credit)

**Strategy:** Premium quality, unlimited customization
- Text: Claude Sonnet 3.5 (40%), GPT-4o (40%), others (20%)
- Images: DALL-E 3 HD (60%), Flux Pro (30%), others (10%)
- Video Scripts: Claude Sonnet 3.5, GPT-4o

**Limits:**
- Unlimited text generations
- Unlimited images
- Unlimited video scripts
- Max 10,000 words per text generation
- Custom AI provider selection
- Dedicated support
- White-label options

---

## Smart Provider Routing System

### Task Complexity Classification

```python
class TaskComplexity(Enum):
    SIMPLE = "simple"           # Social posts, simple emails
    STANDARD = "standard"       # Blog posts, ad copy
    COMPLEX = "complex"         # Long-form articles, white papers
    PREMIUM = "premium"         # Press releases, strategic content

class ContentQuality(Enum):
    BUDGET = "budget"           # Good enough for testing
    STANDARD = "standard"       # Professional quality
    HIGH = "high"              # Marketing-ready
    PREMIUM = "premium"        # Brand-critical content
```

### Routing Logic

```python
# src/content/services/smart_provider_router.py
class SmartProviderRouter:
    """
    Intelligently route content generation to optimal AI provider
    based on user tier, task complexity, and cost constraints
    """

    PROVIDER_MATRIX = {
        # FREE Tier
        "free": {
            "simple": "gemini-flash",
            "standard": "deepseek-v3",
            "complex": "deepseek-v3",  # Best we can offer
            "premium": "deepseek-v3"
        },
        # STARTER Tier
        "starter": {
            "simple": "gemini-flash",
            "standard": "gpt-4o-mini",
            "complex": "gpt-4o-mini",
            "premium": "gpt-4o-mini"
        },
        # PROFESSIONAL Tier
        "professional": {
            "simple": "gpt-4o-mini",
            "standard": "claude-haiku",
            "complex": "gpt-4o",
            "premium": "gpt-4o"
        },
        # AGENCY Tier
        "agency": {
            "simple": "gpt-4o-mini",
            "standard": "gpt-4o",
            "complex": "claude-sonnet-3.5",
            "premium": "claude-sonnet-3.5"
        }
    }

    def select_provider(
        self,
        user_tier: str,
        task_complexity: TaskComplexity,
        content_type: str,
        user_credits_remaining: int,
        user_preference: str = None
    ) -> str:
        """
        Select optimal AI provider based on multiple factors
        """
        # User can override if agency tier
        if user_tier == "agency" and user_preference:
            return user_preference

        # Check if user has enough credits for premium provider
        base_provider = self.PROVIDER_MATRIX[user_tier][task_complexity.value]

        # Fallback to cheaper provider if credits running low
        if user_credits_remaining < 50:
            return self._get_fallback_provider(user_tier)

        return base_provider
```

### Image Provider Routing

```python
IMAGE_PROVIDER_MATRIX = {
    "free": {
        "all": "flux-schnell"  # $0.003 per image
    },
    "starter": {
        "social_media": "flux-schnell",      # Bulk social posts
        "marketing": "sdxl",                 # Standard marketing
        "hero": "dall-e-3-standard"         # Important images
    },
    "professional": {
        "social_media": "flux-schnell",
        "marketing": "dall-e-3-standard",
        "hero": "dall-e-3-hd"
    },
    "agency": {
        "social_media": "flux-schnell",
        "marketing": "dall-e-3-hd",
        "hero": "flux-pro"  # Highest quality
    }
}
```

---

## Cost Tracking & Budget Management

### Real-Time Cost Tracking

```python
class CostTracker:
    """Track AI costs per user, per campaign, per content type"""

    async def track_generation_cost(
        self,
        user_id: UUID,
        campaign_id: UUID,
        content_type: str,
        provider: str,
        tokens_used: int,
        cost: float
    ):
        """Record generation cost"""
        await self.db.execute("""
            INSERT INTO ai_usage_logs
            (user_id, campaign_id, content_type, provider, tokens_used, cost, created_at)
            VALUES (:user_id, :campaign_id, :content_type, :provider, :tokens, :cost, NOW())
        """, {...})

    async def get_user_monthly_spend(self, user_id: UUID) -> float:
        """Get user's AI spend this month"""
        result = await self.db.execute("""
            SELECT SUM(cost) as total
            FROM ai_usage_logs
            WHERE user_id = :user_id
            AND created_at >= date_trunc('month', CURRENT_DATE)
        """, {"user_id": user_id})
        return result.fetchone().total or 0.0

    async def check_budget_limit(
        self,
        user_id: UUID,
        user_tier: str,
        estimated_cost: float
    ) -> Dict[str, Any]:
        """Check if user can afford this generation"""
        current_spend = await self.get_user_monthly_spend(user_id)
        tier_budget = TIER_BUDGETS[user_tier]

        remaining_budget = tier_budget - current_spend

        return {
            "can_generate": estimated_cost <= remaining_budget,
            "current_spend": current_spend,
            "tier_budget": tier_budget,
            "remaining_budget": remaining_budget,
            "estimated_cost": estimated_cost,
            "credits_remaining": self._calculate_credits_remaining(user_id)
        }
```

### Budget Alerts

```python
class BudgetAlertSystem:
    """Alert users when approaching budget limits"""

    ALERT_THRESHOLDS = {
        "warning": 0.75,   # 75% of budget used
        "critical": 0.90,  # 90% of budget used
        "exceeded": 1.0    # 100% of budget used
    }

    async def check_and_alert(self, user_id: UUID):
        """Check budget usage and send alerts if needed"""
        usage_ratio = await self.get_budget_usage_ratio(user_id)

        if usage_ratio >= 0.90:
            await self.send_alert(user_id, "critical")
        elif usage_ratio >= 0.75:
            await self.send_alert(user_id, "warning")
```

---

## Content Type Cost Optimization

### Email Sequences (7 emails)
**Estimated Tokens:** 3500 input + 7000 output = 10,500 tokens

| Tier | Provider | Cost per Sequence | Credits Used |
|------|----------|------------------|--------------|
| Free | Gemini Flash | $0.0039 | 4 credits |
| Starter | GPT-4o Mini | $0.0147 | 5 credits |
| Professional | Claude Haiku | $0.0166 | 5 credits |
| Agency | Claude Sonnet 3.5 | $0.1260 | 10 credits |

### Blog Post (1500 words)
**Estimated Tokens:** 500 input + 2000 output = 2,500 tokens

| Tier | Provider | Cost per Article | Credits Used |
|------|----------|-----------------|--------------|
| Free | DeepSeek V3 | $0.0009 | 1 credit |
| Starter | GPT-4o Mini | $0.0015 | 1 credit |
| Professional | GPT-4o | $0.0325 | 3 credits |
| Agency | Claude Sonnet 3.5 | $0.0450 | 5 credits |

### Ad Copy (3 variations)
**Estimated Tokens:** 400 input + 600 output = 1,000 tokens

| Tier | Provider | Cost per Ad Set | Credits Used |
|------|----------|----------------|--------------|
| Free | Gemini Flash | $0.0004 | 1 credit |
| Starter | GPT-4o Mini | $0.0009 | 1 credit |
| Professional | GPT-4o | $0.0130 | 1 credit |
| Agency | Claude Sonnet 3.5 | $0.0180 | 2 credits |

### Marketing Image
| Tier | Provider | Cost per Image | Credits Used |
|------|----------|---------------|--------------|
| Free | Flux Schnell | $0.003 | 1 credit |
| Starter | Flux Schnell | $0.003 | 1 credit |
| Professional | DALL-E 3 HD | $0.080 | 2 credits |
| Agency | DALL-E 3 HD | $0.080 | 2 credits |

---

## Quality Safeguards

### Minimum Quality Standards

Even on FREE tier, ensure:
- ✅ No placeholder text (e.g., "[Product Name]")
- ✅ Grammatically correct
- ✅ Coherent structure
- ✅ Actionable content
- ✅ Brand name used correctly

### Quality Boosting Strategies

**For Lower-Tier Providers:**
1. **Better Prompts:** More detailed, structured prompts
2. **Few-Shot Examples:** Include examples in prompts
3. **Chain of Thought:** Break complex tasks into steps
4. **Post-Processing:** Fix common issues automatically
5. **Validation:** Reject and retry if quality too low

**Example:**
```python
async def generate_with_quality_guarantee(
    self,
    provider: str,
    prompt: str,
    min_quality_score: float = 0.7
) -> Dict:
    """Generate content with quality guarantee"""

    max_retries = 3
    for attempt in range(max_retries):
        result = await self.generate(provider, prompt)

        quality_score = await self.assess_quality(result)

        if quality_score >= min_quality_score:
            return result

        # Enhance prompt and retry
        prompt = self.enhance_prompt(prompt, result, quality_score)

    # If all retries fail, upgrade to better provider
    return await self.generate(self.upgrade_provider(provider), prompt)
```

---

## Database Schema for Cost Tracking

```sql
-- AI usage logging
CREATE TABLE ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    campaign_id UUID REFERENCES campaigns(id),
    content_type VARCHAR(50),
    provider VARCHAR(50),
    task_complexity VARCHAR(20),
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost DECIMAL(10, 6),
    quality_score DECIMAL(3, 2),
    generation_time DECIMAL(8, 3),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_usage_user_date ON ai_usage_logs(user_id, created_at);
CREATE INDEX idx_ai_usage_campaign ON ai_usage_logs(campaign_id);

-- User tier and credit tracking
CREATE TABLE user_credits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) UNIQUE,
    tier VARCHAR(20) DEFAULT 'free',
    credits_total INTEGER DEFAULT 50,
    credits_used INTEGER DEFAULT 0,
    credits_remaining INTEGER GENERATED ALWAYS AS (credits_total - credits_used) STORED,
    monthly_reset_date DATE,
    ai_budget DECIMAL(10, 2),
    ai_spend_current_month DECIMAL(10, 2) DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Budget alerts
CREATE TABLE budget_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    alert_type VARCHAR(20), -- warning, critical, exceeded
    threshold_percentage DECIMAL(5, 2),
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged BOOLEAN DEFAULT FALSE
);
```

---

## Frontend: Cost Transparency

### Show Estimated Costs Before Generation

```typescript
// src/components/campaigns/CostEstimator.tsx
interface CostEstimator {
    contentType: string;
    userTier: string;
    options: GenerationOptions;

    estimate: {
        credits: number;
        aiCost: number;
        provider: string;
        qualityLevel: string;
    };
}
```

**UI Display:**
```
┌─────────────────────────────────────┐
│ Generate Email Sequence (7 emails) │
├─────────────────────────────────────┤
│ Estimated Cost: 5 credits          │
│ Provider: GPT-4o Mini              │
│ Quality: ⭐⭐⭐⭐ Professional       │
│                                     │
│ Your Balance: 245 credits          │
│ After: 240 credits                 │
│                                     │
│ [Generate] [Cancel]                │
└─────────────────────────────────────┘
```

### Credit Usage Dashboard

```typescript
// src/components/dashboard/CreditUsage.tsx
interface CreditUsage {
    tier: string;
    creditsTotal: number;
    creditsUsed: number;
    creditsRemaining: number;
    resetDate: Date;

    breakdown: {
        emails: number;
        socialPosts: number;
        blogArticles: number;
        adCopy: number;
        images: number;
    };

    costSavings: number; // vs. manual/other platforms
}
```

---

## Cost Optimization Recommendations

### For Users

**Free Tier:**
- Use for testing and experimentation
- Generate in batches to maximize credits
- Focus on high-value content types
- Upgrade when ready to scale

**Starter Tier:**
- Perfect for solo creators and small businesses
- Mix of quality and volume
- Good for social media management

**Professional Tier:**
- Best for agencies and growing businesses
- High-quality content for client work
- Priority support

**Agency Tier:**
- White-label capabilities
- Custom provider selection
- Unlimited scale

### For Platform

1. **Cache Common Patterns:** Reuse similar content structures
2. **Batch Processing:** Generate multiple items in one call when possible
3. **Smart Retries:** Only retry on specific failure types
4. **Provider Fallbacks:** Automatic failover to cheaper providers
5. **Rate Limiting:** Prevent abuse and runaway costs

---

## Implementation Priority

### Phase 1: Core Cost Management (Week 1)
1. ✅ Smart provider router
2. ✅ Cost tracker service
3. ✅ Budget checker
4. ✅ Database schema

### Phase 2: User Experience (Week 2)
1. Cost estimator component
2. Credit usage dashboard
3. Budget alerts
4. Upgrade prompts

### Phase 3: Optimization (Week 3)
1. Quality assessment system
2. Auto-retry with provider upgrade
3. Caching system
4. Analytics and reporting

---

## Success Metrics

**Cost Efficiency:**
- Average cost per content piece < tier budget
- 95%+ of users stay within tier budget
- <5% support tickets related to costs

**Quality Maintenance:**
- All tiers maintain 80%+ quality score
- <10% content rejection rate
- User satisfaction >4.0/5.0 across all tiers

**Business:**
- 60%+ users upgrade from free
- 30%+ users upgrade from starter
- <5% downgrades

---

*This cost optimization strategy ensures every user gets maximum value at their tier while maintaining sustainable economics for the platform.*
