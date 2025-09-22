# CampaignForge Video Generation Tier System

## Platform-Optimized Video Specifications

### Short Video Standard Lengths
- **Micro-content**: 10-15 seconds (high-impact, viral potential)
- **Standard short**: 15-30 seconds (optimal engagement)
- **Extended short**: 30-60 seconds (detailed explanations)
- **Long-form short**: 60-90 seconds (educational content)

## Tier System Design

### **Starter Tier** - $29/month
**Target User**: Solo entrepreneurs, small businesses, testing phase

**Video Quota**:
- 25 videos per month
- Maximum 30 seconds per video
- Standard quality (720p)
- 2 platform variants per video

**Features**:
- ✅ Basic templates (5 styles)
- ✅ Pika Labs generation (cost-effective)
- ✅ Standard social media formats
- ✅ Basic intelligence integration
- ❌ No custom branding overlays
- ❌ No batch generation

**Cost Analysis**:
- Platform cost: ~$12.50 (25 × $0.50 avg per video)
- Margin: ~57% ($16.50 profit)

### **Professional Tier** - $79/month
**Target User**: Marketing agencies, growing businesses, content creators

**Video Quota**:
- 75 videos per month
- Maximum 60 seconds per video
- High quality (1080p)
- 4 platform variants per video

**Features**:
- ✅ Premium templates (15 styles)
- ✅ RunwayML + Pika Labs (quality options)
- ✅ All social media formats + custom dimensions
- ✅ Advanced intelligence integration
- ✅ Custom branding overlays
- ✅ Batch generation (up to 10 videos)
- ✅ A/B testing variants

**Cost Analysis**:
- Platform cost: ~$56.25 (75 × $0.75 avg per video)
- Margin: ~29% ($22.75 profit)

### **Enterprise Tier** - $199/month
**Target User**: Large agencies, enterprise marketing teams, high-volume users

**Video Quota**:
- 200 videos per month
- Maximum 90 seconds per video
- Cinematic quality (1080p+)
- Unlimited platform variants

**Features**:
- ✅ All premium templates + custom template creation
- ✅ RunwayML priority access (highest quality)
- ✅ Custom aspect ratios and specifications
- ✅ Full intelligence suite integration
- ✅ Advanced branding and style customization
- ✅ Unlimited batch generation
- ✅ Priority processing queue
- ✅ Analytics and performance tracking
- ✅ API access for integrations

**Cost Analysis**:
- Platform cost: ~$150 (200 × $0.75 avg per video)
- Margin: ~25% ($49 profit)

### **Pay-Per-Video** - No Monthly Commitment
**Target User**: Occasional users, trial customers, overflow usage

**Pricing**:
- $2.99 per 15-30 second video
- $4.99 per 30-60 second video
- $7.99 per 60-90 second video
- +$0.99 per additional platform variant

**Features**:
- ✅ Access to all templates
- ✅ Standard quality options
- ✅ Basic intelligence integration
- ❌ No batch processing
- ❌ No priority queue

## Quality Thresholds by Tier

### Video Resolution & Frame Rate
- **Starter**: 720p @ 24fps (social media standard)
- **Professional**: 1080p @ 30fps (high quality social)
- **Enterprise**: 1080p+ @ 30-60fps (cinematic quality)

### Processing Priority
- **Starter**: Standard queue (5-15 minutes)
- **Professional**: Priority queue (2-8 minutes)
- **Enterprise**: Express queue (1-5 minutes)

### Platform Variants
- **Starter**: 2 variants (Square 1:1, Vertical 9:16)
- **Professional**: 4 variants (+Horizontal 16:9, Story 9:16)
- **Enterprise**: Unlimited custom dimensions

## Usage Analytics & Recommendations

### Typical Monthly Usage Patterns
- **Small Business**: 15-30 videos/month (social media posts, product features)
- **Marketing Agency**: 50-150 videos/month (client campaigns, A/B testing)
- **Enterprise**: 100-500 videos/month (multi-brand, international campaigns)

### Content Type Distribution
- **Product demos**: 35% of usage (15-30s optimal)
- **Social ads**: 30% of usage (10-20s optimal)
- **Testimonials**: 20% of usage (30-60s optimal)
- **Educational content**: 15% of usage (45-90s optimal)

## Quota Management System

### Smart Quota Allocation
```python
class VideoQuotaManager:
    def calculate_optimal_length(self, content_type: str, platform: str) -> int:
        # Recommend optimal length based on:
        # - Platform best practices
        # - Content type performance data
        # - User's remaining quota
        # - Historical engagement rates
        pass

    def suggest_quota_upgrade(self, usage_pattern: UserUsagePattern) -> TierRecommendation:
        # Analyze user behavior and suggest tier changes
        # Based on quota utilization and content performance
        pass
```

### Overflow Handling
- **Quota Exceeded**: Offer pay-per-video at discounted rate
- **Tier Upgrade**: Prorated billing for immediate upgrade
- **Rollover Credits**: Unused quota rolls over (max 25% of monthly limit)

## Competitive Analysis

### Current Market Pricing (AI Video Generation)
- **Synthesia**: $30/month (10 minutes of avatar video)
- **Pictory**: $19/month (30 videos up to 10 minutes)
- **InVideo**: $15/month (60 exports, templates only)
- **Lumen5**: $19/month (30 videos, limited customization)

### CampaignForge Advantages
1. **Intelligence-driven content** (unique in market)
2. **Multi-platform optimization** (automatic formatting)
3. **Higher quota limits** at competitive pricing
4. **Quality tier options** (not just quantity-based)
5. **Marketing-focused features** (A/B testing, performance tracking)

## Implementation Recommendations

### Phase 1: Launch with 3 Tiers
- Focus on Starter, Professional, and Pay-Per-Video
- Collect usage data for 3-6 months
- Optimize quotas based on actual user behavior

### Phase 2: Add Enterprise Tier
- Introduce Enterprise tier once user base is established
- Add advanced features based on Professional tier feedback
- Implement API access and custom integrations

### Phase 3: Usage-Based Pricing
- Consider hybrid model: base tier + overage charges
- Seasonal adjustments for marketing campaigns
- Volume discounts for enterprise customers

## Success Metrics to Track

### Quota Utilization
- **Healthy usage**: 70-90% of monthly quota
- **Under-utilization**: <50% (consider downgrades)
- **Over-utilization**: >95% (recommend upgrades)

### Content Performance
- **Engagement rates** by video length and platform
- **Conversion tracking** for marketing-focused content
- **User satisfaction** scores for generated videos

### Revenue Optimization
- **Average revenue per user (ARPU)** by tier
- **Churn rates** and upgrade/downgrade patterns
- **Lifetime value (LTV)** analysis by user segment

This tier structure balances user value with sustainable business economics while encouraging growth through the tiers.