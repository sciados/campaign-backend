"""
File: src/intelligence/routers/analytics_routes.py
Analytics Routes - Two-Tier System: Admin & User Analytics
✅ COMPREHENSIVE: Platform monitoring + User performance tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import json

from src.core.database import get_db
from src.auth.dependencies import get_current_user, get_admin_user
from src.models.user import User
from ..schemas.responses import *

router = APIRouter()

# ============================================================================
# 🔐 ADMIN ANALYTICS: Platform-Wide Ultra-Cheap AI Monitoring
# ============================================================================

@router.get("/admin/cost-dashboard", dependencies=[Depends(get_admin_user)])
async def get_admin_cost_dashboard(
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    📊 ADMIN: Platform-wide cost savings and ultra-cheap AI performance
    Requires admin privileges
    """
    try:
        # Get daily cost analytics
        query = text("""
            SELECT 
                date,
                total_generations,
                ultra_cheap_generations,
                standard_generations,
                total_actual_cost,
                total_savings,
                total_openai_equivalent_cost,
                groq_usage,
                together_usage,
                deepseek_usage,
                openai_fallback_usage,
                avg_generation_time,
                avg_tokens_per_generation,
                email_generations,
                ad_copy_generations,
                social_generations
            FROM admin_cost_analytics 
            WHERE date >= CURRENT_DATE - INTERVAL :days
            ORDER BY date DESC
        """)
        
        result = await db.execute(query, {"days": f"{days} days"})
        daily_analytics = [dict(row._mapping) for row in result]
        
        # Calculate summary metrics
        total_savings = sum(float(row['total_savings'] or 0) for row in daily_analytics)
        total_generations = sum(int(row['total_generations'] or 0) for row in daily_analytics)
        ultra_cheap_adoption = sum(int(row['ultra_cheap_generations'] or 0) for row in daily_analytics)
        
        adoption_rate = (ultra_cheap_adoption / max(total_generations, 1)) * 100
        
        return {
            "period_days": days,
            "summary": {
                "total_cost_savings": round(total_savings, 4),
                "total_generations": total_generations,
                "ultra_cheap_adoption_rate": round(adoption_rate, 1),
                "average_savings_per_generation": round(total_savings / max(total_generations, 1), 6),
                "annual_savings_projection": round(total_savings * (365 / days), 2)
            },
            "daily_breakdown": daily_analytics,
            "provider_distribution": {
                "groq": sum(int(row['groq_usage'] or 0) for row in daily_analytics),
                "together": sum(int(row['together_usage'] or 0) for row in daily_analytics),
                "deepseek": sum(int(row['deepseek_usage'] or 0) for row in daily_analytics),
                "openai_fallback": sum(int(row['openai_fallback_usage'] or 0) for row in daily_analytics)
            }
        }
        
    except Exception as e:
        logging.error(f"Admin cost dashboard failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cost dashboard query failed: {str(e)}"
        )

@router.get("/admin/user-analytics", dependencies=[Depends(get_admin_user)])
async def get_admin_user_analytics(
    limit: int = Query(50, description="Number of top users to return"),
    min_generations: int = Query(5, description="Minimum generations to include user"),
    db: AsyncSession = Depends(get_db)
):
    """
    👥 ADMIN: User adoption patterns and usage analytics
    """
    try:
        query = text("""
            SELECT 
                user_id,
                total_generations,
                ultra_cheap_generations,
                user_total_savings,
                active_days,
                last_generation,
                first_generation,
                preferred_content_type,
                content_types_used,
                avg_user_rating,
                published_content,
                usage_tier,
                avg_savings_per_generation
            FROM admin_user_analytics 
            WHERE total_generations >= :min_generations
            ORDER BY user_total_savings DESC
            LIMIT :limit
        """)
        
        result = await db.execute(query, {"min_generations": min_generations, "limit": limit})
        user_analytics = [dict(row._mapping) for row in result]
        
        # Calculate user tier distribution
        tier_distribution = {}
        for user in user_analytics:
            tier = user['usage_tier']
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
        
        return {
            "total_active_users": len(user_analytics),
            "tier_distribution": tier_distribution,
            "top_users": user_analytics,
            "platform_metrics": {
                "avg_savings_per_user": round(
                    sum(float(u['user_total_savings'] or 0) for u in user_analytics) / max(len(user_analytics), 1), 4
                ),
                "avg_generations_per_user": round(
                    sum(int(u['total_generations'] or 0) for u in user_analytics) / max(len(user_analytics), 1), 1
                ),
                "ultra_cheap_adoption_by_users": round(
                    len([u for u in user_analytics if (u['ultra_cheap_generations'] or 0) > (u['total_generations'] or 1) * 0.5]) / max(len(user_analytics), 1) * 100, 1
                )
            }
        }
        
    except Exception as e:
        logging.error(f"Admin user analytics failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User analytics query failed: {str(e)}"
        )

