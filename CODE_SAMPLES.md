# Selected code samples

## `src/motorgest/database.py`

Demonstrates local SQLite initialization, schema metadata, validated JSON-state persistence, WAL configuration, integrity checks and backup/restore support while keeping runtime databases out of source control.

## `src/motorgest/privacy.py`

Demonstrates defense-in-depth sanitization for external analysis: credential removal, stable pseudonymous IDs, relationship preservation, direct-PII removal and cleanup of binary evidence fields.

## `src/motorgest/inspection_export.py`

Demonstrates production-style document generation in both PDF and DOCX, including local branding, image handling, A4 layout and structured inspection data.

## `web/assets/integrity.js`

Demonstrates pure/testable business rules outside the large UI event layer. It covers stock reversal, payment/cash reconciliation, confirmed-vs-pending totals and protected edits for automatic cash movements.

## `tests/`

The included tests target behavior rather than only static strings: stock restoration, orphan prevention, pending-cash exclusion, privacy redaction, SQLite backup/restore and document generation.
