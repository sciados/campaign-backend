FROM campaign_intelligence 

WHERE campaign_intelligence.id = $1::UUID

2025-07-03 18:47:15,045 INFO sqlalchemy.engine.Engine [generated in 0.00019s] (UUID('11e44d6b-c38e-41c1-ac96-799e7f96d732'),)

INFO:sqlalchemy.engine.Engine:[generated in 0.00019s] (UUID('11e44d6b-c38e-41c1-ac96-799e7f96d732'),)

INFO:src.intelligence.handlers.analysis_handler:✅ Created intelligence record: 11e44d6b-c38e-41c1-ac96-799e7f96d732

INFO:src.intelligence.utils.analyzer_factory:✅ SUCCESS: All intelligence analyzers imported successfully via lazy loading

🤖 Initializing ULTRA-CHEAP AI provider system...

INFO:src.intelligence.analyzers:🤖 Starting ULTRA-CHEAP AI provider initialization

✅ Primary ultra-cheap provider: groq

💰 Cost: $0.00020/1K tokens

💎 SAVINGS: 99.3% vs OpenAI!

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.analyzers:✅ Ultra-cheap AI system initialized with 3 providers

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.analyzers:✅ Product extractor initialized

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.handlers.analysis_handler:🔧 Using analyzer: SalesPageAnalyzer

INFO:src.intelligence.amplifier.enhancement:✅ Scientific enhancement module initialized

INFO:src.intelligence.analyzers:Starting COMPREHENSIVE analysis for URL: https://www.hepatoburn.com/

INFO:src.intelligence.analyzers:Successfully fetched 130982 characters from https://www.hepatoburn.com/

INFO:src.intelligence.amplifier.enhancements.market_enhancer:✅ Selected ultra-cheap provider for market enhancement:

INFO:src.intelligence.analyzers:Extracted 9753 characters of clean text

INFO:src.intelligence.amplifier.enhancements.market_enhancer:   Provider: groq

INFO:src.intelligence.analyzers:Page scraping completed successfully

INFO:src.intelligence.amplifier.enhancements.market_enhancer:   Cost: $0.00020/1K tokens

INFO:src.intelligence.analyzers:Content structure extraction completed

INFO:src.intelligence.amplifier.enhancements.market_enhancer:   Quality: 78.0/100

INFO:src.intelligence.extractors.product_extractor:🔍 Starting product name extraction...

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:   Provider: groq

INFO:src.intelligence.amplifier.enhancements.market_enhancer:   Priority: 1

INFO:src.intelligence.extractors.product_extractor:🎯 Product name extraction result: 'Your'

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:   Cost: $0.00020/1K tokens

INFO:src.intelligence.analyzers:✅ Advanced extraction successful: 'Your'

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:   Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:   Priority: 1

INFO:src.intelligence.analyzers:🎯 Product name extracted: 'Your'

INFO:src.intelligence.analyzers:🚀 Starting ULTRA-CHEAP intelligence extraction...

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:🚀 Credibility Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.analyzers:🤖 Using ultra-cheap provider: groq ($0.00020/1K tokens)

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.analyzers:💰 Making ultra-cheap AI request...

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.utils.tiered_ai_provider:🤖 Using groq (free tier) - $0.0001

INFO:src.intelligence.amplifier.enhancement:✅ Credibility enhancement module initialized

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 200 OK"

INFO:src.intelligence.amplifier.enhancements.content_enhancer:✅ Selected ultra-cheap provider for content enhancement:

INFO:src.intelligence.analyzers:✅ Intelligence extraction completed!

INFO:src.intelligence.amplifier.enhancements.content_enhancer:   Provider: groq

INFO:src.intelligence.analyzers:💰 Cost: $0.00011 (saved $0.00214 vs OpenAI)

INFO:src.intelligence.amplifier.enhancements.content_enhancer:   Cost: $0.00020/1K tokens

INFO:src.intelligence.analyzers:🤖 Provider: groq

INFO:src.intelligence.amplifier.enhancements.content_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.amplifier.enhancements.content_enhancer:   Quality: 78.0/100

INFO:src.intelligence.analyzers:📊 Confidence calculation: base=0.71, final=0.71 (71.0%)

INFO:src.intelligence.amplifier.enhancements.content_enhancer:   Priority: 1

INFO:src.intelligence.amplifier.enhancements.content_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.handlers.analysis_handler:📊 Base analysis completed with confidence: 0.7100000000000001

