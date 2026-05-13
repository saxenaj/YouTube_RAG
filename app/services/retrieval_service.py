from typing import List, Dict
from app.config import settings
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.models.schemas import QueryResponse, Source
import logging

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Service for retrieving relevant context and generating answers
    """
    
    def __init__(self):
        self.top_k = settings.TOP_K_CHUNKS
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD
    
    async def query(self, question: str, video_id: str, 
                   top_k: int = None) -> QueryResponse:
        """
        Answer a question about a video
        
        Pipeline:
        1. Embed the question
        2. Search for relevant chunks
        3. Filter by similarity threshold
        4. Generate answer using LLM
        5. Return answer with sources
        """
        k = top_k or self.top_k
        
        logger.info(f"Processing query for video {video_id}: {question[:50]}...")
        
        # Step 1: Embed the question
        logger.info("Embedding question")
        question_embedding = embedding_service.embed_text(question)
        
        # Step 2: Search for relevant chunks
        logger.info(f"Searching for top {k} relevant chunks")
        search_results = vector_store.search(
            query_embedding=question_embedding,
            video_id=video_id,
            k=k
        )
        
        if not search_results:
            logger.warning(f"No chunks found for video {video_id}")
            return QueryResponse(
                answer="I couldn't find any relevant information in this video to answer your question.",
                sources=[],
                video_id=video_id
            )
        
        # Step 3: Filter by similarity threshold
       # filtered_results = [
        #    result for result in search_results
         #   if result['similarity'] >= self.similarity_threshold
       # ]
        #Temporary: Disable filtering to ensure some results are returned
        filtered_results = search_results
        
        if not filtered_results:
            logger.warning(f"No chunks above similarity threshold ({self.similarity_threshold})")
            return QueryResponse(
                answer="I couldn't find sufficiently relevant information in this video to answer your question confidently.",
                sources=[],
                video_id=video_id
            )
        
        logger.info(f"Found {len(filtered_results)} relevant chunks above threshold")
        
        # Step 4: Generate answer using LLM
        logger.info("Generating answer with LLM")
        answer_parts = []
        async for chunk in llm_service.generate_answer(question, filtered_results):
            answer_parts.append(chunk)
        
        answer = "".join(answer_parts)
        
        # Step 5: Format sources
        sources = self._format_sources(filtered_results)
        
        logger.info("Query processing completed")
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            video_id=video_id
        )
    
    async def query_streaming(self, question: str, video_id: str, 
                             top_k: int = None):
        """
        Stream answer generation for real-time responses
        
        Yields:
            - Initially: {"type": "sources", "data": [...]}
            - Then: {"type": "answer_chunk", "data": "..."}
            - Finally: {"type": "done"}
        """
        k = top_k or self.top_k
        
        # Retrieve context
        question_embedding = embedding_service.embed_text(question)
        search_results = vector_store.search(
            query_embedding=question_embedding,
            video_id=video_id,
            k=k
        )
        
        if not search_results:
            yield {
                "type": "error",
                "data": "No relevant information found"
            }
            return
        
        # Filter results
        filtered_results = [
            result for result in search_results
            if result['similarity'] >= self.similarity_threshold
        ]
        
        if not filtered_results:
            yield {
                "type": "error",
                "data": "No sufficiently relevant information found"
            }
            return
        
        # Send sources first
        sources = self._format_sources(filtered_results)
        yield {
            "type": "sources",
            "data": [source.dict() for source in sources]
        }
        
        # Stream answer
        async for chunk in llm_service.generate_answer(question, filtered_results):
            yield {
                "type": "answer_chunk",
                "data": chunk
            }
        
        # Signal completion
        yield {"type": "done"}
    
    def _format_sources(self, search_results: List[Dict]) -> List[Source]:
        """Format search results as Source objects"""
        sources = []
        
        for result in search_results:
            metadata = result.get('metadata', {})
            sources.append(Source(
                chunk_text=result.get('document', '')[:200] + "...",  # Truncate for display
                timestamp=metadata.get('timestamp', 'Unknown'),
                similarity_score=round(result.get('similarity', 0), 3)
            ))
        
        return sources
    
    def get_similar_chunks(self, video_id: str, text: str, k: int = 5) -> List[Dict]:
        """
        Find similar chunks to a given text
        Useful for exploratory search or finding related content
        """
        text_embedding = embedding_service.embed_text(text)
        results = vector_store.search(
            query_embedding=text_embedding,
            video_id=video_id,
            k=k
        )
        return results


# Global service instance
retrieval_service = RetrievalService()