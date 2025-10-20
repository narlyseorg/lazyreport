import os
import sys
import glob
import re
import zipfile
from docx import Document
from datetime import datetime
from typing import List, Dict
from . import cli, config
from .models import Vulnerability, GeneratedFile
from .processors import hfclient, cvsscalc, docxhandler
from colorama import Fore, Style

def run() -> None:
    ## --- Main application entry point ---
    try:
        try:
            print("\033c\033[3J", end="")
        except Exception:
            os.system('cls' if os.name == 'nt' else 'clear')

        cli.printTitle()

        if not _docxInput():
            return

        apiKey = _getApiKey()
        if not apiKey:
            print(Fore.RED + Style.BRIGHT + " Specify HF_API_KEY via environment or config.py.\n")
            return

        vulnerabilityCount = cli.getVulnerabilityCount()
        vulnerabilities = cli.collectVulnerabilities(vulnerabilityCount)

        reportService = docxhandler.ReportService()
        generatedFiles: List[GeneratedFile] = []

        for idx, vuln in enumerate(vulnerabilities, start=1):
            print(Fore.BLUE + Style.BRIGHT + f"\n Processing vulnerability #{idx}: {vuln.name}...")
            replacements = _generateReplacements(apiKey, vuln)

            outputPath = f"output-{idx}.docx"
            reportService.createVulnerabilityReport(
                config.TEMPLATE_DOCX,
                outputPath,
                replacements,
            )
            generatedFiles.append(GeneratedFile(path=outputPath, score=vuln.score if vuln.score is not None else -1.0))

        _finalizeReports(reportService, generatedFiles)
        _cleanup(generatedFiles)

        print(Fore.GREEN + Style.BRIGHT + " All done. Enjoy your ciggarette.\n")

    except KeyboardInterrupt:
        print(Fore.RED + Style.BRIGHT + "\n\n Exiting lazyreport...\n")
        sys.exit(0)

def _docxInput() -> bool:
    ## --- Validates the input .docx template file ---
    X = config.TEMPLATE_DOCX
    errorMsg = None

    if not os.path.exists(X):
        errorMsg = f"Cannot locate {X} in the current directory."
    else:
        try:
            with zipfile.ZipFile(X) as z:
                if "word/document.xml" not in z.namelist():
                    raise ValueError
            Document(X)
        except (zipfile.BadZipFile, ValueError):
            errorMsg = f"{X} is not a valid .docx file."
        except Exception:
            errorMsg = f"{X} is corrupt."

    if errorMsg:
        print(Fore.RED + Style.BRIGHT + f" {errorMsg}\n")
        return False

    return True

def _getApiKey() -> str:
    ## --- Retrieves the Hugging Face API key ---
    if config.HF_API_KEY and str(config.HF_API_KEY).strip():
        return str(config.HF_API_KEY).strip()
    return os.getenv("HF_API_KEY", "")

def _generateReplacements(apiKey: str, vuln: Vulnerability) -> Dict[str, str]:
    ## --- Generates all text and marker replacements for a single vulnerability ---
    sectionResults: Dict[str, str] = {}
    totalSections = len(config.SECTIONS)

    for i, sectionInfo in enumerate(config.SECTIONS, start=1):
        print(Fore.BLUE + f"\n [{i}/{totalSections}] Generating {sectionInfo.name}...")
        try:
            text = hfclient.generateSectionText(
                apiKey, vuln.name, vuln.condition, sectionInfo.name, sectionInfo.prompt
            )
            print(Fore.GREEN + f" [✓] {sectionInfo.name} done.")
            sectionResults[sectionInfo.marker] = text
        except Exception as e:
            print(Fore.RED + f" [x] {sectionInfo.name} failed: {e}")
            sectionResults[sectionInfo.marker] = f" Error: {e}"

    ## --- Static and CVSS-based replacements ---
    sectionResults["xXBUGXx"] = vuln.name
    sectionResults["xXSCOPEXx"] = vuln.scopeEndpoint if vuln.scopeEndpoint else ""

    if vuln.vector:
        sectionResults["xXVECTORXx"] = vuln.vector
        _addCvssMarkers(sectionResults, vuln.vector)
        _addCiaMarkers(sectionResults, vuln.vector)
        
    return sectionResults

def _addCvssMarkers(results: Dict[str, str], vector: str) -> None:
    ## --- Adds severity markers based on CVSS score ---
    score, severity = cvsscalc.calculateScoreAndSeverity(vector)
    if score is not None and severity is not None:
        scoreStr = f"{score} ({severity})"
        markerMap = {"none": "xXINFOXx", "low": "xXLOWXx", "medium": "xXMEDXx", "high": "xXHGHXx", "critical": "xXCRTXx"}
        sevKey = severity.lower()
        for key, marker in markerMap.items():
            results[marker] = scoreStr if key == sevKey else ""

def _addCiaMarkers(results: Dict[str, str], vector: str) -> None:
    ## --- Adds CIA impact markers based on the CVSS vector ---
    def getVectorValue(v: str, k: str) -> str:
        match = re.search(rf"{k}:([A-Z])", v)
        return match.group(1) if match else ""
    
    if vector.startswith("CVSS:4.0/"):
        results["xXVCXx"], results["xXVIXx"], results["xXVAXx"] = getVectorValue(vector, "VC"), getVectorValue(vector, "VI"), getVectorValue(vector, "VA")
        results["xXSCXx"], results["xXSIXx"], results["xXSAXx"] = getVectorValue(vector, "SC"), getVectorValue(vector, "SI"), getVectorValue(vector, "SA")
    elif vector.startswith("CVSS:3.1/"):
        results["xXCXx"], results["xXIXx"], results["xXAXx"] = getVectorValue(vector, "C"), getVectorValue(vector, "I"), getVectorValue(vector, "A")

def _finalizeReports(reportService: docxhandler.ReportService, files: List[GeneratedFile]) -> None:
    ## --- Merges or renames the generated docx files into a final report ---
    if not files: return
    
    nowStr = datetime.now().strftime("%Y%m%d%H%M%S")
    resultFile = f"result-{nowStr}.docx"
    
    if len(files) > 1:
        filePaths = [f.path for f in files]
        if config.ENABLE_CVSS_INTERACTIVE:
            sortedFiles = sorted(files, key=lambda x: x.score, reverse=True)
            sortedPaths = [f.path for f in sortedFiles]
            print(Fore.BLUE + Style.BRIGHT + f"\n Merging {len(sortedPaths)} files into {resultFile} (sorted by CVSS)...\n")
            reportService.mergeReports(sortedPaths, resultFile)
        else:
            print(Fore.BLUE + Style.BRIGHT + f"\n Merging {len(filePaths)} files into {resultFile}...\n")
            reportService.mergeReports(filePaths, resultFile)
        print(Fore.GREEN + Style.BRIGHT + f" [✓] All vulnerabilities merged into {resultFile}\n")
    else:
        os.rename(files[0].path, resultFile)
        print(Fore.GREEN + Style.BRIGHT + f"\n [✓] Only one vulnerability, saved as {resultFile}\n")

def _cleanup(files: List[GeneratedFile]) -> None:
    ## --- Removes temporary output-*.docx files ---
    for f in glob.glob("output-*.docx"):
        try:
            os.remove(f)
        except OSError as e:
            print(Fore.YELLOW + f" Could not remove temporary file {f}: {e}")

if __name__ == '__main__':
    run()

