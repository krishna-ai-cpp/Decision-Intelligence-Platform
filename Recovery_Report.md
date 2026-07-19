# Recovery Report

Source: `zipped.zip` (79 files, 76 regular files + directories)
Output: `Decision-Intelligence-Platform-Final/`

## 1. What the upload actually contained

The zip held **two overlapping copies** of the same backend:

| Copy | Location | State |
|---|---|---|
| Current | root (`/phase*.py`) | Aiven MySQL over SSL, env-var password |
| Stale | `backend/phase*.py` | localhost MySQL, **hardcoded plaintext password** |

`app.py` imports the flat module names (`import phase1_database`, etc.),
**and also contained this line near the top:**

```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
```

Because `sys.path.insert(0, ...)` puts `backend/` *ahead of* the
script's own directory, Python would have resolved every `import
phaseN` to the **stale `backend/` copy first**, not the current
root-level files. In practice this meant the app was one path-ordering
accident away from silently connecting to a nonexistent `localhost`
MySQL server using a hardcoded password, instead of the intended Aiven
database - a serious, easy-to-miss bug and a credential exposure.

**This is the single most important fix in this recovery.**

## 2. Decisions - what was kept, what was removed, and why

### Kept (canonical source)
- All 19 root-level `phase*.py` / `phase1_*.py` modules - these are the
  newer, Aiven/SSL/env-var-password versions, and match what `app.py`
  is actually meant to use.
- `app.py` (829 lines, 26 routes) - the real, complete Flask
  application. It's the only file in the upload that defines any
  routes.
- `templates/`, `static/css/style.css`, `static/js/app.js`, `ca.pem`,
  `Procfile`, `.gitignore` - all single, unduplicated, and correct.

### Removed - duplicates, backups, and dead code
| Removed | Reason |
|---|---|
| `backend/` (18 files) | Stale duplicate of the root modules; not imported by any correct code path; contained a hardcoded local DB password (see below). Nothing in it was newer or more complete than the root version, except one line (merged, see below). |
| `phase_main.py` (522 lines) | An earlier draft of `app.py` with **zero Flask routes** (`@app.route` count: 0) and no `Flask(...)` app instance. Superseded entirely by `app.py`. |
| `.vscode.zip`, `.vscode (2).zip` | Old point-in-time backups of the whole project (one even contains a full second copy of `backend/`, `static/`, `templates/`, `app.py`, etc., zipped inside itself). Editor/session junk, not part of the runnable app. |
| `ca - Copy.pem` | Byte-for-byte identical duplicate of `ca.pem`. |
| ` - Copy.gitignore` | Byte-for-byte identical duplicate of `.gitignore`. |
| `__pycache__/*.pyc` | Compiled bytecode cache, regenerated automatically, never belongs in source control or a shipped zip. |
| `.vscode/settings.json` | Editor-local configuration, not part of the application. |

### Merged (kept the better logic from each copy)
`backend/phase14.py` had one small correctness improvement over the
root copy that `app.py` actually uses:

```python
# root (before):      if inp:
# backend (better):   if inp and isinstance(inp, list):
```

This guards against a crash if `inp` (feature importances) comes back
as something other than a list. The isinstance check was merged into
the kept `phase14.py`; nothing else from `backend/` was used.

Three other files differed only in trivial ways between root and
`backend/` (`phase1_config.py`, `phase1_database.py`, `phase10.py`) -
in each case the root version was already the correct, current one and
`backend/`'s version was the older draft (see Section 3).

## 3. Bugs fixed beyond de-duplication

1. **Import-shadowing bug (critical)** - removed the
   `sys.path.insert(0, ".../backend")` line in `app.py` described
   above. Root-level modules now resolve unambiguously.
2. **Plaintext password storage** - `phase1_authentication.py`
   previously stored and compared passwords as plain text
   (`VARCHAR(50)` column, raw string equality in SQL). Rewritten to
   hash with `werkzeug.security.generate_password_hash` /
   `check_password_hash`. The `Users.password` column was widened from
   `VARCHAR(50)` to `VARCHAR(255)` in `phase1_database.py` to hold the
   hash. The public function signatures (`register_user(name,
   password)`, `login(name, password)`) and return shapes are
   unchanged, so `app.py` did not need to change.
3. **Hardcoded Flask secret key** - `app.secret_key` was a fixed
   string committed to source (`"change-this-secret-key-before-you-
   deploy"`). Now read from the `FLASK_SECRET_KEY` environment
   variable, with a clearly-labeled insecure fallback for local dev
   only.
4. **`debug=True` hardcoded at startup** - `app.run(debug=True)` would
   enable the Werkzeug interactive debugger (a known remote-code-
   execution risk) any time `app.py` was run directly. Now controlled
   by `FLASK_DEBUG` (default off). Note: this only affects `python
   app.py` - the production start command in `Procfile` uses Gunicorn
   and was never affected by this flag.
5. **`requirements.txt` was missing `Flask` and `gunicorn`** -
   the original `requirements.txt` listed only
   `mysql-connector-python, pandas, numpy, matplotlib, scikit-learn,
   joblib`. Neither Flask (used throughout `app.py`) nor Gunicorn
   (the process the `Procfile` starts) were listed, so a clean
   `pip install -r requirements.txt` would not have produced a
   working app. Both were added, along with `Werkzeug` (used directly
   for password hashing) and `python-dotenv` (for local `.env`
   loading). All packages are now version-pinned.
6. **Stale README and code comments** - the original `README.md` and
   the `app.py` module docstring both described a `backend/phase*.py`
   layout that no longer matched what `app.py` actually imports.
   Rewritten to describe the real, current layout.

## 4. What was verified to already be correct (no changes needed)

- All SQL in every `phase*.py` module goes through
  `phase1_database.run_query()`, which always uses parameterized
  queries (`%s` + a values tuple) - no SQL string formatting/injection
  risk found anywhere in the codebase.
- `matplotlib.use("Agg")` is already set before any `pyplot` import in
  both `phase8.py` and `phase16.py`, so chart generation works
  headless on a server with no display - no fix needed.
- Every `os.makedirs(...)` call for `models/`/`charts/`/`reports/` is
  already guarded with `exist_ok=True` or an `os.path.exists()` check,
  so re-running the app doesn't crash on existing folders.
- All 23 `render_template(...)` calls in `app.py` reference templates
  that exist; `base.html` (extended by all page templates) and
  `profile.html` are both used, just not via a literal grep match in
  the first pass - a full parse confirmed 0 missing and 0 orphaned
  templates.
- Both static assets referenced by templates (`css/style.css`,
  `js/app.js`) exist under `static/`.
- Every `phase*.py` and `app.py` file parses as valid Python
  (AST-checked) and imports cleanly with all pinned dependencies
  installed.
