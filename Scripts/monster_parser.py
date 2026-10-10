import pypdf
import argparse
from typing import List, Dict, Any, Literal, Optional
import os
import re
from collections.abc import Callable


# Strategies
def _kobold_press(text: str) -> None:
    raise NotImplementedError("Kobold Press strategy is not implemented yet.")


def _tome_of_foes(text: str) -> None:
    raise NotImplementedError("Tome of Foes strategy is not implemented yet.")


def _fluffy_folio(text: str) -> None:
    return


def _default_strategy(text: str) -> None:
    raise NotImplementedError("Default strategy is not implemented yet.")


# Constants
VERBOSE = False
STRATEGIES = Literal["kobold press", "tome of foes", "fluffy folio"]
STRATEGY_HELPERS: Dict[STRATEGIES, Any] = {
    "kobold press": _kobold_press,
    "tome of foes": _tome_of_foes,
    "fluffy folio": _fluffy_folio,
}
STRATEGY_REGEXES: Dict[STRATEGIES, re.Pattern] = {
    "fluffy folio": r"fluffy folio",
}


# Logging
def _logger(
    message: str,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
) -> None:
    match level:
        case "DEBUG":
            if VERBOSE:
                print(f"[DEBUG] {message}")
        case "INFO":
            if VERBOSE:
                print(f"[INFO] {message}")
        case "WARNING":
            if VERBOSE:
                print(f"[WARNING] {message}")
        case "ERROR":
            print(f"[ERROR] {message}")
        case "CRITICAL":
            print(f"[CRITICAL] {message}")
        case _:
            return


def _select_strategy(text: str) -> Callable[[str], None]:
    for strategy, regex in STRATEGY_REGEXES.items():
        if re.search(regex, text, re.IGNORECASE):
            _logger(f"Selected strategy: {strategy}", "INFO")
            return STRATEGY_HELPERS[strategy]
    _logger("No matching strategy found. Using default strategy.", "WARNING")
    return _default_strategy


def _main(
    filename: Optional[str],
    directory: Optional[str],
    output: str,
    extension: str,
    verbose: bool,
):
    global VERBOSE
    VERBOSE = verbose

    pdf_files: List[str] = []
    if filename is not None:
        pdf_files.append(filename)
    else:
        for file in os.listdir(directory):
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(directory, file))
        _logger(f"Found {len(pdf_files)} PDF files in directory '{directory}'", "INFO")

    for pdf_file in pdf_files:
        _logger(f"Processing file: {pdf_file}", "INFO")

        reader = pypdf.PdfReader(pdf_file)
        _logger(f"Number of pages in PDF: {len(reader.pages)}", "INFO")

        strategy = _select_strategy(reader.pages[0].extract_text())
        for page in reader.pages:
            _logger(f"Processing page {reader.pages.index(page) + 1}", "INFO")
            text = page.extract_text()
            _logger(f"Extracted text: {text}", "DEBUG")
            strategy(text)

        _logger(f"Finished processing file: {pdf_file}", "INFO")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Parser to extract monsters from a PDF into a more manageable SQL format."
        )
    )

    parser.add_argument("-filename", type=str, help="File to process", default=None)
    parser.add_argument(
        "-directory",
        type=str,
        help="Directory to process [Defaults to current directory]",
        default=".",
    )
    parser.add_argument(
        "-output",
        type=str,
        help="Output file [Defaults to output._file_extension_]",
        default="output",
    )
    parser.add_argument(
        "-extension",
        type=str,
        help="Select what type of file to output [csv, sql]",
        default="sql",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase logs for debugging purposes",
        default=False,
    )

    _args = parser.parse_args()
    if _args.filename is None and _args.directory is None:
        raise ValueError(
            "You must provide either a filename or a directory to process."
        )
    if _args.filename is not None and _args.directory != ".":
        raise ValueError(
            "You cannot provide both a filename and a directory to process."
        )

    _logger("Starting monster parser...", "INFO")

    _main(**vars(_args))
