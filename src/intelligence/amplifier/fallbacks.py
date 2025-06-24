# ------------ fallbacks.py ------------
def fallback_url_analysis(source):
    return {
        "fallback": True,
        "source": source,
        "analysis": {
            "product_mentions": ["ExampleProduct"],
            "benefit_keywords": ["improve", "boost"],
            "emotional_words": ["amazing"],
            "urgency_indicators": ["limited time"]
        }
    }

def fallback_video_analysis(source):
    return {
        "fallback": True,
        "source": source,
        "analysis": {
            "key_phrases": ["This works!"],
            "claims_mentioned": ["guaranteed to help"],
            "emotional_language": ["powerful"]
        }
    }

def fallback_document_analysis(source):
    return {
        "fallback": True,
        "source": source,
        "analysis": {
            "main_topics": ["productivity", "workflow"],
            "data_points": ["30% faster"],
            "references": ["https://example.com"]
        }
    }