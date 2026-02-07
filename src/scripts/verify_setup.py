"""Verify all dependencies are installed correctly"""

def verify_setup():
    """Check if all required packages are available"""
    
    checks = []
    
    # Check LangChain
    try:
        import langchain
        checks.append(("✓", "LangChain", langchain.__version__))
    except ImportError as e:
        checks.append(("✗", "LangChain", f"Error: {e}"))
    
    # Check Qdrant
    try:
        from qdrant_client import QdrantClient
        checks.append(("✓", "Qdrant Client", "Installed"))
    except ImportError as e:
        checks.append(("✗", "Qdrant Client", f"Error: {e}"))
    
    # Check sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        checks.append(("✓", "Sentence Transformers", "Installed"))
    except ImportError as e:
        checks.append(("✗", "Sentence Transformers", f"Error: {e}"))
    
    # Check PyPDF
    try:
        import pdfplumber
        checks.append(("✓", "PDFPlumber", "Installed"))
    except ImportError as e:
        checks.append(("✗", "PDFPlumber", f"Error: {e}"))
    
    # Check Streamlit
    try:
        import streamlit
        checks.append(("✓", "Streamlit", streamlit.__version__))
    except ImportError as e:
        checks.append(("✗", "Streamlit", f"Error: {e}"))
    
    # Print results
    print("\n" + "="*60)
    print("TaxBuddy Setup Verification")
    print("="*60 + "\n")
    
    for status, package, version in checks:
        print(f"{status} {package:.<30} {version}")
    
    # Check if all passed
    all_passed = all(check[0] == "✓" for check in checks)
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ All dependencies installed successfully!")
    else:
        print("✗ Some dependencies are missing. Please check errors above.")
    print("="*60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    verify_setup()