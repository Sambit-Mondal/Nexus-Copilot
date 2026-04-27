"""
LLM integration service using Groq API with streaming support.
Handles prompt generation, streaming responses, and error handling.
"""

from typing import AsyncGenerator, List, Optional
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from app.config import settings
from app.logger import get_logger
from app.exceptions import LLMError

logger = get_logger(__name__)


class LLMService:
    """Service for LLM-based response generation with streaming support."""

    def __init__(self):
        """Initialize Groq LLM client."""
        try:
            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY not set")

            logger.info(
                f"Initializing Groq LLM (model: {settings.groq_model}, "
                f"temperature: {settings.groq_temperature})"
            )

            self.llm = ChatGroq(
                api_key=settings.groq_api_key,
                model_name=settings.groq_model,
                temperature=settings.groq_temperature,
                streaming=True,
                max_tokens=2048,
            )

            logger.info("Groq LLM initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise LLMError(f"LLM initialization failed: {str(e)}")

    def build_rag_prompt(self, context: str, query: str) -> str:
        """
        Build detailed RAG prompt to prevent hallucinations.

        Args:
            context: Retrieved context chunks (concatenated)
            query: User's query

        Returns:
            Complete prompt text
        """
        prompt = f"""You are a professional financial advisor AI system for enterprise clients.

CRITICAL INSTRUCTIONS:
1. You MUST ONLY use information explicitly provided in the CONTEXT section below
2. NEVER invent, extrapolate, or assume any facts not mentioned in the context
3. If the context does not contain information needed to answer the query, respond with: "I don't have sufficient information to answer this question based on available documents."
4. When citing information, always reference the exact source document
5. Be precise with numerical data, dates, and financial figures
6. Acknowledge data limitations and uncertainty when appropriate
7. If information is partial or incomplete, state this clearly

CONTEXT FROM DOCUMENTS:
{context}

USER QUERY:
{query}

RESPONSE:
Please provide a detailed, accurate response based solely on the context provided above."""

        return prompt

    async def stream_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Stream LLM response token-by-token.

        Args:
            prompt: Full prompt text

        Yields:
            Response tokens as they are generated

        Raises:
            LLMError: If streaming fails
        """
        try:
            logger.info("Starting LLM streaming...")

            messages = [
                SystemMessage(
                    content="You are a professional financial advisor. Be accurate, precise, and honest."
                ),
                HumanMessage(content=prompt),
            ]

            # Stream from LLM
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content

            logger.info("LLM streaming completed successfully")

        except Exception as e:
            logger.error(f"LLM streaming failed: {str(e)}")
            raise LLMError(f"LLM streaming failed: {str(e)}")

    async def generate_response(self, prompt: str) -> str:
        """
        Generate complete LLM response (non-streaming).

        Args:
            prompt: Full prompt text

        Returns:
            Generated response text

        Raises:
            LLMError: If generation fails
        """
        try:
            logger.info("Generating LLM response...")

            messages = [
                SystemMessage(
                    content="You are a professional financial advisor. Be accurate, precise, and honest."
                ),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            result = response.content

            logger.info(f"LLM response generated ({len(result)} characters)")
            return result

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise LLMError(f"LLM generation failed: {str(e)}")

    def format_context(self, chunks: List) -> str:
        """
        Format retrieved chunks into context string.

        Args:
            chunks: List of Chunk objects from retriever

        Returns:
            Formatted context string with source attribution

        Raises:
            LLMError: If formatting fails
        """
        try:
            context_parts = []

            for i, chunk in enumerate(chunks, 1):
                # Format each chunk with source information
                source_info = f"[Source: {chunk.source}"
                if chunk.page:
                    source_info += f", Page {chunk.page}"
                source_info += f", Relevance: {chunk.score:.2%}]"

                formatted_chunk = f"{i}. {chunk.text}\n{source_info}"
                context_parts.append(formatted_chunk)

            context = "\n\n".join(context_parts)
            logger.debug(f"Formatted context ({len(context)} characters)")
            return context

        except Exception as e:
            logger.error(f"Context formatting failed: {str(e)}")
            raise LLMError(f"Context formatting failed: {str(e)}")

    def extract_citations(self, chunks: List) -> List[dict]:
        """
        Extract citations from retrieved chunks.

        Args:
            chunks: List of Chunk objects

        Returns:
            List of citation dictionaries with document, page, score

        Raises:
            LLMError: If extraction fails
        """
        try:
            citations = []

            for chunk in chunks:
                citation = {
                    "document": chunk.source,
                    "page": chunk.page,
                    "score": round(chunk.score, 4),
                }
                citations.append(citation)

            logger.debug(f"Extracted {len(citations)} citations")
            return citations

        except Exception as e:
            logger.error(f"Citation extraction failed: {str(e)}")
            raise LLMError(f"Citation extraction failed: {str(e)}")


# Global LLM service instance
_llm_service: LLMService = None


def get_llm_service() -> LLMService:
    """
    Get or create the global LLM service instance.

    Returns:
        LLMService instance (singleton)
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
