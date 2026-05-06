import argparse
from datetime import datetime
from pathlib import Path

from icat_extract.config import load_config
from icat_extract.models import InvestigationQueryParams
from icat_extract.queries.investigations import build_investigation_query
from icat_extract.client import query_icat, write_to_csv

import sys
import logging

logger = logging.getLogger(__name__)


def configure_logging(log_file: Path | None, verbose: bool):
    """
    Configure logging for the application.

    Parameters:
    - log_file: Optional path to a log file. If None, logs will only be output to the console.
    - verbose: If True, set log level to DEBUG. Otherwise, set to INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    logger.info("Logger initiated with level %s", logging.getLevelName(level))


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments using argparse.

    Returns:
    - An argparse.Namespace object containing the parsed arguments.
    """
    logger.info("Parsing command line arguments...")
    parser = argparse.ArgumentParser(
        description="A tool to extract investigation metadata from ICAT and write to CSV."
    )

    parser.add_argument(
        "--config",
        help="Path to config file",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--force",
        help="Allow potentially expensive queries",
        action="store_true",
    )
    parser.add_argument(
        "--verbose",
        help="Enable verbose logging",
        action="store_true",
    )
    parser.add_argument(
        "--log-file",
        help="Path to log file",
        type=Path,
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to write output CSV file",
        type=Path,
    )
    parser.add_argument(
        "--start-date",
        help="Start date for investigation search using ISO format (e.g. 2023-01-01)",
    )
    parser.add_argument(
        "--instrument",
        help="Instrument for investigation search",
        action="append",
    )
    parser.add_argument(
        "--rb-number",
        help="RB number / Investigation name (e.g. 2220008)",
    )
    parser.add_argument(
        "--include",
        help="Repeatable ICAT INCLUDE path (e.g. 'i.datasets')",
        action="append",
    )
    parser.add_argument(
        "--include-profile",
        help="Named INCLUDE profile",
        choices=["minimal", "medium", "full"],
    )

    return parser.parse_args()


def resolve_params(args, config) -> InvestigationQueryParams:
    """
    Resolve query parameters from command line arguments and config file.
    Command line arguments take precedence over config file values.

    Parameters:
     - args: Parsed command line arguments
     - config: Loaded configuration from file
    """
    start_date = None

    if args.start_date:
        start_date = datetime.fromisoformat(args.start_date)
    elif "start_date" in config.get("investigations", {}):
        start_date = datetime.fromisoformat(config["investigations"]["start_date"])

    instruments = (
        args.instrument
        if args.instrument
        else config["investigations"].get("instruments", [])
    )

    rb_number = (
        args.rb_number
        if args.rb_number
        else config.get("investigations", {}).get("rb_number")
    )

    include_fields = None

    if args.include:
        include_fields = args.include
    elif args.include_profile:
        include_fields = (
            config.get("investigations", {})
            .get("include_profiles", {})
            .get(args.include_profile)
        )
    else:
        include_fields = config.get("investigations", {}).get("include")

    return InvestigationQueryParams(
        start_date=start_date,
        instruments=instruments,
        facility=config["icat"].get("facility"),
        include_fields=include_fields,
        rb_number=rb_number,
    )


def resolve_output_dir(args, config: dict) -> Path:
    """
    Resolve the output directory for the CSV file from command line arguments and config file.
    Command line arguments take precedence over config file values.

    Parameters:
     - args: Parsed command line arguments
     - config: Loaded configuration from file

    Returns:
     - A Path object representing the resolved output directory
    """
    if args.output_dir:
        return args.output_dir
    output_cfg = config.get("output", {})
    if "lake_root" in output_cfg:
        return Path(output_cfg["lake_root"])
    return Path.cwd() / "results"


def is_heavy_include(include_fields: list[str]) -> bool:
    """
    Determine if the INCLUDE fields indicate a potentially expensive query.
    For example, including datasets or samples can lead to large result sets.

    Parameters:
     - include_fields: List of INCLUDE paths specified in the query parameters

    Returns:
     - True if the INCLUDE fields suggest a heavy query, False otherwise
    """
    return any(
        f.startswith("i.datasets") or f.startswith("i.samples") for f in include_fields
    )


def is_selective(params: InvestigationQueryParams) -> bool:
    """
    Determine if the query parameters include any filters that would limit the result set.
    This is used to prevent running unbounded queries with heavy INCLUDE graphs.

    Parameters:
    - params: The resolved query parameters

    Returns:
    - True if the query is selective, False otherwise
    """
    return (
        params.rb_number is not None
        or params.start_date is not None
        or bool(params.instruments)
    )


def main():

    args = parse_args()
    logger.info("Command line arguments parsed successfully.")
    config = load_config(args.config)
    logger.info(f"Configuration loaded successfully from {args.config}")

    configure_logging(args.log_file, args.verbose)
    logger.info("Logging configured successfully.")

    params = resolve_params(args, config)
    logger.info(f"Resolved query parameters: {params}")

    if params.include_fields and is_heavy_include(params.include_fields):
        if not is_selective(params) and not args.force:
            print(
                "ERROR: Refusing to run unbounded query with deep INCLUDE graph.\n"
                "Add a filter (rb-number,start-date, instrument) or use --force.",
                file=sys.stderr,
            )
            sys.exit(2)

    jpql = build_investigation_query(params)

    logger.info(f"Executing ICAT query: {jpql}")
    results = query_icat(jpql, config["icat"])
    logger.info("ICAT query executed successfully.")

    output_dir = resolve_output_dir(args, config)
    logger.info(f"Resolved output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "investigations.csv"
    write_to_csv(results, output_file)
    logger.info("Results written to CSV successfully.")


if __name__ == "__main__":
    sys.exit(main())
