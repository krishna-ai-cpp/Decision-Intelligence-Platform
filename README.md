# Decision Intelligence Platform

**A guided, database-backed journey from a CSV dataset to model comparison and a business report.**

A Flask application that brings data profiling, cleaning, feature engineering, exploratory analysis, model training, and decision-support views into one interface. The project uses MySQL to store user and workflow records, while the original `phase*.py` modules carry the data-processing logic.

`Python` · `Flask` · `MySQL` · `pandas` · `scikit-learn` · `Jinja2`

[Workflow](#workflow) · [Run locally](#run-locally) · [Source map](#source-map) · [Design & current scope](#design--current-scope)

## Workflow

```text
Register / sign in → create project → upload CSV → profile → select goal
    → clean → engineer features → explore → train → compare
    → decisions / recommendations / what-if → report
```

| Stage | What a reader can explore |
| :--- | :--- |
| Accounts & projects | Password hashing, login sessions, project creation, and stored session records |
| Data preparation | CSV upload, data-quality inspection, cleaning, and feature engineering |
| Modeling | Regression, classification, clustering, and exploration-only paths |
| Comparison | Evaluation metrics, model rankings, training times, and prediction times |
| Decision support | Recommendations, what-if inputs, explanation summaries, and alerts |
| Reporting | Saved charts and a downloadable text report |

Regression compares Linear Regression, Decision Tree, and Random Forest. Classification compares Logistic Regression, KNN, Decision Tree, and Random Forest. Clustering uses KMeans with an inertia-based selection heuristic.

## Run locally

### Prerequisites

- Python 3.11 or 3.12.
- An accessible MySQL database and credentials, with permission to initialize the project tables.
- Appropriate TLS configuration; the current connection uses `ca.pem`.

From your **existing repository folder**, in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` locally and set `DB_PASSWORD` and a unique `FLASK_SECRET_KEY`. A key can be generated with:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Review the host, user, port, database, and certificate settings in [phase1_config.py](phase1_config.py) for your database. They are currently configured in that file; they are not all read from `.env`.

```powershell
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:5000**. Startup attempts database/table initialization. If initialization is skipped because the database cannot be reached, a running web page alone does not mean account and project operations will work.

### Suggested walkthrough

1. Register a local demo account and sign in.
2. Create one project and upload a small, non-sensitive CSV.
3. Inspect the profile and choose a supported goal and target.
4. Follow cleaning, features, EDA, training, and comparison in order.
5. Inspect a recommendation or what-if result, then generate a report.

A walkthrough writes project records and local artifacts. The README describes this flow; it does not claim a recent live database test.

## Source map

| Files | Responsibility |
| :--- | :--- |
| [app.py](app.py) | Flask routes, page rendering, session coordination, and captured console output |
| [phase1_config.py](phase1_config.py), [phase1_database.py](phase1_database.py), [phase1_authentication.py](phase1_authentication.py) | Configuration, MySQL operations, registration, and login |
| [phase2.py](phase2.py), [phase3.py](phase3.py), [phase4_5.py](phase4_5.py) | Workflow sessions, data upload/profile, and goal selection |
| [phase6.py](phase6.py), [phase7.py](phase7.py), [phase8.py](phase8.py) | Cleaning, feature engineering, and exploration |
| [phase9.py](phase9.py), [phase10.py](phase10.py) | Model training and comparison |
| [phase11.py](phase11.py)–[phase15.py](phase15.py) | Decision-support outputs, recommendations, what-if, explanations, and alerts |
| [phase16.py](phase16.py), [phase17.py](phase17.py) | Saved charts and report generation |
| [templates/](templates/), [static/](static/) | Jinja2 pages, CSS, and JavaScript |
| [.env.example](.env.example), [.gitignore](.gitignore) | Local environment template and generated-file exclusions |

Runtime output includes uploaded data, saved models, charts, and reports. Keep those outputs and credentials out of Git.

## Design & current scope

- **Separation of responsibilities:** `app.py` exposes the workflow through forms while the phase modules carry data and model operations.
- **Visible processing:** a Console Output panel surfaces the backend's printed summaries alongside the web controls.
- **State:** database records persist, but working DataFrames and model objects also live in a process-local `STATE` dictionary. Complete in-memory workflow state is not guaranteed to survive a restart or work consistently across multiple workers.
- **Evaluation:** model scores describe the chosen data and split. The workflow is an educational implementation; preprocessing order, leakage, and validation strategy should be reviewed before treating results as benchmarks.
- **Deployment:** the included `Procfile` starts Gunicorn on a compatible host. Database reachability, durable artifact storage, and session handling still need deployment-specific validation.

## Configuration notes

Passwords use Werkzeug hashing. Set a unique session secret, leave `FLASK_DEBUG=0` outside local development, and keep `.env` private. Historical recovery/deployment details remain in [Recovery_Report.md](Recovery_Report.md) and [Deployment_Report.md](Deployment_Report.md); they are background records rather than proof of current deployment status.

---

**Krishna Agrawal** · [FastAPI-based IBDE](https://github.com/krishna-ai-cpp/IBDE-Intelligent---Business--Decision--Engine-) · [Portfolio](https://github.com/krishna-ai-cpp)