INFO:src.intelligence.amplifier.enhancements.content_enhancer:🚀 Content Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.amplifier.enhancements.content_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.handlers.analysis_handler:🚀 Starting intelligence amplification...

INFO:src.intelligence.handlers.analysis_handler:💰 ULTRA-CHEAP AI AMPLIFICATION:

INFO:src.intelligence.amplifier.enhancement:✅ Content enhancement module initialized

INFO:src.intelligence.handlers.analysis_handler:   Primary provider: groq

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:✅ Selected ultra-cheap provider for emotional enhancement:

INFO:src.intelligence.handlers.analysis_handler:   Cost: $0.00020/1K tokens

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:   Provider: groq

INFO:src.intelligence.handlers.analysis_handler:   Available providers: 3

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:   Cost: $0.00020/1K tokens

INFO:src.intelligence.handlers.analysis_handler:   💎 SAVINGS: 99.3% vs OpenAI

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:   Quality: 78.0/100

INFO:src.intelligence.handlers.analysis_handler:   Provider priority: ['groq', 'together', 'deepseek']

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:   Priority: 1

INFO:src.intelligence.handlers.analysis_handler:💰 AMPLIFICATION using ULTRA-CHEAP providers: ['groq', 'together', 'deepseek']

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:🚀 Emotional Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.handlers.analysis_handler:✅ ULTRA-CHEAP optimization confirmed: groq is primary provider

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.handlers.analysis_handler:🔍 Identifying enhancement opportunities...

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancement:🔍 Identifying enhancement opportunities with modular AI system...

INFO:src.intelligence.amplifier.enhancements.market_enhancer:🚀 Market Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:✅ Selected ultra-cheap provider for scientific enhancement:

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.amplifier.enhancements.market_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:   Provider: groq

INFO:src.intelligence.amplifier.enhancement:✅ Emotional enhancement module initialized

INFO:src.intelligence.amplifier.enhancements.market_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:   Cost: $0.00020/1K tokens

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:✅ Selected ultra-cheap provider for authority enhancement:

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:   Provider: groq

INFO:src.intelligence.amplifier.enhancements.market_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:   Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancement:✅ Market enhancement module initialized

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:   Cost: $0.00020/1K tokens

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:   Priority: 1

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:✅ Selected ultra-cheap provider for credibility enhancement:

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:🚀 Scientific Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:   Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:   Priority: 1

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:🚀 Authority Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.amplifier.enhancement:✅ Authority enhancement module initialized

INFO:src.intelligence.amplifier.enhancement:🚀 Initialized 6 enhancement modules

INFO:src.intelligence.amplifier.enhancement:⚡ Running opportunity identification across all AI modules...

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:✅ Selected ultra-cheap provider for scientific enhancement:

INFO:src.intelligence.amplifier.enhancement:✅ Identified 30 opportunities across all AI modules

INFO:src.intelligence.handlers.analysis_handler:✅ Identified 30 enhancement opportunities

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:   Provider: groq

INFO:src.intelligence.handlers.analysis_handler:🚀 Generating AI-powered enhancements...

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:   Cost: $0.00020/1K tokens

INFO:src.intelligence.amplifier.enhancement:🚀 Generating AI-powered enhancements with modular system...

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:   Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:   Priority: 1

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:🚀 Scientific Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.amplifier.enhancement:✅ Scientific enhancement module initialized

INFO:src.intelligence.amplifier.enhancements.market_enhancer:✅ Selected ultra-cheap provider for market enhancement:

INFO:src.intelligence.amplifier.enhancements.market_enhancer:   Provider: groq

INFO:src.intelligence.amplifier.enhancements.market_enhancer:   Cost: $0.00020/1K tokens

INFO:src.intelligence.amplifier.enhancements.market_enhancer:   Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.market_enhancer:   Priority: 1

INFO:src.intelligence.amplifier.enhancements.market_enhancer:🚀 Market Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.amplifier.enhancements.market_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.amplifier.enhancements.market_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.market_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.amplifier.enhancement:✅ Market enhancement module initialized

ERROR:src.intelligence.amplifier.enhancements.content_enhancer:❌ Social proof amplification failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:✅ Selected ultra-cheap provider for credibility enhancement:

INFO:src.intelligence.amplifier.enhancements.content_enhancer:📖 Generating success story frameworks with groq

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:   Provider: groq

