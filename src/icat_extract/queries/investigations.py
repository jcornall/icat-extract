from icat_extract.models import InvestigationQueryParams

import logging


logger = logging.getLogger(__name__)


def build_investigation_query(params: InvestigationQueryParams) -> str:
    """
    Build an ICAT query string for retrieving investigations based on the provided parameters.
    The function constructs a WHERE clause based on the filters specified in the parameters.

    Parameters:
    - params: An instance of InvestigationQueryParams containing the query parameters

    Returns:
    - A string representing the ICAT query to retrieve investigations matching the parameters
    """
    where = []

    if params.rb_number:
        where.append(f"i.name = '{params.rb_number}'")

    if params.start_date:
        where.append(f"i.startDate >= '{params.start_date.isoformat()}'")

    if params.facility:
        where.append(f"i.facility.name = '{params.facility}'")

    if params.instruments:
        instruments = ",".join(f"'{i}'" for i in params.instruments)
        where.append(
            "i.id IN ("
            "SELECT ii.investigation.id "
            "FROM InvestigationInstrument ii "
            f"WHERE ii.instrument.fullName IN ({instruments})"
            ")"
        )

    if not where:
        raise ValueError("Refusing to build query with no WHERE clause")

    where_clause = " AND ".join(where)

    include_fields = params.include_fields or [
        "i.facility",
        "i.type",
    ]

    include_clause = ", ".join(include_fields)

    return (
        "SELECT DISTINCT i FROM Investigation i "
        f"WHERE {where_clause} "
        "ORDER BY i.startDate DESC "
        f"INCLUDE {include_clause}"
    )
