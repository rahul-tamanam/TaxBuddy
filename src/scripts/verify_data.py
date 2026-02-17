"""
Verify all data has been collected properly
"""

from pathlib import Path
import json

def verify_data_collection():
    """Check if all required data is present"""
    
    print("\n" + "="*60)
    print("Data Collection Verification")
    print("="*60 + "\n")
    
    checks = []
    
    # Check IRS PDFs
    irs_dir = Path('data/raw/irs_pubs')
    if irs_dir.exists():
        pdf_count = len(list(irs_dir.glob('*.pdf')))
        checks.append(("✓" if pdf_count >= 5 else "✗", 
                      f"IRS PDFs", 
                      f"{pdf_count} files found"))
    else:
        checks.append(("✗", "IRS PDFs", "Directory not found"))
    
    # Check treaty data
    treaty_file = Path('data/processed/treaty_lookup.json')
    if treaty_file.exists():
        with open(treaty_file) as f:
            treaty_data = json.load(f)
        checks.append(("✓", "Treaty Database", f"{len(treaty_data)} countries"))
    else:
        checks.append(("✗", "Treaty Database", "File not found"))
    
    # Check visa data
    visa_file = Path('data/processed/visa_types.json')
    if visa_file.exists():
        with open(visa_file) as f:
            visa_data = json.load(f)
        checks.append(("✓", "Visa Database", f"{len(visa_data)} visa types"))
    else:
        checks.append(("✗", "Visa Database", "File not found"))
    
    # Print results
    for status, component, details in checks:
        print(f"{status} {component:.<30} {details}")
    
    all_passed = all(check[0] == "✓" for check in checks)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All data collected successfully!")
        print("\nNext step: Document Processing (Step 3)")
    else:
        print("❌ Some data is missing. Please run:")
        print("  python src/scripts/download_irs_docs.py")
        print("  python src/scripts/create_treaty_data.py")
        print("  python src/scripts/create_visa_data.py")
    print("="*60 + "\n")

if __name__ == "__main__":
    verify_data_collection()