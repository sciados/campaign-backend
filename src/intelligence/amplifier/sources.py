# ------------ sources.py ------------
from .fallbacks import fallback_url_analysis, fallback_video_analysis, fallback_document_analysis

async def analyze_sources(sources, providers):
    results = []
    for source in sources:
        if source["type"] == "url":
            result = await _analyze_url_source(source, providers)
        elif source["type"] == "video":
            result = await _analyze_video_source(source, providers)
        elif source["type"] == "document":
            result = await _analyze_document_source(source, providers)
        else:
            result = {"error": "Unsupported source type", "type": source["type"]}
        results.append(result)
    return results

async def _analyze_url_source(source, providers):
    for provider in providers:
        try:
            return {"provider": provider["name"], "analysis": "url content analyzed"}
        except Exception:
            continue
    return fallback_url_analysis(source)

async def _analyze_video_source(source, providers):
    return fallback_video_analysis(source)

async def _analyze_document_source(source, providers):
    return fallback_document_analysis(source)
