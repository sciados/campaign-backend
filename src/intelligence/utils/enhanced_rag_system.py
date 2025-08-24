# Enhanced Intelligence RAG System for CampaignForge
# Add this to your intelligence/utils/ directory

import os
from intelligence.analyzers import SalesPageAnalyzer
import numpy as np
from typing import List, Dict, Any, Optional
import cohere
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class IntelligenceRAGSystem:
    """
    Enhanced RAG system optimized for CampaignForge intelligence gathering
    Focuses on research document analysis and competitive intelligence
    """
    
    def __init__(self):
        self.cohere_client = cohere.AsyncClient(api_key=os.getenv("COHERE_API_KEY"))
        self.document_embeddings = {}
        self.document_chunks = {}
        
    async def add_research_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None):
        """Add research document to RAG system with semantic chunking"""
        
        try:
            # Smart chunking for research content
            chunks = self._intelligent_chunk_research_content(content)
            
            # Generate embeddings using Cohere (best for research)
            embeddings = await self._generate_embeddings(chunks)
            
            # Store with metadata
            self.document_embeddings[doc_id] = embeddings
            self.document_chunks[doc_id] = {
                'chunks': chunks,
                'metadata': metadata or {},
                'content_type': self._classify_content_type(content)
            }
            
            logger.info(f"Added research document {doc_id} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add research document {doc_id}: {str(e)}")
            return False
    
    async def intelligent_research_query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Intelligent research query with context-aware retrieval
        Optimized for competitive intelligence and market research
        """
        
        try:
            # Generate query embedding
            query_embedding = await self._generate_embeddings([query])
            query_vec = query_embedding[0]
            
            # Find most relevant chunks across all documents
            relevant_chunks = []
            
            for doc_id, embeddings in self.document_embeddings.items():
                similarities = cosine_similarity([query_vec], embeddings)[0]
                doc_chunks = self.document_chunks[doc_id]['chunks']
                
                for i, similarity in enumerate(similarities):
                    if similarity > 0.7:  # Threshold for relevance
                        relevant_chunks.append({
                            'doc_id': doc_id,
                            'chunk_index': i,
                            'content': doc_chunks[i],
                            'similarity': float(similarity),
                            'metadata': self.document_chunks[doc_id]['metadata']
                        })
            
            # Sort by relevance and return top_k
            relevant_chunks.sort(key=lambda x: x['similarity'], reverse=True)
            return relevant_chunks[:top_k]
            
        except Exception as e:
            logger.error(f"Research query failed: {str(e)}")
            return []
    
    async def generate_enhanced_intelligence(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate enhanced intelligence using RAG-retrieved context
        Uses Claude for deep analysis of research materials
        """
        
        try:
            # Prepare context from retrieved chunks
            context = self._format_research_context(context_chunks)
            
            # Use Claude for deep research analysis (optimal for this task)
            enhanced_prompt = f"""
            Based on the following research context, provide comprehensive intelligence analysis:
            
            QUERY: {query}
            
            RESEARCH CONTEXT:
            {context}
            
            Provide analysis in these areas:
            1. Key Insights & Findings
            2. Competitive Intelligence
            3. Market Opportunities  
            4. Strategic Recommendations
            5. Supporting Evidence
            
            Focus on actionable intelligence for marketing campaigns.
            """
            
            # Use your existing AI provider system but specify Claude for research
            if hasattr(self, 'claude_client') and self.claude_client:
                response = await self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": enhanced_prompt}]
                )
                analysis = response.content[0].text
            else:
                # Fallback to your load balanced system
                analysis = await self._fallback_analysis(enhanced_prompt)
            
            return {
                'intelligence_analysis': analysis,
                'source_documents': [chunk['doc_id'] for chunk in context_chunks],
                'confidence_score': self._calculate_rag_confidence(context_chunks),
                'research_depth': len(context_chunks),
                'methodology': 'RAG-enhanced intelligence gathering'
            }
            
        except Exception as e:
            logger.error(f"Enhanced intelligence generation failed: {str(e)}")
            return {'error': str(e)}
    
    def _intelligent_chunk_research_content(self, content: str) -> List[str]:
        """Smart chunking optimized for research content"""
        
        # Research-specific chunking patterns
        section_patterns = [
            r'\n#{1,3}\s+',  # Markdown headers
            r'\n\d+\.\s+',   # Numbered lists
            r'\n[A-Z][A-Z\s]+:\s*',  # Section headers (METHODOLOGY:, FINDINGS:)
            r'\n\n+'  # Paragraph breaks
        ]
        
        chunks = []
        current_chunk = ""
        max_chunk_size = 1000  # Optimal for embeddings
        
        sentences = content.split('. ')
        
        for sentence in sentences:
            if len(current_chunk + sentence) > max_chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence + '. '
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Cohere (optimal for research)"""
        
        try:
            response = await self.cohere_client.embed(
                texts=texts,
                model="embed-english-v3.0",
                input_type="search_document"
            )
            return response.embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            # Fallback to basic embeddings
            return [[0.0] * 1024 for _ in texts]
    
    def _classify_content_type(self, content: str) -> str:
        """Classify research content type for optimal processing"""
        
        content_lower = content.lower()
        
        if any(term in content_lower for term in ['competitor', 'market share', 'versus', 'vs']):
            return 'competitive_intelligence'
        elif any(term in content_lower for term in ['market', 'industry', 'trend', 'analysis']):
            return 'market_research'
        elif any(term in content_lower for term in ['product', 'feature', 'service', 'offering']):
            return 'product_analysis'
        elif any(term in content_lower for term in ['campaign', 'marketing', 'advertising']):
            return 'campaign_intelligence'
        else:
            return 'general_research'
    
    def _format_research_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks for research analysis"""
        
        formatted_context = []
        
        for i, chunk in enumerate(chunks):
            doc_id = chunk['doc_id']
            content = chunk['content']
            similarity = chunk['similarity']
            
            formatted_context.append(f"""
            SOURCE {i+1} (Document: {doc_id}, Relevance: {similarity:.2f}):
            {content}
            """)
        
        return "\n".join(formatted_context)
    
    def _calculate_rag_confidence(self, chunks: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on retrieval quality"""
        
        if not chunks:
            return 0.0
        
        avg_similarity = sum(chunk['similarity'] for chunk in chunks) / len(chunks)
        document_diversity = len(set(chunk['doc_id'] for chunk in chunks))
        content_depth = sum(len(chunk['content'].split()) for chunk in chunks)
        
        # Weighted confidence calculation
        confidence = (
            avg_similarity * 0.4 +  # Relevance quality
            (document_diversity / len(chunks)) * 0.3 +  # Source diversity
            min(content_depth / 1000, 1.0) * 0.3  # Content depth
        )
        
        return min(confidence, 1.0)
    
    async def _fallback_analysis(self, prompt: str) -> str:
        """Fallback to existing analysis system"""
        # This would integrate with your existing load balanced system
        return "Analysis completed using fallback system - integrate with your existing analyzers.py"

# Usage example for integration with existing CampaignForge system
class EnhancedSalesPageAnalyzer(SalesPageAnalyzer):
    """Enhanced analyzer with RAG capabilities"""
    
    def __init__(self):
        super().__init__()
        self.rag_system = IntelligenceRAGSystem()
    
    async def analyze_with_research_context(self, url: str, research_docs: List[str] = None) -> Dict[str, Any]:
        """Analyze sales page with additional research context"""
        
        # Standard analysis first
        base_analysis = await self.analyze(url)
        
        if research_docs:
            # Add research documents to RAG
            for i, doc_content in enumerate(research_docs):
                await self.rag_system.add_research_document(f"research_doc_{i}", doc_content)
            
            # Query for relevant context
            product_name = base_analysis.get('product_name', 'Product')
            research_query = f"competitive analysis market research {product_name}"
            
            relevant_chunks = await self.rag_system.intelligent_research_query(research_query)
            
            if relevant_chunks:
                # Generate enhanced intelligence
                enhanced_intel = await self.rag_system.generate_enhanced_intelligence(
                    research_query, relevant_chunks
                )
                
                # Merge with base analysis
                base_analysis['enhanced_intelligence'] = enhanced_intel
                base_analysis['research_enhanced'] = True
                base_analysis['research_sources'] = len(research_docs)
        
        return base_analysis