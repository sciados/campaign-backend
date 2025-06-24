# ------------ ai_providers.py ------------
def initialize_ai_providers():
    import os
    import openai
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return [{"name": "openai", "client": openai.AsyncOpenAI(api_key=api_key)}]
    return []