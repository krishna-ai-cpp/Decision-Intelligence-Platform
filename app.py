"""
app.py
-------
Flask web application for the Decision Intelligence Platform.

This file does NOT contain any machine learning, cleaning, database, or
business logic of its own. Every real piece of work is done by calling
your existing backend modules (phase*.py, in this same folder) exactly as
they are.

This file's only job is:
1. Turn each phase into a web page (a Flask route + an HTML template).
2. Hold the in-progress objects (the DataFrame, trained models, results...)
   in memory between page loads, since a web browser can't keep a Python
   variable alive between requests the way a terminal script can.
3. Capture whatever your backend functions print(), so that console
   output you already wrote is shown on the page instead of being lost.

Two backend functions use input() (select_business_goal, ask_user_input),
which only works in a terminal. For those two spots, this file collects
the same values from an HTML form instead, then hands them to your
UNCHANGED functions (select_workflow, sing_pred) exactly like the
terminal version would have.
"""

import os
import io
import sys
import contextlib
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()  # loads DB_PASSWORD / FLASK_SECRET_KEY / etc. from a local .env file if present

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_from_directory
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

import phase1_database
import phase1_authentication
import phase2
import phase3
import phase4_5
import phase6
import phase7
import phase8
import phase9
import phase10
import phase11
import phase12
import phase13
import phase14
import phase15
import phase16
import phase17
import phase1_config

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-insecure-key-change-me")
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "0") == "1"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------------------------------------------------------------
# In-memory store for the live Python objects of each in-progress project.
# Key = the database session_id. This is what lets a DataFrame, a trained
# model, or a results list survive between one page load and the next.
# ----------------------------------------------------------------------
STATE = {}


def get_state():
    """Returns the state dict for whichever session the user currently has open."""
    sid = session.get("session_id")
    if sid is None:
        return None
    return STATE.setdefault(sid, {})


def run_and_capture(func, *args, **kwargs):
    """
    Calls a backend function exactly as-is, but also grabs everything it
    prints() so the web page can display it (nothing your functions print
    gets lost, it just moves from the terminal onto the page).
    """
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = func(*args, **kwargs)
    return result, buffer.getvalue()


# ----------------------------------------------------------------------
# GOAL OPTIONS - the exact same 5 options phase4_5.select_business_goal()
# prints and reads with input(). We show them as a web form instead, then
# still call your real phase4_5.select_workflow() with whichever one the
# user picked.
# ----------------------------------------------------------------------
GOAL_OPTIONS = {
    "1": "predict a numeric value",
    "2": "classify records into categories",
    "3": "group similar records together",
    "4": "just explore the dataset (no modeling)",
    "5": "comparing multiple machine learning models",
}