@router.get("/admin/provider-performance", dependencies=[Depends(get_admin_user)])
async def get_admin_provider_performance(db: AsyncSession = Depends(get_db)):
    """
    ⚡ ADMIN: Ultra-cheap AI provider performance and reliability metrics
    """
    try:
        query = text("""
            SELECT 
                provider,
                total_usage,
                avg_cost,
                avg_generation_time,
                avg_tokens,
                successful_generations,
                avg_quality_score,
                total_savings_provided,
                avg_savings_per_use,
                last_7_days,
                last_30_days,
                speed_rating
            FROM admin_provider_analytics
            ORDER BY total_usage DESC
        """)
        
        result = await db.execute(query)
        provider_analytics = [dict(row._mapping) for row in result]
        
        # Calculate provider health scores
        for provider in provider_analytics:
            # Health score based on usage, speed, and reliability
            usage_score = min(provider['total_usage'] / 100, 1.0) * 30  # Max 30 points
            speed_score = 25 if provider['speed_rating'] == 'fast' else 15 if provider['speed_rating'] == 'medium' else 5
            quality_score = (provider['avg_quality_score'] or 0) / 100 * 25  # Max 25 points
            savings_score = min((provider['avg_savings_per_use'] or 0) / 0.02, 1.0) * 20  # Max 20 points
            
            provider['health_score'] = round(usage_score + speed_score + quality_score + savings_score, 1)
            provider['health_status'] = (
                'excellent' if provider['health_score'] >= 80 else
                'good' if provider['health_score'] >= 60 else
                'fair' if provider['health_score'] >= 40 else
                'poor'
            )
        
        return {
            "provider_performance": provider_analytics,
            "recommendations": [
                f"Primary provider: {provider_analytics[0]['provider']}" if provider_analytics else "No data",
                f"Fastest provider: {min(provider_analytics, key=lambda x: x['avg_generation_time'] or 999)['provider']}" if provider_analytics else "No data",
                f"Most cost-effective: {max(provider_analytics, key=lambda x: x['avg_savings_per_use'] or 0)['provider']}" if provider_analytics else "No data"
            ]
        }
        
    except Exception as e:
        logging.error(f"Admin provider performance failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Provider performance query failed: {str(e)}"
        )

@router.get("/admin/financial-summary", dependencies=[Depends(get_admin_user)])
async def get_admin_financial_summary(db: AsyncSession = Depends(get_db)):
    """
    💰 ADMIN: Financial impact and ROI analysis for ultra-cheap AI
    """
    try:
        query = text("""
            SELECT 
                period,
                period_start,
                total_generations,
                active_users,
                actual_costs,
                openai_equivalent_costs,
                total_savings,
                savings_percentage,
                annual_savings_projection
            FROM admin_financial_summary
            ORDER BY period_start DESC
        """)
        
        result = await db.execute(query)
        financial_data = [dict(row._mapping) for row in result]
        
        return {
            "financial_summary": financial_data,
            "business_impact": {
                "monthly_platform_savings": financial_data[0]['total_savings'] if financial_data else 0,
                "cost_reduction_percentage": financial_data[0]['savings_percentage'] if financial_data else 0,
                "user_growth_impact": len(financial_data),
                "roi_multiplier": round((financial_data[0]['total_savings'] or 0) / max(financial_data[0]['actual_costs'] or 1, 0.001), 2) if financial_data else 0
            }
        }
        
    except Exception as e:
        logging.error(f"Admin financial summary failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Financial summary query failed: {str(e)}"
        )

