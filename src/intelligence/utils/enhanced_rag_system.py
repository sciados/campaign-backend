# Enhanced Intelligence RAG System for CampaignForge
# File: src/intelligence/utils/enhanced_rag_system.py

import datetime
import hashlib
import json
import os
import uuid
import numpy as np
from typing import List, Dict, Any, Optional
import cohere
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

from src.core.crud.intelligence_crud import intelligence_crud

logger = logging.getLogger(__name__)

class IntelligenceRAGSystem:
    """
    Enhanced RAG system optimized for CampaignForge intelligence gathering
    Updated to work with new 6-table intelligence schema
    """
    
    def __init__(self, db: AsyncSession = None):
        self.cohere_client = cohere.AsyncClient(api_key=os.getenv("COHERE_API_KEY"))
        self.document_embeddings = {}
        self.document_chunks = {}
        self.db = db
        
    def set_database_connection(self, db: AsyncSession):
        """Set database connection for RAG system"""
        self.db = db
        
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
    
    async def add_research_document_to_db(self, doc_id: str, content: str, research_type: str, metadata: Dict[str, Any] = None):
        """Add research document to both RAG system and knowledge_base table"""
        
        try:
            # Add to RAG system (existing method)
            success = await self.add_research_document(doc_id, content, metadata)
            
            if success and self.db:
                # Store in new knowledge_base table
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                
                query = text("""
                    INSERT INTO knowledge_base (id, content_hash, content, research_type, source_metadata, created_at)
                    VALUES (:id, :content_hash, :content, :research_type, :source_metadata, NOW())
                    ON CONFLICT (content_hash) DO UPDATE SET
                        source_metadata = EXCLUDED.source_metadata,
                        updated_at = NOW()
                """)
                
                await self.db.execute(query, {
                    "id": doc_id,
                    "content_hash": content_hash,
                    "content": content,
                    "research_type": research_type,
                    "source_metadata": json.dumps(metadata or {})
                })
                
                await self.db.commit()
                logger.info(f"Stored research document {doc_id} in knowledge_base")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add research document to database: {str(e)}")
            return False

    async def link_intelligence_to_research(self, intelligence_id: str, research_ids: List[str], relevance_scores: List[float]):
        """Link intelligence analysis to research documents in intelligence_research table"""
        
        try:
            if not self.db:
                return False
            
            # Store links in intelligence_research table
            for research_id, relevance_score in zip(research_ids, relevance_scores):
                query = text("""
                    INSERT INTO intelligence_research (intelligence_id, research_id, relevance_score)
                    VALUES (:intelligence_id, :research_id, :relevance_score)
                    ON CONFLICT (intelligence_id, research_id) DO UPDATE SET
                        relevance_score = EXCLUDED.relevance_score
                """)
                
                await self.db.execute(query, {
                    "intelligence_id": intelligence_id,
                    "research_id": research_id,
                    "relevance_score": relevance_score
                })
            
            await self.db.commit()
            logger.info(f"Linked intelligence {intelligence_id} to {len(research_ids)} research documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to link intelligence to research: {str(e)}")
            return False

    async def retrieve_research_for_intelligence(self, intelligence_id: str) -> List[Dict[str, Any]]:
        """Retrieve linked research documents for an intelligence analysis"""
        
        try:
            if not self.db:
                return []
            
            # Get linked research from new schema
            query = text("""
                SELECT kb.*, ir.relevance_score
                FROM knowledge_base kb
                JOIN intelligence_research ir ON kb.id = ir.research_id
                WHERE ir.intelligence_id = :intelligence_id
                ORDER BY ir.relevance_score DESC
            """)
            
            result = await self.db.execute(query, {"intelligence_id": intelligence_id})
            rows = result.fetchall()
            
            research_docs = []
            for row in rows:
                research_docs.append({
                    'research_id': row.id,
                    'content': row.content,
                    'research_type': row.research_type,
                    'relevance_score': row.relevance_score,
                    'metadata': json.loads(row.source_metadata or '{}'),
                    'created_at': row.created_at
                })
            
            return research_docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve research for intelligence: {str(e)}")
            return []

    async def get_research_from_knowledge_base(self, research_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve research documents from knowledge_base table"""
        
        try:
            if not self.db:
                return []
            
            if research_type:
                query = text("""
                    SELECT * FROM knowledge_base 
                    WHERE research_type = :research_type
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)
                result = await self.db.execute(query, {"research_type": research_type, "limit": limit})
            else:
                query = text("""
                    SELECT * FROM knowledge_base 
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)
                result = await self.db.execute(query, {"limit": limit})
            
            rows = result.fetchall()
            
            research_docs = []
            for row in rows:
                research_docs.append({
                    'id': row.id,
                    'content': row.content,
                    'research_type': row.research_type,
                    'metadata': json.loads(row.source_metadata or '{}'),
                    'created_at': row.created_at,
                    'content_hash': row.content_hash
                })
            
            return research_docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve research from knowledge base: {str(e)}")
            return []
    
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
        Uses available AI provider for deep analysis of research materials
        """
        
        try:
            # Prepare context from retrieved chunks
            context = self._format_research_context(context_chunks)
            
            # Enhanced prompt for research analysis
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
            
            # Use your existing AI provider system
            analysis = await self._generate_ai_analysis(enhanced_prompt)
            
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
    
    async def _generate_ai_analysis(self, prompt: str) -> str:
        """Generate AI analysis using available provider"""
        try:
            # This would integrate with your existing AI provider system
            # For now, using a fallback implementation
            return f"Enhanced analysis based on research context: {prompt[:200]}..."
        except Exception as e:
            logger.error(f"AI analysis generation failed: {str(e)}")
            return "Analysis could not be generated at this time."
    
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
            return 'marketing_intelligence'
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

    def _classify_research_type(self, content: str) -> str:
        """Classify research document type for database storage"""
        content_lower = content.lower()
        
        if any(term in content_lower for term in ['clinical', 'study', 'trial', 'research']):
            return 'clinical'
        elif any(term in content_lower for term in ['market', 'industry', 'competitor']):
            return 'market'
        elif any(term in content_lower for term in ['ingredient', 'formula', 'component']):
            return 'ingredient'
        else:
            return 'general'


# Enhanced Sales Page Analyzer with RAG capabilities
class EnhancedSalesPageAnalyzer:
    """Enhanced analyzer with RAG capabilities - Updated for new schema"""
    
    def __init__(self, db: AsyncSession = None):
        self.rag_system = IntelligenceRAGSystem(db)
        self._base_analyzer = None
    
    async def _get_base_analyzer(self):
        """Lazy load base analyzer to avoid circular imports"""
        if self._base_analyzer is None:
            from src.intelligence.analyzers import SalesPageAnalyzer
            self._base_analyzer = SalesPageAnalyzer()
        return self._base_analyzer
    
    async def analyze_with_research_context(self, url: str, research_docs: List[str] = None) -> Dict[str, Any]:
        """Analyze sales page with additional research context - Updated for new schema"""
        
        try:
            # Get base analyzer and do standard analysis first
            base_analyzer = await self._get_base_analyzer()
            base_analysis = await base_analyzer.analyze(url)
            
            if research_docs and len(research_docs) > 0:
                research_ids = []
                relevance_scores = []
                
                # Add research documents to RAG and database
                for i, doc_content in enumerate(research_docs):
                    research_id = f"research_doc_{uuid.uuid4().hex[:8]}"
                    research_type = self.rag_system._classify_research_type(doc_content)
                    
                    success = await self.rag_system.add_research_document_to_db(
                        research_id, 
                        doc_content, 
                        research_type,
                        {'source': 'user_provided', 'index': i}
                    )
                    
                    if success:
                        research_ids.append(research_id)
                        relevance_scores.append(0.8 - (i * 0.1))  # Decreasing relevance
                
                # Query for relevant context
                product_name = base_analysis.get('product_name', 'Product')
                research_query = f"competitive analysis market research {product_name}"
                
                relevant_chunks = await self.rag_system.intelligent_research_query(research_query)
                
                if relevant_chunks:
                    # Generate enhanced intelligence
                    enhanced_intel = await self.rag_system.generate_enhanced_intelligence(
                        research_query, relevant_chunks
                    )
                    
                    # Link intelligence to research in database
                    if base_analysis.get('analysis_id') and research_ids:
                        await self.rag_system.link_intelligence_to_research(
                            base_analysis['analysis_id'],
                            research_ids,
                            relevance_scores
                        )
                    
                    # Merge with base analysis
                    base_analysis['enhanced_intelligence'] = enhanced_intel
                    base_analysis['research_enhanced'] = True
                    base_analysis['research_sources'] = len(research_docs)
                    base_analysis['research_ids'] = research_ids
            
            return base_analysis
            
        except Exception as e:
            logger.error(f"Error in enhanced analysis: {str(e)}")
            # Return base analysis even if enhancement fails
            base_analyzer = await self._get_base_analyzer()
            return await base_analyzer.analyze(url)


# RAG Integration for existing intelligence system
class RAGIntelligenceIntegration:
    """Integration layer for RAG with existing intelligence system"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag_system = IntelligenceRAGSystem(db)
    
    async def enhance_intelligence_with_research(self, intelligence_id: str) -> Dict[str, Any]:
        """Enhance existing intelligence analysis with RAG research"""
        
        try:
            # Get intelligence data using new CRUD
            intelligence_data = await intelligence_crud.get_intelligence_by_id(self.db, intelligence_id)
            
            if not intelligence_data:
                return {"error": "Intelligence not found"}
            
            # Get linked research documents
            research_docs = await self.rag_system.retrieve_research_for_intelligence(intelligence_id)
            
            if research_docs:
                # Use research content for enhanced analysis
                research_content = [doc['content'] for doc in research_docs]
                
                product_name = intelligence_data.get('product_name', 'Product')
                query = f"detailed analysis {product_name} competitive intelligence"
                
                # Add research to RAG system
                for i, doc in enumerate(research_docs):
                    await self.rag_system.add_research_document(
                        f"existing_research_{i}",
                        doc['content'],
                        doc.get('metadata', {})
                    )
                
                # Query for insights
                relevant_chunks = await self.rag_system.intelligent_research_query(query)
                
                if relevant_chunks:
                    enhanced_analysis = await self.rag_system.generate_enhanced_intelligence(
                        query, relevant_chunks
                    )
                    
                    return {
                        "intelligence_id": intelligence_id,
                        "enhanced_analysis": enhanced_analysis,
                        "research_sources": len(research_docs),
                        "enhancement_timestamp": datetime.now().isoformat()
                    }
            
            return {"message": "No research available for enhancement"}
            
        except Exception as e:
            logger.error(f"Error enhancing intelligence with research: {str(e)}")
            return {"error": str(e)}
    
    async def get_rag_system_stats(self) -> Dict[str, Any]:
        """Get statistics about RAG system usage"""
        
        try:
            # Get knowledge base stats
            kb_stats_query = text("""
                SELECT 
                    COUNT(*) as total_documents,
                    COUNT(DISTINCT research_type) as research_types,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_additions
                FROM knowledge_base
            """)
            
            result = await self.db.execute(kb_stats_query)
            kb_stats = result.fetchone()
            
            # Get intelligence-research link stats
            link_stats_query = text("""
                SELECT 
                    COUNT(*) as total_links,
                    COUNT(DISTINCT intelligence_id) as enhanced_intelligence,
                    AVG(relevance_score) as avg_relevance
                FROM intelligence_research
            """)
            
            result = await self.db.execute(link_stats_query)
            link_stats = result.fetchone()
            
            return {
                "knowledge_base": {
                    "total_documents": kb_stats[0] if kb_stats else 0,
                    "research_types": kb_stats[1] if kb_stats else 0,
                    "recent_additions": kb_stats[2] if kb_stats else 0
                },
                "intelligence_links": {
                    "total_links": link_stats[0] if link_stats else 0,
                    "enhanced_intelligence": link_stats[1] if link_stats else 0,
                    "avg_relevance": round(float(link_stats[2]), 2) if link_stats and link_stats[2] else 0.0
                },
                "in_memory_documents": len(self.rag_system.document_embeddings),
                "system_status": "operational" if len(self.rag_system.document_embeddings) > 0 else "empty"
            }
            
        except Exception as e:
            logger.error(f"Error getting RAG stats: {str(e)}")
            return {"error": str(e)}