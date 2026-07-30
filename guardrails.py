"""
guardrails.py - Lightweight input/output guardrails for the PPT Semantic RAG Chatbot

Implements 4 protection categories using LangChain-native primitives (reusing
sentence-transformers/all-MiniLM-L6-v2 and LangChain output parsers) to prevent extra model overhead:

  1. Prompt injection detection               (input guardrail, regex pattern matching)
  2. Off-topic query detection                (input guardrail, embedding similarity threshold)
  3. Hallucination / unsupported output check (output guardrail, embedding similarity threshold)
  4. Malformed output format detection        (output guardrail, LangChain OutputParser validation)
"""

import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.exceptions import OutputParserException

# -----------------------------------------------------------------------
# 1. PROMPT INJECTION DETECTION (input guardrail)
# -----------------------------------------------------------------------
INJECTION_PATTERNS = [
    r"ignore\s+(all|any|previous|prior)(\s+(all|any|previous|prior))*\s+instructions",
    r"disregard (the|your|all) (system|previous) prompt",
    r"you are now",
    r"act as (if|though)",
    r"pretend (you are|to be)",
    r"reveal (your|the) (system prompt|instructions)",
    r"what (is|are) your (system prompt|instructions)",
    r"forget (everything|all) (you|that)",
    r"new instructions?:",
    r"override (your|the) (rules|instructions|guidelines)",
]

def check_prompt_injection(question: str):
    """Returns (is_blocked: bool, reason: str|None). Evaluates ONLY current question."""
    q_lower = question.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, q_lower):
            return True, f"Detected prompt-injection pattern: '{pattern}'"
    return False, None


# -----------------------------------------------------------------------
# 2. OFF-TOPIC QUERY DETECTION (input guardrail)
# -----------------------------------------------------------------------
DOMAIN_REFERENCE_PHRASES = [
    "HSE Health Safety Environment Management System incident tracking",
    "PowerPoint slide content RAG chatbot retrieval",
    "Apache Solr vector search embeddings Ollama Llama",
    "authentication user management PostgreSQL FastAPI React",
]

OFF_TOPIC_THRESHOLD = 0.25  # below this cosine similarity to ALL reference phrases -> off-topic

def check_off_topic(question: str, embedding_model):
    """Returns (is_blocked: bool, reason: str|None, max_similarity: float)."""
    def cos_sim(v1, v2):
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = sum(a * a for a in v1) ** 0.5
        n2 = sum(b * b for b in v2) ** 0.5
        if n1 == 0 or n2 == 0:
            return 0.0
        return dot / (n1 * n2)

    q_vec = embedding_model.embed_query(question)
    sims = []
    for phrase in DOMAIN_REFERENCE_PHRASES:
        ref_vec = embedding_model.embed_query(phrase)
        sims.append(cos_sim(q_vec, ref_vec))

    max_sim = max(sims)
    if max_sim < OFF_TOPIC_THRESHOLD:
        return True, f"Question similarity to domain topics is only {max_sim:.3f} (threshold {OFF_TOPIC_THRESHOLD})", max_sim
    return False, None, max_sim


# -----------------------------------------------------------------------
# 3. HALLUCINATION / UNSUPPORTED OUTPUT DETECTION (output guardrail)
# -----------------------------------------------------------------------
FAITHFULNESS_THRESHOLD = 0.30  # below this, the answer doesn't align with retrieved context

def check_hallucination(answer: str, context: str, embedding_model):
    """Returns (is_flagged: bool, reason: str|None, faithfulness_score: float)."""
    def cos_sim(v1, v2):
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = sum(a * a for a in v1) ** 0.5
        n2 = sum(b * b for b in v2) ** 0.5
        if n1 == 0 or n2 == 0:
            return 0.0
        return dot / (n1 * n2)

    if not context.strip():
        return False, None, None

    ans_vec = embedding_model.embed_query(answer)
    ctx_vec = embedding_model.embed_query(context[:2000])
    score = cos_sim(ans_vec, ctx_vec)

    if score < FAITHFULNESS_THRESHOLD:
        return True, f"Answer has low semantic overlap with retrieved context (faithfulness={score:.3f})", score
    return False, None, score


# -----------------------------------------------------------------------
# 4. MALFORMED OUTPUT FORMAT DETECTION (LangChain-native output parser)
# -----------------------------------------------------------------------
class LangChainOutputValidator(StrOutputParser):
    """
    LangChain-native Output Validator & Parser.
    Inherits from LangChain's built-in StrOutputParser to validate LLM output structure.
    Validates that output is non-empty, meaningful, and free of prompt template leaks.
    """
    def parse(self, text: str) -> str:
        parsed_text = super().parse(text)
        if not parsed_text or not parsed_text.strip():
            raise OutputParserException("Empty or whitespace-only answer")
        if len(parsed_text.strip()) < 3:
            raise OutputParserException("Answer is too short to be meaningful")
        leak_markers = ["Conversation History", "Retrieved Context", "-----------------------------"]
        if any(marker in parsed_text for marker in leak_markers):
            raise OutputParserException("Answer appears to leak the internal prompt template")
        return parsed_text

def check_output_format(answer: str):
    """Returns (is_blocked: bool, reason: str|None) using LangChainOutputValidator."""
    validator = LangChainOutputValidator()
    try:
        validator.parse(answer)
        return False, None
    except OutputParserException as e:
        return True, str(e)
    except Exception as e:
        return True, str(e)


# -----------------------------------------------------------------------
# Convenience wrappers combining input and output checks
# -----------------------------------------------------------------------
def run_input_guardrails(question: str, embedding_model, context_question: str = None):
    """
    Runs all input guardrails in order.
    - Prompt injection is evaluated ONLY on raw question (current user input).
    - Off-topic query detection is evaluated on context_question if provided, else raw question.
    Returns (is_blocked, reason).
    """
    # 1. Prompt injection evaluates ONLY raw user question
    blocked, reason = check_prompt_injection(question)
    if blocked:
        return True, reason

    # 2. Off-topic detection evaluates expanded context query if provided
    query_to_check = context_question if (context_question and context_question.strip()) else question
    blocked, reason, sim = check_off_topic(query_to_check, embedding_model)
    if blocked:
        return True, reason

    return False, None


def run_output_guardrails(answer: str, context: str, embedding_model):
    """Runs all output guardrails in order. Returns (is_flagged, reason)."""
    blocked, reason = check_output_format(answer)
    if blocked:
        return True, reason

    flagged, reason, score = check_hallucination(answer, context, embedding_model)
    if flagged:
        return True, reason

    return False, None
