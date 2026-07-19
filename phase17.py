import os
from datetime import datetime
import phase1_config
import phase1_database


def generate_report(report_data, session_id):
    print("________FINAL REPORT_______")
    if not os.path.exists(phase1_config.reports_f):
        os.mkdir(phase1_config.reports_f)
    path = os.path.join(phase1_config.reports_f, f"report_{session_id}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("FINAL BUSINESS REPORT\n")
        f.write("********************************\n")
        f.write(f"Session Id: {session_id}\n")
        f.write(f"Date: {datetime.now()}\n\n")
        f.write("1. Dataset Information:\n")
        f.write(f"Shape: {report_data.get('dataset.shape')} \n\n")
        f.write("2. Data quality score:\n")
        f.write(f"Score: {report_data.get('quality_score')}\n\n")
        f.write("3. What Cleaning We Did\n")
        for item in report_data.get("cleaning_summary", []):
            f.write(f"- {item}\n")
        f.write("\n")

        f.write("4. Workflow Type\n")
        f.write(f"{report_data.get('workflow')}\n\n")

        f.write("5. Models We Tried\n")
        for item in report_data.get("model_ranking", []):
            f.write(f"- {item}\n")
        f.write("\n")

        f.write("6. Best Model\n")
        f.write(f"{report_data.get('best_model_name')}\n\n")

        f.write("7. Model Result\n")
        for name, value in report_data.get("evaluation_metrics", {}).items():
            f.write(f"{name}: {value}\n")
        f.write("\n")

        f.write("8. Charts Saved At\n")
        for chart_path in report_data.get("chart_paths", []):
            f.write(f"- {chart_path}\n")
        f.write("\n")

        f.write("9. Insights\n")
        for text in report_data.get("insights", []):
            f.write(f"- {text}\n")
        f.write("\n")

        f.write("10. Recommendations\n")
        for text in report_data.get("recommendations", []):
            f.write(f"- {text}\n")
        f.write("\n")

        f.write("11. Prediction Results\n")
        for text in report_data.get("prediction_results", []):
            f.write(f"- {text}\n")
        f.write("\n")

        f.write("12. Explainability Summary\n")
        f.write(f"{report_data.get('explainability_summary')}\n\n")

        f.write("--- END OF REPORT ---\n")

    print("Report Saved:", path)

    phase1_database.run_query(
        "INSERT INTO reports (session_id, report_path, created_on) VALUES (%s, %s, %s)",
        (session_id, path, datetime.now())
    )

    print("Done!\n")
    return path
