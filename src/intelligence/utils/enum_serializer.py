"""
Universal Enum Serialization Mixin for PostgreSQL JSONB columns
Handles the conversion between JSON strings (database) and Python dicts (code)
"""
import json
import logging
from typing import Dict, Any, Union, List

from src.utils.json_utils import safe_json_dumps

logger = logging.getLogger(__name__)

class EnumSerializerMixin:
    """Universal mixin to handle PostgreSQL JSONB enum serialization"""
    
    def _serialize_enum_field(self, field_value: Any) -> Dict[str, Any]:
        """
        Convert JSONB field from database to Python dict
        Handles: JSON string -> Python dict conversion
        """
        if field_value is None:
            return {}
        
        # If it's already a dict, return as-is
        if isinstance(field_value, dict):
            return field_value
        
        # If it's a JSON string, parse it
        if isinstance(field_value, str):
            try:
                parsed = json.loads(field_value)
                return parsed if isinstance(parsed, dict) else {}
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse JSONB field: {field_value[:100]}... Error: {e}")
                return {}
        
        # If it's a list, wrap in dict
        if isinstance(field_value, list):
            return {"items": field_value}
        
        # Fallback for any other type
        logger.warning(f"Unexpected JSONB field type: {type(field_value)} - {field_value}")
        return {"value": str(field_value)}
    
    def _deserialize_for_storage(self, data: Union[Dict, List, str]) -> str:
        """
        Convert Python object to JSON string for database storage
        Handles: Python dict/list -> JSON string conversion
        """
        if isinstance(data, str):
            # Already a string, validate it's valid JSON
            try:
                json.loads(data)
                return data
            except (json.JSONDecodeError, ValueError):
                return safe_json_dumps({"error": "Invalid JSON", "original": data})
        
        try:
            return safe_json_dumps(data)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize data for storage: {e}")
            return safe_json_dumps({"error": "Serialization failed", "type": str(type(data))})
    
    def _serialize_intelligence_source(self, source) -> Dict[str, Any]:
        """
        Serialize a complete IntelligenceSourceType object with all JSONB fields
        """
        if not source:
            return {}
        
        return {
            "id": str(source.id),
            "source_url": source.source_url,
            "source_title": source.source_title,
            "confidence_score": source.confidence_score or 0.0,
            "created_at": source.created_at.isoformat() if source.created_at else None,
            "analysis_status": source.analysis_status.value if source.analysis_status else "pending",
            
            # Core intelligence categories with enum serialization
            "offer_intelligence": self._serialize_enum_field(source.offer_intelligence),
            "psychology_intelligence": self._serialize_enum_field(source.psychology_intelligence),
            "content_intelligence": self._serialize_enum_field(source.content_intelligence),
            "competitive_intelligence": self._serialize_enum_field(source.competitive_intelligence),
            "brand_intelligence": self._serialize_enum_field(source.brand_intelligence),
            
            # AI-enhanced categories with enum serialization
            "scientific_intelligence": self._serialize_enum_field(source.scientific_intelligence),
            "credibility_intelligence": self._serialize_enum_field(source.credibility_intelligence),
            "market_intelligence": self._serialize_enum_field(source.market_intelligence),
            "emotional_transformation_intelligence": self._serialize_enum_field(source.emotional_transformation_intelligence),
            "scientific_authority_intelligence": self._serialize_enum_field(source.scientific_authority_intelligence),
            
            # Metadata with enum serialization
            "processing_metadata": self._serialize_enum_field(source.processing_metadata),
            "amplification_applied": bool(
                self._serialize_enum_field(source.processing_metadata).get("amplification_applied", False)
            )
        }
    
    def _serialize_campaign_data(self, campaign) -> Dict[str, Any]:
        """
        Serialize a Campaign object with all JSONB fields
        """
        if not campaign:
            return {}
        
        return {
            "id": str(campaign.id),
            "title": campaign.name,
            "description": campaign.description,
            "status": campaign.status.value if campaign.status else "draft",
            "workflow_state": campaign.workflow_state.value if campaign.workflow_state else "basic_setup",
            
            # JSONB fields with serialization
            "keywords": self._serialize_enum_field(campaign.keywords),
            "target_audience": self._serialize_enum_field(campaign.target_audience),
            "settings": self._serialize_enum_field(campaign.settings),
            "step_states": self._serialize_enum_field(campaign.step_states),
            "current_session": self._serialize_enum_field(campaign.current_session),
            "content": self._serialize_enum_field(campaign.content),
            
            # Progress data
            "sources_count": campaign.sources_count or 0,
            "intelligence_count": campaign.intelligence_extracted or 0,
            "content_count": campaign.content_generated or 0,
        }
    
    def _serialize_company_data(self, company) -> Dict[str, Any]:
        """
        Serialize a Company object with all JSONB fields
        """
        if not company:
            return {}
        
        return {
            "id": str(company.id),
            "company_name": company.company_name,
            "company_slug": company.company_slug,
            "subscription_tier": company.subscription_tier,
            
            # JSONB fields with serialization
            "brand_colors": self._serialize_enum_field(company.brand_colors),
            "brand_guidelines": self._serialize_enum_field(company.brand_guidelines),
            "settings": self._serialize_enum_field(company.settings),
        }