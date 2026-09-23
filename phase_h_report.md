# Phase H — SQLite Audit & MySQL Migration Report

**Project:** NeoNatal Watch AI  
**Phase:** H — SQLite Audit  
**Date:** 2026-09-22  
**Status:** ✅ PASS

---

## 1. Audit Summary

A complete search of the repository was performed for the following patterns:

- `sqlite`, `sqlite3`, `SQLite`
- `.db` file references
- `sqlite://` connection strings
- `create_engine("sqlite..."`
- `aiosqlite`
- `check_same_thread` (SQLite-only engine argument)

**Total SQLite references found:** 12 distinct locations (across source files, documentation, and compiled `.pyc` caches).

**Active runtime SQLite usage:** ✅ **NONE** — MySQL is the sole production database.

---

## 2. SQLite References Classification Table

| # | File | Line(s) | Snippet | Classification |
|---|------|---------|---------|----------------|
| 1 | `tests/conftest.py` | 33–38 | `TEST_DATABASE_URL = "sqlite:///./test_neonatal.db"` + `connect_args={"check_same_thread": False}` | **WAS: TEST-ONLY DEPENDENCY → NOW MIGRATED TO MYSQL** |
| 2 | `tests/test_database.py` | 12 | `# never touch the real neonatal.db file.` | **DOCUMENTATION ONLY** (comment) |
| 3 | `PRESENTATION_FLOW.md` | 103–105 | `### 13. PostgreSQL (Currently SQLite)` | **DOCUMENTATION ONLY** — historic prototyping note |
| 4 | `PROJECT_COMPONENT_MAP.md` | 5, 39–40 | `SQLite instead of PostgreSQL … points to neonatal.db` | **DOCUMENTATION ONLY** — historic prototyping note |
| 5 | `reports/PROJECT_HEALTH_REPORT.md` | 44–50, 173 | `WORKING (using SQLite instead of PostgreSQL)` | **DOCUMENTATION ONLY** — outdated health report |
| 6 | `neonatal.db` | — | Binary SQLite database file (legacy prototype) | **UNUSED / LEGACY** — no code reads from it at runtime |
| 7 | `backend/app/db/models.py` (comments) | 227–375 | `# This file used to contain an SQLite fallback URL…` | **DOCUMENTATION ONLY** — in-code historical comment |
| 8 | `migrations/env.py` | 16–17 | Imports `SQLALCHEMY_DATABASE_URL` (which is MySQL) | **NOT SQLite** — MySQL reference, safe |
| 9 | `alembic.ini` (commented) | — | `#sqlalchemy.url = sqlite:///./neonatal.db` | **SAFE TO REMOVE** — commented-out fallback, never executed |
| 10 | `tests/__pycache__/*.pyc` | — | Compiled bytecache of old `conftest.py` | **AUTO-GENERATED** — will be regenerated automatically |
| 11 | `backend/app/__pycache__/*.pyc` | — | Compiled bytecache | **AUTO-GENERATED** — will be regenerated automatically |
| 12 | `test_neonatal.db` (root dir) | — | Leftover SQLite file from old test runs | **SAFE TO REMOVE** — orphaned artifact |

---

## 3. Runtime Impact — MySQL is Sole Source of Truth

### Production Engine (`backend/app/db/database.py`)
```python
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
```
- Credentials are read exclusively from environment variables / `.env`.
- **No SQLite fallback exists.**
- **No conditional logic** that would switch to SQLite at runtime.

### Alembic Migration Engine (`migrations/env.py`)
```python
from backend.app.db.database import SQLALCHEMY_DATABASE_URL
# → Inherits MySQL URL from database.py
```
- Alembic migrations target MySQL.
- The commented-out `#sqlalchemy.url = sqlite:///./neonatal.db` in `alembic.ini` is **never read**.

### Test Engine (`tests/conftest.py`) — AFTER PHASE H FIX
```python
_encoded_password = urllib.parse.quote_plus(DB_PASSWORD)
TEST_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{_encoded_password}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"
test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
```
- Tests now run against the **dedicated `test_neonatal_watch_ai` MySQL schema**.
- Tables are created fresh before the session and dropped after, providing full isolation.
- Production schema `neonatal_watch_ai` is **never touched by tests**.

