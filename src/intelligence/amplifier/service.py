# ------------ service.py ------------
from .core import IntelligenceAmplifier

class IntelligenceAmplificationService:
    def __init__(self):
        self.amplifier = IntelligenceAmplifier()

    async def process_sources(self, sources, preferences={}):
        result = await self.amplifier.amplify_intelligence(sources, preferences)
        enriched = result.get("enriched_intelligence", {})
        enriched["confidence_score"] = result["summary"].get("successful", 0) / max(result["summary"].get("total", 1), 1)
        return {
            "intelligence_data": enriched,
            "summary": result["summary"]
        }