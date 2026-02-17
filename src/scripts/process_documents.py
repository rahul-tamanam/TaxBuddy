"""
Complete document processing pipeline
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pdf_processor import PDFProcessor
from core.document_chunker import TaxDocumentChunker

try:
    from scripts.create_supplementary_chunks import create_supplementary_chunks
except ImportError:
    create_supplementary_chunks = None

def run_processing_pipeline():
    """Run complete document processing pipeline"""
    
    print("\n" + "="*60)
    print("TaxBuddy - Document Processing Pipeline")
    print("="*60 + "\n")
    
    # Step 1: Extract text from PDFs
    print("STEP 1: Extracting text from PDFs...")
    processor = PDFProcessor()
    processed_files = processor.process_all_pdfs()
    
    if not processed_files:
        print("❌ No documents processed. Exiting.")
        return
    
    print(f"✅ Step 1 complete: {len(processed_files)} documents processed\n")
    
    # Step 2: Chunk documents (larger chunks = more context per retrieval)
    print("STEP 2: Chunking documents...")
    chunker = TaxDocumentChunker(chunk_size=800, chunk_overlap=150)
    output_file = chunker.chunk_all_documents()
    
    if not output_file:
        print("❌ Chunking failed. Exiting.")
        return
    
    print(f"✅ Step 2 complete: Chunks saved to {output_file}\n")

    # Step 3: Create supplementary chunks (treaty + visa) for RAG
    if create_supplementary_chunks:
        print("STEP 3: Creating supplementary chunks (treaty + visa)...")
        try:
            supp_path = create_supplementary_chunks()
            print(f"✅ Step 3 complete: {supp_path}\n")
        except Exception as e:
            print(f"⚠️  Supplementary chunks skipped: {e}\n")
    else:
        print("STEP 3: Skipped (run from project root: python -m src.scripts.process_documents)\n")

    # Final summary
    print("="*60)
    print("✅ PROCESSING PIPELINE COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("  1. Review chunks: data/chunked/all_chunks.json")
    print("  2. Check summary: data/chunked/chunking_summary.json")
    print("  3. Proceed to Step 4: Vector Database Setup (run setup_vector_db.py)")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_processing_pipeline()