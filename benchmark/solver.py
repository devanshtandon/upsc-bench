from __future__ import annotations
"""LLM solver for UPSC Bench questions using LiteLLM.

Handles both text-only and multimodal (image) question prompts.
"""

import base64
import os
from pathlib import Path

import litellm
from litellm import completion


SYSTEM_PROMPT = """You are taking the UPSC Civil Services Preliminary Examination. Answer each multiple-choice question by selecting exactly one option: A, B, C, or D.

Instructions:
- Read the question carefully
- Consider all options before answering
- State your final answer clearly as a single letter (A, B, C, or D)
- Format your answer as: "Answer: (X)" where X is your chosen option letter"""


QUESTION_TEMPLATE = """Question {number}:

{question_text}

Options:
(A) {option_a}
(B) {option_b}
(C) {option_c}
(D) {option_d}

Provide your answer."""


def build_prompt(question: dict) -> str:
    """Build the question prompt text.

    Args:
        question: Question dict from the dataset.

    Returns:
        Formatted question prompt string.
    """
    return QUESTION_TEMPLATE.format(
        number=question["question_number"],
        question_text=question["question_text"],
        option_a=question["options"]["a"],
        option_b=question["options"]["b"],
        option_c=question["options"]["c"],
        option_d=question["options"]["d"],
    )


def encode_image(image_path: str) -> str:
    """Encode an image file to base64 data URI.

    Args:
        image_path: Path to the image file.

    Returns:
        Base64-encoded data URI string.
    """
    suffix = Path(image_path).suffix.lower()
    mime_types = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
    mime = mime_types.get(suffix, "image/png")

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


def build_messages(question: dict, supports_vision: bool = True) -> list[dict]:
    """Build LiteLLM messages for a question.

    If the question has images and the model supports vision, images are
    included as base64-encoded content. Otherwise, image_description is
    used as text fallback.

    Args:
        question: Question dict from the dataset.
        supports_vision: Whether the model supports image inputs.

    Returns:
        List of message dicts for LiteLLM.
    """
    prompt_text = build_prompt(question)

    has_image = question.get("has_image", False)
    image_paths = question.get("image_paths", [])
    image_description = question.get("image_description", "")

    # Text-only path
    if not has_image or not image_paths or not supports_vision:
        if has_image and image_description:
            prompt_text += f"\n\n[Image description: {image_description}]"

        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text},
        ]

    # Multimodal path — build content array with text + images
    content = [{"type": "text", "text": prompt_text}]

    for img_path in image_paths:
        if os.path.exists(img_path):
            data_uri = encode_image(img_path)
            content.append({
                "type": "image_url",
                "image_url": {"url": data_uri},
            })
        elif image_description:
            content.append({
                "type": "text",
                "text": f"[Image not found. Description: {image_description}]",
            })

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]


def solve_question(
    question: dict,
    model: str,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    supports_vision: bool = True,
) -> dict:
    """Send a question to an LLM and return the response.

    Args:
        question: Question dict from the dataset.
        model: LiteLLM model identifier (e.g., "anthropic/claude-opus-4").
        temperature: Sampling temperature.
        max_tokens: Maximum response tokens.
        supports_vision: Whether the model supports image inputs.

    Returns:
        Dict with 'raw_output', 'model', 'usage' (tokens), 'question_id'.
    """
    messages = build_messages(question, supports_vision)

    response = completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    raw_output = response.choices[0].message.content or ""
    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return {
        "question_id": question["id"],
        "raw_output": raw_output,
        "model": model,
        "usage": usage,
    }
