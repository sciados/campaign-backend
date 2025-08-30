# src/routes/waitlist.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, func, desc
from typing import List
import logging

from src.core.database import get_async_db
from src.models.waitlist import Waitlist
from src.schemas.waitlist import (
    WaitlistCreate, 
    WaitlistResponse, 
    WaitlistStatsResponse,
    WaitlistEntry
)

router = APIRouter()

def get_client_ip(request: Request) -> str:
    """Extract client IP from request headers (Railway/Vercel compatible)"""
    # Check various headers for the real IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    cf_connecting_ip = request.headers.get("CF-Connecting-IP")  # Cloudflare
    if cf_connecting_ip:
        return cf_connecting_ip
    
    return request.client.host if request.client else "unknown"

@router.post("/join", response_model=WaitlistResponse)
async def join_waitlist(
    waitlist_data: WaitlistCreate,
    request: Request,
    db: Session = Depends(get_async_db)
):
    """Join the waitlist"""
    try:
        # Get client information
        ip_address = get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        
        # Create new waitlist entry
        new_entry = Waitlist(
            email=waitlist_data.email,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=waitlist_data.referrer
        )
        
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        # Get total count and position
        total_count = db.query(Waitlist).count()
        position = db.query(Waitlist).filter(
            Waitlist.id <= new_entry.id
        ).count()
        
        logging.info(f"New waitlist signup: {waitlist_data.email} (position {position})")
        
        return WaitlistResponse(
            message="Successfully added to waitlist!",
            total_signups=total_count,
            position=position,
            email=waitlist_data.email
        )
        
    except IntegrityError:
        db.rollback()
        # Check if email already exists and get their position
        existing = db.query(Waitlist).filter(Waitlist.email == waitlist_data.email).first()
        if existing:
            position = db.query(Waitlist).filter(Waitlist.id <= existing.id).count()
            total_count = db.query(Waitlist).count()
            
            return WaitlistResponse(
                message="You're already on our waitlist!",
                total_signups=total_count,
                position=position,
                email=waitlist_data.email
            )
        
        raise HTTPException(
            status_code=409, 
            detail="Email already registered!"
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Waitlist signup error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error"
        )

@router.get("/stats", response_model=WaitlistStatsResponse)
async def get_waitlist_stats(db: Session = Depends(get_async_db)):
    """Get waitlist statistics (for admin use)"""
    try:
        # Total signups
        total = db.query(Waitlist).count()
        
        # Today's signups
        today_result = db.execute(
            text("""
                SELECT COUNT(*) 
                FROM waitlist 
                WHERE DATE(created_at) = CURRENT_DATE
            """)
        ).scalar()
        today = today_result or 0
        
        # This week's signups
        week_result = db.execute(
            text("""
                SELECT COUNT(*) 
                FROM waitlist 
                WHERE created_at >= DATE_TRUNC('week', CURRENT_DATE)
            """)
        ).scalar()
        this_week = week_result or 0
        
        # This month's signups
        month_result = db.execute(
            text("""
                SELECT COUNT(*) 
                FROM waitlist 
                WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
            """)
        ).scalar()
        this_month = month_result or 0
        
        # Recent signups (last 10)
        recent = db.query(Waitlist).order_by(desc(Waitlist.created_at)).limit(10).all()
        recent_signups = [
            {
                "email": entry.email,
                "created_at": entry.created_at.isoformat(),
                "id": entry.id
            } for entry in recent
        ]
        
        # Daily stats for the last 30 days
        daily_stats_result = db.execute(
            text("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM waitlist 
                WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
        ).fetchall()
        
        daily_stats = [
            {
                "date": row[0].isoformat(),
                "count": row[1]
            } for row in daily_stats_result
        ]
        
        return WaitlistStatsResponse(
            total=total,
            today=today,
            this_week=this_week,
            this_month=this_month,
            recent_signups=recent_signups,
            daily_stats=daily_stats
        )
        
    except Exception as e:
        logging.error(f"Waitlist stats error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to fetch statistics"
        )

@router.get("/export")
async def export_waitlist(db: Session = Depends(get_async_db)):
    """Export all emails for marketing campaigns"""
    try:
        entries = db.query(Waitlist).order_by(Waitlist.created_at.asc()).all()
        
        emails = [
            {
                "id": entry.id,
                "email": entry.email,
                "joined_date": entry.created_at.isoformat(),
                "is_notified": entry.is_notified,
                "referrer": entry.referrer
            } for entry in entries
        ]
        
        return {
            "emails": emails, 
            "total": len(emails),
            "export_date": func.now()
        }
        
    except Exception as e:
        logging.error(f"Waitlist export error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to export waitlist"
        )

@router.get("/check/{email}")
async def check_email_status(email: str, db: Session = Depends(get_async_db)):
    """Check if an email is on the waitlist"""
    try:
        entry = db.query(Waitlist).filter(Waitlist.email == email.lower().strip()).first()
        
        if not entry:
            return {"on_waitlist": False, "message": "Email not found on waitlist"}
        
        position = db.query(Waitlist).filter(Waitlist.id <= entry.id).count()
        total_count = db.query(Waitlist).count()
        
        return {
            "on_waitlist": True,
            "position": position,
            "total_signups": total_count,
            "joined_date": entry.created_at.isoformat(),
            "is_notified": entry.is_notified
        }
        
    except Exception as e:
        logging.error(f"Email check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to check email status"
        )

@router.get("/list", response_model=List[WaitlistEntry])
async def get_waitlist_entries(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_async_db)
):
    """Get paginated waitlist entries (admin only)"""
    try:
        entries = db.query(Waitlist).order_by(
            desc(Waitlist.created_at)
        ).offset(skip).limit(limit).all()
        
        return entries
        
    except Exception as e:
        logging.error(f"Waitlist entries error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch waitlist entries"
        )