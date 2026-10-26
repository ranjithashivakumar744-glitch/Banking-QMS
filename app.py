from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "qms.db"
app = Flask(__name__)
app.secret_key = "banking-qms-demo-key-change-for-production"

QUALITY_OBJECTIVES = [
    ("Protect financial correctness", "Prevent incorrect balances, duplicate transfers, and invalid transaction amounts."),
    ("Protect customer data", "Ensure access control, privacy, and secure handling of customer information."),
    ("Meet regulatory and audit needs", "Keep approved requirements, review records, test evidence, and release decisions traceable."),
    ("Find defects early", "Review requirements and designs before implementation and test high-risk rules."),
    ("Control releases", "Block releases when critical defects or mandatory verification activities remain unresolved."),
]

QUALITY_FACTORS = [
    ("Correctness", "Balances, fees, interest, transfer limits, and loan calculations match approved rules."),
    ("Security", "Authentication, authorization, session handling, and sensitive-data protection."),
    ("Reliability", "Transactions are consistent, recoverable, and not duplicated."),
    ("Usability", "Customers can understand transaction status, errors, and confirmations."),
    ("Performance", "Account and transaction operations meet agreed response-time targets."),
    ("Maintainability", "Code, configuration, and requirements are traceable and controlled."),
]

RELEASE_CHECKS = [
    ("Approved requirements and business rules", "Requirements with financial, security, or regulatory impact have named approval."),
    ("Peer review completed", "High-risk code changes have independent review and recorded evidence."),
    ("Automated tests passed", "Unit, integration, and regression tests pass for the release candidate."),
    ("Security checks completed", "No unresolved critical/high security findings without formally approved exception."),
    ("Reconciliation and transaction integrity verified", "Balance updates, rollback, duplicate prevention, and audit records are tested."),
    ("No open Critical defects", "Critical defects block release."),
    ("High defects resolved or formally accepted", "Any exception has documented risk, compensating control, owner, and approval."),
    ("Deployment and rollback plan approved", "Version, configuration, backup, monitoring, and rollback steps are documented."),
]

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, category TEXT NOT NULL, risk TEXT NOT NULL,
            description TEXT NOT NULL, owner TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending Review',
            approver TEXT DEFAULT '', review_notes TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS defects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, category TEXT NOT NULL, severity TEXT NOT NULL,
            description TEXT NOT NULL, found_in TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open', owner TEXT NOT NULL,
            corrective_action TEXT DEFAULT '', preventive_action TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, doc_type TEXT NOT NULL, version TEXT NOT NULL,
            owner TEXT NOT NULL, status TEXT NOT NULL, notes TEXT DEFAULT '',
            updated_at TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS test_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL, area TEXT NOT NULL, result TEXT NOT NULL,
            evidence TEXT DEFAULT '', run_date TEXT NOT NULL
        )""")
        # Seed sample data only when tables are empty, so the demo opens with useful records.
        if con.execute("SELECT COUNT(*) FROM requirements").fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            seed_reqs = [
                ("Funds transfer validation", "Financial business rule", "Critical", "Reject transfers above available balance and prevent duplicate processing.", "Business Analyst", "Approved", "Product Owner", "Reviewed against transfer policy and ledger consistency rules."),
                ("Multi-factor authentication", "Security", "High", "Require approved authentication controls for sensitive account operations.", "Security Lead", "Pending Review", "", ""),
                ("Loan interest calculation", "Financial business rule", "Critical", "Calculate interest using the approved rate, schedule, rounding, and repayment rules.", "Loan Product Owner", "Pending Review", "", ""),
            ]
            con.executemany("""INSERT INTO requirements
                (title,category,risk,description,owner,status,approver,review_notes,created_at)
                VALUES (?,?,?,?,?,?,?,?,?)""", [(*r, now) for r in seed_reqs])
        if con.execute("SELECT COUNT(*) FROM defects").fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            seed_defects = [
                ("Transfer can be submitted twice", "Transaction integrity", "Critical", "Repeated click may create duplicate transfer requests.", "Integration Testing", "Open", "Payments Team", "", "", now),
                ("Incorrect loan interest rounding", "Business rule", "High", "Interest total differs from approved rounding rule for a sample repayment schedule.", "System Testing", "In Progress", "Loans Team", "Add boundary tests and correct rounding implementation.", "Add loan-calculation examples to review checklist.", now),
                ("Transaction history date filter", "Usability / functional", "Medium", "End-date transactions are omitted in one timezone scenario.", "System Testing", "Open", "Digital Banking Team", "", "", now),
            ]
            con.executemany("""INSERT INTO defects
                (title,category,severity,description,found_in,status,owner,corrective_action,preventive_action,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)""", seed_defects)
        if con.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            seed_docs = [
                ("Banking requirements specification", "Requirements", "v1.2", "Business Analyst", "Approved", "Controlled baseline; changes require impact analysis.", now),
                ("Transfer test plan", "Test Plan", "v0.9", "QA Lead", "In Review", "Includes duplicate, limit, insufficient-funds, and rollback cases.", now),
                ("Release checklist", "Procedure", "v1.0", "Release Manager", "Approved", "Must be completed before production release.", now),
            ]
            con.executemany("""INSERT INTO documents
                (name,doc_type,version,owner,status,notes,updated_at)
                VALUES (?,?,?,?,?,?,?)""", seed_docs)
        if con.execute("SELECT COUNT(*) FROM test_runs").fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d")
            seed_tests = [
                ("Transfer within limit", "Funds Transfer", "Pass", "Test evidence: TX-001"),
                ("Transfer above balance", "Funds Transfer", "Pass", "Test evidence: TX-002"),
                ("Duplicate transfer request", "Transaction Integrity", "Fail", "Test evidence: TX-003"),
                ("Loan interest boundary values", "Loan Processing", "Pass", "Test evidence: LN-007"),
                ("Unauthorized account access", "Security", "Pass", "Test evidence: SEC-004"),
            ]
            con.executemany("INSERT INTO test_runs (test_name,area,result,evidence,run_date) VALUES (?,?,?,?,?)",
                            [(*r, now) for r in seed_tests])

@app.route("/")
def dashboard():
    with connect() as con:
        reqs = con.execute("SELECT * FROM requirements ORDER BY id DESC").fetchall()
        defects = con.execute("SELECT * FROM defects ORDER BY id DESC").fetchall()
        docs = con.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
        tests = con.execute("SELECT * FROM test_runs ORDER BY id DESC").fetchall()
    total_tests = len(tests)
    passed = sum(1 for t in tests if t["result"] == "Pass")
    failed = sum(1 for t in tests if t["result"] == "Fail")
    pass_rate = round((passed / total_tests) * 100, 1) if total_tests else 0
    open_critical = sum(1 for d in defects if d["severity"] == "Critical" and d["status"] != "Closed")
    open_high = sum(1 for d in defects if d["severity"] == "High" and d["status"] != "Closed")
    pending_reviews = sum(1 for r in reqs if r["status"] != "Approved")
    release_ready = open_critical == 0 and all(t["result"] == "Pass" for t in tests) and pending_reviews == 0
    return render_template("dashboard.html", objectives=QUALITY_OBJECTIVES, factors=QUALITY_FACTORS,
                           reqs=reqs, defects=defects, docs=docs, tests=tests, total_tests=total_tests,
                           passed=passed, failed=failed, pass_rate=pass_rate, open_critical=open_critical,
                           open_high=open_high, pending_reviews=pending_reviews, release_ready=release_ready,
                           release_checks=RELEASE_CHECKS)

@app.route("/requirements", methods=["GET", "POST"])
def requirements():
    if request.method == "POST":
        data = [request.form.get(k, "").strip() for k in
                ["title", "category", "risk", "description", "owner"]]
        if not all(data):
            flash("Please complete every required requirement field.", "error")
        else:
            with connect() as con:
                con.execute("""INSERT INTO requirements
                    (title,category,risk,description,owner,status,created_at)
                    VALUES (?,?,?,?,?,'Pending Review',?)""", (*data, datetime.now().strftime("%Y-%m-%d %H:%M")))
            flash("Requirement added with status Pending Review.", "success")
        return redirect(url_for("requirements"))
    with connect() as con:
        rows = con.execute("SELECT * FROM requirements ORDER BY id DESC").fetchall()
    return render_template("requirements.html", rows=rows)

@app.route("/requirements/<int:item_id>/review", methods=["POST"])
def review_requirement(item_id):
    status = request.form.get("status", "Pending Review")
    approver = request.form.get("approver", "").strip()
    notes = request.form.get("review_notes", "").strip()
    if status == "Approved" and not approver:
        flash("An approver is required before a requirement can be approved.", "error")
    else:
        with connect() as con:
            con.execute("UPDATE requirements SET status=?, approver=?, review_notes=? WHERE id=?",
                        (status, approver, notes, item_id))
        flash("Requirement review updated.", "success")
    return redirect(url_for("requirements"))

@app.route("/defects", methods=["GET", "POST"])
def defects():
    if request.method == "POST":
        data = [request.form.get(k, "").strip() for k in
                ["title", "category", "severity", "description", "found_in", "owner"]]
        if not all(data):
            flash("Please complete every required defect field.", "error")
        else:
            with connect() as con:
                con.execute("""INSERT INTO defects
                    (title,category,severity,description,found_in,status,owner,created_at)
                    VALUES (?,?,?,?,?,'Open',?,?)""",
                    (*data, datetime.now().strftime("%Y-%m-%d %H:%M")))
            flash("Defect recorded.", "success")
        return redirect(url_for("defects"))
    with connect() as con:
        rows = con.execute("SELECT * FROM defects ORDER BY id DESC").fetchall()
    return render_template("defects.html", rows=rows)

@app.route("/defects/<int:item_id>/update", methods=["POST"])
def update_defect(item_id):
    status = request.form.get("status", "Open")
    corrective = request.form.get("corrective_action", "").strip()
    preventive = request.form.get("preventive_action", "").strip()
    with connect() as con:
        con.execute("""UPDATE defects SET status=?, corrective_action=?, preventive_action=? WHERE id=?""",
                    (status, corrective, preventive, item_id))
    flash("Defect and action plan updated.", "success")
    return redirect(url_for("defects"))

@app.route("/tests", methods=["GET", "POST"])
def tests():
    if request.method == "POST":
        name = request.form.get("test_name", "").strip()
        area = request.form.get("area", "").strip()
        result = request.form.get("result", "").strip()
        evidence = request.form.get("evidence", "").strip()
        if not name or not area or result not in ("Pass", "Fail", "Blocked"):
            flash("Enter a test name, area, and valid result.", "error")
        else:
            with connect() as con:
                con.execute("INSERT INTO test_runs (test_name,area,result,evidence,run_date) VALUES (?,?,?,?,?)",
                            (name, area, result, evidence, datetime.now().strftime("%Y-%m-%d")))
            flash("Test result recorded.", "success")
        return redirect(url_for("tests"))
    with connect() as con:
        rows = con.execute("SELECT * FROM test_runs ORDER BY id DESC").fetchall()
    return render_template("tests.html", rows=rows)

@app.route("/documents", methods=["GET", "POST"])
def documents():
    if request.method == "POST":
        data = [request.form.get(k, "").strip() for k in ["name", "doc_type", "version", "owner", "status", "notes"]]
        if not all(data[:5]):
            flash("Complete the document name, type, version, owner, and status.", "error")
        else:
            with connect() as con:
                con.execute("""INSERT INTO documents (name,doc_type,version,owner,status,notes,updated_at)
                    VALUES (?,?,?,?,?,?,?)""", (*data, datetime.now().strftime("%Y-%m-%d %H:%M")))
            flash("Document register updated.", "success")
        return redirect(url_for("documents"))
    with connect() as con:
        rows = con.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
    return render_template("documents.html", rows=rows)

@app.route("/process")
def process():
    return render_template("process.html", objectives=QUALITY_OBJECTIVES, factors=QUALITY_FACTORS, checks=RELEASE_CHECKS)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
