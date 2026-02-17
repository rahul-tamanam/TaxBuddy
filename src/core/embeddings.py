"""
Generate embeddings for document chunks using sentence-transformers
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np
from pathlib import Path
import json
from tqdm import tqdm

class EmbeddingGenerator:
    """Generate embeddings for text chunks"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedding model
        
        Args:
            model_name: Name of sentence-transformer model
                       'all-MiniLM-L6-v2' - Fast, 384 dimensions (recommended)
                       'all-mpnet-base-v2' - Better quality, 768 dimensions (slower)
        """
        print(f"📦 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"✅ Model loaded (dimension: {self.embedding_dim})")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str], 
                                  batch_size: int = 32,
                                  show_progress: bool = True) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        
        embeddings = []
        
        # Process in batches for efficiency
        for i in tqdm(range(0, len(texts), batch_size), 
                     desc="Generating embeddings",
                     disable=not show_progress):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            embeddings.extend(batch_embeddings.tolist())
        
        return embeddings
    
    def embed_chunks(self, chunks: List[Dict], 
                    output_file: Path = None) -> List[Dict]:
        """Add embeddings to document chunks"""
        
        print("\n" + "="*60)
        print("Generating Embeddings")
        print("="*60 + "\n")
        
        print(f"Model: {self.model_name}")
        print(f"Embedding dimension: {self.embedding_dim}")
        print(f"Total chunks: {len(chunks)}\n")
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        print("Generating embeddings (this may take a few minutes)...")
        embeddings = self.generate_embeddings_batch(texts)
        
        # Add embeddings to chunks
        print("\nAdding embeddings to chunks...")
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i]
        
        # Save if output file specified
        if output_file:
            print(f"\n💾 Saving chunks with embeddings to: {output_file}")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            # Get file size
            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"   File size: {file_size_mb:.2f} MB")
        
        print("\n" + "="*60)
        print(f"✅ Generated {len(embeddings)} embeddings")
        print("="*60 + "\n")
        
        return chunks
    
    def test_embedding(self, text: str = "This is a test."):
        """Test embedding generation"""
        
        print(f"\nTesting embedding generation...")
        print(f"Input text: '{text}'")
        
        embedding = self.generate_embedding(text)
        
        print(f"Embedding dimension: {len(embedding)}")
        print(f"Sample values: {embedding[:5]}")
        print(f"✅ Embedding generation working!\n")


def main():
    """Test embedding generation"""
    
    # Load chunks
    chunks_file = Path('data/chunked/all_chunks.json')
    
    if not chunks_file.exists():
        print(f"❌ Chunks file not found: {chunks_file}")
        print("Run: python src/scripts/process_documents.py")
        return
    
    print(f"📖 Loading chunks from: {chunks_file}")
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks\n")
    
    # Generate embeddings
    generator = EmbeddingGenerator(model_name='all-MiniLM-L6-v2')
    
    # Test first
    generator.test_embedding()
    
    # Embed all chunks
    output_file = Path('data/embeddings/chunks_with_embeddings.json')
    chunks_with_embeddings = generator.embed_chunks(chunks, output_file)
    
    print(f"✅ Complete! Embeddings saved to: {output_file}")


if __name__ == "__main__":
    main()