INFO:src.intelligence.amplifier.enhancements.content_enhancer:💰 AI Call: groq | ~78 tokens | ~$0.000016

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:   Cost: $0.00020/1K tokens

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:🔬 Generating clinical evidence with groq

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:   Quality: 78.0/100

ERROR:src.intelligence.amplifier.enhancements.credibility_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:   Priority: 1

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:💰 AI Call: groq | ~104 tokens | ~$0.000021

ERROR:src.intelligence.amplifier.enhancements.credibility_enhancer:❌ Trust indicators generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:🚀 Credibility Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:👑 Generating authority signals with groq

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:💰 AI Call: groq | ~196 tokens | ~$0.000039

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:💰 AI Call: groq | ~187 tokens | ~$0.000037

ERROR:src.intelligence.amplifier.enhancements.emotional_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.amplifier.enhancement:✅ Credibility enhancement module initialized

ERROR:src.intelligence.amplifier.enhancements.emotional_enhancer:❌ Psychological triggers generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

ERROR:src.intelligence.amplifier.enhancements.scientific_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancements.content_enhancer:✅ Selected ultra-cheap provider for content enhancement:

ERROR:src.intelligence.amplifier.enhancements.scientific_enhancer:❌ Clinical evidence generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:💝 Generating emotional value propositions with groq

ERROR:src.intelligence.amplifier.enhancements.credibility_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancements.content_enhancer:   Provider: groq

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:🛡️ Generating safety profile with groq

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:💰 AI Call: groq | ~86 tokens | ~$0.000017

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:💰 AI Call: groq | ~94 tokens | ~$0.000019

INFO:src.intelligence.amplifier.enhancements.content_enhancer:   Cost: $0.00020/1K tokens

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

ERROR:src.intelligence.amplifier.enhancements.credibility_enhancer:❌ Expertise indicators generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.amplifier.enhancements.content_enhancer:   Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:✅ Credibility intelligence generated using groq

INFO:src.intelligence.amplifier.enhancements.content_enhancer:   Priority: 1

ERROR:src.intelligence.amplifier.enhancements.authority_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.handlers.analysis_handler:✅ Generated 51 enhancements with 25.0% confidence boost

ERROR:src.intelligence.amplifier.enhancements.content_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:📊 Generated 41 credibility items

INFO:src.intelligence.amplifier.enhancements.content_enhancer:🚀 Content Enhancer using ULTRA-CHEAP provider: groq

ERROR:src.intelligence.amplifier.enhancements.authority_enhancer:❌ Professional authority markers generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.handlers.analysis_handler:✨ Creating enriched intelligence...

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:💰 Cost optimization: 99.3% savings

INFO:src.intelligence.amplifier.enhancements.content_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:🎯 Generating expertise demonstration with groq

ERROR:src.intelligence.amplifier.enhancement:❌ Enhancement module 1 failed: 'MarketIntelligenceEnhancer' object has no attribute '_generate_fallback_market_intelligence'

INFO:src.intelligence.amplifier.enhancement:✨ Creating enriched intelligence with modular AI system...

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:💰 AI Call: groq | ~81 tokens | ~$0.000016

INFO:src.intelligence.amplifier.enhancements.content_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancement:✅ Generated 51 enhancements across 5 modules - Confidence boost: 25.0%

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.amplifier.enhancement:📊 INPUT - Base intel keys: ['offer_intelligence', 'psychology_intelligence', 'competitive_intelligence', 'content_intelligence', 'brand_intelligence', 'source_url', 'page_title', 'product_name', 'analysis_timestamp', 'confidence_score', 'raw_content', 'ultra_cheap_analysis']

INFO:src.intelligence.amplifier.enhancements.content_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.amplifier.enhancement:🔍 Enhancement 'research_support': Type=<class 'dict'>, Length=0

INFO:src.intelligence.amplifier.enhancement:✅ Content enhancement module initialized

ERROR:src.intelligence.amplifier.enhancements.emotional_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancement:📊 INPUT - Enhancements keys: ['scientific_validation', 'credibility_boosters', 'competitive_advantages', 'research_support', 'market_positioning', 'content_optimization', 'emotional_transformation', 'authority_establishment', 'enhancement_metadata']

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:✅ Selected ultra-cheap provider for emotional enhancement:

