import os
from typing import Type, Any
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_community.cache import SQLiteCache


def get_llm_client(use_cache: bool = True, with_retry: bool = True) -> BaseChatModel:
    """
    Get LLM client based on environment configuration.

    Uses LLM_MODEL env var to select LangChain model.
    Uses LLM_TEMPERATURE env var to set model temperature.
    Uses REQUEST_TIMEOUT env var for API timeout (default: 300s).
    Uses MAX_TOKENS env var for max tokens (default: 20000).
    Uses 'langgraph-cache.db' for disk-based LLM call caching.
    """
    cache = SQLiteCache("langgraph-cache.db")
    
    llm = init_chat_model(
        model=os.getenv("LLM_MODEL"),
        temperature=float(os.getenv("LLM_TEMPERATURE", 0.0)),
        timeout=float(os.getenv("REQUEST_TIMEOUT", 300)),
        max_tokens=int(os.getenv("MAX_TOKENS", 20000)),
        cache=cache if use_cache else None, # cache LLM output to save costs and time when reprocessing same doc
    )
    if with_retry:
        llm = llm.with_retry(stop_after_attempt=int(os.getenv("MAX_RETRIES", 3)))
    return llm


def get_structured_llm(output_model: Type[BaseModel], use_cache: bool = True) -> Any:
    """
    Get LLM configured for structured output.

    Returns LLM with .with_structured_output() applied for Pydantic model and with_retry() applied for retries.
    """
    client = get_llm_client(with_retry=False)
    llm = client.with_structured_output(output_model)
    return llm.with_retry(stop_after_attempt=int(os.getenv("MAX_RETRIES", 3)))
    # return llm
