"""
PDF text extraction and processing for IRS tax documents
"""

import pdfplumber
from pathlib import Path
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from .text_preprocessor import preprocess_irs_text

@dataclass
class DocumentPage:
    """Represents a single page from a PDF"""
    page_number: int
    text: str
    tables: List[List[List[str]]]
    source_file: str
    word_count: int
    
    def to_dict(self):
        return asdict(self)

class PDFProcessor:
    """Extract and process text from IRS PDF documents"""
    
    def __init__(self, input_dir: str = 'data/raw/irs_pubs',
                 output_dir: str = 'data/processed'):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[DocumentPage]:
        """Extract text and tables from a PDF file"""
        
        print(f"📄 Processing: {pdf_path.name}")
        
        pages = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"   Pages: {total_pages}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text() or ""
                    
                    # Extract tables
                    tables = page.extract_tables() or []
                    
                    # Create page object
                    doc_page = DocumentPage(
                        page_number=page_num,
                        text=text,
                        tables=tables,
                        source_file=pdf_path.name,
                        word_count=len(text.split())
                    )
                    
                    pages.append(doc_page)
                
                print(f"   ✅ Extracted {len(pages)} pages")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
        
        return pages
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text from IRS documents using full preprocessing pipeline."""
        return preprocess_irs_text(text)
    
    def extract_section_headers(self, text: str) -> List[str]:
        """Extract section headers from text"""
        
        headers = []
        
        # Common IRS section patterns
        patterns = [
            r'^Chapter \d+\..*$',
            r'^Part [IVX]+\..*$',
            r'^Section \d+\..*$',
            r'^[A-Z][A-Z\s]{10,}$',  # ALL CAPS headers
        ]
        
        for line in text.split('\n'):
            line = line.strip()
            for pattern in patterns:
                if re.match(pattern, line):
                    headers.append(line)
                    break
        
        return headers
    
    def process_tables(self, tables: List[List[List[str]]]) -> str:
        """Convert table data to searchable text"""
        
        if not tables:
            return ""
        
        text_parts = []
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # Assume first row is header
            headers = table[0]
            rows = table[1:]
            
            # Convert to text format
            text_parts.append("\n[TABLE]")
            
            for row in rows:
                if len(row) == len(headers):
                    row_text = " | ".join([
                        f"{headers[i]}: {cell}" 
                        for i, cell in enumerate(row)
                        if cell and cell.strip()
                    ])
                    if row_text:
                        text_parts.append(row_text)
            
            text_parts.append("[/TABLE]\n")
        
        return "\n".join(text_parts)
    
    def process_single_pdf(self, pdf_path: Path) -> Optional[Path]:
        """Process a single PDF file"""
        
        # Extract pages
        pages = self.extract_text_from_pdf(pdf_path)
        
        if not pages:
            return None
        
        # Process each page
        processed_pages = []
        
        for page in pages:
            # Clean text
            cleaned_text = self.clean_text(page.text)
            
            # Process tables
            table_text = self.process_tables(page.tables)
            
            # Combine
            full_text = cleaned_text
            if table_text:
                full_text += "\n\n" + table_text
            
            # Update page
            processed_page = {
                'page_number': page.page_number,
                'text': full_text,
                'source_file': page.source_file,
                'word_count': len(full_text.split()),
                'has_tables': len(page.tables) > 0
            }
            
            processed_pages.append(processed_page)
        
        # Save processed document
        output_file = self.output_dir / f"{pdf_path.stem}_processed.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_pages, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Saved: {output_file.name}")
        
        return output_file
    
    def process_all_pdfs(self) -> List[Path]:
        """Process all PDFs in input directory"""
        
        print("\n" + "="*60)
        print("PDF Text Extraction & Processing")
        print("="*60 + "\n")
        
        pdf_files = list(self.input_dir.glob('*.pdf'))
        
        if not pdf_files:
            print("❌ No PDF files found in", self.input_dir)
            return []
        
        print(f"Found {len(pdf_files)} PDF files\n")
        
        processed_files = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"[{i}/{len(pdf_files)}]")
            output_file = self.process_single_pdf(pdf_file)
            if output_file:
                processed_files.append(output_file)
            print()
        
        # Summary
        print("="*60)
        print(f"✅ Processed {len(processed_files)} documents")
        print(f"📁 Output directory: {self.output_dir}")
        print("="*60 + "\n")
        
        return processed_files

def main():
    """Main execution"""
    processor = PDFProcessor()
    processor.process_all_pdfs()

if __name__ == "__main__":
    main()