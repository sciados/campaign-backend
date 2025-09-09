"""
Intelligence Enhancement System
Amplifies intelligence data with additional insights and optimizations.

FIXED: Added enum serialization support and safe data handling
"""

import logging
from typing import Dict, Any, List, Optional

# 🔧 CRITICAL FIX: JSON serialization helper for datetime objects
from src.utils.json_utils import safe_json_dumps


logger = logging.getLogger(__name__)

class IntelligenceEnhancer:
    """
    Enhances intelligence data with advanced insights
    
    FIXED: Now includes enum-safe data handling and serialization support
    """
    
    def __init__(self):
        self.enhancement_strategies = {
            'scientific_backing': self._enhance_scientific_backing,
            'emotional_triggers': self._enhance_emotional_triggers,
            'trust_signals': self._enhance_trust_signals,
            'urgency_elements': self._enhance_urgency_elements,
            'conversion_psychology': self._enhance_conversion_psychology
        }
    
    def _serialize_enum_field(self, enum_value: Any) -> Dict[str, Any]:
        """
        Helper method to safely serialize enum fields from intelligence data
        
        Args:
            enum_value: The enum field value (could be string, dict, or actual enum)
            
        Returns:
            Dict containing the serialized enum data
        """
        if enum_value is None:
            return {}
        
        # If it's already a dictionary (serialized), return as-is
        if isinstance(enum_value, dict):
            return enum_value
        
        # If it's a string, try to parse as JSON
        if isinstance(enum_value, str):
            try:
                import json
                return json.loads(enum_value)
            except (json.JSONDecodeError, ValueError):
                logger.warning(f"Could not parse enum field as JSON: {enum_value}")
                return {}
        
        # If it has a .value attribute (actual enum), try to access it
        if hasattr(enum_value, 'value'):
            try:
                return enum_value.value if isinstance(enum_value.value, dict) else {}
            except:
                logger.warning(f"Could not access enum value: {enum_value}")
                return {}
        
        # Fallback: try to convert to dict
        try:
            return dict(enum_value) if enum_value else {}
        except:
            logger.warning(f"Could not convert enum field to dict: {enum_value}")
            return {}

    def _serialize_enum_field_for_output(self, data: Dict[str, Any]) -> str:
        """
        Convert dictionary back to JSON string for database storage
        
        Args:
            data: Dictionary to serialize
            
        Returns:
            JSON string representation
        """
        try:
            import json
            return safe_json_dumps(data)
        except:
            logger.warning(f"Could not serialize data to JSON: {data}")
            return "{}"
    
    def enhance_intelligence(
        self, 
        base_intelligence: Dict[str, Any], 
        niche_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance intelligence with advanced insights"""
        
        # FIXED: Create a deep copy to avoid modifying original data
        enhanced = self._deep_copy_intelligence(base_intelligence)
        
        # Apply each enhancement strategy
        for strategy_name, enhancement_func in self.enhancement_strategies.items():
            try:
                enhanced = enhancement_func(enhanced, niche_context)
            except Exception as e:
                logger.warning(f"Enhancement strategy {strategy_name} failed: {str(e)}")
        
        enhanced['amplified_intelligence'] = True
        enhanced['enhancement_score'] = self._calculate_enhancement_score(enhanced)
        
        return enhanced
    
    def _deep_copy_intelligence(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deep copy of intelligence data with enum field serialization
        
        Args:
            intelligence_data: Original intelligence data
            
        Returns:
            Deep copy with properly serialized enum fields
        """
        import copy
        
        # Create base copy
        enhanced = copy.deepcopy(intelligence_data)
        
        # Enum fields that need special handling
        enum_fields = [
            'scientific_authority_intelligence',
            'credibility_intelligence', 
            'market_intelligence',
            'emotional_transformation_intelligence',
            'offer_intelligence',
            'psychology_intelligence',
            'content_intelligence',
            'competitive_intelligence',
            'brand_intelligence',
            'processing_metadata'
        ]
        
        # Ensure enum fields are properly serialized as dictionaries
        for field in enum_fields:
            if field in enhanced:
                enhanced[field] = self._serialize_enum_field(enhanced[field])
        
        return enhanced
    
    def _enhance_scientific_backing(
        self, 
        intelligence: Dict[str, Any], 
        niche_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance with scientific backing and credibility"""
        
        # FIXED: Safe access to scientific intelligence enum field
        if 'scientific_authority_intelligence' not in intelligence:
            intelligence['scientific_authority_intelligence'] = {}
        
        scientific_intel = intelligence['scientific_authority_intelligence']
        
        # Ensure it's a dictionary (handle enum serialization)
        if not isinstance(scientific_intel, dict):
            scientific_intel = self._serialize_enum_field(scientific_intel)
            intelligence['scientific_authority_intelligence'] = scientific_intel
        
        # Add clinical studies if not present
        if 'clinical_studies' not in scientific_intel:
            scientific_intel['clinical_studies'] = [
                'Peer-reviewed research',
                'Clinical trial validation',
                'Laboratory testing'
            ]
        
        # Add credibility markers
        if 'credibility_markers' not in scientific_intel:
            scientific_intel['credibility_markers'] = [
                'Expert endorsements',
                'Scientific validation',
                'Research-backed claims'
            ]
        
        return intelligence
    
    def _enhance_emotional_triggers(
        self, 
        intelligence: Dict[str, Any], 
        niche_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance with emotional triggers and transformation elements"""
        
        # FIXED: Safe access to emotional intelligence enum field
        if 'emotional_transformation_intelligence' not in intelligence:
            intelligence['emotional_transformation_intelligence'] = {}
        
        emotional_intel = intelligence['emotional_transformation_intelligence']
        
        # Ensure it's a dictionary (handle enum serialization)
        if not isinstance(emotional_intel, dict):
            emotional_intel = self._serialize_enum_field(emotional_intel)
            intelligence['emotional_transformation_intelligence'] = emotional_intel
        
        # Add transformation promises
        if 'transformation_promises' not in emotional_intel:
            emotional_intel['transformation_promises'] = [
                'Life-changing results',
                'Complete transformation',
                'Breakthrough success'
            ]
        
        # Add emotional hooks
        if 'emotional_hooks' not in emotional_intel:
            emotional_intel['emotional_hooks'] = [
                'Finally achieve your goals',
                'Stop struggling with...',
                'Discover the secret to...'
            ]
        
        return intelligence
    
    def _enhance_trust_signals(
        self, 
        intelligence: Dict[str, Any], 
        niche_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance with trust signals and social proof"""
        
        if 'trust_signals' not in intelligence:
            intelligence['trust_signals'] = []
        
        # Add niche-specific trust elements
        trust_elements = niche_context.get('trust_elements', [])
        for element in trust_elements:
            if element not in intelligence['trust_signals']:
                intelligence['trust_signals'].append(element)
        
        # Ensure minimum trust signals
        default_trust = [
            'Money-back guarantee',
            'Secure checkout',
            'Privacy protected',
            'Award-winning support'
        ]
        
        for signal in default_trust:
            if signal not in intelligence['trust_signals']:
                intelligence['trust_signals'].append(signal)
        
        return intelligence
    
    def _enhance_urgency_elements(
        self, 
        intelligence: Dict[str, Any], 
        niche_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance with urgency and scarcity elements"""
        
        if 'urgency_elements' not in intelligence:
            intelligence['urgency_elements'] = []
        
        # Add niche-specific urgency triggers
        urgency_triggers = niche_context.get('urgency_triggers', [])
        for trigger in urgency_triggers:
            if trigger not in intelligence['urgency_elements']:
                intelligence['urgency_elements'].append(trigger)
        
        return intelligence
    
    def _enhance_conversion_psychology(
        self, 
        intelligence: Dict[str, Any], 
        niche_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance with conversion psychology principles"""
        
        if 'conversion_psychology' not in intelligence:
            intelligence['conversion_psychology'] = {}
        
        psychology = intelligence['conversion_psychology']
        
        # Add psychological triggers
        if 'psychological_triggers' not in psychology:
            psychology['psychological_triggers'] = [
                'Social proof',
                'Authority',
                'Scarcity',
                'Reciprocity',
                'Commitment'
            ]
        
        # Add persuasion elements
        if 'persuasion_elements' not in psychology:
            psychology['persuasion_elements'] = [
                'Problem agitation',
                'Solution revelation',
                'Benefit amplification',
                'Risk reversal'
            ]
        
        return intelligence
    
    def _calculate_enhancement_score(self, intelligence: Dict[str, Any]) -> float:
        """Calculate overall enhancement score"""
        
        score = 0.0
        max_score = 100.0
        
        # Score based on intelligence completeness
        if intelligence.get('scientific_authority_intelligence'):
            score += 20
        if intelligence.get('emotional_transformation_intelligence'):
            score += 20
        if intelligence.get('trust_signals'):
            score += 15
        if intelligence.get('urgency_elements'):
            score += 15
        if intelligence.get('conversion_psychology'):
            score += 20
        if intelligence.get('amplified_intelligence'):
            score += 10
        
        return min(score, max_score)
    
    def prepare_for_database_storage(self, enhanced_intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare enhanced intelligence data for database storage
        
        Converts dictionary enum fields back to JSON strings for database compatibility
        
        Args:
            enhanced_intelligence:  intelligence data with dict enum fields
            
        Returns:
            Intelligence data ready for database storage
        """
        storage_ready = enhanced_intelligence.copy()
        
        # Enum fields that need to be converted back to JSON strings
        enum_fields = [
            'scientific_authority_intelligence',
            'credibility_intelligence', 
            'market_intelligence',
            'emotional_transformation_intelligence',
            'offer_intelligence',
            'psychology_intelligence',
            'content_intelligence',
            'competitive_intelligence',
            'brand_intelligence',
            'processing_metadata'
        ]
        
        # Convert enum fields back to JSON strings for database storage
        for field in enum_fields:
            if field in storage_ready and isinstance(storage_ready[field], dict):
                storage_ready[field] = self._serialize_enum_field_for_output(storage_ready[field])
        
        return storage_ready