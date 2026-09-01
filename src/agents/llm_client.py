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

_model_logs: dict[str, deque] = {}


def _rate_guard(model_name: str, limit: int = 7000, estimated_tokens: int = 1500) -> None:
    if model_name not in _model_logs:
        _model_logs[model_name] = deque()
    log = _model_logs[model_name]

    now = time.time()
    while log and now - log[0][0] > 60:
        log.popleft()
    window_tokens = sum(t for _, t in log)
    if window_tokens + estimated_tokens > limit:
        wait = 61.0 - (now - log[0][0])
        if wait > 0:
            print(f"[rate-guard] {window_tokens} tokens in window for {model_name} — waiting {wait:.1f}s")
            time.sleep(wait)
    log.append((time.time(), estimated_tokens))


def get_llm(role: str = "analyst") -> BaseChatModel:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set in .env")

    temperature = _ROLE_TEMPS.get(role, ANALYST_TEMPERATURE)
    max_tok = MAX_TOKENS.get(role, 800)

    from langchain_groq import ChatGroq

    selected_model = VOLUME_MODEL if role in _VOLUME_ROLES else PRIMARY_MODEL
    
    # 7000 token limit to safely stay below 8000 TPM free tier caps
    _rate_guard(selected_model, limit=7000, estimated_tokens=max_tok + 500)

    return ChatGroq(
        model=selected_model,
        temperature=temperature,
        max_tokens=max_tok,
        max_retries=5,
        api_key=GROQ_API_KEY,
    )

