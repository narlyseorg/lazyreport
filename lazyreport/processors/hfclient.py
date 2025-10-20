import json
import time
import requests
from dataclasses import asdict
from typing import List
from ..models import AiRequest, AiMessage
from .. import config

HF_ENDPOINT = "https://router.huggingface.co/v1/chat/completions"

def generateSectionText(
    apiKey: str,
    vulnerabilityName: str,
    condition: str,
    sectionName: str,
    sectionPrompt: str
) -> str:
    
    ## Synchronous streaming POST to HF router. Returns generated text.
    ## Raises RuntimeError/ValueError on failure.
    
    sectionInfo = next((s for s in config.SECTIONS if s.name.lower() == sectionName.lower()), None)
    if sectionInfo is not None and getattr(sectionInfo, 'ignore', False):
        userPrompt = sectionInfo.prompt.format(vuln=vulnerabilityName, cond=condition)
    else:
        userPrompt = config.parentPrompt.format(
            vulnerabilityName=vulnerabilityName,
            condition=condition,
            sectionPrompt=sectionPrompt
        )

    requestBody = AiRequest(
        model=config.MODEL_NAME,
        stream=True,
        messages=[AiMessage(role="user", content=userPrompt)],
    )

    requestBodyDict = asdict(requestBody)

    headers = {
        "Authorization": f"Bearer {apiKey}",
        "Content-Type": "application/json",
    }

    with requests.post(HF_ENDPOINT, headers=headers, json=requestBodyDict, stream=True, timeout=120) as response:
        if response.status_code >= 400:
            raise RuntimeError(f" HF API error {response.status_code}: {response.text}")

        outputParts: List[str] = []
        time.sleep(0.5)

        for rawLine in response.iter_lines(decode_unicode=False):
            if not rawLine:
                continue

            line = rawLine.decode('utf-8').strip()
            if line.startswith("data: "):
                data = line.removeprefix("data: ").strip()
                if data == "[DONE]":
                    break
                try:
                    partial = json.loads(data)
                except json.JSONDecodeError:
                    continue

                choices = partial.get("choices")
                if isinstance(choices, list) and choices:
                    firstChoice = choices[0]
                    if isinstance(firstChoice, dict):
                        delta = firstChoice.get("delta", {})
                        if isinstance(delta, dict):
                            content = delta.get("content")
                            if isinstance(content, str) and content:
                                outputParts.append(content)
                                print(content, end="", flush=True)

        text = "".join(outputParts).strip()
        print()
        if not text:
            raise ValueError(f" No text generated for section {sectionName}")
        
        text = "\n".join([p.strip() for p in text.split("\n") if p.strip()])
        return text
