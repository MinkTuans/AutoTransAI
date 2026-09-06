# SUPABASE INSTALLATION & DEPENDENCY REQUIREMENTS

## 1. Current Technology Stack
- **Backend Language & Runtime:** Python 3.12 (CPython)
- **Backend Framework:** FastAPI 0.115.0 + Uvicorn
- **Package Manager:** `pip` (`requirements.txt`)
- **Frontend Framework:** React 18.3.1 (SPA) + Vite 5.4.0 (`package.json`)
- **Frontend HTTP Client:** Axios 1.19.0

---

## 2. Existing Database Driver & ORM
- **ORM:** SQLAlchemy 2.0.30 (`sqlalchemy[asyncio]`)
- **Database Engine:** Supabase PostgreSQL (via `asyncpg` driver), with SQLite WAL fallback (`aiosqlite`).
- **Active Driver:** `asyncpg` 0.31.0 for PostgreSQL async execution.

---

## 3. Existing Cloud Storage Library
- **Previous Library:** Cloudflare R2 via `boto3` (S3 API).
- **Status:** **REMOVED**. Cloudflare R2 is completely decommissioned.

---

## 4. Required Supabase Libraries
- `supabase>=2.7.0`: Official Supabase Python SDK providing Storage API access, bucket management, signed URL generation, and public URL resolution.

---

## 5. Required PostgreSQL Libraries
- `asyncpg>=0.29.0`: High-performance asynchronous PostgreSQL driver required by SQLAlchemy 2.0 async engine (`postgresql+asyncpg://`).

---

## 6. Packages To Install
| Package Name | Version Specifier | Ecosystem | Purpose |
|---|---|---|---|
| `supabase` | `>=2.7.0` | Python / Backend | Supabase Storage API & Client SDK |
| `asyncpg` | `>=0.29.0` | Python / Backend | PostgreSQL Async Driver for SQLAlchemy |

---

## 7. Packages To Remove
| Package Name | Ecosystem | Reason for Removal |
|---|---|---|
| `boto3` | Python / Backend | Cloudflare R2 S3 API client is decommissioned. Storage is 100% Supabase. |

---

## 8. Frontend Package Policy
- **No Direct Frontend Supabase SDK (`@supabase/supabase-js`):** Frontend communicates exclusively with FastAPI Backend REST API. FastAPI Backend manages Supabase authentication using `SUPABASE_SERVICE_ROLE_KEY` and passes media URLs / SSE events to the frontend. No unnecessary frontend SDK bundle bloat.

---

## 9. Dependency Verification
- `requirements.txt` will be updated to remove `boto3` and retain `supabase` and `asyncpg`.