INFO:src.intelligence.amplifier.enhancement:🔍 Enhancement 'market_positioning': Type=<class 'dict'>, Length=0

INFO:src.intelligence.amplifier.enhancement:🔍 Enhancement 'scientific_validation': Type=<class 'dict'>, Length=10

ERROR:src.intelligence.amplifier.enhancements.emotional_enhancer:❌ Emotional value propositions generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:   Provider: groq

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:📖 Generating transformation narratives with groq

INFO:src.intelligence.amplifier.enhancement:🔍 Enhancement 'content_optimization': Type=<class 'dict'>, Length=10

INFO:src.intelligence.amplifier.enhancement:   └── Sample keys: ['scientific_backing', 'ingredient_research', 'mechanism_of_action', 'clinical_evidence', 'safety_profile']

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:   Cost: $0.00020/1K tokens

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:💰 AI Call: groq | ~79 tokens | ~$0.000016

INFO:src.intelligence.amplifier.enhancement:🔍 Enhancement 'credibility_boosters': Type=<class 'dict'>, Length=11

INFO:src.intelligence.amplifier.enhancement:   └── Sample keys: ['enhanced_key_messages', 'social_proof_amplification', 'success_story_frameworks', 'messaging_hierarchy', 'engagement_optimization']

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:   Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancement:   └── Sample keys: ['trust_indicators', 'authority_signals', 'social_proof_enhancement', 'credibility_scoring', 'reputation_factors']

INFO:src.intelligence.amplifier.enhancement:🔍 Enhancement 'emotional_transformation': Type=<class 'dict'>, Length=10

ERROR:src.intelligence.amplifier.enhancements.content_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancement:🔍 Enhancement 'competitive_advantages': Type=<class 'dict'>, Length=0

INFO:src.intelligence.amplifier.enhancement:   └── Sample keys: ['emotional_journey_mapping', 'psychological_triggers', 'emotional_value_propositions', 'transformation_narratives', 'emotional_engagement_strategies']

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:   Priority: 1

ERROR:src.intelligence.amplifier.enhancements.content_enhancer:❌ Success story frameworks generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancement:🏆 Credibility enhancement received: <class 'dict'>, 11

INFO:src.intelligence.amplifier.enhancement:🔍 Enhancement 'authority_establishment': Type=<class 'dict'>, Length=10

INFO:src.intelligence.amplifier.enhancements.content_enhancer:🏗️ Generating messaging hierarchy with groq

INFO:src.intelligence.amplifier.enhancement:✅ MAPPED credibility_intelligence: 11 items

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:🚀 Emotional Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.amplifier.enhancement:   └── Sample keys: ['research_validation_framework', 'professional_authority_markers', 'expertise_demonstration', 'thought_leadership_positioning', 'scientific_credibility_framework']

INFO:src.intelligence.amplifier.enhancements.content_enhancer:💰 AI Call: groq | ~174 tokens | ~$0.000035

INFO:src.intelligence.amplifier.enhancement:💭 Emotional enhancement received: <class 'dict'>, 10

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.amplifier.enhancement:🔬 Scientific enhancement received: <class 'dict'>, 10

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.amplifier.enhancement:✅ MAPPED emotional_transformation_intelligence: 10 items

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancement:🎓 Authority enhancement received: <class 'dict'>, 10

ERROR:src.intelligence.amplifier.enhancements.scientific_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.amplifier.enhancement:✅ MAPPED scientific_authority_intelligence: 10 items

INFO:src.intelligence.amplifier.enhancement:✅ Emotional enhancement module initialized

ERROR:src.intelligence.amplifier.enhancements.scientific_enhancer:❌ Safety profile generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancement:📝 Content enhancement received: <class 'dict'>, 10

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:✅ Scientific intelligence generated using groq

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:✅ Selected ultra-cheap provider for authority enhancement:

INFO:src.intelligence.amplifier.enhancement:✅ ENHANCED content_intelligence: 10 new items

INFO:src.intelligence.amplifier.enhancement:✅ MAPPED scientific_intelligence: 10 items

INFO:src.intelligence.amplifier.enhancement:🗺️ MAPPING RESULTS:

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:📊 Generated 18 intelligence items

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:   Provider: groq

INFO:src.intelligence.amplifier.enhancement:📈 Market enhancement received: <class 'dict'>, 0

