"""
Re-apply text preprocessing to existing processed JSON and/or chunked JSON.
Use this when you have already run the pipeline once and want to clean
existing data without re-downloading or re-extracting PDFs.
"""

from pathlib import Path
import sys
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.text_preprocessor import preprocess_irs_text, preprocess_chunk_text


def repreprocess_processed_dir(processed_dir: str = "data/processed") -> int:
    """
    Re-preprocess all *_processed.json in processed_dir (in place).
    Returns number of files updated.
    """
    processed_dir = Path(processed_dir)
    if not processed_dir.exists():
        print(f"❌ Directory not found: {processed_dir}")
        return 0

    files = list(processed_dir.glob("*_processed.json"))
    if not files:
        print(f"No *_processed.json files in {processed_dir}")
        return 0

    print(f"Re-preprocessing {len(files)} processed document(s)...")
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            pages = json.load(f)
        updated = 0
        for page in pages:
            if "text" in page and page["text"]:
                old_len = len(page["text"])
                page["text"] = preprocess_irs_text(page["text"])
                if len(page["text"]) != old_len:
                    updated += 1
                if "word_count" in page:
                    page["word_count"] = len(page["text"].split())
        with open(path, "w", encoding="utf-8") as f:
            json.dump(pages, f, indent=2, ensure_ascii=False)
        print(f"  ✅ {path.name} ({updated} pages changed)")
    return len(files)


def repreprocess_chunks_file(chunks_path: str = "data/chunked/all_chunks.json") -> bool:
    """
    Re-preprocess all chunk texts in all_chunks.json (in place).
    Returns True if file was updated.
    """
    chunks_path = Path(chunks_path)
    if not chunks_path.exists():
        print(f"❌ File not found: {chunks_path}")
        return False

    print(f"Re-preprocessing chunks in {chunks_path}...")
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    updated = 0
    for chunk in chunks:
        if "text" in chunk and chunk["text"]:
            old = chunk["text"]
            chunk["text"] = preprocess_chunk_text(old)
            if chunk["text"] != old:
                updated += 1
            if "metadata" in chunk and "word_count" in chunk["metadata"]:
                chunk["metadata"]["word_count"] = len(chunk["text"].split())
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"  ✅ {updated} chunks updated")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Re-apply text preprocessing to existing data.")
    parser.add_argument("--processed", action="store_true", default=True,
                        help="Re-preprocess data/processed/*_processed.json (default: True)")
    parser.add_argument("--no-processed", action="store_false", dest="processed",
                        help="Skip processed documents")
    parser.add_argument("--chunks", action="store_true",
                        help="Re-preprocess data/chunked/all_chunks.json")
    parser.add_argument("--processed-dir", default="data/processed",
                        help="Directory containing *_processed.json")
    parser.add_argument("--chunks-file", default="data/chunked/all_chunks.json",
                        help="Path to all_chunks.json")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("TaxBuddy - Re-preprocess existing documents")
    print("=" * 60 + "\n")

    if args.processed:
        repreprocess_processed_dir(args.processed_dir)
    if args.chunks:
        repreprocess_chunks_file(args.chunks_file)

    if not args.processed and not args.chunks:
        print("Nothing to do. Use --chunks to also clean all_chunks.json.")
        print("After re-preprocessing processed docs, re-run chunking:")
        print("  python -m src.scripts.chunk_documents_only")
    else:
        print("\n✅ Done. If you re-preprocessed processed docs, run chunking to regenerate chunks:")
        print("  python -m src.scripts.chunk_documents_only")
        print("Then run setup_vector_db.py to refresh the vector database.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
