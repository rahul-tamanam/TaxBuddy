"""
Run only the chunking step (and optional supplementary chunks).
Use after re-preprocessing data/processed JSON so you don't have to re-extract PDFs.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.document_chunker import TaxDocumentChunker

try:
    from scripts.create_supplementary_chunks import create_supplementary_chunks
except ImportError:
    create_supplementary_chunks = None


def main():
    print("\n" + "=" * 60)
    print("TaxBuddy - Chunk documents only")
    print("=" * 60 + "\n")

    chunker = TaxDocumentChunker(chunk_size=800, chunk_overlap=150)
    output_file = chunker.chunk_all_documents()
    if not output_file:
        print("❌ Chunking failed.")
        return

    if create_supplementary_chunks:
        print("Creating supplementary chunks (treaty + visa)...")
        try:
            create_supplementary_chunks()
        except Exception as e:
            print(f"⚠️  Supplementary chunks skipped: {e}")

    print("\n✅ Done. Next: run setup_vector_db.py to refresh the vector database.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
