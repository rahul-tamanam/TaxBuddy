"""
Local vector store for document chunks (ChromaDB backend).

This replaces the previous Qdrant-based implementation with an embedded,
fully local and free vector database – no separate server required.
"""

from typing import List, Dict, Optional
from pathlib import Path
from uuid import uuid4
import json

from chromadb import PersistentClient


class ChromaVectorStore:
    """Vector store using ChromaDB for document retrieval"""

    def __init__(
        self,
        collection_name: str = "tax_documents",
        storage_path: str = "./qdrant_storage",
        embedding_dim: int = 384,
    ):
        """
        Initialize local vector store.

        Args:
            collection_name: Name of the collection
            storage_path: Path to store Chroma data
            embedding_dim: Dimension of embeddings (384 for all-MiniLM-L6-v2)
        """
        self.collection_name = collection_name
        self.storage_path = Path(storage_path)
        self.embedding_dim = embedding_dim

        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize Chroma client (local persistent storage)
        print(f"🔌 Connecting to Chroma (local storage: {storage_path})")
        self.client = PersistentClient(path=str(self.storage_path))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        print("✅ Connected to Chroma")

    def create_collection(self, recreate: bool = False):
        """Ensure collection exists (optionally recreating it)."""

        if recreate:
            print(f"🗑️  Deleting existing collection (if any): {self.collection_name}")
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                # If it doesn't exist yet, that's fine
                pass

        print(f"📦 Ensuring collection exists: {self.collection_name}")
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        print("✅ Collection ready")

    def add_documents(self, chunks: List[Dict], batch_size: int = 100):
        """Add document chunks to Chroma."""

        print("\n" + "=" * 60)
        print("Adding Documents to vector store (Chroma)")
        print("=" * 60 + "\n")

        print(f"Total chunks: {len(chunks)}")
        print(f"Batch size: {batch_size}\n")

        ids: List[str] = []
        embeddings: List[List[float]] = []
        documents: List[str] = []
        metadatas: List[Dict] = []

        def flush_batch():
            nonlocal ids, embeddings, documents, metadatas
            if not ids:
                return
            batch_idx = (total_added // batch_size) + 1
            print(f"📤 Uploading batch {batch_idx} ({len(ids)} points)...")
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
            ids, embeddings, documents, metadatas = [], [], [], []

        total_added = 0

        for i, chunk in enumerate(chunks):
            meta = chunk.get("metadata", {})

            ids.append(str(uuid4()))
            embeddings.append(chunk["embedding"])
            documents.append(chunk["text"])
            metadatas.append(
                {
                    "source": meta.get("source"),
                    "page": meta.get("page"),
                    "chunk_index": meta.get("chunk_index"),
                    "context": meta.get("context", ""),
                    "word_count": meta.get("word_count"),
                }
            )

            total_added += 1

            # Upload in batches
            if len(ids) >= batch_size or i == len(chunks) - 1:
                flush_batch()

        points_count = self.collection.count()

        print("\n" + "=" * 60)
        print(f"✅ Successfully added {points_count} documents")
        print("=" * 60 + "\n")

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.0,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Search for similar documents.

        Args:
            query_vector: Query embedding vector
            limit: Number of results to return
            score_threshold: Minimum similarity score (0-1, applied after conversion)
            filters: Optional filters (e.g., {'source': 'p519'})

        Returns:
            List of results with text and metadata
        """

        where = filters or None

        result = self.collection.query(
            query_embeddings=[query_vector],
            n_results=limit,
            where=where,
            include=["metadatas", "documents", "distances"],
        )

        # Chroma returns lists per query
        ids_list = result.get("ids", [[]])[0]
        docs_list = result.get("documents", [[]])[0]
        metas_list = result.get("metadatas", [[]])[0]
        dists_list = result.get("distances", [[]])[0]

        formatted_results: List[Dict] = []

        for _id, doc, meta, dist in zip(ids_list, docs_list, metas_list, dists_list):
            # Convert distance -> similarity in [0, 1], higher is better
            if dist is not None:
                similarity = 1.0 / (1.0 + float(dist))
            else:
                similarity = 1.0

            if score_threshold > 0 and similarity < score_threshold:
                continue

            meta = meta or {}
            formatted_results.append(
                {
                    "text": doc,
                    "metadata": {
                        "source": meta.get("source"),
                        "page": meta.get("page"),
                        "context": meta.get("context", ""),
                        "chunk_index": meta.get("chunk_index"),
                    },
                    "similarity": similarity,
                    "id": _id,
                }
            )

        return formatted_results

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""

        points_count = self.collection.count()

        return {
            "name": self.collection_name,
            "points_count": points_count,
            "vectors_count": points_count,
            "indexed_vectors_count": points_count,
        }


def main():
    """Initialize Qdrant and add documents"""
    
    # Load chunks with embeddings
    embeddings_file = Path('data/embeddings/chunks_with_embeddings.json')
    
    if not embeddings_file.exists():
        print(f"❌ Embeddings file not found: {embeddings_file}")
        print("Run: python src/core/embeddings.py")
        return
    
    print(f"📖 Loading chunks with embeddings from: {embeddings_file}")
    with open(embeddings_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks\n")
    
    # Initialize vector store
    vector_store = ChromaVectorStore(
        collection_name="tax_documents",
        storage_path="./qdrant_storage",
        embedding_dim=384  # all-MiniLM-L6-v2 dimension
    )
    
    # Create collection
    vector_store.create_collection(recreate=True)
    
    # Add documents
    vector_store.add_documents(chunks)
    
    # Show stats
    stats = vector_store.get_collection_stats()
    print("\nCollection Statistics:")
    print(f"  Name: {stats['name']}")
    print(f"  Total points: {stats['points_count']}")
    print(f"  Indexed vectors: {stats['indexed_vectors_count']}")
    
    print("\n✅ Vector store setup complete!")


if __name__ == "__main__":
    main()

# Backwards-compatible alias so other modules don't need to change imports
QdrantVectorStore = ChromaVectorStore