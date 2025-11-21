"""
Advanced Semantic Search with Vector Embeddings

This module provides semantic search capabilities using sentence transformers
and FAISS for efficient vector similarity search.
"""
import os
from typing import List, Optional, Dict, Any
from functools import lru_cache
# numpy only needed indirectly via embeddings returned; avoid hard dependency at import time.
from sqlalchemy.orm import Session
from app.db.models import Memory

# Conditional imports for optional dependencies
try:
    from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss  # type: ignore[import-not-found]
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class SemanticSearchEngine:
    """
    Advanced semantic search using vector embeddings and FAISS indexing.
    
    Features:
    - Sentence-BERT embeddings for semantic similarity
    - FAISS for efficient nearest neighbor search
    - Hybrid search (semantic + keyword + importance)
    - Query result caching
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize semantic search engine.
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.enabled = self._check_dependencies()
        self.model_name = model_name
        self.model = None
        self.index = None
        self.memory_ids = []
        
        if self.enabled:
            self._initialize()
    
    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("⚠ sentence-transformers not installed. Semantic search disabled.")
            print("  Install: pip install sentence-transformers")
            return False
        
        if not FAISS_AVAILABLE:
            print("⚠ faiss not installed. Using fallback search.")
            print("  Install: pip install faiss-cpu  # or faiss-gpu for CUDA")
            return False
        
        return os.getenv("CRECALL_ENABLE_SEMANTIC_SEARCH", "0") == "1"
    
    def _initialize(self):
        """Initialize the embedding model and FAISS index"""
        if not self.enabled:
            return
        
        print(f"🔍 Initializing semantic search with {self.model_name}...")
        self.model = self._get_model()
        print("✓ Semantic search ready")
    
    @lru_cache(maxsize=1)
    def _get_model(self) -> Optional[SentenceTransformer]:
        """Get or load the sentence transformer model (cached)"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return None
        
        return SentenceTransformer(self.model_name)
    
    def build_index(self, db: Session, session_id: Optional[int] = None):
        """
        Build FAISS index from all memories in database.
        
        Args:
            db: Database session
            session_id: Optional filter by session
        """
        if not self.enabled:
            return
        
        # Fetch memories
        query = db.query(Memory)
        if session_id:
            query = query.filter(Memory.session_id == session_id)
        
        memories = query.all()
        
        if not memories:
            print("No memories to index")
            return
        
        print(f"Building index for {len(memories)} memories...")
        
        # Generate embeddings
        if self.model is None:  # Extra guard for mypy
            print("Semantic model unavailable - skipping index build")
            return

        texts = [m.content for m in memories]
        embeddings = self.model.encode(texts, show_progress_bar=True)  # type: ignore[attr-defined]
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance
        self.index.add(embeddings.astype('float32'))
        
        # Store memory IDs for retrieval
        self.memory_ids = [m.id for m in memories]
        
        print(f"✓ Index built with {self.index.ntotal} vectors")
    
    def semantic_search(
        self,
        query: str,
        db: Session,
        top_k: int = 10,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search across memories.
        
        Args:
            query: Search query text
            db: Database session
            top_k: Number of results to return
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of results with memory and similarity score
        """
        if not self.enabled or self.index is None:
            # Fallback to basic keyword search
            return self._fallback_search(query, db, top_k)
        
        # Generate query embedding
        if self.model is None:  # Guard for optional dependency absence
            return self._fallback_search(query, db, top_k)

        query_embedding = self.model.encode([query])[0]  # type: ignore[attr-defined]
        
        # Search FAISS index
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            top_k
        )
        
        # Convert distances to similarity scores (cosine similarity)
        # L2 distance to similarity: similarity = 1 / (1 + distance)
        similarities = 1 / (1 + distances[0])
        
        # Fetch memories and build results
        results = []
        for idx, similarity in zip(indices[0], similarities):
            if similarity < min_score:
                continue
            
            memory_id = self.memory_ids[idx]
            memory = db.query(Memory).get(memory_id)
            
            if memory:
                results.append({
                    "memory": memory,
                    "similarity": float(similarity),
                    "score": float(similarity) * (memory.importance / 3.0)  # Hybrid scoring
                })
        
        # Sort by hybrid score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def hybrid_search(
        self,
        query: str,
        db: Session,
        session_id: Optional[int] = None,
        top_k: int = 10,
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.2,
        importance_weight: float = 0.2
    ) -> List[Memory]:
        """
        Hybrid search combining semantic, keyword, and importance.
        
        Args:
            query: Search query
            db: Database session
            session_id: Optional session filter
            top_k: Results to return
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword match (0-1)
            importance_weight: Weight for importance (0-1)
            
        Returns:
            Ranked list of memories
        """
        # Get semantic results
        semantic_results = self.semantic_search(query, db, top_k=top_k * 2)
        
        # Get keyword results
        keyword_results = self._keyword_search(query, db, session_id, top_k * 2)
        
        # Combine and score
        combined_scores = {}
        
        for result in semantic_results:
            memory_id = result["memory"].id
            combined_scores[memory_id] = {
                "memory": result["memory"],
                "semantic": result["similarity"] * semantic_weight,
                "keyword": 0.0,
                "importance": 0.0
            }
        
        for memory in keyword_results:
            memory_id = memory.id
            if memory_id not in combined_scores:
                combined_scores[memory_id] = {
                    "memory": memory,
                    "semantic": 0.0,
                    "keyword": 0.0,
                    "importance": 0.0
                }
            
            # Simple keyword score (term frequency)
            keyword_score = query.lower().count(memory.content.lower()[:20]) / 10.0
            combined_scores[memory_id]["keyword"] = keyword_score * keyword_weight
        
        # Add importance scores
        for memory_id, data in combined_scores.items():
            importance_score = data["memory"].importance / 3.0
            data["importance"] = importance_score * importance_weight
        
        # Calculate final scores
        final_results = []
        for memory_id, data in combined_scores.items():
            total_score = (
                data["semantic"] +
                data["keyword"] +
                data["importance"]
            )
            final_results.append((data["memory"], total_score))
        
        # Sort and return top_k
        final_results.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, score in final_results[:top_k]]
    
    def _fallback_search(self, query: str, db: Session, top_k: int) -> List[Dict[str, Any]]:
        """Fallback search when semantic search unavailable"""
        memories = db.query(Memory).filter(
            Memory.content.like(f"%{query}%")
        ).order_by(Memory.importance.desc()).limit(top_k).all()
        
        return [{"memory": m, "similarity": 0.5, "score": m.importance / 3.0} for m in memories]
    
    def _keyword_search(
        self, query: str, db: Session, session_id: Optional[int], top_k: int
    ) -> List[Memory]:
        """Simple keyword search"""
        q = db.query(Memory).filter(Memory.content.like(f"%{query}%"))
        
        if session_id:
            q = q.filter(Memory.session_id == session_id)
        
        return q.order_by(Memory.importance.desc()).limit(top_k).all()
    
    def save_index(self, filepath: str):
        """Save FAISS index to disk"""
        if self.index is not None and FAISS_AVAILABLE:
            faiss.write_index(self.index, filepath)
            print(f"✓ Index saved to {filepath}")
    
    def load_index(self, filepath: str):
        """Load FAISS index from disk"""
        if os.path.exists(filepath) and FAISS_AVAILABLE:
            self.index = faiss.read_index(filepath)
            print(f"✓ Index loaded from {filepath}")


# Global instance
_search_engine = None


def get_search_engine() -> SemanticSearchEngine:
    """Get or create the global search engine instance"""
    global _search_engine
    
    if _search_engine is None:
        _search_engine = SemanticSearchEngine()
    
    return _search_engine
