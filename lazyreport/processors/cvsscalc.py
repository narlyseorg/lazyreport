from typing import Optional, Tuple
from cvss import CVSS3, CVSS4

def calculateScoreAndSeverity(vector: str) -> Tuple[Optional[float], Optional[str]]:

    ## Return (score, severity) tuple for a given CVSS vector string.
    ## Returns (None, None) if parsing fails or vector is not recognized.

    try:
        score: Optional[float] = None
        severity: Optional[str] = None
        
        if vector.startswith("CVSS:4.0/"):
            cvssObject = CVSS4(vector)
            score = cvssObject.scores()[0] if cvssObject.scores() else None
            severity = cvssObject.severities()[0] if cvssObject.severities() else None
        elif vector.startswith("CVSS:3.1/"):
            cvssObject = CVSS3(vector)
            score = cvssObject.scores()[0] if cvssObject.scores() else None
            severity = cvssObject.severities()[0] if cvssObject.severities() else None
            
        return score, severity
    except Exception:
        return None, None
