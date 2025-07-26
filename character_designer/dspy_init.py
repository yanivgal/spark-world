import dspy
from dotenv import load_dotenv
import os
import threading
# Global variables to store the initialized DSPy and LM
_dspy_instance = None
_lm_instance = None
_init_lock = threading.Lock()
def get_dspy():
    """Initialize and configure DSPy with OpenAI GPT-4o-mini"""
    global _dspy_instance, _lm_instance
    # If already initialized, return the instances
    if _dspy_instance is not None and _lm_instance is not None:
        return _dspy_instance, _lm_instance
    # Use a lock to ensure thread-safe initialization
    with _init_lock:
        # Double-check after acquiring the lock
        if _dspy_instance is not None and _lm_instance is not None:
            return _dspy_instance, _lm_instance
        load_dotenv()
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        _lm_instance = dspy.LM('openai/gpt-4o-mini', api_key=OPENAI_API_KEY, cache=False)
        dspy.configure(lm=_lm_instance)
        dspy.settings.configure(track_usage=True)
        _dspy_instance = dspy
        return _dspy_instance, _lm_instance