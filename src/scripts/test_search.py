"""
Test vector search functionality
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.embeddings import EmbeddingGenerator
from core.vector_store import QdrantVectorStore

def test_search():
    """Interactive search testing"""
    
    print("\n" + "="*60)
    print("TaxBuddy - Search Test")
    print("="*60 + "\n")
    
    # Initialize
    generator = EmbeddingGenerator(model_name='all-MiniLM-L6-v2')
    vector_store = QdrantVectorStore(
        collection_name="tax_documents",
        storage_path="./qdrant_storage",
        embedding_dim=384
    )
    
    # Test queries
    test_queries = [
        "Do I need to file Form 8843?",
        "What is the substantial presence test?",
        "Can I claim tax treaty benefits?",
        "What forms do F-1 students need?",
        "How do I report scholarship income?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        # Generate embedding
        query_embedding = generator.generate_embedding(query)
        
        # Search
        results = vector_store.search(
            query_vector=query_embedding,
            limit=3,
            score_threshold=0.3
        )
        
        print(f"\nFound {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"[{i}] Similarity: {result['similarity']:.3f}")
            print(f"    Source: {result['metadata']['source']} (Page {result['metadata']['page']})")
            print(f"    Text: {result['text'][:200]}...")
            print()
    
    print("="*60)
    print("✅ Search test complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_search()