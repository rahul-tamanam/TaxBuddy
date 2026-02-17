# TaxBuddy

An AI-powered chatbot to help international students navigate U.S. tax filing.

## Tech Stack

- **Vector Database:** Qdrant (local)
- **LLM:** Groq (Llama 3.1 8B Instant via API)
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
- A [Groq](https://console.groq.com) API key (free tier available)
- 8GB+ RAM recommended for embeddings and Qdrant

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

4. Set up Groq API key  
   Copy `.env.example` to `.env` and add your key:
```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key
```
   Get a key at [console.groq.com](https://console.groq.com). Optionally set `GROQ_MODEL` in `.env` (default: `llama-3.1-8b-instant`).

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