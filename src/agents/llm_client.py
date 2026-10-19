"""
LLM client — two Groq models with separate daily token pools.

  llama-3.1-8b-instant   (500K tokens/day) → 'analyst', 'debate', 'reflection'
  llama-3.3-70b-versatile (100K tokens/day) → 'synthesis', 'risk', 'judge'

max_tokens capped per role to prevent runaway output and conserve daily budget.
Rate guard keeps each model under its per-minute token limit.
"""
import time
from collections import deque

from langchain_core.language_models import BaseChatModel

from src.config import (
    GROQ_API_KEY,
    PRIMARY_MODEL, VOLUME_MODEL,
    ANALYST_TEMPERATURE, DEBATE_TEMPERATURE, JUDGE_TEMPERATURE,
    MAX_TOKENS,
)

_VOLUME_ROLES = {"analyst", "debate", "reflection"}

_ROLE_TEMPS: dict[str, float] = {
    "analyst":    ANALYST_TEMPERATURE,
    "debate":     DEBATE_TEMPERATURE,
    "synthesis":  ANALYST_TEMPERATURE,
    "risk":       JUDGE_TEMPERATURE,
    "judge":      JUDGE_TEMPERATURE,
    "reflection": ANALYST_TEMPERATURE,
}

_primary_log: deque = deque()   # Primary pool
_volume_log:  deque = deque()   # Volume pool


def _rate_guard(log: deque, limit: int = 25000, estimated_tokens: int = 800) -> None:
    """Lightweight rate guard that tracks TPM without forcing multi-minute sleeps."""
    now = time.time()
    while log and now - log[0][0] > 60:
        log.popleft()
    window_tokens = sum(t for _, t in log)
    if window_tokens + estimated_tokens > limit:
        wait = min(61.0 - (now - log[0][0]), 2.0)  # Cap wait to max 2s instead of 60s
        if wait > 0:
            time.sleep(wait)
    log.append((time.time(), estimated_tokens))


def get_llm(role: str = "analyst") -> BaseChatModel:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set in .env")

    temperature  = _ROLE_TEMPS.get(role, ANALYST_TEMPERATURE)
    max_tok      = MAX_TOKENS.get(role, 800)

    from langchain_groq import ChatGroq

    if role in _VOLUME_ROLES:
        _rate_guard(_volume_log, limit=30000, estimated_tokens=max_tok)
        return ChatGroq(
            model=VOLUME_MODEL,
            temperature=temperature,
            max_tokens=max_tok,
            api_key=GROQ_API_KEY,
        )

    _rate_guard(_primary_log, limit=25000, estimated_tokens=max_tok)
    return ChatGroq(
        model=PRIMARY_MODEL,
        temperature=temperature,
        max_tokens=max_tok,
        api_key=GROQ_API_KEY,
    )
