"""
Simple RAG test with one question at a time
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rag_pipeline import RAGPipeline

def test_single_question():
    """Test RAG with a single question"""
    
    print("\n" + "="*60)
    print("TaxBuddy - RAG Test")
    print("="*60 + "\n")
    
    # Initialize
    print("Initializing RAG pipeline...")
    rag = RAGPipeline()
    
    # Test question
    question = "Do F-1 students need to file Form 8843?"
    
    print(f"\nQuestion: {question}\n")
    
    # Get answer
    result = rag.answer_question(
        query=question,
        user_context={
            'visa_type': 'F-1',
            'country': 'India',
            'years_in_us': 2,
            'state': 'TX'
        },
        verbose=True
    )
    
    # Display result
    print("\n" + "="*60)
    print("ANSWER:")
    print("="*60)
    print(result['answer'])
    
    print("\n" + "="*60)
    print("SOURCES:")
    print("="*60)
    for i, source in enumerate(result['sources'], 1):
        print(f"{i}. {source['source']} (page {source['page']}) - similarity: {source['similarity']:.3f}")
    
    print("\n" + "="*60)
    print(f"Confidence: {result['confidence']}")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_single_question()