# ======================================================================
# LOGIN / REGISTER / LOGOUT
# ======================================================================
@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        result, console = run_and_capture(phase1_authentication.login, name, password)
        if result:
            session["user_id"] = result[0][0]
            session["user_name"] = name
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.", "error")
        return render_template("login.html", console=console)
    return render_template("login.html", console=None)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        new_id, console = run_and_capture(phase1_authentication.register_user, name, password)
        if new_id:
            flash("Account created. You can log in now.", "success")
            return redirect(url_for("login"))
        return render_template("register.html", console=console)
    return render_template("register.html", console=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def login_required():
    return session.get("user_id") is not None


# ======================================================================
# ERROR HANDLERS — presentation only, no backend behaviour changed.
# ======================================================================
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.exception("Unhandled server error")
    return render_template("500.html"), 500


# ======================================================================
# DASHBOARD / RESUME / NEW PROJECT
# ======================================================================
@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    sessions, console = run_and_capture(phase2.show_unfinished_sessions, session["user_id"])
    return render_template("dashboard.html", sessions=sessions or [], console=console)


@app.route("/saved-projects")
def saved_projects():
    if not login_required():
        return redirect(url_for("login"))
    sessions, console = run_and_capture(phase2.show_unfinished_sessions, session["user_id"])
    return render_template("saved_projects.html", sessions=sessions or [], console=console)


@app.route("/new-project", methods=["GET", "POST"])
def new_project():
    if not login_required():
        return redirect(url_for("login"))
    if request.method == "POST":
        dataset_name = request.form.get("dataset_name", "").strip()
        new_sid, console = run_and_capture(
            phase2.create_new_session, session["user_id"], dataset_name
        )
        session["session_id"] = new_sid
        STATE[new_sid] = {"dataset_name": dataset_name}
        flash(console, "console")
        return redirect(url_for("upload"))
    return render_template("new_project.html")


@app.route("/resume/<int:sid>")
def resume(sid):
    if not login_required():
        return redirect(url_for("login"))
    session["session_id"] = sid
    STATE.setdefault(sid, {})

    step, _ = run_and_capture(phase2.get_session_step, sid)
    rows, _ = run_and_capture(
        phase1_database.run_query,
        "SELECT file_path FROM DATASET_METADATA WHERE Session_ID = %s ORDER BY Dataset_id DESC LIMIT 1",
        (sid,), True
    )
    if rows:
        file_path = rows[0][0]
        df, console = run_and_capture(phase3.upload_read_csv, file_path, sid)
        if df is not None:
            STATE[sid]["df"] = df
            STATE[sid]["file_path"] = file_path
        flash(f"Resumed from step: {step}", "console")
    else:
        flash("Could not find the original file for this session. Please re-upload.", "error")
    return redirect(url_for("upload"))


# ======================================================================
# PHASE 3 - UPLOAD DATA
# ======================================================================
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if state is None:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        file = request.files.get("csv_file")
        typed_path = request.form.get("csv_path", "").strip()

        file_path = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
        elif typed_path:
            file_path = typed_path

        if not file_path:
            flash("Please choose a file or type a path.", "error")
            return render_template("upload.html", console=None)

        df, console = run_and_capture(phase3.upload_read_csv, file_path, session["session_id"])
        if df is None:
            flash("Could not read that CSV file.", "error")
            return render_template("upload.html", console=console)

        state["df"] = df
        state["file_path"] = file_path
        run_and_capture(phase2.update_session_step, session["session_id"], "dataset_uploaded")

        return render_template(
            "upload.html", console=console, uploaded=True,
            shape=df.shape, columns=list(df.columns),
            head=df.head().to_html(classes="data-table"),
        )

    return render_template("upload.html", console=None)


# ======================================================================
# PHASE 3 - PROFILE DATA
# ======================================================================
@app.route("/profile")
def profile():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state or "df" not in state:
        flash("Upload a dataset first.", "error")
        return redirect(url_for("upload"))

    df = state["df"]
    sid = session["session_id"]

    _, console = run_and_capture(phase3.profile, df, sid, state["file_path"])

    (nc, cc, dc, bc), _ = run_and_capture(phase3.detect, df)
    con, _ = run_and_capture(phase3.constant, df)
    co, _ = run_and_capture(phase3.correlated, df, nc)
    sk, _ = run_and_capture(phase3.skewed, df, nc)
    mc = int(df.isnull().sum().sum())
    dup = int(df.duplicated().sum())
    dq, _ = run_and_capture(phase3.data_quality, df, mc, dup, con, co)

    state.update(nc=nc, cc=cc, dc=dc, bc=bc, con=con, co=co, sk=sk, dq=dq, mc=mc, dup=dup)
    run_and_capture(phase2.update_session_step, sid, "profiling_done")

    return render_template(
        "profile.html", console=console, nc=nc, cc=cc, dc=dc, bc=bc,
        con=con, co=co, sk=sk, dq=dq, mc=mc, dup=dup
    )


# ======================================================================
# PHASE 5/6 - CHOOSE GOAL -> CHOOSE WORKFLOW
# ======================================================================
@app.route("/goal", methods=["GET", "POST"])
def goal():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state or "dq" not in state:
        flash("Profile your dataset first.", "error")
        return redirect(url_for("profile"))

    if request.method == "POST":
        choice = request.form.get("goal_choice")
        goal_text = GOAL_OPTIONS.get(choice)
        workflow, console = run_and_capture(phase4_5.select_workflow, goal_text)
        state["goal"] = goal_text
        state["workflow"] = workflow
        run_and_capture(phase2.update_session_step, session["session_id"], f"workflow_selected_{workflow}")
        return render_template("goal.html", options=GOAL_OPTIONS, chosen=goal_text,
                                workflow=workflow, console=console)

    return render_template("goal.html", options=GOAL_OPTIONS, chosen=None, workflow=None, console=None)


# ======================================================================
# PHASE 7 - CLEAN DATA
# ======================================================================
@app.route("/clean", methods=["GET", "POST"])
def clean():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state or "workflow" not in state:
        flash("Choose a goal first.", "error")
        return redirect(url_for("goal"))

    if request.method == "POST":
        df, console = run_and_capture(phase6.clean_dataset, state["df"], session["session_id"])
        state["df"] = df
        run_and_capture(phase2.update_session_step, session["session_id"], "cleaning_done")
        return render_template("clean.html", console=console, cleaned=True, shape=df.shape)

    return render_template("clean.html", console=None, cleaned=False)


# ======================================================================
# PHASE 8 - FEATURE ENGINEERING
# ======================================================================
@app.route("/features", methods=["GET", "POST"])
def features():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state or "df" not in state:
        flash("Clean your dataset first.", "error")
        return redirect(url_for("clean"))

    workflow = state.get("workflow")
    df = state["df"]
    sid = session["session_id"]

    if request.method == "POST":
        if workflow in ("regression", "classification"):
            target_col = request.form.get("target_column")
            (feat, target, pp), console = run_and_capture(phase7.prepare, df, target_col, sid)
            state["features"], state["target"], state["pipeline_path"] = feat, target, pp
            state["target_col"] = target_col
        else:
            feat = df.copy()
            (feat, encoders), c1 = run_and_capture(phase7.encoding, feat)
            (feat, scaler), c2 = run_and_capture(phase7.scaling, feat)
            state["features"] = feat
            console = c1 + c2

        run_and_capture(phase2.update_session_step, sid, "feature_engineering_done")
        return render_template("features.html", workflow=workflow, columns=list(df.columns),
                                console=console, done=True, feature_shape=state["features"].shape)

    return render_template("features.html", workflow=workflow, columns=list(df.columns),
                            console=None, done=False)


# ======================================================================
# PHASE 9 - EXPLORE DATA (EDA)
# ======================================================================
@app.route("/eda", methods=["GET", "POST"])
def eda():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state or "features" not in state:
        flash("Run feature engineering first.", "error")
        return redirect(url_for("features"))

    if request.method == "POST":
        insights, console = run_and_capture(
            phase8.explore_dataset, state["df"], state["nc"], state["cc"], session["session_id"]
        )
        state["insights"] = insights
        run_and_capture(phase2.update_session_step, session["session_id"], "eda_done")

        chart_files = sorted(os.listdir(phase1_config.charts_f)) if os.path.exists(phase1_config.charts_f) else []
        return render_template("eda.html", console=console, insights=insights, charts=chart_files, done=True)

    return render_template("eda.html", console=None, insights=None, charts=[], done=False)


# ======================================================================
# PHASE 10 - TRAIN MODELS
# ======================================================================
@app.route("/train", methods=["GET", "POST"])
def train():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state or "features" not in state:
        flash("Run feature engineering first.", "error")
        return redirect(url_for("features"))

    workflow = state.get("workflow")
    sid = session["session_id"]

    if request.method == "POST":
        console = ""
        if workflow == "regression":
            results, c = run_and_capture(phase9.train_reg, state["features"], state["target"], sid)
            console += c
            state["results"] = results
            state["best"] = max(results, key=lambda r: r["r2"])
            state["evs"] = state["best"]["r2"]
        elif workflow == "classification":
            results, c = run_and_capture(phase9.train_class, state["features"], state["target"], sid)
            console += c
            state["results"] = results
            state["best"] = max(results, key=lambda r: r["accuracy"])
            state["evs"] = state["best"]["accuracy"]
        elif workflow == "clustering":
            result, c = run_and_capture(phase9.clustering, state["features"], sid)
            console += c
            state["cluster_result"] = result

            elbow_path, c_elbow = run_and_capture(
                phase16.plot_elbow_curve, result["k_values"], result["inertia_values"]
            )
            cluster_viz_path, c_viz = run_and_capture(
                phase16.plot_cluster_visualization, state["features"], result["cluster_labels"]
            )
            console += c_elbow + c_viz
            state["elbow_chart"] = os.path.basename(elbow_path) if elbow_path else None
            state["cluster_viz_chart"] = os.path.basename(cluster_viz_path) if cluster_viz_path else None
        else:
            flash("This workflow does not train a model, only exploration was done.", "error")
            return redirect(url_for("eda"))

        run_and_capture(phase2.update_session_step, sid, "model_training_done")
        return render_template("train.html", workflow=workflow, console=console, done=True,
                                results=state.get("results"), cluster_result=state.get("cluster_result"),
                                elbow_chart=state.get("elbow_chart"), cluster_viz_chart=state.get("cluster_viz_chart"))

    return render_template("train.html", workflow=workflow, console=None, done=False)


# ======================================================================
# PHASE 11 - COMPARE MODELS
# ======================================================================
@app.route("/compare", methods=["GET", "POST"])
def compare():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    workflow = state.get("workflow") if state else None

    if workflow == "clustering":
        return redirect(url_for("decisions"))

    if not state or "results" not in state:
        flash("Train your models first.", "error")
        return redirect(url_for("train"))

    if request.method == "POST":
        console = ""
        if workflow == "regression":
            exp, c = run_and_capture(phase10.rank_regression_winner, state["results"])
            console += c
            chart_path, c3 = run_and_capture(
                phase16.plot_act_pred, state["best"]["y_test"], state["best"]["predictions"]
            )
            console += c3
        else:
            exp, c = run_and_capture(phase10.rank_winner_class, state["results"])
            console += c
            _, c2 = run_and_capture(phase10.comp_reg_class, state["results"])
            console += c2
            chart_path, c3 = run_and_capture(
                phase16.plot_conf_mat, state["best"]["y_test"], state["best"]["predictions"]
            )
            console += c3

        state["exp"] = exp
        state["result_chart"] = os.path.basename(chart_path) if chart_path else None
        return render_template("compare.html", workflow=workflow, console=console,
                                explanation=exp, results=state["results"], best=state["best"],
                                done=True, result_chart=state["result_chart"])

    return render_template("compare.html", workflow=workflow, console=None,
                            explanation=None, results=state["results"], best=state["best"],
                            done=False, result_chart=None)


# ======================================================================
# PHASE 12 - EXPLAIN DECISIONS (DECISION INTELLIGENCE)
# ======================================================================
@app.route("/decisions", methods=["GET", "POST"])
def decisions():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state:
        return redirect(url_for("train"))

    workflow = state.get("workflow")

    if workflow == "clustering":
        if "cluster_result" not in state:
            flash("Train your clustering model first.", "error")
            return redirect(url_for("train"))
        if request.method == "POST":
            features = state["features"]
            result = state["cluster_result"]
            cluster_summary = features.assign(cluster=result["cluster_labels"]) \
                                       .groupby("cluster").mean(numeric_only=True)
            state["cluster_summary"] = cluster_summary
            run_and_capture(phase2.update_session_step, session["session_id"], "model_training_done")
            return render_template("decisions.html", workflow=workflow, done=True,
                                    cluster_summary=cluster_summary.to_html(classes="data-table"),
                                    console="Cluster summary computed.")
        return render_template("decisions.html", workflow=workflow, done=False)

    if "best" not in state:
        flash("Train and compare your models first.", "error")
        return redirect(url_for("compare"))

    if request.method == "POST":
        model = state["best"]["model_object"]
        feature_names = list(state["features"].columns)

        imp, c1 = run_and_capture(phase11.get_feature_imp, model, feature_names)
        drivers, c2 = run_and_capture(phase11.identify_drivers, imp)
        lines, c3 = run_and_capture(phase11.gen_decision_exp, drivers)
        _, c4 = run_and_capture(phase11.gen_decision, session["session_id"], lines)
        chart_path, c5 = run_and_capture(phase16.plot_feat_imp, imp)

        state["imp"] = imp
        state["drivers"] = drivers
        state["decision_lines"] = lines
        state["imp_chart"] = os.path.basename(chart_path) if chart_path else None
        console = c1 + c2 + c3 + c4 + c5

        return render_template("decisions.html", workflow=workflow, done=True,
                                imp=imp, drivers=drivers, lines=lines, console=console,
                                imp_chart=state["imp_chart"])

    return render_template("decisions.html", workflow=workflow, done=False)


# ======================================================================
# PHASE 13 - GET RECOMMENDATIONS
# ======================================================================
@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state:
        return redirect(url_for("decisions"))

    workflow = state.get("workflow")

    if request.method == "POST":
        rec = []
        console = ""

        if workflow == "classification":
            pred_df = pd.DataFrame({"predicted": state["best"]["predictions"]})
            sample_label = state["best"]["predictions"][0]
            r, c = run_and_capture(phase12.rec_for_class, pred_df, "predicted", sample_label)
            rec += r
            console += c
        elif workflow == "regression":
            r, c = run_and_capture(phase12.rec_for_reg, state.get("drivers", []))
            rec += r
            console += c
        elif workflow == "clustering":
            r, c = run_and_capture(phase12.rec_for_clus, state.get("cluster_summary"))
            rec += r
            console += c

        r2, c2 = run_and_capture(phase12.rec_for_dqs, state.get("dq", 100))
        rec += r2
        console += c2

        _, c3 = run_and_capture(phase12.gen_rec, session["session_id"], rec)
        console += c3

        state["rec"] = rec
        return render_template("recommend.html", rec=rec, console=console, done=True)

    return render_template("recommend.html", rec=None, console=None, done=False)


# ======================================================================
# PHASE 14 - WHAT-IF SIMULATION
# ======================================================================
@app.route("/whatif", methods=["GET", "POST"])
def whatif():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state or "best" not in state:
        flash("This is only available after training a regression or classification model.", "error")
        return redirect(url_for("train"))

    feature_names = list(state["features"].columns)
    model = state["best"]["model_object"]

    if request.method == "POST":
        # We collect the same values ask_user_input() would have collected
        # with input(), just from a web form instead of a terminal prompt.
        uvs = {}
        for col in feature_names:
            uvs[col] = float(request.form.get(col, 0))

        pred, console = run_and_capture(phase13.sing_pred, model, feature_names, uvs)

        now = datetime.now()
        phase1_database.run_query(
            "INSERT INTO predictions (session_id, input_values, predicted_value, created_on) VALUES (%s, %s, %s, %s)",
            (session["session_id"], str(uvs), str(pred), now)
        )

        state["last_whatif_input"] = uvs
        state["last_whatif_pred"] = pred

        return render_template("whatif.html", feature_names=feature_names, prediction=pred,
                                inputs=uvs, console=console, done=True)

    return render_template("whatif.html", feature_names=feature_names, prediction=None,
                            inputs=None, console=None, done=False)


# ======================================================================
# PHASE 15 - EXPLAINABILITY
# ======================================================================
@app.route("/explain", methods=["GET", "POST"])
def explain():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state or "best" not in state:
        flash("Train a model first.", "error")
        return redirect(url_for("train"))

    if request.method == "POST":
        model = state["best"]["model_object"]
        imp = state.get("imp", [])
        pred = state.get("last_whatif_pred", state["best"]["predictions"][0])
        evs = state["evs"]

        rel, c1 = run_and_capture(phase14.model_reliability, evs)
        _, c2 = run_and_capture(phase14.exp_pred, model, imp, pred, evs)

        return render_template("explain.html", reliability=rel, prediction=pred,
                                evaluation=evs, console=c1 + c2, done=True)

    return render_template("explain.html", done=False)


# ======================================================================
# PHASE 16 - SMART ALERTS
# ======================================================================
@app.route("/alerts", methods=["GET", "POST"])
def alerts():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state or "df" not in state:
        return redirect(url_for("upload"))

    workflow = state.get("workflow")

    if request.method == "POST":
        console = ""
        warnings = []
        if workflow in ("regression", "classification"):
            evs = state.get("evs", 0)
            target = state.get("target")
            co = state.get("co", [])
            _, console = run_and_capture(phase15.run_all, state["df"], target, co, evs, evs, evs)
        else:
            for fn, arg in [
                (phase15.check_small_datasets, state["df"]),
                (phase15.check_miss_values, state["df"]),
                (phase15.check_high_correlation, state.get("co", [])),
            ]:
                w, c = run_and_capture(fn, arg)
                console += c
                if w:
                    warnings.append(w)

        return render_template("alerts.html", console=console, warnings=warnings, done=True)

    return render_template("alerts.html", console=None, warnings=None, done=False)


# ======================================================================
# PHASE 17 - FINAL REPORT
# ======================================================================
@app.route("/report", methods=["GET", "POST"])
def report():
    if not login_required():
        return redirect(url_for("login"))
    state = get_state()
    if not state or "df" not in state:
        return redirect(url_for("upload"))

    workflow = state.get("workflow", "data_analytics")

    if request.method == "POST":
        chart_files = sorted(os.listdir(phase1_config.charts_f)) if os.path.exists(phase1_config.charts_f) else []
        chart_paths = [os.path.join(phase1_config.charts_f, c) for c in chart_files]

        if workflow == "clustering" and "cluster_result" in state:
            best_name = "KMeans"
            ranking = [f"KMeans -> Silhouette Score = {state['cluster_result']['silhouette_score']}"]
            metrics = {"Best K": state["cluster_result"]["best_k"],
                       "Silhouette Score": state["cluster_result"]["silhouette_score"]}
            explainability_summary = "Clustering groups similar records together; there is no single winner to compare."
        elif "best" in state:
            best_name = state["best"]["model_name"]
            if workflow == "regression":
                ranking = [f"{r['model_name']} -> R2 = {r['r2']:.4f}" for r in state["results"]]
                metrics = {"R2": state["best"]["r2"], "MAE": state["best"]["mae"], "RMSE": state["best"]["rmse"]}
            else:
                ranking = [f"{r['model_name']} -> Accuracy = {r['accuracy']:.4f}" for r in state["results"]]
                metrics = {"Accuracy": state["best"]["accuracy"], "Precision": state["best"]["precision"],
                           "Recall": state["best"]["recall"], "F1": state["best"]["f1"]}
            explainability_summary = state.get("exp", "")
        else:
            best_name = "N/A"
            ranking = []
            metrics = {}
            explainability_summary = "No model was trained; exploration only."

        report_data = {
            "dataset.shape": state["df"].shape,
            "quality_score": state.get("dq", 0),
            "cleaning_summary": ["See the CLEANED_LOGS table for full details."],
            "workflow": workflow,
            "model_ranking": ranking,
            "best_model_name": best_name,
            "evaluation_metrics": metrics,
            "chart_paths": chart_paths,
            "insights": state.get("insights", []),
            "recommendations": state.get("rec", []),
            "prediction_results": ["See the predictions table for full history."],
            "explainability_summary": explainability_summary
        }

        path, console = run_and_capture(phase17.generate_report, report_data, session["session_id"])
        run_and_capture(phase2.update_session_step, session["session_id"], "report_done")
        run_and_capture(phase2.mark_session_completed, session["session_id"])

        state["report_path"] = path
        return render_template("report.html", console=console, done=True,
                                report_path=path, report_filename=os.path.basename(path))

    return render_template("report.html", console=None, done=False)


@app.route("/reports/<path:filename>")
def download_report(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), phase1_config.reports_f), filename)


@app.route("/charts/<path:filename>")
def chart_file(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), phase1_config.charts_f), filename)


# ======================================================================
# SETTINGS / HELP
# ======================================================================
@app.route("/settings")
def settings():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("settings.html", config=phase1_config)


@app.route("/help")
def help_page():
    return render_template("help.html")


# ======================================================================
# STARTUP - create the database and tables, same as the CLI version did
# ======================================================================
def setup_database():
    phase1_database.create_database_if_not_exists()
    phase1_database.creating_all_tables()


# Run database initialization when the app starts
try:
    setup_database()
except Exception as e:
    print(f"Database initialization skipped: {e}")


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])