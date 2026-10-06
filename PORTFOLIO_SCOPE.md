# Portfolio scope

This repository is a deliberately reduced **public Portfolio Edition** of MotorGest Pro V3.1.4.

## Included publicly

- project/version documentation;
- architecture overview;
- synthetic-data screenshots;
- SQLite persistence sample (`database.py`);
- privacy/anonymization sample (`privacy.py`);
- PDF/DOCX export sample (`inspection_export.py`);
- stock/cash integrity rules (`integrity.js`);
- regression tests for those selected areas;
- project logo used by the selected document-export test.

## Intentionally private

The private Full Source repository retains, among other components:

- the complete desktop entry point and Qt/WebChannel runtime;
- the full application frontend and UI event layer;
- the complete backend service layer;
- authentication and email-service implementation;
- all inspection templates and runtime UI assets;
- Windows launch/build tooling;
- the complete regression suite.

This separation is intentional. Missing full-application files in the public repository are not an incomplete upload or build error.

## Technical review

For a legitimate recruitment/code-review process, deeper access can be granted deliberately to the private Full Source repository rather than publishing the entire product implementation permanently.
