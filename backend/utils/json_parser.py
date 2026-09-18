import json
import re


def parse_json(text: str):

    text = text.strip()

    # Strip markdown fences: ```json ... ``` or ``` ... ```
    text = re.sub(r"^```(?:json)?", "", text)
    text = re.sub(r"```$", "", text)

    text = text.strip()

    # Happy path: the text is already clean JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract the first {...} block in case the LLM
    # added explanatory text before or after the JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Nothing worked — raise a clear error with the raw output for debugging
    raise ValueError(
        f"LLM returned output that could not be parsed as JSON.\n"
        f"Raw output (first 400 chars):\n{text[:400]}"
    )