# ============================================================================
# 👤 USER ANALYTICS: Personal Performance & Campaign Success
# ============================================================================

@router.get("/user/dashboard")
async def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📈 USER: Personal content performance dashboard
    Shows individual user's ultra-cheap AI usage and content success
    """
    try:
        # Get user's content analytics
        query = text("""
            SELECT * FROM get_user_content_analytics(:user_id)
        """)
        
        result = await db.execute(query, {"user_id": current_user.id})
        content_analytics = [dict(row._mapping) for row in result]
        
        # Get user's ROI analytics
        roi_query = text("""
            SELECT * FROM get_user_roi_analytics(:user_id, 30)
        """)
        
        roi_result = await db.execute(roi_query, {"user_id": current_user.id})
        roi_data = roi_result.fetchone()
        roi_summary = dict(roi_data._mapping) if roi_data else {}
        
        return {
            "user_id": current_user.id,
            "content_performance": content_analytics,
            "roi_analysis": roi_summary,
            "quick_stats": {
                "total_content": sum(int(c['total_content'] or 0) for c in content_analytics),
                "total_savings": sum(float(c['total_cost_savings'] or 0) for c in content_analytics),
                "avg_rating": round(
                    sum(float(c['avg_rating'] or 0) for c in content_analytics if c['avg_rating']) / 
                    max(len([c for c in content_analytics if c['avg_rating']]), 1), 2
                ),
                "ultra_cheap_adoption": round(
                    sum(float(c['ultra_cheap_usage_rate'] or 0) for c in content_analytics) / 
                    max(len(content_analytics), 1), 1
                )
            }
        }
        
    except Exception as e:
        logging.error(f"User dashboard failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User dashboard query failed: {str(e)}"
        )

@router.get("/user/campaign/{campaign_id}")
async def get_user_campaign_analytics(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🎯 USER: Detailed campaign performance analytics
    Shows success metrics for a specific campaign
    """
    try:
        query = text("""
            SELECT * FROM get_campaign_analytics(:campaign_id, :user_id)
        """)
        
        result = await db.execute(query, {"campaign_id": campaign_id, "user_id": current_user.id})
        campaign_data = result.fetchone()
        
        if not campaign_data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or access denied"
            )
        
        campaign_summary = dict(campaign_data._mapping)['campaign_summary']
        
        return {
            "campaign_analytics": campaign_summary,
            "insights": {
                "performance_trend": "improving" if campaign_summary.get('avg_performance_score', 0) > 70 else "needs_attention",
                "content_diversity": len(campaign_summary.get('content_breakdown', {})),
                "ultra_cheap_effectiveness": campaign_summary.get('ultra_cheap_ai_usage', 0) / max(campaign_summary.get('total_content', 1), 1) * 100,
                "publish_recommendation": "Consider publishing more content" if campaign_summary.get('published_rate', 0) < 50 else "Great publishing rate!"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"User campaign analytics failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign analytics query failed: {str(e)}"
        )

@router.get("/user/insights")
async def get_user_content_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    💡 USER: Personalized insights and recommendations
    AI-driven suggestions for improving content performance
    """
    try:
        query = text("""
            SELECT 
                content_type,
                ultra_cheap_avg_rating,
                standard_avg_rating,
                rating_vs_generation_time_correlation,
                performance_vs_length_correlation,
                best_performing_provider,
                recommendation
            FROM user_content_insights 
            WHERE user_id = :user_id
        """)
        
        result = await db.execute(query, {"user_id": current_user.id})
        insights = [dict(row._mapping) for row in result]
        
        # Generate AI-powered recommendations
        recommendations = []
        for insight in insights:
            content_type = insight['content_type']
            
            # Ultra-cheap AI effectiveness
            if insight['ultra_cheap_avg_rating'] and insight['standard_avg_rating']:
                if insight['ultra_cheap_avg_rating'] > insight['standard_avg_rating']:
                    recommendations.append(f"✅ Use ultra-cheap AI for {content_type} - it performs {(insight['ultra_cheap_avg_rating'] - insight['standard_avg_rating']):.1f} points better")
                
            # Provider recommendations
            if insight['best_performing_provider']:
                recommendations.append(f"🎯 For {content_type}, {insight['best_performing_provider']} gives you the best results")
            
            # Custom recommendation
            if insight['recommendation']:
                recommendations.append(f"💡 {content_type}: {insight['recommendation']}")
        
        return {
            "content_insights": insights,
            "personalized_recommendations": recommendations,
            "optimization_score": calculate_user_optimization_score(insights),
            "next_steps": generate_next_steps(insights)
        }
        
    except Exception as e:
        logging.error(f"User insights failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User insights query failed: {str(e)}"
        )

# ============================================================================
# 🔮 FUTURE-PROOF: Multi-Generator Analytics Framework
# ============================================================================

@router.get("/admin/generator-performance", dependencies=[Depends(get_admin_user)])
async def get_generator_performance_analytics(
    generator_type: Optional[str] = Query(None, description="Filter by generator type"),
    days: int = Query(30, description="Analysis period"),
    db: AsyncSession = Depends(get_db)
):
    """
    🛠️ ADMIN: Multi-generator performance analytics
    ✅ FUTURE-PROOF: Scales automatically as new generators are added
    """
    try:
        # Dynamic query that adapts to any generator types in the database
        base_query = """
            SELECT 
                content_type as generator_type,
                COUNT(*) as total_usage,
                COUNT(*) FILTER (WHERE generation_settings->>'ultra_cheap_ai_used' = 'true') as ultra_cheap_usage,
                COUNT(*) FILTER (WHERE generation_settings->>'ultra_cheap_ai_used' = 'false') as standard_usage,
                
                -- Performance Metrics
                AVG((content_metadata->>'generation_time')::decimal) as avg_generation_time,
                AVG((content_metadata->>'total_tokens')::decimal) as avg_tokens,
                AVG((content_metadata->>'quality_score')::decimal) as avg_quality_score,
                
                -- Cost Analytics
                SUM((generation_settings->>'generation_cost')::decimal) as total_cost,
                SUM((generation_settings->>'cost_savings')::decimal) as total_savings,
                AVG((generation_settings->>'cost_savings')::decimal) as avg_savings_per_generation,
                
                -- Provider Distribution
                COUNT(*) FILTER (WHERE generation_settings->>'provider' = 'groq') as groq_usage,
                COUNT(*) FILTER (WHERE generation_settings->>'provider' = 'together') as together_usage,
                COUNT(*) FILTER (WHERE generation_settings->>'provider' = 'deepseek') as deepseek_usage,
                COUNT(*) FILTER (WHERE generation_settings->>'provider' = 'anthropic') as anthropic_usage,
                COUNT(*) FILTER (WHERE generation_settings->>'provider' = 'openai') as openai_usage,
                COUNT(*) FILTER (WHERE generation_settings->>'provider' = 'replicate') as replicate_usage,
                COUNT(*) FILTER (WHERE generation_settings->>'provider' = 'perplexity') as perplexity_usage,
                
                -- User Satisfaction
                AVG(user_rating) as avg_user_rating,
                COUNT(*) FILTER (WHERE is_published = true) as published_count,
                (COUNT(*) FILTER (WHERE is_published = true)::decimal / NULLIF(COUNT(*), 0) * 100) as publish_rate,
                
                -- Trends
                COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') as last_7_days,
                COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '1 day') as last_24_hours
                
            FROM generated_content 
            WHERE created_at >= CURRENT_DATE - INTERVAL :days
        """
        
        if generator_type:
            base_query += " AND content_type = :generator_type"
            
        base_query += """
            GROUP BY content_type
            ORDER BY total_usage DESC
        """
        
        params = {"days": f"{days} days"}
        if generator_type:
            params["generator_type"] = generator_type
            
        result = await db.execute(text(base_query), params)
        generator_analytics = [dict(row._mapping) for row in result]
        
        # Calculate efficiency scores for each generator
        for generator in generator_analytics:
            # Efficiency score: cost savings + speed + quality + adoption
            cost_efficiency = min((generator['avg_savings_per_generation'] or 0) / 0.02, 1) * 25
            speed_efficiency = max(25 - (generator['avg_generation_time'] or 10), 0)
            quality_efficiency = (generator['avg_quality_score'] or 0) / 100 * 25
            adoption_efficiency = (generator['ultra_cheap_usage'] or 0) / max(generator['total_usage'], 1) * 25
            
            generator['efficiency_score'] = round(cost_efficiency + speed_efficiency + quality_efficiency + adoption_efficiency, 1)
            generator['ultra_cheap_adoption_rate'] = round((generator['ultra_cheap_usage'] or 0) / max(generator['total_usage'], 1) * 100, 1)
        
        return {
            "generator_performance": generator_analytics,
            "platform_summary": {
                "total_generators_active": len(generator_analytics),
                "most_used_generator": generator_analytics[0]['generator_type'] if generator_analytics else None,
                "highest_efficiency_generator": max(generator_analytics, key=lambda x: x['efficiency_score'])['generator_type'] if generator_analytics else None,
                "total_platform_savings": sum(float(g['total_savings'] or 0) for g in generator_analytics),
                "average_ultra_cheap_adoption": round(
                    sum(float(g['ultra_cheap_adoption_rate'] or 0) for g in generator_analytics) / max(len(generator_analytics), 1), 1
                )
            },
            "future_generators_ready": True,  # Framework supports any new generator automatically
            "scaling_recommendations": generate_scaling_recommendations(generator_analytics)
        }
        
    except Exception as e:
        logging.error(f"Generator performance analytics failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generator analytics query failed: {str(e)}"
        )

@router.get("/user/generator-preferences")
async def get_user_generator_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ⚙️ USER: Personal generator preferences and optimization suggestions
    ✅ FUTURE-PROOF: Adapts to new generators automatically
    """
    try:
        query = text("""
            SELECT 
                content_type as generator_type,
                COUNT(*) as usage_count,
                AVG(user_rating) as avg_rating,
                AVG((generation_settings->>'cost_savings')::decimal) as avg_savings,
                COUNT(*) FILTER (WHERE generation_settings->>'ultra_cheap_ai_used' = 'true') as ultra_cheap_usage,
                
                -- Preferred settings
                MODE() WITHIN GROUP (ORDER BY generation_settings->>'provider') as preferred_provider,
                MODE() WITHIN GROUP (ORDER BY generation_settings->>'generation_method') as preferred_method,
                
                -- Performance indicators
                AVG(performance_score) as avg_performance,
                COUNT(*) FILTER (WHERE is_published = true) as published_count,
                
                -- Recent usage
                COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') as recent_usage
                
            FROM generated_content 
            WHERE user_id = :user_id
            GROUP BY content_type
            HAVING COUNT(*) >= 3  -- Only show generators with sufficient usage
            ORDER BY usage_count DESC
        """)
        
        result = await db.execute(query, {"user_id": current_user.id})
        preferences = [dict(row._mapping) for row in result]
        
        # Generate personalized optimization recommendations
        optimization_tips = []
        for pref in preferences:
            generator = pref['generator_type']
            
            # Ultra-cheap adoption recommendations
            adoption_rate = pref['ultra_cheap_usage'] / max(pref['usage_count'], 1) * 100
            if adoption_rate < 80:
                potential_savings = (pref['avg_savings'] or 0) * (pref['usage_count'] - pref['ultra_cheap_usage'])
                optimization_tips.append(f"💰 Enable ultra-cheap AI for {generator} to save ${potential_savings:.4f} more")
            
            # Performance recommendations
            if pref['avg_rating'] and pref['avg_rating'] < 4:
                optimization_tips.append(f"📈 Try different settings for {generator} to improve quality (current: {pref['avg_rating']:.1f}/5)")
            
            # Publishing recommendations
            publish_rate = pref['published_count'] / max(pref['usage_count'], 1) * 100
            if publish_rate < 30:
                optimization_tips.append(f"📝 Consider publishing more {generator} content (currently {publish_rate:.0f}% published)")
        
        return {
            "generator_preferences": preferences,
            "optimization_opportunities": optimization_tips,
            "user_generator_profile": {
                "most_used_generator": preferences[0]['generator_type'] if preferences else None,
                "total_generators_used": len(preferences),
                "overall_ultra_cheap_adoption": round(
                    sum(p['ultra_cheap_usage'] for p in preferences) / max(sum(p['usage_count'] for p in preferences), 1) * 100, 1
                ),
                "total_personal_savings": sum(float(p['avg_savings'] or 0) * p['usage_count'] for p in preferences)
            }
        }
        
    except Exception as e:
        logging.error(f"User generator preferences failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generator preferences query failed: {str(e)}"
        )

