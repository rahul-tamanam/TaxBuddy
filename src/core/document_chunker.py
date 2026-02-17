"""
Intelligent document chunking for tax documents
"""

from pathlib import Path
import json
from typing import List, Dict
from dataclasses import dataclass
import re

from .text_preprocessor import preprocess_chunk_text

@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document"""
    text: str
    metadata: Dict
    chunk_id: str
    
    def to_dict(self):
        return {
            'text': self.text,
            'metadata': self.metadata,
            'chunk_id': self.chunk_id
        }

class TaxDocumentChunker:
    """Specialized chunker for tax documents"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Semantic separators for tax documents
        self.separators = [
            "\n## ",       # Major sections
            "\n### ",      # Subsections
            "\nExample",   # Examples
            "\nNote:",     # Notes
            "\n\n",        # Paragraphs
            ". ",          # Sentences
            " ",           # Words
        ]
    
    def split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separators"""
        
        # Base case: text is small enough
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []
        
        # Try each separator
        for separator in separators:
            if separator in text:
                splits = text.split(separator)
                chunks = []
                current_chunk = ""
                
                for split in splits:
                    # Add separator back (except for space)
                    if separator != " ":
                        split = separator + split if current_chunk else split
                    
                    # Check if adding this split exceeds chunk size
                    if len(current_chunk) + len(split) <= self.chunk_size:
                        current_chunk += split if separator == " " else (separator + split if current_chunk else split)
                    else:
                        # Save current chunk
                        if current_chunk.strip():
                            chunks.append(current_chunk)
                        
                        # Start new chunk with overlap
                        if self.chunk_overlap > 0 and current_chunk:
                            overlap_text = current_chunk[-self.chunk_overlap:]
                            current_chunk = overlap_text + split
                        else:
                            current_chunk = split
                
                # Add final chunk
                if current_chunk.strip():
                    chunks.append(current_chunk)
                
                return chunks
        
        # Fallback: split at chunk_size
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]
    
    def extract_context(self, text: str, page_num: int) -> str:
        """Extract section context from text"""
        
        # Look for section headers
        lines = text.split('\n')
        for line in lines[:5]:  # Check first few lines
            if re.match(r'^(Chapter|Part|Section|\d+\.)', line.strip()):
                return line.strip()
        
        return f"Page {page_num}"
    
    def chunk_document(self, doc_data: List[Dict], source_file: str) -> List[DocumentChunk]:
        """Chunk a processed document"""
        
        all_chunks = []
        chunk_counter = 0
        
        for page_data in doc_data:
            page_num = page_data['page_number']
            text = page_data['text']
            
            if not text.strip():
                continue

            # Normalize text for LLM readability (idempotent if already cleaned)
            text = preprocess_chunk_text(text)

            # Get context
            context = self.extract_context(text, page_num)

            # Split into chunks
            text_chunks = self.split_text(text, self.separators)

            for chunk_text in text_chunks:
                chunk_counter += 1
                
                # Create chunk
                chunk = DocumentChunk(
                    text=chunk_text,
                    metadata={
                        'source': source_file,
                        'page': page_num,
                        'chunk_index': chunk_counter,
                        'context': context,
                        'char_count': len(chunk_text),
                        'word_count': len(chunk_text.split())
                    },
                    chunk_id=f"{source_file}_{chunk_counter}"
                )
                
                all_chunks.append(chunk)
        
        return all_chunks
    
    def chunk_all_documents(self, input_dir: str = 'data/processed',
                           output_dir: str = 'data/chunked') -> Path:
        """Chunk all processed documents"""
        
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("\n" + "="*60)
        print("Document Chunking")
        print("="*60 + "\n")
        
        print(f"Chunk size: {self.chunk_size} characters")
        print(f"Chunk overlap: {self.chunk_overlap} characters\n")
        
        # Find all processed documents
        processed_files = list(input_dir.glob('*_processed.json'))
        
        if not processed_files:
            print(f"❌ No processed documents found in {input_dir}")
            return None
        
        print(f"Found {len(processed_files)} processed documents\n")
        
        all_chunks = []
        
        for i, json_file in enumerate(processed_files, 1):
            print(f"[{i}/{len(processed_files)}] Chunking: {json_file.stem}")
            
            # Load processed document
            with open(json_file, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
            
            # Extract source filename (remove _processed suffix)
            source_file = json_file.stem.replace('_processed', '')
            
            # Chunk document
            chunks = self.chunk_document(doc_data, source_file)
            
            print(f"   Created {len(chunks)} chunks")
            
            all_chunks.extend(chunks)
        
        # Save all chunks
        output_file = output_dir / 'all_chunks.json'
        
        chunks_dict = [chunk.to_dict() for chunk in all_chunks]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_dict, f, indent=2, ensure_ascii=False)
        
        # Create summary
        summary = {
            'total_chunks': len(all_chunks),
            'total_documents': len(processed_files),
            'avg_chunk_size': sum(len(c.text) for c in all_chunks) / len(all_chunks) if all_chunks else 0,
            'sources': list(set(c.metadata['source'] for c in all_chunks))
        }
        
        summary_file = output_dir / 'chunking_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("Chunking Summary")
        print("="*60)
        print(f"Total chunks: {summary['total_chunks']}")
        print(f"Documents processed: {summary['total_documents']}")
        print(f"Average chunk size: {summary['avg_chunk_size']:.0f} characters")
        print(f"\n📁 Output: {output_file}")
        print("="*60 + "\n")
        
        return output_file

def main():
    """Main execution"""
    chunker = TaxDocumentChunker(chunk_size=500, chunk_overlap=100)
    chunker.chunk_all_documents()

if __name__ == "__main__":
    main()