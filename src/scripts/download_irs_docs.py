"""
Download IRS publications and forms for international student tax guidance
"""

import requests
from pathlib import Path
import time
from typing import Dict, List
import json

class IRSDocumentDownloader:
    """Download and organize IRS tax documents"""
    
    # Core IRS documents we need
    IRS_DOCUMENTS = {
        # Publications
        'p519': {
            'url': 'https://www.irs.gov/pub/irs-pdf/p519.pdf',
            'name': 'Publication 519 - U.S. Tax Guide for Aliens',
            'category': 'publication',
            'priority': 1
        },
        'p901': {
            'url': 'https://www.irs.gov/pub/irs-pdf/p901.pdf',
            'name': 'Publication 901 - U.S. Tax Treaties',
            'category': 'publication',
            'priority': 1
        },
        'p970': {
            'url': 'https://www.irs.gov/pub/irs-pdf/p970.pdf',
            'name': 'Publication 970 - Tax Benefits for Education',
            'category': 'publication',
            'priority': 2
        },
        
        # Form Instructions
        'i1040nr': {
            'url': 'https://www.irs.gov/pub/irs-pdf/i1040nr.pdf',
            'name': 'Form 1040-NR Instructions',
            'category': 'form_instructions',
            'priority': 1
        },
        'i8843': {
            'url': 'https://www.irs.gov/pub/irs-pdf/i8843.pdf',
            'name': 'Form 8843 Instructions',
            'category': 'form_instructions',
            'priority': 1
        },
        'i1042s': {
            'url': 'https://www.irs.gov/pub/irs-pdf/i1042s.pdf',
            'name': 'Form 1042-S Instructions',
            'category': 'form_instructions',
            'priority': 2
        },
        'i8233': {
            'url': 'https://www.irs.gov/pub/irs-pdf/i8233.pdf',
            'name': 'Form 8233 Instructions',
            'category': 'form_instructions',
            'priority': 3
        },
        
        # Blank Forms (for reference)
        'f1040nr': {
            'url': 'https://www.irs.gov/pub/irs-pdf/f1040nr.pdf',
            'name': 'Form 1040-NR',
            'category': 'blank_form',
            'priority': 3
        },
        'f8843': {
            'url': 'https://www.irs.gov/pub/irs-pdf/f8843.pdf',
            'name': 'Form 8843',
            'category': 'blank_form',
            'priority': 3
        },
    }
    
    def __init__(self, output_dir: str = 'data/raw/irs_pubs'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create metadata file to track downloads
        self.metadata_file = self.output_dir / 'download_metadata.json'
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load existing download metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save download metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def download_document(self, doc_id: str, doc_info: Dict) -> bool:
        """Download a single IRS document"""
        
        url = doc_info['url']
        name = doc_info['name']
        
        # Output filename
        output_file = self.output_dir / f"{doc_id}.pdf"
        
        # Skip if already downloaded
        if output_file.exists():
            print(f"⏭️  Skipping {doc_id} - Already exists")
            return True
        
        print(f"📥 Downloading: {name}...")
        print(f"   URL: {url}")
        
        try:
            # Download with timeout
            response = requests.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Get file size
            file_size = int(response.headers.get('content-length', 0))
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"   Size: {file_size_mb:.2f} MB")
            
            # Save file
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Update metadata
            self.metadata[doc_id] = {
                'name': name,
                'url': url,
                'category': doc_info['category'],
                'file_size_mb': file_size_mb,
                'download_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'file_path': str(output_file)
            }
            self._save_metadata()
            
            print(f"✅ Downloaded: {doc_id}.pdf")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {doc_id}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error saving {doc_id}: {e}")
            return False
    
    def download_all(self, priority_filter: int = None):
        """Download all IRS documents"""
        
        print("\n" + "="*60)
        print("IRS Document Downloader - TaxBuddy")
        print("="*60 + "\n")
        
        # Filter by priority if specified
        docs_to_download = self.IRS_DOCUMENTS.items()
        if priority_filter:
            docs_to_download = [
                (doc_id, info) for doc_id, info in docs_to_download
                if info['priority'] <= priority_filter
            ]
        
        total = len(docs_to_download)
        successful = 0
        failed = 0
        
        for i, (doc_id, doc_info) in enumerate(docs_to_download, 1):
            print(f"\n[{i}/{total}] Processing: {doc_id}")
            
            if self.download_document(doc_id, doc_info):
                successful += 1
            else:
                failed += 1
            
            # Be nice to IRS servers - wait between downloads
            if i < total:
                time.sleep(2)
        
        # Summary
        print("\n" + "="*60)
        print("Download Summary")
        print("="*60)
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Output directory: {self.output_dir}")
        print("="*60 + "\n")
        
        return successful, failed
    
    def list_downloaded(self):
        """List all downloaded documents"""
        print("\n" + "="*60)
        print("Downloaded IRS Documents")
        print("="*60 + "\n")
        
        if not self.metadata:
            print("No documents downloaded yet.")
            return
        
        for doc_id, info in self.metadata.items():
            print(f"📄 {doc_id}")
            print(f"   Name: {info['name']}")
            print(f"   Size: {info['file_size_mb']:.2f} MB")
            print(f"   Downloaded: {info['download_date']}")
            print()


def main():
    """Main execution"""
    
    # Create downloader
    downloader = IRSDocumentDownloader()
    
    # Download priority 1 & 2 documents (essential ones)
    print("Starting download of essential IRS documents...")
    print("This may take a few minutes depending on your connection.\n")
    
    successful, failed = downloader.download_all(priority_filter=2)
    
    # Show what was downloaded
    downloader.list_downloaded()
    
    if failed > 0:
        print(f"\n⚠️  {failed} downloads failed. You can re-run this script to retry.")
    else:
        print("\n🎉 All essential documents downloaded successfully!")


if __name__ == "__main__":
    main()