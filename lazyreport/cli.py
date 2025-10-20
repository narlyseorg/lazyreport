import sys
import shutil
import questionary
from typing import List, Optional, Any
from .models import Vulnerability, CvssField
from .processors.cvsscalc import calculateScoreAndSeverity
from . import config
from colorama import Fore, Style, init

init(autoreset=True)

def safeAsk(question: Any) -> Any:
    ## --- Wraps questionary calls to gracefully handle KeyboardInterrupt ---
    try:
        return question.unsafe_ask()
    except KeyboardInterrupt:
        print(Fore.RED + Style.BRIGHT + "\n\n Exiting lazyreport...\n")
        sys.exit(0)

def printTitle() -> None:
    ## --- Selects ASCII banner based on terminal size ---
    longTitle = r"""
  d6b
  66P                                                                           d6P
 d66                                                                         d666666P
 666   d666b6b  d66666P ?66   d6P   66bd66b d6666b?66,.d66b, d6666b   66bd66b  ?66'
 ?66  d6P' ?66     d6P' d66   66    66P'  `d6b_,dP`?66'  ?66d6P' ?66  66P'  `  66P
  66b 66b  ,66b  d6P'   ?6(  d66   d66     66b      66b  d6P66b  d66 d66       66b
   66b`?66P'`66bd66666P'`?66P'?6b d66'     `?666P'  666666P'`?6666P'd66'       `?6b
                               )66                  66P'
                              ,d6P                 d66
                           `?666P'                 ?6P
"""
    shortTitle = r"""
  d6b
  66P                                                  d6P
 d66                                                d666666P
 666  d66666P ?66   d6P   66bd66b?66,.d66b,  66bd66b  ?66'
 ?66     d6P' d66   66    66P'  ``?66'  ?66  66P'  `  66P
  66b  d6P'   ?6(  d66   d66       66b  d6P d66       66b
   66bd66666P'`?66P'?6b d66'       666666P'd66'       `?6b
                     )66           66P'
                    ,d6P          d66
                 `?666P'          ?6P
"""
    thresholdWidth = 85
    try:
        terminalSize = shutil.get_terminal_size(fallback=(80, 20)).columns
        asciiTitle = longTitle if terminalSize >= thresholdWidth else shortTitle
    except Exception:
        asciiTitle = shortTitle
    print(Fore.RED + Style.BRIGHT + asciiTitle)
    print(Fore.RED + " Reporting SUCKS.")
    print(Fore.RED + " Let the machine suffer instead.\n")

def getVulnerabilityCount() -> int:
    ## --- Prompts the user for the total number of vulnerabilities ---
    while True:
        try:
            numVuln = int(input(Fore.GREEN + Style.BRIGHT + " Total vulnerabilities?! "))
            if numVuln < 1:
                print(Fore.RED + " Please enter a number greater than 0.")
                continue
            return numVuln
        except (ValueError):
            print(Fore.RED + " Please enter a valid number.")

def collectVulnerabilities(count: int) -> List[Vulnerability]:
    ## --- Collects details for each vulnerability from the user ---
    vulnerabilities: List[Vulnerability] = []
    
    cvssVersion: Optional[str] = None
    if config.ENABLE_CVSS_INTERACTIVE:
        cvssVersion = safeAsk(questionary.select("CVSS Version:", choices=["4.0", "3.1"]))

    scopeType: Optional[str] = None
    fixedEndpoint: Optional[str] = None
    if config.ENABLE_SCOPE_INTERACTIVE:
        scopeType = safeAsk(questionary.select("Scope:", choices=["Fixed", "Adjustable"]))
        if scopeType == "Fixed":
            endpointValue = safeAsk(questionary.text("Endpoint:"))
            fixedEndpoint = '\n'.join([ep.strip() for ep in endpointValue.split(';') if ep.strip()])

    for i in range(count):
        print(Fore.BLUE + Style.BRIGHT + f"\n --- Vulnerability #{i+1} ---")
        
        while True:
            vulnName = input(Fore.GREEN + " Vulnerability name: " + Style.RESET_ALL)
            if vulnName.strip(): break
            print(Fore.RED + Style.BRIGHT + " Please enter vulnerability name.")
        
        condition = input(Fore.GREEN + " Condition: " + Style.RESET_ALL)
        
        scopeEndpoint = fixedEndpoint if scopeType == "Fixed" else None
        if scopeType == "Adjustable":
            endpointValue = input(Fore.GREEN + " Endpoint: " + Style.RESET_ALL)
            scopeEndpoint = '\n'.join([ep.strip() for ep in endpointValue.split(';') if ep.strip()])
            
        vector, score = None, None
        if config.ENABLE_CVSS_INTERACTIVE and cvssVersion:
            vector = _getVectorFromUser(cvssVersion)
            if vector:
                print(Fore.GREEN + f"\n Vector: {vector}")
                score, severity = calculateScoreAndSeverity(vector)
                if score is not None and severity is not None:
                    print(Fore.GREEN + f" Score: {score} ({severity})")
        
        vulnerabilities.append(Vulnerability(vulnName, condition, vector, scopeEndpoint, score))
        
    return vulnerabilities

def _getVectorFromUser(version: str) -> Optional[str]:
    ## --- Handles the interactive CVSS vector builder ---
    print()
    fields: List[CvssField] = config.CVSS4_FIELDS if version == "4.0" else config.CVSS31_FIELDS
    values = []
    
    for field in fields:
        choices = [opt.description for opt in field.options]
        chosenDesc = safeAsk(questionary.select(f"{field.label}", choices=choices))
        
        ## --- Find the code corresponding to the description ---
        chosenCode = next((opt.code for opt in field.options if opt.description == chosenDesc), None)
        if chosenCode:
            values.append((field.fieldName, chosenCode))
            
    if values:
        return f"CVSS:{version}/" + "/".join(f"{fname}:{code}" for fname, code in values)
    return None
