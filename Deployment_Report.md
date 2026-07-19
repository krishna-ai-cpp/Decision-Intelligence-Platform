# Deployment Report

## Verified locally

The following was actually executed in a clean environment (Python
venv, pinned `requirements.txt` installed from PyPI, no network access
to the real database), not just inspected:

- [x] `pip install -r requirements.txt` completes with no errors or
      version conflicts.
- [x] `import app` succeeds - all 19 backend modules import cleanly,
      no `ImportError`/`ModuleNotFoundError`.
- [x] `app.py` registers 27 routes (26 `@app.route` view functions +
      Flask's built-in static route).
- [x] Every `phase*.py` and `app.py` file parses as valid Python
      (`ast.parse`, zero syntax errors across all 19 files).
- [x] `GET /`, `/login`, `/register`, `/help` all return the expected
      status codes via Flask's test client (302 for `/` before login,
      200 for the rest).
- [x] Database connection failure at startup is handled gracefully -
      `setup_database()` is wrapped in `try/except` in `app.py`, so a
      DB that isn't reachable (as in this sandbox, which has no route
      to the Aiven host) logs an error and the app still boots instead
      of crashing.
- [x] All `render_template()` calls resolve to an existing template
      file; no missing templates.
- [x] All `url_for('static', ...)` references in templates resolve to
      files that exist under `static/`.
- [x] `ca.pem` is present at the app root and matches the path
      `phase1_config.db_ssl_ca = "ca.pem"` expects.
- [x] `Procfile` (`web: gunicorn app:app`) matches the actual module
      name (`app.py`) and Flask app variable name (`app`).

## Cannot be verified without live credentials / a live deployment

These require access this environment doesn't have (a live Aiven
database, or an actual Render service) and should be checked once you
deploy:

1. **Actual database connectivity** - the app correctly *attempts* an
   SSL connection to the Aiven host in `phase1_config.py` and fails
   gracefully when it can't reach it from here. Whether the real
   `DB_PASSWORD`, host, port, and `ca.pem` are all valid together can
   only be confirmed against the live Aiven instance.
2. **Schema creation end-to-end** - `creating_all_tables()` was read
   and is idempotent (`CREATE TABLE IF NOT EXISTS` throughout), but
   was not run against a real database in this pass.
3. **Full pipeline run with real data** - upload → clean → feature
   engineering → train → compare → decide → report was verified by
   reading the code path (`app.py` routes call through to each
   `phase*.py` function with matching signatures), not by executing it
   against an actual CSV and live database, since that requires a
   working DB connection.
4. **Render-specific behavior** - build/start commands were checked
   for correctness (`requirements.txt`, `Procfile`), but the actual
   Render build, cold start time, memory limits (scikit-learn +
   pandas + matplotlib can be memory-heavy on small instances), and
   whether `FLASK_SECRET_KEY`/`DB_PASSWORD` are set correctly in the
   Render dashboard were not and cannot be verified from here.
5. **Ephemeral filesystem impact** - `uploads/`, `models/`, `charts/`,
   `reports/` are written to local disk. On Render's free/standard web
   services this disk is ephemeral (wiped on every deploy and
   restart). This doesn't break the app, but any dataset, trained
   model, or report a user generated will be lost on the next deploy
   unless you attach a persistent disk or switch to external storage.
   Not fixed in this pass since it's an infrastructure choice, not a
   bug.

## Action items before going live

- [ ] Set `DB_PASSWORD` and `FLASK_SECRET_KEY` as environment
      variables in the Render dashboard (see `README.md`).
- [ ] Rotate the Aiven database password if the `backend/`
      copy's hardcoded `"krishna@2006"` (found during recovery, see
      `Recovery_Report.md`) was ever a real credential used anywhere,
      or if this project was ever pushed to a public/shared repo with
      it inside.
- [ ] Decide on a persistence strategy for `uploads/` / `models/` /
      `charts/` / `reports/` if users need their work to survive a
      redeploy.
- [ ] Consider adding a request size limit
      (`app.config["MAX_CONTENT_LENGTH"]`) for the CSV upload route,
      since it currently accepts files of any size.
