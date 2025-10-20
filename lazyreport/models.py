from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class CvssOption:
    ## --- Represents a single choice for a CVSS metric ---
    description: str
    code: str

@dataclass
class CvssField:
    ## --- Represents a CVSS metric field with its possible options ---
    label: str
    fieldName: str
    options: List[CvssOption]

@dataclass
class ReportSectionInfo:
    ## --- Configuration for a single section of the report ---
    marker: str
    name: str
    prompt: str
    ignore: bool = False

@dataclass
class Vulnerability:
    ## --- Holds all data for a single vulnerability ---
    name: str
    condition: str
    vector: Optional[str] = None
    scopeEndpoint: Optional[str] = None
    score: Optional[float] = None

@dataclass
class GeneratedFile:
    ## --- Tracks a generated output file and its associated score ---
    path: str
    score: float

@dataclass
class AiMessage:
    ## --- A message structure for the AI model API request ---
    role: str
    content: str

@dataclass
class AiRequest:
    ## --- Defines the request body for the AI model API ---
    model: str
    stream: bool
    messages: List[AiMessage]
    ## -- Output randomness and relevance controls --
    temperature: float = 0.6
    top_p: float = 0.3
