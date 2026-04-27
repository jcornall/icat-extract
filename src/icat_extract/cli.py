import argparse
from datetime import datetime
from pathlib import Path

from icat_extract.config import load_config
from icat_extract.models import InvestigationQueryParams
from icat_extract.queries.investigations import build_investigation_query
from icat_extract.client import query_icat, write_to_csv

import sys
import logging


def configure_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Extract ICAT investigations")

    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--start-date")
    parser.add_argument("--instrument", action="append")

    parser.add_argument(
        "--rb-number", help="RB number / Investigation name (e.g. 2220008)"
    )

    parser.add_argument(
        "--include",
        action="append",
        help="Repeatable ICAT INCLUDE path (e.g. 'i.datasets')",
    )
    parser.add_argument(
        "--include-profile",
        choices=["minimal", "medium", "full"],
        help="Named INCLUDE profile",
    )

    parser.add_argument(
        "--force", action="store_true", help="Allow potentially expensive queries"
    )

    return parser.parse_args()


def resolve_params(args, config) -> InvestigationQueryParams:
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


def is_heavy_include(include_fields: list[str]) -> bool:
    return any(
        f.startswith("i.datasets") or f.startswith("i.samples") for f in include_fields
    )


def is_selective(params: InvestigationQueryParams) -> bool:
    return (
        params.rb_number is not None
        or params.start_date is not None
        or bool(params.instruments)
    )


def main():
    configure_logging(args.verbose)
    args = parse_args()
    config = load_config(args.config)

    params = resolve_params(args, config)

    if params.include_fields and is_heavy_include(params.include_fields):
        if not is_selective(params) and not args.force:
            print(
                "ERROR: Refusing to run unbounded query with deep INCLUDE graph.\n"
                "Add a filter (rb-number,start-date, instrument) or use --force.",
                file=sys.stderr,
            )
            sys.exit(2)

    jpql = build_investigation_query(params)

    print("Executing query with parameters:")
    print(params)
    print(jpql)

    results = query_icat(jpql)
    write_to_csv(results, "investigations.csv")


if __name__ == "__main__":
    main()
