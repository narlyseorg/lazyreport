from typing import List, Final, Optional
from .models import ReportSectionInfo, CvssField, CvssOption

## --- Core Application Settings ---
TEMPLATE_DOCX: Final[str] = "template.docx"
MODEL_NAME: Final[str] = "deepseek-ai/DeepSeek-V3.2-Exp"
HF_API_KEY: Final[Optional[str]] = None

## --- Feature Toggles ---
ENABLE_CVSS_INTERACTIVE: Final[bool] = True
ENABLE_SCOPE_INTERACTIVE: Final[bool] = True

# --- Parent Prompt Definitions ---
parentPrompt: Final[str] = """
You are an expert in writing executive technical summaries in Indonesian.
Write in a professional and technically clear style, accessible to both technical and managerial audiences.
Use direct paragraphs only — no headings, bullet points, or numbering.
Strictly prohibited awkwardly localized English terms (e.g., kueri, basis data, disaring [use query, database, difilter instead])
Vulnerability: {vulnerabilityName}
Condition: {condition}
{sectionPrompt}
"""

## --- Section Prompt Definitions ---
SECTIONS: Final[List[ReportSectionInfo]] = [
    ReportSectionInfo(
        marker="xXDESCXx",
        name="Description",
        prompt="Write a concise technical description of the vulnerability. Use one paragraph containing 3-4 sentences. RULES: Exclude impact, recommendation and POC."
    ),
    ReportSectionInfo(
        marker="xXIMPACTXx",
        name="Impact",
        prompt="Explain the technical impact of this vulnerability. Use two paragraphs, each with 2—3 sentences. Maintain a factual and professional tone with practical technical terms."
    ),
    ReportSectionInfo(
        marker="xXFIXXx",
        name="Recommendation",
        prompt="Provide technical mitigation. Use two paragraphs, each with 2—3 sentences. Focus on actionable and realistic measures. Do not explain the root cause or why it happens."
    ),
    ReportSectionInfo(
        marker="xXPOCXx",
        name="POC",
        prompt="Write a simple step-by-step POC to reproduce Vulnerability in one paragraph max (2—3 sentences) based on our POV. Based on Vulnerability and Condition above. Do not explain the root cause or why it happens."
    ),
    ## -- Reference must ignore parent prompt entirely --
    ReportSectionInfo(
        marker="xXREFXx",
        name="Reference",
        prompt="Provide between one and three concise references title only (no explanation) without bullet points or numbering. Focus on the vulnerability category. Use formats like: 'CWE-200: Exposure of Sensitive Information to an Unauthorized Actor' or 'OWASP A03:2021 — Injection' or 'CAPEC-103: Clickjacking'. Vulnerability : {vuln}. Condition : {cond}.",
        ignore=True
    )
]

## --- CVSS 4.0 Fields ---
CVSS4_FIELDS: Final[List[CvssField]] = [
    CvssField("Attack Vector (AV)", "AV", [CvssOption("Network", "N"), CvssOption("Adjacent", "A"), CvssOption("Local", "L"), CvssOption("Physical", "P")]),
    CvssField("Attack Complexity (AC)", "AC", [CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("Attack Requirements (AT)", "AT", [CvssOption("None", "N"), CvssOption("Present", "P")]),
    CvssField("Privileges Required (PR)", "PR", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("User Interaction (UI)", "UI", [CvssOption("None", "N"), CvssOption("Passive", "P"), CvssOption("Active", "A")]),
    CvssField("Confidentiality (VC)", "VC", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("Integrity (VI)", "VI", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("Availability (VA)", "VA", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("Confidentiality (SC)", "SC", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("Integrity (SI)", "SI", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("Availability (SA)", "SA", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
]

## --- CVSS 3.1 Fields ---
CVSS31_FIELDS: Final[List[CvssField]] = [
    CvssField("Attack Vector (AV)", "AV", [CvssOption("Network", "N"), CvssOption("Adjacent", "A"), CvssOption("Local", "L"), CvssOption("Physical", "P")]),
    CvssField("Attack Complexity (AC)", "AC", [CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("Privileges Required (PR)", "PR", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("User Interaction (UI)", "UI", [CvssOption("None", "N"), CvssOption("Required", "R")]),
    CvssField("Scope (S)", "S", [CvssOption("Unchanged", "U"), CvssOption("Changed", "C")]),
    CvssField("Confidentiality (C)", "C", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("Integrity (I)", "I", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
    CvssField("Availability (A)", "A", [CvssOption("None", "N"), CvssOption("Low", "L"), CvssOption("High", "H")]),
]
