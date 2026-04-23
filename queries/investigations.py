def investigations_by_rb(rb_number: str) -> str:
    return (
        "SELECT DISTINCT i "
        "FROM Investigation i "
        "WHERE i.name = '{rb}' "
        "ORDER BY i.createTime DESC "
        "INCLUDE "
        "i.facility, "
        "i.dataCollectionInvestigations.dataCollection, "
        "i.samples.parameters, "
        "i.type, "
        "i.investigationInstruments, "
        "i.studyInvestigations.study, "
        "i.shifts, "
        "i.fundingReferences, "
        "i.investigationUsers.user, "
        "i.keywords, "
        "i.datasets, "
        "i.publications, "
        "i.investigationFacilityCycles.facilityCycle, "
        "i.parameters.type"
    ).format(rb=rb_number.replace("'", "''"))


def investigations_by_instrument(instrument_name: str) -> str:
    return (
        "SELECT DISTINCT i "
        "FROM Investigation i, InvestigationInstrument ii "
        "WHERE ii.investigation = i "
        "AND ii.instrument.fullName = '{instrument}' "
        "ORDER BY i.createTime DESC "
        "INCLUDE i.investigationInstruments.instrument"
    ).format(instrument=instrument_name.replace("'", "''"))


def investigations_by_user(user_name: str) -> str:
    return (
        "SELECT DISTINCT i "
        "FROM Investigation i, InvestigationUser ii "
        "WHERE ii.investigation = i "
        "AND ii.user.fullName = '{user}' "
        "ORDER BY i.createTime DESC "
        "INCLUDE i.investigationUsers.user"
    ).format(user=user_name.replace("'", "''"))


def investigations_by_start_date(start_date: str) -> str:
    return (
        "SELECT DISTINCT i "
        "FROM Investigation i "
        "WHERE i.startDate >= '{start_date}' "
        "ORDER BY i.startDate DESC "
        "INCLUDE "
        "i.facility, "
        "i.type"
    ).format(start_date=start_date)