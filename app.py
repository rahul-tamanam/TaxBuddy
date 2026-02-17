"""
TaxBuddy - Streamlit Chat Interface
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.rag_pipeline import RAGPipeline

# Page config
st.set_page_config(
    page_title="TaxBuddy - Tax Assistant for International Students",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize RAG pipeline (cached)
@st.cache_resource
def load_rag_pipeline():
    """Load RAG pipeline (cached to avoid reloading)"""
    return RAGPipeline()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'user_context' not in st.session_state:
    st.session_state.user_context = {
        'visa_type': '',
        'country': '',
        'years_in_us': 0,
        'state': ''
    }

# Sidebar - User Context
with st.sidebar:
    st.header("👤 Your Information")
    st.caption("Help us provide better answers")
    
    visa_type = st.selectbox(
        "Visa Type",
        ["", "F-1", "J-1", "M-1", "Other"],
        key="visa_select"
    )
    
    country = st.selectbox(
        "Country of Origin",
        ["", "India", "China", "South Korea", "Canada", "Mexico", 
         "Germany", "Vietnam", "Taiwan", "Saudi Arabia", "Japan", 
         "Brazil", "Nigeria", "Pakistan", "Other"],
        key="country_select"
    )
    
    years_in_us = st.number_input(
        "Years in U.S.",
        min_value=0,
        max_value=10,
        value=0,
        key="years_select"
    )
    
    state = st.selectbox(
        "State of Residence",
        ["", "CA", "NY", "TX", "MA", "IL", "PA", "FL", "OH", "MI", "WA", "Other"],
        key="state_select"
    )
    
    # Update context
    st.session_state.user_context = {
        'visa_type': visa_type,
        'country': country,
        'years_in_us': years_in_us,
        'state': state
    }
    
    st.divider()
    
    # Quick questions
    st.subheader("💡 Common Questions")
    
    common_questions = [
        "Do I need to file Form 8843?",
        "What is the substantial presence test?",
        "Can I claim tax treaty benefits?",
        "What forms do I need to file?",
        "Do I need to pay Social Security tax?"
    ]
    
    for question in common_questions:
        if st.button(question, key=f"btn_{question}", use_container_width=True):
            st.session_state.messages.append({
                'role': 'user',
                'content': question
            })
            st.rerun()
    
    st.divider()
    
    # Reset button
    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main area
st.markdown('<div class="main-header">📋 TaxBuddy</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Tax Assistant for International Students</div>', unsafe_allow_html=True)

# Disclaimer
with st.expander("⚠️ Important Disclaimer - Read First", expanded=False):
    st.warning("""
    **This is an educational tool, not professional tax advice.**
    
    - Information provided is for general guidance only
    - Tax situations vary by individual circumstances
    - Always verify information with official IRS sources (irs.gov)
    - Consult a licensed tax professional for personalized advice
    - This tool does not file taxes or store your personal information
    
    By using this tool, you acknowledge these limitations.
    """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
        
        # Show sources if available
        if message['role'] == 'assistant' and 'sources' in message:
            with st.expander("📚 Sources", expanded=False):
                for i, source in enumerate(message['sources'], 1):
                    st.markdown(f"{i}. **{source['source']}** (Page {source['page']}) - Similarity: {source['similarity']:.2f}")

# Chat input
if prompt := st.chat_input("Ask a tax question..."):
    # Add user message
    st.session_state.messages.append({
        'role': 'user',
        'content': prompt
    })
    
    # Display user message
    with st.chat_message('user'):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message('assistant'):
        with st.spinner("🔍 Searching IRS documentation..."):
            try:
                # Load RAG pipeline
                rag = load_rag_pipeline()
                
                # Get answer
                result = rag.answer_question(
                    query=prompt,
                    user_context=st.session_state.user_context,
                    top_k=8,
                    verbose=False
                )
                
                # Display answer
                st.markdown(result['answer'])
                
                # Show confidence
                confidence_color = {
                    'high': '🟢',
                    'medium': '🟡',
                    'low': '🔴',
                    'none': '⚪'
                }
                
                st.caption(f"{confidence_color.get(result['confidence'], '⚪')} Confidence: {result['confidence']}")
                
                # Save assistant message with sources
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': result['answer'],
                    'sources': result['sources']
                })
                
            except Exception as e:
                # #region agent log
                try:
                    import json
                    from pathlib import Path
                    _logpath = Path.cwd() / ".cursor" / "debug.log"
                    _logpath.parent.mkdir(parents=True, exist_ok=True)
                    with open(_logpath, "a", encoding="utf-8") as _f:
                        _f.write(json.dumps({"id": "app_exception", "timestamp": __import__("time").time() * 1000, "location": "app.py:except", "message": "chatbot exception", "data": {"exception_type": type(e).__name__, "exception_msg": str(e)}, "hypothesisId": "C"}) + "\n")
                except Exception:
                    pass
                # #endregion
                error_msg = f"❌ Error: {str(e)}\n\nMake sure GROQ_API_KEY is set in .env (get a key at https://console.groq.com)."
                st.error(error_msg)
                
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': error_msg
                })

# Footer
st.divider()
st.caption("""
💡 **Tip**: Provide your visa type and country in the sidebar for more personalized answers.

🔗 **Official Resources**: [IRS.gov](https://www.irs.gov) | [Publication 519](https://www.irs.gov/publications/p519) | [Form 1040-NR](https://www.irs.gov/forms-pubs/about-form-1040-nr)

📊 **Stats**: {total_docs} documents indexed | Powered by Groq
""".format(total_docs=3580))