INFO:src.intelligence.amplifier.enhancement:   scientific_intelligence: ✅ HAS DATA (11 items)

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:   Cost: $0.00020/1K tokens

WARNING:src.intelligence.amplifier.enhancement:⚠️ Market enhancement is empty or None: {}

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:💰 Cost optimization: 99.3% savings

INFO:src.intelligence.amplifier.enhancement:🔥 ADDED credibility_intelligence to enriched data with 12 items

INFO:src.intelligence.amplifier.enhancement:   credibility_intelligence: ✅ HAS DATA (12 items)

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:   Quality: 78.0/100

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.amplifier.enhancement:   emotional_transformation_intelligence: ✅ HAS DATA (11 items)

INFO:src.intelligence.amplifier.enhancement:🔥 ADDED emotional_transformation_intelligence to enriched data with 11 items

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:   Priority: 1

ERROR:src.intelligence.amplifier.enhancements.credibility_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancement:   scientific_authority_intelligence: ✅ HAS DATA (11 items)

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:🚀 Authority Enhancer using ULTRA-CHEAP provider: groq

INFO:src.intelligence.amplifier.enhancement:🔥 ADDED scientific_authority_intelligence to enriched data with 11 items

INFO:src.intelligence.amplifier.enhancement:   content_intelligence: ✅ HAS DATA (16 items)

ERROR:src.intelligence.amplifier.enhancements.credibility_enhancer:❌ Authority signals generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:💰 Cost: $0.00020/1K tokens (vs $0.030 OpenAI)

INFO:src.intelligence.amplifier.enhancement:🔥 ADDED content_intelligence to enriched data with 16 items

INFO:src.intelligence.amplifier.enhancement:🔥 ADDED scientific_intelligence to enriched data with 11 items

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:👥 Generating social proof enhancement with groq

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:🎯 Quality: 78.0/100

INFO:src.intelligence.amplifier.enhancement:📊 Final confidence: 0.71 → 0.96 (+0.25)

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:💰 AI Call: groq | ~108 tokens | ~$0.000022

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:💎 SAVINGS: 99.3% cost reduction!

INFO:src.intelligence.amplifier.enhancement:📤 OUTPUT - Enriched data keys: ['offer_intelligence', 'psychology_intelligence', 'competitive_intelligence', 'content_intelligence', 'brand_intelligence', 'source_url', 'page_title', 'product_name', 'analysis_timestamp', 'confidence_score', 'raw_content', 'ultra_cheap_analysis', 'scientific_intelligence', 'credibility_intelligence', 'emotional_transformation_intelligence', 'scientific_authority_intelligence']

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.handlers.analysis_handler:🔍 POST-AMPLIFICATION DIAGNOSIS

INFO:src.intelligence.amplifier.enhancement:✅ Authority enhancement module initialized

INFO:src.intelligence.amplifier.enhancement:📤 OUTPUT - Categories added: 5/6

INFO:src.intelligence.handlers.analysis_handler:🔍 AMPLIFICATION OUTPUT DIAGNOSIS

ERROR:src.intelligence.amplifier.enhancements.emotional_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancement:🚀 Initialized 6 enhancement modules

INFO:src.intelligence.handlers.analysis_handler:==================================================

INFO:src.intelligence.amplifier.enhancement:✅ scientific_intelligence is in enriched data: 11 items

INFO:src.intelligence.amplifier.enhancement:⚡ Running all AI enhancement modules in parallel...

ERROR:src.intelligence.amplifier.enhancements.emotional_enhancer:❌ Transformation narratives generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:🤝 Generating emotional engagement with groq

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:🧬 Starting scientific intelligence generation with groq

INFO:src.intelligence.amplifier.enhancement:✅ credibility_intelligence is in enriched data: 12 items

INFO:src.intelligence.amplifier.enhancements.emotional_enhancer:💰 AI Call: groq | ~79 tokens | ~$0.000016

ERROR:src.intelligence.amplifier.enhancement:❌ market_intelligence is MISSING from enriched data

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:🧬 Generating scientific backing with groq