# ============================================================================
# 📊 HELPER FUNCTIONS
# ============================================================================

def calculate_user_optimization_score(insights: List[Dict]) -> Dict[str, Any]:
    """Calculate how well user is optimizing their content generation"""
    if not insights:
        return {"score": 0, "level": "beginner", "areas_for_improvement": ["Generate more content to get personalized insights"]}
    
    # Score factors
    ultra_cheap_adoption = sum(1 for i in insights if i.get('ultra_cheap_avg_rating', 0) > i.get('standard_avg_rating', 0))
    content_diversity = len(insights)
    
    base_score = (ultra_cheap_adoption / len(insights)) * 50  # Max 50 points for ultra-cheap adoption
    diversity_score = min(content_diversity * 10, 30)  # Max 30 points for diversity
    quality_score = 20  # Default 20 points for having insights
    
    total_score = base_score + diversity_score + quality_score
    
    if total_score >= 80:
        level = "expert"
    elif total_score >= 60:
        level = "advanced"
    elif total_score >= 40:
        level = "intermediate"
    else:
        level = "beginner"
    
    return {
        "score": round(total_score, 1),
        "level": level,
        "breakdown": {
            "ultra_cheap_optimization": round(base_score, 1),
            "content_diversity": round(diversity_score, 1),
            "experience_bonus": 20
        }
    }

