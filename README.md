# TaxBuddy

An AI-powered chatbot to help international students navigate U.S. tax filing.

## Tech Stack

- **Vector Database:** Qdrant (local)
- **LLM:** Llama 3.1 via LM Studio (local)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Framework:** LangChain
- **Interface:** Streamlit

## Project Structure
```
RAG/
├── data/                  # Data storage
│   ├── raw/              # Original documents
│   ├── processed/        # Cleaned documents
│   ├── chunked/          # Document chunks
│   └── embeddings/       # Generated embeddings
├── src/                   # Source code
│   ├── core/             # Core functionality
│   ├── scripts/          # Utility scripts
│   └── evaluation/       # Testing & evaluation
├── tests/                 # Unit tests
├── notebooks/            # Jupyter notebooks
├── config/               # Configuration files
├── qdrant_storage/       # Vector database storage
├── requirements.txt      # Python dependencies
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- LM Studio installed and running
- 8GB+ RAM recommended

### Installation

1. Clone the repository
```bash
git clone <your-repo-url>
cd RAG
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up LM Studio
- Download and install LM Studio
- Download Llama 3.1 model (8B recommended for consumer hardware)
- Start local server on port 1234

5. Run the application
```bash
streamlit run app.py
```

## Development Status

- [x] Step 1: Project setup
- [ ] Step 2: Data collection
- [ ] Step 3: Document processing
- [ ] Step 4: Vector database setup
- [ ] Step 5: LLM integration
- [ ] Step 6: RAG pipeline
- [ ] Step 7: UI development
- [ ] Step 8: Testing & evaluation

## License

MIT