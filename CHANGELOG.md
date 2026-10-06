# Changelog — Portfolio Edition

## 3.1.4 — Public/private repository separation

- Added a dedicated public Portfolio Edition with selected real source modules and selected regression tests.
- Kept the complete runnable application in a separate private Full Source edition.
- Added six synthetic-data portfolio screenshots built from the actual MotorGest Pro visual system.
- Added `PORTFOLIO_SCOPE.md`, `CODE_SAMPLES.md` and a public architecture overview.
- Clarified proprietary licensing and third-party software boundaries.
- Reformatted the private Full Source `app.js` for code-review readability.
- Removed a duplicated legacy `renderCash()` declaration in the private Full Source application.

## 3.1.3 — Integrity and privacy hardening

- Added traceable stock reconciliation for case/unit/client deletion paths.
- Reconciled automatic cash movements when source payments are removed or reversed.
- Protected financial fields on payment-derived cash entries.
- Separated confirmed cash totals from pending/projection values.
- Added backend-enforced anonymization for external-analysis packages.
- Expanded regression coverage for stock, cash, privacy and backup/restore behavior.