---

## 4. Changes Made During Phase H

| Change | File | Action |
|--------|------|--------|
| Replaced `sqlite:///./test_neonatal.db` with MySQL URL | `tests/conftest.py` | ✅ Modified |
| Removed SQLite-only `connect_args={"check_same_thread": False}` | `tests/conftest.py` | ✅ Removed |
| Added `urllib.parse.quote_plus()` for password encoding | `tests/conftest.py` | ✅ Added |
| Removed `.db` file cleanup code (not needed for MySQL) | `tests/conftest.py` | ✅ Removed |
| Loaded `.env` explicitly in test setup | `tests/conftest.py` | ✅ Added |
| Created `test_neonatal_watch_ai` MySQL test schema | MySQL server | ✅ Created |

**No production code was modified.**  
**No synthetic data was altered.**  
**No ML models were changed.**

---

## 5. Security Findings

| Finding | Severity | Status |
|---------|----------|--------|
| Database password contains special character `@` | Low | ✅ Fixed — `urllib.parse.quote_plus()` applied in both `database.py` and `conftest.py` |
| No credentials hardcoded in source files | — | ✅ Confirmed — all credentials from `.env` |
| `.env` should be in `.gitignore` | Low | ℹ️ Verify `.env` is excluded from version control |

---

## 6. Recommendations

| Item | Priority | Action |
|------|----------|--------|
| Delete `neonatal.db` from project root | Low | Safe to remove — legacy prototype artifact |
| Delete `test_neonatal.db` from project root (if present) | Low | Safe to remove — leftover from old SQLite test runs |
| Update `PRESENTATION_FLOW.md` | Low | Replace "Currently SQLite" with "MySQL (`neonatal_watch_ai`)" |
| Update `PROJECT_COMPONENT_MAP.md` | Low | Replace SQLite prototype note with MySQL production note |
| Update `reports/PROJECT_HEALTH_REPORT.md` | Low | Replace outdated SQLite status with MySQL status |
| Remove commented `#sqlalchemy.url = sqlite:...` from `alembic.ini` | Optional | Safe to remove — purely cosmetic cleanup |

---

## 7. Test Verification

### Test Suite Results — BEFORE Phase H (SQLite)
```
70 passed, 56 warnings in 18.55s  (using sqlite:///./test_neonatal.db)
```

### Test Suite Results — AFTER Phase H (MySQL)
```
70 passed, 56 warnings in 13.78s  (using mysql+pymysql://...test_neonatal_watch_ai)
```

✅ **All 70 tests pass against MySQL. Zero regressions.**

---

## 8. Database Architecture (Final State)

```
┌──────────────────────────────────────────────────────────────────────┐
│                        NeoNatal Watch AI                             │
├─────────────────────────┬────────────────────────────────────────────┤
│  PRODUCTION             │  TEST                                      │
│  mysql://...            │  mysql://...                               │
│  neonatal_watch_ai      │  test_neonatal_watch_ai                    │
│  (7 patients, 139 rows) │  (isolated, created/dropped per session)   │
├─────────────────────────┴────────────────────────────────────────────┤
│  SQLite: NOT USED anywhere in runtime or tests                        │
│  Legacy neonatal.db file: orphaned artifact, safe to delete           │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 9. Final Result

| Check | Result |
|-------|--------|
| No active runtime SQLite dependency | ✅ PASS |
| MySQL is sole production source of truth | ✅ PASS |
| Alembic targets MySQL | ✅ PASS |
| Tests migrated from SQLite to MySQL | ✅ PASS |
| Password encoding fixed (special char `@`) | ✅ PASS |
| All 70 tests pass on MySQL | ✅ PASS |
| No production data modified | ✅ PASS |
| No synthetic records altered | ✅ PASS |
| No ML models changed | ✅ PASS |

## **Phase H: ✅ COMPLETE — PASS**

