import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from app.config import settings
from app.models.schemas import Chunk
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        logger.info(f"Initializing ChromaDB at: {settings.CHROMA_DB_PATH}")
        
        self.client = chromadb.PersistentClient(
            path=str(settings.CHROMA_DB_PATH),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",  # cosine similarity
                "description": "YouTube transcript chunks with embeddings"
            }
        )
        
        logger.info(f"Collection '{settings.CHROMA_COLLECTION_NAME}' ready. "
                   f"Total items: {self.collection.count()}")
    
    def add_chunks(self, video_id: str, chunks: List[Chunk], 
                   embeddings: List[List[float]]) -> None:
        """
        Add chunks with embeddings to vector store
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        logger.info(f"Adding {len(chunks)} chunks for video {video_id}")
        
        # Prepare data for ChromaDB
        ids = [f"{video_id}_{chunk.chunk_index}" for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "video_id": video_id,
                "chunk_index": chunk.chunk_index,
                "timestamp": chunk.timestamp,
                "start_time": chunk.start_time,
                "end_time": chunk.end_time
            }
            for chunk in chunks
        ]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully added {len(chunks)} chunks to vector store")
    
    def search(self, query_embedding: List[float], video_id: str = None, 
               k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity
        
        Args:
            query_embedding: Query vector
            video_id: Optional video ID to filter results
            k: Number of results to return
        
        Returns:
            List of results with documents, metadatas, and distances
        """
        logger.info(f"Searching for top {k} similar chunks" +
                   (f" in video {video_id}" if video_id else ""))
        
        # Build where filter if video_id provided
        where_filter = {"video_id": video_id} if video_id else None
        
        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results['ids'][0]:  # Check if we got any results
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
                })
        
        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results
    
    def delete_video(self, video_id: str) -> int:
        """
        Delete all chunks for a video
        Returns number of deleted items
        """
        logger.info(f"Deleting chunks for video {video_id}")
        
        # Get all IDs for this video
        results = self.collection.get(
            where={"video_id": video_id},
            include=[]
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            logger.info(f"Deleted {len(results['ids'])} chunks")
            return len(results['ids'])
        
        return 0
    
    def get_video_chunk_count(self, video_id: str) -> int:
        """Get number of chunks for a video"""
        results = self.collection.get(
            where={"video_id": video_id},
            include=[]
        )
        return len(results['ids']) if results['ids'] else 0
    
    def list_videos(self) -> List[str]:
        """Get list of all unique video IDs in the store"""
        # This is a bit inefficient but ChromaDB doesn't have a direct way
        all_items = self.collection.get(include=["metadatas"])
        
        if not all_items['metadatas']:
            return []
        
        video_ids = set(item['video_id'] for item in all_items['metadatas'])
        return list(video_ids)
    
    def reset_collection(self) -> None:
        """Delete all data in the collection (use with caution!)"""
        logger.warning("Resetting collection - deleting all data!")
        self.client.delete_collection(settings.CHROMA_COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Collection reset complete")


# Global service instance
vector_store = VectorStore()