INFO:src.intelligence.handlers.analysis_handler:     Sample: emotional_journey_mapping = {'current_emotional_state': ['Frustrated with current health situation', 'Skepti...

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.amplifier.enhancement:✅ emotional_transformation_intelligence is in enriched data: 11 items

INFO:src.intelligence.handlers.analysis_handler:Top-level keys: ['offer_intelligence', 'psychology_intelligence', 'competitive_intelligence', 'content_intelligence', 'brand_intelligence', 'source_url', 'page_title', 'product_name', 'analysis_timestamp', 'confidence_score', 'raw_content', 'ultra_cheap_analysis', 'scientific_intelligence', 'credibility_intelligence', 'emotional_transformation_intelligence', 'scientific_authority_intelligence', 'enrichment_metadata']

INFO:src.intelligence.amplifier.enhancements.scientific_enhancer:💰 AI Call: groq | ~130 tokens | ~$0.000026

INFO:src.intelligence.amplifier.enhancement:✅ scientific_authority_intelligence is in enriched data: 11 items

ERROR:src.intelligence.amplifier.enhancements.authority_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.handlers.analysis_handler:  ✅ scientific_authority_intelligence: <class 'dict'> - 11

INFO:src.intelligence.amplifier.enhancements.market_enhancer:📈 Starting market intelligence generation with groq

INFO:src.intelligence.handlers.analysis_handler:📊 AI Intelligence Categories:

INFO:src.intelligence.amplifier.enhancement:✅ Enriched intelligence created - Categories populated: 5/6

INFO:src.intelligence.handlers.analysis_handler:     Sample: research_validation_framework = {'methodology_standards': ['Rigorous scientific methodology application', 'Evide...

ERROR:src.intelligence.amplifier.enhancements.market_enhancer:❌ Ultra-cheap market intelligence generation failed: 'MarketIntelligenceEnhancer' object has no attribute '_generate_market_analysis'

ERROR:src.intelligence.amplifier.enhancements.authority_enhancer:❌ Expertise demonstration generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.handlers.analysis_handler:  ✅ scientific_intelligence: <class 'dict'> - 11

INFO:src.intelligence.handlers.analysis_handler:==================================================

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:💡 Generating thought leadership with groq

INFO:src.intelligence.amplifier.enhancements.market_enhancer:🔄 Falling back to static market intelligence

INFO:src.intelligence.handlers.analysis_handler:     Sample: scientific_backing = ['Research indicates that natural compounds may support overall health and welln...

INFO:src.intelligence.handlers.analysis_handler:✅ Amplification completed successfully - Final confidence: 0.96

INFO:src.intelligence.amplifier.enhancements.authority_enhancer:💰 AI Call: groq | ~86 tokens | ~$0.000017

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:🏆 Starting credibility intelligence generation with groq

INFO:src.intelligence.utils.ai_intelligence_saver:🔄 Saving credibility_intelligence with 12 items

INFO:src.intelligence.handlers.analysis_handler:  ✅ credibility_intelligence: <class 'dict'> - 12

INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"

INFO:src.intelligence.handlers.analysis_handler:💰 Ultra-cheap optimization status: Primary provider = groq

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:🔒 Generating trust indicators with groq

INFO:src.intelligence.handlers.analysis_handler:     Sample: trust_indicators = {'trust_building_elements': ['Money-back satisfaction guarantee', 'Transparent i...

INFO:src.intelligence.utils.ai_intelligence_saver:🔧 Attempting Strategy 1: Orm Setattr

ERROR:src.intelligence.amplifier.enhancements.content_enhancer:❌ Ultra-cheap AI call failed for groq: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.handlers.analysis_handler:🔄 About to store analysis results...

INFO:src.intelligence.amplifier.enhancements.credibility_enhancer:💰 AI Call: groq | ~105 tokens | ~$0.000021

INFO:src.intelligence.handlers.analysis_handler:  ❌ market_intelligence: MISSING

INFO:src.intelligence.utils.ai_intelligence_saver:✅ ORM setattr: credibility_intelligence set on object

INFO:src.intelligence.handlers.analysis_handler:✅ Base intelligence stored successfully

INFO:src.intelligence.amplifier.enhancements.content_enhancer:📝 Starting content intelligence generation with groq

INFO:src.intelligence.handlers.analysis_handler:  ✅ emotional_transformation_intelligence: <class 'dict'> - 11

ERROR:src.intelligence.amplifier.enhancements.content_enhancer:❌ Messaging hierarchy generation failed: Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}

INFO:src.intelligence.utils.ai_intelligence_saver:✅ credibility_intelligence: Successfully saved via Orm Setattr

INFO:src.intelligence.handlers.analysis_handler:🔧 Using simplified approach: size=18.0KB