# Decision Intelligence Platform - Web App

A Flask web interface for an end-to-end data science pipeline: upload a
CSV, profile it, clean it, engineer features, explore it, train and
compare models, get decision-intelligence explanations, run what-if
predictions, and generate a final report - all backed by a MySQL
(Aiven) database.

`app.py` is a thin web layer only. All machine learning, cleaning,
database, and business logic lives in the `phase*.py` modules in this
same folder and is called by `app.py` unchanged.

## Project layout

```
app.py                    Flask app - one route per pipeline phase
phase1_config.py          Central configuration (DB connection, folder names)
phase1_database.py        MySQL connection pool, schema, parameterized query helper
phase1_authentication.py  Register / login (passwords hashed with Werkzeug)
phase2.py .. phase17.py   Pipeline steps: sessions, upload, cleaning, feature
                           engineering, EDA, training, comparison, decision
                           intelligence, recommendations, what-if, explainability,
                           alerts, charts, reporting
templates/                Jinja2 HTML templates (one per page)
static/css/style.css      Styling
static/js/app.js          Client-side behaviour
ca.pem                    Aiven MySQL CA certificate (required for SSL connection)
uploads/                  CSVs uploaded through the browser land here (created at runtime)
models/ charts/ reports/  Created automatically by the backend functions
Procfile                  Render/Heroku start command (gunicorn)
requirements.txt          Pinned Python dependencies
.env.example              Template for local environment variables
```

## Requirements

- Python 3.11 or 3.12
- A MySQL-compatible database reachable over SSL (this project is
  configured for an **Aiven MySQL** instance out of the box)

## Local setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the environment template and fill in your real values:

```bash
cp .env.example .env
```

Edit `.env`:

```
DB_PASSWORD=your-aiven-db-password
FLASK_SECRET_KEY=a-long-random-string
FLASK_DEBUG=0
```

`app.py` loads `.env` automatically via `python-dotenv`. `.env` is
already listed in `.gitignore` - never commit it.

The database host, user, database name, port, and CA cert path are set
in `phase1_config.py`. Only the password is read from the environment;
update the other values there if you point this at a different Aiven
project.

## Run locally

From this folder (the app root, so the `uploads/`, `models/`,
`charts/`, `reports/` folders resolve correctly):

```bash
python app.py
```

Then open **http://127.0.0.1:5000**. On startup the app automatically
calls `phase1_database.create_database_if_not_exists()` and
`creating_all_tables()`, so the schema is created/verified every time
it boots.

Set `FLASK_DEBUG=1` in `.env` only for local development - never in
production, since Flask's debugger allows arbitrary code execution if
it's ever exposed.

## Production deployment (Render)

1. Push this project to a Git repository (see `.gitignore` - it
   already excludes `venv/`, `__pycache__/`, uploaded data, generated
   charts/reports/models, and `.env`).
2. Create a new **Web Service** on Render pointing at the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command is read from the `Procfile`:
   ```
   web: gunicorn app:app
   ```
5. Set environment variables in the Render dashboard:
   - `DB_PASSWORD` - your Aiven MySQL password
   - `FLASK_SECRET_KEY` - a long random string (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`)
   - Leave `FLASK_DEBUG` unset (defaults to off)
6. Render's filesystem is ephemeral - `uploads/`, `models/`,
   `charts/`, and `reports/` will be recreated on each deploy/restart.
   If you need those files to persist across deploys, attach a Render
   Disk mounted at the app root, or move them to external object
   storage (out of scope for this recovery pass).

## Database

- Connection settings live in `phase1_config.py`; the password comes
  from the `DB_PASSWORD` environment variable.
- `phase1_database.sql_server()` connects over SSL using `ca.pem`
  (`ssl_verify_cert=True`), matching Aiven's required SSL mode.
- All queries in every `phase*.py` module go through
  `phase1_database.run_query()`, which always uses parameterized
  queries (`%s` placeholders + a values tuple) - no string-formatted
  SQL anywhere in the codebase.
- Tables are created with `CREATE TABLE IF NOT EXISTS`, so
  `creating_all_tables()` is safe to run on every startup.

## Security notes

- User passwords are hashed with Werkzeug's `generate_password_hash` /
  `check_password_hash` before being stored or compared - the
  database never holds a plaintext password.
- The Flask session `secret_key` is read from `FLASK_SECRET_KEY`. Set
  a real random value in production; do not use the placeholder
  default.
- `FLASK_DEBUG` defaults to off; only enable it locally.
- Regenerate your Aiven database password and rotate
  `FLASK_SECRET_KEY` if either was ever committed to source control or
  shared outside your team - see `Recovery_Report.md` for details on
  what was found in the original upload.

## Two spots where `input()` was swapped for a web form

- `phase4_5.select_business_goal()` originally read a choice with
  `input()`. The `/goal` page shows the same 5 options as radio
  buttons, then passes the choice straight into the unchanged
  `phase4_5.select_workflow()`.
- `phase13.ask_user_input()` originally read one number per feature
  with `input()`. The `/whatif` page shows one number field per
  feature column, then passes the values straight into the unchanged
  `phase13.sing_pred()`.

Nothing else in the backend modules was changed except the fixes
listed in `Recovery_Report.md`.

## Console output panel

Every pipeline page shows a **Console Output** panel that captures
everything the backend functions `print()`, via `run_and_capture()` in
`app.py`. Nothing printed by the original CLI-style functions is lost;
it's shown on the page instead of the terminal.

## Further reading

- `Recovery_Report.md` - what was found, kept, merged, or removed
  during recovery, and why.
- `Deployment_Report.md` - deployment readiness checklist and what
  could not be verified without live credentials.
