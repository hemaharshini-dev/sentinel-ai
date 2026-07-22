import json
import re


def parse_json(text: str):

    text = text.strip()

    # Remove ```json or ```
    text = re.sub(r"^```(?:json)?", "", text)
    text = re.sub(r"```$", "", text)

    text = text.strip()

    return json.loads(text)