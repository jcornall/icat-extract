from icat_extract.models import InvestigationQueryParams

import logging


logger = logging.getLogger(__name__)


def build_investigation_query(params: InvestigationQueryParams) -> str:
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


# def investigations_by_rb(rb_number: str) -> str:
#     return (
#         "SELECT DISTINCT i "
#         "FROM Investigation i "
#         "WHERE i.name = '{rb}' "
#         "ORDER BY i.createTime DESC "
#         "INCLUDE "
#         "i.facility, "
#         "i.dataCollectionInvestigations.dataCollection, "
#         "i.samples.parameters, "
#         "i.type, "
#         "i.investigationInstruments, "
#         "i.studyInvestigations.study, "
#         "i.shifts, "
#         "i.fundingReferences, "
#         "i.investigationUsers.user, "
#         "i.keywords, "
#         "i.datasets, "
#         "i.publications, "
#         "i.investigationFacilityCycles.facilityCycle, "
#         "i.parameters.type"
#     ).format(rb=rb_number.replace("'", "''"))


# def investigations_by_instrument(instrument_name: str) -> str:
#     return (
#         "SELECT DISTINCT i "
#         "FROM Investigation i, InvestigationInstrument ii "
#         "WHERE ii.investigation = i "
#         "AND ii.instrument.fullName = '{instrument}' "
#         "ORDER BY i.createTime DESC "
#         "INCLUDE i.investigationInstruments.instrument"
#     ).format(instrument=instrument_name.replace("'", "''"))


# def investigations_by_user(user_name: str) -> str:
#     return (
#         "SELECT DISTINCT i "
#         "FROM Investigation i, InvestigationUser ii "
#         "WHERE ii.investigation = i "
#         "AND ii.user.fullName = '{user}' "
#         "ORDER BY i.createTime DESC "
#         "INCLUDE i.investigationUsers.user"
#     ).format(user=user_name.replace("'", "''"))


# def investigations_by_start_date(start_date: str) -> str:
#     return (
#         "SELECT DISTINCT i "
#         "FROM Investigation i "
#         "WHERE i.startDate >= '{start_date}' "
#         "ORDER BY i.startDate DESC "
#         "INCLUDE "
#         "i.facility, "
#         "i.type"
#     ).format(start_date=start_date)
