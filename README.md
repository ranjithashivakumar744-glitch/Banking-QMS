# Banking Software Quality Management System (QMS)

An MCA Software Quality Assurance prototype for **Team 3 – Banking and Financial Software**.

## What it demonstrates

The QMS supports the quality-management lifecycle:

**PLAN → DEFINE → EXECUTE → VERIFY → MEASURE → REPORT → IMPROVE**

Features:
- Dashboard with test pass rate, open critical defects, and pending requirement approvals.
- Requirement register with risk level, review notes, status, and named approver.
- Defect/non-conformance register with severity, owner, corrective action, and preventive action.
- Test execution register with Pass / Fail / Blocked results and evidence references.
- Document/configuration register with version, owner, status, and change notes.
- Release checklist and banking-specific quality metrics.
- SQLite database that is created automatically and seeded with demonstration records.

## Requirements

- Python 3.10 or newer recommended
- Internet is not required to run the application after Flask is installed; the visual font may fall back to a system font if offline.

## Run on Windows (VS Code / PowerShell)

1. Extract `Banking_QMS.zip`.
2. Open the extracted `Banking_QMS` folder in VS Code.
3. Open Terminal → New Terminal.
4. Check Python:
   ```powershell
   python --version
   ```
5. Create a virtual environment:
   ```powershell
   python -m venv venv
   ```
6. Activate it:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run this in the current terminal and retry:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   ```
7. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
8. Start the application:
   ```powershell
   python app.py
   ```
9. Open the local address printed in the terminal, normally:
   `http://127.0.0.1:5000`
10. Keep the terminal running while using the site. Press `Ctrl+C` to stop it.

## Important demo notes

- The first run creates `qms.db` and inserts sample requirements, defects, test runs, and document records.
- Data you add is saved locally in `qms.db` and remains after restarting the application.
- To reset to the original demo data, stop the app and delete `qms.db`. Run `python app.py` again.
- This is an academic prototype, not production software. It has no real banking integration, user authentication, role-based access control, or validated regulatory compliance. Do not enter real customer or financial information.

## Suggested demonstration sequence

1. Dashboard: explain quality objectives and release gate.
2. Requirements: add a high-risk business rule and show the review/approval workflow.
3. Defects: add a critical duplicate-transfer defect, record corrective and preventive actions, and explain why Critical defects block release.
4. Test Results: record a failed test and show how evidence is tracked.
5. Documents: add a new version of a test plan or requirements document.
6. QMS Process: explain lifecycle steps, release checks, metrics, and handling of unresolved high-severity defects.

## Banking-specific quality controls to explain

- Requirements with financial calculations, transfer limits, access permissions, privacy, auditability, and regulatory impact require stronger review and explicit approval.
- Critical defects can affect balances, duplicate or unauthorized transfers, major data exposure, or material financial loss. They block release.
- High-severity defects must be fixed or receive documented, authorized risk acceptance with compensating controls and an owner. A verbal approval is insufficient.
- Release checks include approved requirements, peer review, automated tests, security checks, transaction integrity/reconciliation, defect status, and rollback readiness.
- Configuration/document control ensures that the team tests and releases the intended approved versions and can trace changes to reviews, tests, and release evidence.
