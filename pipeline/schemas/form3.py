FORM3_SCHEMA = {
    # Filing
    "document_type": None,
    "schema_version": None,
    "period_of_report": None,
    "no_securities_owned": None,

    # Issuer
    "issuer_name": None,
    "issuer_cik": None,
    "issuer_ticker": None,
    "issuer_foreign_ticker": None,

    # Primary Reporting Owner (first owner for convenience)
    "reporting_owner_name": None,
    "reporting_owner_cik": None,

    # All Reporting Owners
    "reporting_owners": [],

    # Holdings
    "non_derivative_holdings": [],
    "derivative_holdings": [],

    # Footnotes & Signatures
    "footnotes": [],
    "signatures": [],
}