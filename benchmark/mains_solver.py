from __future__ import annotations
"""LLM solver for UPSC Mains questions using LiteLLM.

Handles long-form subjective answers: essays (1000-1200 words) and
GS short answers (150-250 words).
"""

import os

from litellm import completion


SYSTEM_PROMPTS = {
    "mains_essay": (
        "You are taking the UPSC Civil Services Mains Essay paper. "
        "Write a well-structured essay of approximately {word_limit} words. "
        "Include an introduction with a clear thesis, body paragraphs with "
        "specific examples, data, and case studies from India and the world, "
        "and a balanced conclusion. Cover multiple perspectives. "
        "Do not use bullet points or numbered lists — write in continuous prose."
    ),
    "mains_gs1": (
        "You are taking UPSC Civil Services Mains General Studies Paper I "
        "(Indian Heritage & Culture, History, Geography, Society). "
        "Answer the following question in approximately {word_limit} words. "
        "Be specific, structured, and include relevant examples, historical "
        "references, data points, and case studies as appropriate."
    ),
    "mains_gs2": (
        "You are taking UPSC Civil Services Mains General Studies Paper II "
        "(Governance, Constitution, Polity, Social Justice, International Relations). "
        "Answer the following question in approximately {word_limit} words. "
        "Be specific, structured, and include relevant constitutional provisions, "
        "government schemes, committee recommendations, and international comparisons."
    ),
    "mains_gs3": (
        "You are taking UPSC Civil Services Mains General Studies Paper III "
        "(Technology, Economic Development, Biodiversity, Environment, Security, "
        "Disaster Management). Answer the following question in approximately "
        "{word_limit} words. Be specific, structured, and include relevant data, "
        "government policies, economic indicators, and technological developments."
    ),
    "mains_gs4": (
        "You are taking UPSC Civil Services Mains General Studies Paper IV "
        "(Ethics, Integrity, Aptitude). Answer the following question in "
        "approximately {word_limit} words. Demonstrate ethical reasoning, "
        "stakeholder analysis, and value-based decision making. For case studies, "
        "identify the ethical issues, stakeholders, options available, and recommend "
        "a course of action with justification."
    ),
}


QUESTION_TEMPLATE = """Question {number} ({max_marks} marks):

{question_text}

Write your answer in approximately {word_limit} words."""


def build_mains_prompt(question: dict) -> str:
    """Build the question prompt text for a Mains question.

    Args:
        question: Question dict from the Mains dataset.

    Returns:
        Formatted question prompt string.
    """
    return QUESTION_TEMPLATE.format(
        number=question["question_number"],
        max_marks=question["max_marks"],
        question_text=question["question_text"],
        word_limit=question["word_limit"],
    )


def build_mains_messages(question: dict) -> list[dict]:
    """Build LiteLLM messages for a Mains question.

    Args:
        question: Question dict from the Mains dataset.

    Returns:
        List of message dicts for LiteLLM.
    """
    paper = question["paper"]
    system_template = SYSTEM_PROMPTS.get(paper, SYSTEM_PROMPTS["mains_gs1"])
    system_prompt = system_template.format(word_limit=question["word_limit"])

    prompt_text = build_mains_prompt(question)

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt_text},
    ]


def solve_mains_question(
    question: dict,
    model: str,
    temperature: float = 0.0,
    max_tokens: int = 8192,
) -> dict:
    """Send a Mains question to an LLM and return the long-form response.

    Args:
        question: Question dict from the Mains dataset.
        model: LiteLLM model identifier.
        temperature: Sampling temperature.
        max_tokens: Maximum response tokens.

    Returns:
        Dict with 'question_id', 'raw_output', 'word_count', 'model', 'usage'.
    """
    messages = build_mains_messages(question)

    response = completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    raw_output = response.choices[0].message.content or ""
    word_count = len(raw_output.split())
    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return {
        "question_id": question["id"],
        "raw_output": raw_output,
        "word_count": word_count,
        "model": model,
        "usage": usage,
    }
