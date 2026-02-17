"""
Verify document processing results
"""

from pathlib import Path
import json

def verify_processing():
    """Verify all processing steps completed successfully"""
    
    print("\n" + "="*60)
    print("Document Processing Verification")
    print("="*60 + "\n")
    
    checks = []
    
    # Check processed documents
    processed_dir = Path('data/processed')
    if processed_dir.exists():
        processed_count = len(list(processed_dir.glob('*_processed.json')))
        checks.append(("✓" if processed_count > 0 else "✗",
                      "Processed Documents",
                      f"{processed_count} files"))
    else:
        checks.append(("✗", "Processed Documents", "Directory not found"))
    
    # Check chunks
    chunks_file = Path('data/chunked/all_chunks.json')
    if chunks_file.exists():
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        checks.append(("✓", "Document Chunks", f"{len(chunks)} chunks"))
    else:
        checks.append(("✗", "Document Chunks", "File not found"))
    
    # Check summary
    summary_file = Path('data/chunked/chunking_summary.json')
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        checks.append(("✓", "Chunking Summary", 
                      f"Avg size: {summary['avg_chunk_size']:.0f} chars"))
    else:
        checks.append(("✗", "Chunking Summary", "File not found"))
    
    # Print results
    for status, component, details in checks:
        print(f"{status} {component:.<30} {details}")
    
    all_passed = all(check[0] == "✓" for check in checks)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All processing steps completed successfully!")
        print("\nReady for Step 4: Vector Database Setup")
        
        # Show sample chunk
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            print("\nSample chunk:")
            print("-" * 60)
            sample = chunks[0]
            print(f"Source: {sample['metadata']['source']}")
            print(f"Page: {sample['metadata']['page']}")
            print(f"Text preview: {sample['text'][:200]}...")
            print("-" * 60)
    else:
        print("❌ Some processing steps failed.")
        print("\nRun: python src/scripts/process_documents.py")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    verify_processing()