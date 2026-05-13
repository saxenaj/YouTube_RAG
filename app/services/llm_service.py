import ollama
from typing import List, Dict, AsyncGenerator
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)
        self.model = settings.LLM_MODEL
        self._check_model()
    
    def _check_model(self):
        """Check if model is available, attempt to pull if not"""
        try:
            # List available models
            models = self.client.list()
            model_names = [model['name'] for model in models.get('models', [])]
            
            if self.model not in model_names:
                logger.warning(f"Model {self.model} not found. Attempting to pull...")
                self.pull_model()
            else:
                logger.info(f"Model {self.model} is available")
                
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            logger.info("Make sure Ollama is running and the model is pulled")
    
    def pull_model(self):
        """Pull the model from Ollama"""
        logger.info(f"Pulling model: {self.model}")
        try:
            self.client.pull(self.model)
            logger.info(f"Model {self.model} pulled successfully")
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            raise
    
    async def generate_answer(self, question: str, 
                             context_chunks: List[Dict]) -> AsyncGenerator[str, None]:
        """
        Generate answer using context chunks, with streaming
        
        Args:
            question: User's question
            context_chunks: List of relevant chunks from vector search
        
        Yields:
            Answer text chunks (for streaming)
        """
        prompt = self._build_prompt(question, context_chunks)
        
        logger.info(f"Generating answer for question: {question[:50]}...")
        
        try:
            # Stream response from Ollama
            stream = self.client.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                stream=True,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'num_predict': 512,
                }
            )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            yield f"Error generating answer: {str(e)}"
    
    def _build_prompt(self, question: str, context_chunks: List[Dict]) -> str:
        """Build prompt with context and question"""
        # Format context chunks
        context_text = self._format_context(context_chunks)
        
        prompt = f"""You are a helpful AI assistant answering questions about a YouTube video based on its transcript.

Context from the video transcript:
{context_text}

Question: {question}

Instructions:
- Answer the question based ONLY on the context provided above
- Be concise and specific
- If the context doesn't contain enough information to answer the question, say so
- Reference specific timestamps when relevant (e.g., "At 02:35, the speaker mentioned...")
- Use a conversational but informative tone

Answer:"""
        
        return prompt
    
    def _format_context(self, chunks: List[Dict]) -> str:
        """Format context chunks for the prompt"""
        formatted = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get('metadata', {})
            timestamp = metadata.get('timestamp', 'Unknown')
            text = chunk.get('document', '')
            similarity = chunk.get('similarity', 0)
            
            formatted.append(
                f"[Chunk {i} - Timestamp: {timestamp}, Relevance: {similarity:.2f}]\n{text}\n"
            )
        
        return "\n".join(formatted)
    
    def generate_answer_sync(self, question: str, 
                            context_chunks: List[Dict]) -> str:
        """
        Generate answer synchronously (non-streaming)
        Useful for testing or simple use cases
        """
        prompt = self._build_prompt(question, context_chunks)
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                stream=False
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"


# Global service instance
llm_service = LLMService()