"""
LLM client for Groq (OpenAI-compatible API)
"""

import os
import json
from pathlib import Path
import httpx
from openai import OpenAI
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# #region agent log
try:
    _cwd = os.getcwd()
    _logpath = Path(_cwd) / ".cursor" / "debug.log"
    _logpath.parent.mkdir(parents=True, exist_ok=True)
    _env_path = Path(_cwd) / ".env"
    _key = os.getenv("GROQ_API_KEY") or ""
    with open(_logpath, "a", encoding="utf-8") as _f:
        _f.write(json.dumps({"id": "llm_import", "timestamp": __import__("time").time() * 1000, "location": "llm_client.py:after load_dotenv", "message": "env after load_dotenv", "data": {"cwd": _cwd, "env_path": str(_env_path), "env_exists": _env_path.exists(), "GROQ_API_KEY_set": bool(_key), "key_len": len(_key.strip()), "key_has_whitespace": _key != _key.strip()}, "hypothesisId": "A"}) + "\n")
except Exception:
    pass
# #endregion

# Groq OpenAI-compatible endpoint
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqClient:
    """Client for Groq cloud LLM (OpenAI-compatible API)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.1-8b-instant",
    ):
        """
        Initialize Groq client.

        Args:
            api_key: Groq API key (default: GROQ_API_KEY env var)
            model: Model name (e.g. llama-3.1-8b-instant, llama-3.3-70b-versatile)
        """
        # #region agent log
        try:
            _raw = api_key or os.getenv("GROQ_API_KEY") or ""
            _logpath = Path(os.getcwd()) / ".cursor" / "debug.log"
            _logpath.parent.mkdir(parents=True, exist_ok=True)
            with open(_logpath, "a", encoding="utf-8") as _f:
                _f.write(json.dumps({"id": "groq_init", "timestamp": __import__("time").time() * 1000, "location": "llm_client.py:GroqClient.__init__", "message": "GroqClient init", "data": {"api_key_passed": api_key is not None, "key_from_env_len": len(_raw), "key_stripped_len": len(_raw.strip()), "key_empty": not (_raw and _raw.strip())}, "hypothesisId": "B"}) + "\n")
        except Exception:
            pass
        # #endregion
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is required. Set it in .env or pass api_key=..."
            )
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        # Use explicit httpx client to avoid openai+httpx 0.28 "proxies" argument error
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=GROQ_BASE_URL,
            http_client=httpx.Client(),
        )

        print("🤖 LLM Client (Groq) initialized")
        print(f"   Model: {self.model}")

    def test_connection(self) -> bool:
        """Test if Groq API is reachable and key is valid."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )
            print("✅ Connection successful!")
            print(f"   Response: {response.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\nCheck that GROQ_API_KEY is set in .env and valid at https://console.groq.com")
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate response from LLM.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Creativity (0.0 = focused, 1.0 = creative)
            max_tokens: Maximum response length

        Returns:
            Generated text
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"Error generating response: {e}"

    def generate_with_context(
        self,
        query: str,
        context_chunks: List[Dict],
        user_info: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate answer using retrieved context (RAG).

        Args:
            query: User question
            context_chunks: Retrieved document chunks
            user_info: User context (visa, country, etc.)
            system_prompt: System instructions

        Returns:
            Generated answer
        """
        if not system_prompt:
            system_prompt = """You are a helpful AI assistant specialized in U.S. tax filing for international students on F-1 and J-1 visas.

Your role:
- Answer questions clearly and accurately based ONLY on the provided IRS documentation and reference data
- Be specific: quote exact form numbers (e.g. Form 8843, 1040-NR), dollar amounts, and conditions from the sources
- Cite every important fact with its source (e.g. "Publication 519, page 12" or "treaty_lookup - India")
- Use simple language suitable for non-native English speakers
- If the provided context does not clearly support an answer, say so explicitly and recommend consulting IRS.gov or a tax professional—do not guess or give vague generalities

Important:
- You provide educational information, NOT professional tax advice
- Do not generalize beyond what the sources say; when in doubt, state the limitation
- Always include a brief disclaimer that this is not professional tax advice"""

        context_text = "\n\n".join(
            [
                f"[Source: {chunk['metadata']['source']}, Page: {chunk['metadata']['page']}]\n{chunk['text']}"
                for chunk in context_chunks
            ]
        )

        profile_text = ""
        if user_info:
            profile_text = f"""User Profile:
- Visa Type: {user_info.get('visa_type', 'Not specified')}
- Country: {user_info.get('country', 'Not specified')}
- Years in U.S.: {user_info.get('years_in_us', 'Not specified')}
- State: {user_info.get('state', 'Not specified')}

"""

        prompt = f"""{profile_text}Relevant IRS Documentation and Reference Data:
{context_text}

User Question: {query}

Instructions:
1. Answer based ONLY on the text above. Do not add information from outside the provided context
2. Be specific: name forms, amounts, and conditions from the sources. Cite source and page (or reference name) for each fact
3. If the context does not contain enough information to answer, say "The provided sources do not clearly address this. Please check IRS.gov or a tax professional" instead of giving a vague answer
4. Keep the answer concise but complete. Use simple, clear language
5. End with: "This is educational information only, not professional tax advice"

Answer:"""

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=1024,
        )


def main():
    """Test Groq LLM client."""
    print("\n" + "=" * 60)
    print("Groq LLM Client Test")
    print("=" * 60 + "\n")

    try:
        client = GroqClient()
    except ValueError as e:
        print(f"❌ {e}")
        return

    print("\nTesting connection to Groq...")
    if not client.test_connection():
        return

    print("\n" + "=" * 60)
    print("Test: Simple Generation")
    print("=" * 60 + "\n")

    response = client.generate(
        prompt="What is the capital of France?",
        temperature=0.1,
        max_tokens=50,
    )
    print(f"Response: {response}")

    print("\n" + "=" * 60)
    print("Test: Tax Question (No Context)")
    print("=" * 60 + "\n")

    response = client.generate(
        prompt="Do F-1 students need to file taxes?",
        system_prompt="You are a tax assistant for international students.",
        temperature=0.1,
        max_tokens=200,
    )
    print(f"Response: {response}")

    print("\n✅ LLM client test complete!")


if __name__ == "__main__":
    main()
