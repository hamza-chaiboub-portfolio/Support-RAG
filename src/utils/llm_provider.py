"""LLM provider wrappers for OpenAI and Cohere"""

import logging
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM provider
        
        Args:
            api_key: API key for the provider
        """
        self.api_key = api_key
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text using LLM
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0-1)
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text with context for RAG
        
        Args:
            query: User query
            context: List of context documents
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated response with context
        """
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", base_url: Optional[str] = None):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-3.5-turbo, gpt-4, etc.)
            base_url: Optional custom base URL (e.g., for OpenRouter)
        """
        super().__init__(api_key)
        self.model = model
        self.base_url = base_url
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        except ImportError:
            raise ImportError("openai package not installed. Install: pip install openai")
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text using OpenAI
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated text
            
        Raises:
            Exception: If generation fails
        """
        try:
            logger.info(f"OpenAI generation with {self.model}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise Exception(f"OpenAI generation failed: {str(e)}")
    
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate response using OpenAI with context
        
        Args:
            query: User query
            context: List of context documents
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated response
        """
        # Build context string
        context_str = "\n\n".join(
            [f"Document {i+1}:\n{doc}" for i, doc in enumerate(context[:5])]
        )
        
        prompt = f"""Based on the following context, answer the user's question.
        
Context:
{context_str}

Question: {query}

Answer:"""
        
        return await self.generate(prompt, max_tokens, temperature, **kwargs)


class CohereProvider(BaseLLMProvider):
    """Cohere LLM provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "command"):
        """
        Initialize Cohere provider
        
        Args:
            api_key: Cohere API key
            model: Model to use
        """
        super().__init__(api_key)
        self.model = model
        
        try:
            import cohere
            self.client = cohere.AsyncClient(api_key=api_key)
        except ImportError:
            raise ImportError("cohere package not installed. Install: pip install cohere")
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text using Cohere
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated text
            
        Raises:
            Exception: If generation fails
        """
        try:
            logger.info(f"Cohere generation with {self.model}")
            
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return response.generations[0].text
            
        except Exception as e:
            logger.error(f"Cohere generation failed: {str(e)}")
            raise Exception(f"Cohere generation failed: {str(e)}")
    
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate response using Cohere with context
        
        Args:
            query: User query
            context: List of context documents
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated response
        """
        # Build context string
        context_str = "\n\n".join(
            [f"Document {i+1}:\n{doc}" for i, doc in enumerate(context[:5])]
        )
        
        prompt = f"""Based on the following context, answer the user's question.
        
Context:
{context_str}

Question: {query}

Answer:"""
        
        return await self.generate(prompt, max_tokens, temperature, **kwargs)


class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    @staticmethod
    def create_provider(
        provider_type: str,
        api_key: Optional[str] = None,
        **kwargs
    ) -> BaseLLMProvider:
        """
        Create an LLM provider
        
        Args:
            provider_type: Type of provider ("openai" or "cohere")
            api_key: API key for the provider
            **kwargs: Additional arguments (e.g., model)
            
        Returns:
            LLM provider instance
            
        Raises:
            ValueError: If provider type is unknown
        """
        if provider_type.lower() == "openai":
            return OpenAIProvider(api_key=api_key, **kwargs)
        elif provider_type.lower() == "cohere":
            return CohereProvider(api_key=api_key, **kwargs)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing"""
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate mock response
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Mock generated text
        """
        return "This is a mock response for testing purposes."
    
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate mock response with context
        
        Args:
            query: User query
            context: List of context documents
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Mock generated response
        """
        return f"Based on the provided context, here's the answer to '{query}': [mock response]"
