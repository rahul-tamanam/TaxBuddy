"""
Complete RAG (Retrieval-Augmented Generation) pipeline
"""

from typing import List, Dict, Optional
from .embeddings import EmbeddingGenerator
from .vector_store import QdrantVectorStore
from .llm_client import GroqClient


class RAGPipeline:
    """End-to-end RAG pipeline for tax questions"""

    def __init__(
        self,
        collection_name: str = "tax_documents",
        storage_path: str = "./qdrant_storage",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialize RAG pipeline.

        Args:
            collection_name: Qdrant collection name
            storage_path: Path to Qdrant storage
            embedding_model: Sentence transformer model name
        """
        print("🚀 Initializing RAG Pipeline...")

        self.embedding_generator = EmbeddingGenerator(model_name=embedding_model)

        self.vector_store = QdrantVectorStore(
            collection_name=collection_name,
            storage_path=storage_path,
            embedding_dim=self.embedding_generator.embedding_dim,
        )

        self.llm_client = GroqClient()

        print("✅ RAG Pipeline ready!\n")
    def retrieve(self,
                query: str,
                top_k: int = 8,
                score_threshold: float = 0.25,
                filters: Optional[Dict] = None) -> List[Dict]:
        """Retrieve relevant documents for query"""
        
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        results = self.vector_store.search(
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=score_threshold,
            filters=filters
        )
        
        return results
    
    def answer_question(self,
                       query: str,
                       user_context: Optional[Dict] = None,
                       top_k: int = 8,
                       verbose: bool = False) -> Dict:
        """Answer user question using RAG"""
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print('='*60)
        
        # Retrieve
        if verbose:
            print("\n📚 Retrieving relevant documents...")
        
        retrieved_docs = self.retrieve(
            query=query,
            top_k=top_k,
            score_threshold=0.25
        )
        
        if verbose:
            print(f"Found {len(retrieved_docs)} relevant documents")
            for i, doc in enumerate(retrieved_docs, 1):
                print(f"  [{i}] {doc['metadata']['source']} (page {doc['metadata']['page']}) - similarity: {doc['similarity']:.3f}")
        
        if not retrieved_docs:
            return {
                'answer': "I don't have enough information in my knowledge base to answer this question. Please consult the IRS website or a tax professional.",
                'sources': [],
                'confidence': 'none'
            }
        
        # Generate answer
        if verbose:
            print("\n🤖 Generating answer...")
        
        answer = self.llm_client.generate_with_context(
            query=query,
            context_chunks=retrieved_docs,
            user_info=user_context
        )
        
        # Format response
        sources = []
        for doc in retrieved_docs:
            sources.append({
                'source': doc['metadata']['source'],
                'page': doc['metadata']['page'],
                'similarity': doc['similarity']
            })
        
        avg_similarity = sum(d['similarity'] for d in retrieved_docs) / len(retrieved_docs)
        confidence = 'high' if avg_similarity > 0.5 else 'medium' if avg_similarity > 0.3 else 'low'
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': confidence,
            'num_sources': len(retrieved_docs)
        }