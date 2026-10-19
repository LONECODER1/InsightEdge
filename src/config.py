import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM Config ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Quality-critical nodes (synthesis, risk, judge)
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "openai/gpt-oss-120b")

# Volume nodes (research + debate + reflection)
VOLUME_MODEL = os.getenv("VOLUME_MODEL", "openai/gpt-oss-20b")

# Temperature settings
ANALYST_TEMPERATURE = 0.1    # research agents need consistency
DEBATE_TEMPERATURE = 0.4     # debate agents benefit from some creativity
JUDGE_TEMPERATURE = 0.1      # judge needs to be deterministic

# --- Financial Data ---
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# --- Memory Config ---
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "./data/episodic_memory.db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # local, no API cost

# Timeliness decay: half-life ~14 days for market data
PROCEDURAL_DECAY_LAMBDA = 0.05

# --- Risk Thresholds ---
CVAR_THRESHOLD = -0.03        # -3% daily CVaR triggers risk flag
VOL_MULTIPLIER_THRESHOLD = 2.0  # 2x sector vol triggers flag
CVAR_WINDOW_DAYS = 252

# --- Token limits per role (controls LLM output length, saves tokens) ---
MAX_TOKENS: dict[str, int] = {
    "analyst":   1000,  # research agents — structured JSON output
    "debate":    1200,  # combined bull+bear+winner — needs more room
    "synthesis": 1000,  # merges 3 research outputs
    "risk":      1200,  # risk flags JSON — increased to prevent truncated output
    "judge":     1000,  # final decision JSON
    "reflection": 600,  # belief extraction
}

# --- CVRF Config ---
CVRF_LOOKBACK_DECISIONS = 10  # how many past decisions to analyze for belief extraction
CVRF_MAX_BELIEFS = 5          # max belief statements to extract per cycle

# --- SEC EDGAR ---
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "ai_hedge_fund contact@example.com")
SEC_FILINGS_DIR = os.getenv("SEC_FILINGS_DIR", "./data/sec_filings")
