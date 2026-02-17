"""
Complete pipeline to set up vector database
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.embeddings import EmbeddingGenerator
from core.vector_store import QdrantVectorStore
import json

def setup_vector_database():
    """Complete setup pipeline for vector database"""
    
    print("\n" + "="*60)
    print("TaxBuddy - Vector Database Setup Pipeline")
    print("="*60 + "\n")
    
    # Step 1: Load chunks (PDF chunks + supplementary treaty/visa chunks)
    chunks_file = Path('data/chunked/all_chunks.json')
    supplementary_file = Path('data/chunked/supplementary_chunks.json')

    if not chunks_file.exists():
        print(f"❌ Chunks file not found: {chunks_file}")
        print("Run: python src/scripts/process_documents.py first")
        return

    print(f"📖 Loading chunks from: {chunks_file}")
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    n_pdf = len(chunks)

    if supplementary_file.exists():
        print(f"📖 Loading supplementary chunks from: {supplementary_file}")
        with open(supplementary_file, 'r', encoding='utf-8') as f:
            supplementary = json.load(f)
        chunks = chunks + supplementary
        print(f"✅ Loaded {n_pdf} PDF chunks + {len(supplementary)} supplementary (treaty/visa) = {len(chunks)} total\n")
    else:
        print(f"✅ Loaded {len(chunks)} chunks (run create_supplementary_chunks.py to add treaty/visa data)\n")
    
    # Step 2: Generate embeddings
    print("STEP 1: Generating embeddings...")
    generator = EmbeddingGenerator(model_name='all-MiniLM-L6-v2')
    
    output_file = Path('data/embeddings/chunks_with_embeddings.json')
    chunks_with_embeddings = generator.embed_chunks(chunks, output_file)
    
    print(f"✅ Step 1 complete: Embeddings generated\n")
    
    # Step 3: Setup Qdrant
    print("STEP 2: Setting up Qdrant vector database...")
    vector_store = QdrantVectorStore(
        collection_name="tax_documents",
        storage_path="./qdrant_storage",
        embedding_dim=generator.embedding_dim
    )
    
    # Create collection
    vector_store.create_collection(recreate=True)
    
    # Add documents
    vector_store.add_documents(chunks_with_embeddings)
    
    print(f"✅ Step 2 complete: Vector database ready\n")
    
    # Step 4: Test search
    print("STEP 3: Testing search functionality...")
    test_query = "Do I need to file taxes if I had no income?"
    
    print(f"\nTest query: '{test_query}'")
    test_embedding = generator.generate_embedding(test_query)
    
    results = vector_store.search(
        query_vector=test_embedding,
        limit=3
    )
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n[Result {i}] (similarity: {result['similarity']:.3f})")
        print(f"Source: {result['metadata']['source']}, Page: {result['metadata']['page']}")
        print(f"Text: {result['text'][:150]}...")
    
    # Final summary
    stats = vector_store.get_collection_stats()
    
    print("\n" + "="*60)
    print("✅ VECTOR DATABASE SETUP COMPLETE")
    print("="*60)
    print(f"\nCollection: {stats['name']}")
    print(f"Total documents: {stats['points_count']}")
    print(f"Embedding dimension: {generator.embedding_dim}")
    print(f"\nStorage location: ./qdrant_storage")
    print("\nNext steps:")
    print("  1. Set GROQ_API_KEY in .env and run the app (streamlit run app.py)")
    print("="*60 + "\n")


if __name__ == "__main__":
    setup_vector_database()