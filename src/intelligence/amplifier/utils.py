# ------------ utils.py ------------
def summarize_analysis(analyses):
    return {
        "total": len(analyses),
        "successful": len([a for a in analyses if "error" not in a])
    }

def merge_intelligence(existing, amplified):
    merged = existing.copy()
    for key in amplified:
        if isinstance(amplified[key], list):
            merged[key] = merged.get(key, []) + amplified[key]
        elif isinstance(amplified[key], dict):
            merged[key] = merge_intelligence(merged.get(key, {}), amplified[key])
        else:
            merged[key] = amplified[key]
    return merged