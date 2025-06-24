# ------------ core.py ------------
from .sources import analyze_sources
from .utils import summarize_analysis, merge_intelligence
from .enhancement import identify_opportunities, generate_enhancements, create_enriched_intelligence
from .ai_providers import initialize_ai_providers

class IntelligenceAmplifier:
    def __init__(self):
        self.providers = initialize_ai_providers()

    async def amplify_intelligence(self, user_sources, preferences):
        # analysis = await analyze_sources(user_sources, self.providers)
        analysis = user_sources  # Don't await - just use the sources directly
        # summary = await summarize_analysis(analysis)
        summary = summarize_analysis(analysis)  # Remove await
        base_intel = self._extract_base_intelligence(analysis)
        opportunities = await identify_opportunities(base_intel, preferences, self.providers)
        enhancements = await generate_enhancements(base_intel, opportunities, self.providers)
        enriched = create_enriched_intelligence(base_intel, enhancements)
        return {
            "analysis": analysis,
            "summary": summary,
            "enriched_intelligence": enriched
        }

    def _extract_base_intelligence(self, analyses):
        return {"offer_intelligence": {"benefits": ["Example claim"]}}