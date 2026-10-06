# MotorGest Pro architecture — public overview

## Runtime model

MotorGest Pro is a Windows-oriented local-first desktop application. The complete private product uses a PySide6 `QWebEngineView` shell to host an HTML/CSS/JavaScript interface. JavaScript communicates with Python desktop services through Qt WebChannel; no internal HTTP server is required.

```text
Windows desktop
└── PySide6 / Qt WebEngine
    ├── HTML/CSS/JavaScript UI
    │   └── domain integrity helpers
    └── Qt WebChannel
        └── Python services
            ├── SQLite persistence
            ├── backups / restore
            ├── PDF / DOCX exports
            ├── privacy sanitization
            ├── SMTP / email verification
            └── logging / local OS services
```

## Persistence

The current compatibility schema stores the validated application state in SQLite using `app_state` and `metadata`. The database is created automatically in the user's Documents area and is never committed to the repository.

This design preserves compatibility with the historical application model while leaving room for incremental relational normalization if future commercial scale requires stronger SQL constraints and querying.

The public sample `src/motorgest/database.py` shows this persistence boundary.

## Business integrity

Complex domain rules are progressively isolated from the UI. The public `web/assets/integrity.js` sample includes testable rules for:

- compensating stock restoration when a source diagnostic/case is removed;
- payment-to-cash reconciliation;
- orphan-source cleanup;
- confirmed vs pending cash totals;
- protection of financial fields on automatic cash entries.

## Privacy boundary

The complete UI removes sensitive fields when preparing an external-analysis package, but privacy is enforced again in Python. This defense-in-depth boundary prevents the external package from relying solely on a frontend convention.

The public `src/motorgest/privacy.py` sample shows the Python-side sanitization logic.

## Security model

The complete private product includes password hashing, account lockout, role/action checks, email verification, rate limiting and Windows DPAPI protection for the SMTP password.

MotorGest Pro is currently a local desktop system rather than a remote multi-user server. UI permissions protect normal product workflows. Moving every privileged mutation behind a Python session-aware authorization service is documented as future hardening for a commercial multi-user deployment.

## Public/private source boundary

The public repository intentionally demonstrates representative engineering components. The complete frontend event layer, backend services and runtime assets remain in the private Full Source repository. See `PORTFOLIO_SCOPE.md`.