def generate_next_steps(insights: List[Dict]) -> List[str]:
    """Generate actionable next steps for users"""
    if not insights:
        return ["Start generating content to get personalized recommendations"]
    
    steps = []
    
    # Check for ultra-cheap AI opportunities
    underutilized = [i for i in insights if i.get('ultra_cheap_avg_rating', 0) > i.get('standard_avg_rating', 0)]
    if underutilized:
        steps.append(f"Enable ultra-cheap AI for {', '.join(i['content_type'] for i in underutilized[:2])} - it performs better for you")
    
    # Content diversity suggestions
    if len(insights) < 3:
        steps.append("Try different content types to find what works best for your audience")
    
    # Performance improvements
    low_performing = [i for i in insights if i.get('ultra_cheap_avg_rating', 0) < 3.5]
    if low_performing:
        steps.append(f"Experiment with different settings for {low_performing[0]['content_type']} to improve results")
    
    return steps[:5]  # Limit to 5 actionable steps

def generate_scaling_recommendations(generator_analytics: List[Dict]) -> List[str]:
    """Generate recommendations for scaling ultra-cheap AI across generators"""
    recommendations = []
    
    if not generator_analytics:
        return ["No generator data available"]
    
    # Identify high-potential generators
    high_usage = [g for g in generator_analytics if g['total_usage'] > 100]
    low_adoption = [g for g in high_usage if g['ultra_cheap_adoption_rate'] < 70]
    
    if low_adoption:
        recommendations.append(f"Focus ultra-cheap AI adoption on {', '.join(g['generator_type'] for g in low_adoption[:2])} - high usage but low adoption")
    
    # Identify efficiency leaders
    top_efficiency = sorted(generator_analytics, key=lambda x: x['efficiency_score'], reverse=True)[:2]
    recommendations.append(f"Promote best practices from {top_efficiency[0]['generator_type']} (efficiency: {top_efficiency[0]['efficiency_score']}) to other generators")
    
    # Cost optimization opportunities
    high_cost = [g for g in generator_analytics if (g['total_cost'] or 0) > (g['total_savings'] or 0)]
    if high_cost:
        recommendations.append(f"Optimize cost efficiency for {', '.join(g['generator_type'] for g in high_cost[:2])}")
    
    return recommendations