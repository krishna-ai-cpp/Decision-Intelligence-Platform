import datetime
import phase1_database

def get_feature_imp(model, features):
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        coef = model.coef_
        if len(coef.shape) > 1:
            importances = [abs(value) for value in coef[0]]
        else:
            importances = [abs(value) for value in coef]
    else:
        return []

    return sorted(zip(features, importances), key=lambda pair: pair[1], reverse=True)

def identify_drivers(imp_pairs, top=3):
    total = sum(abs(value) for _, value in imp_pairs)
    if total == 0:
        return []

    return [
        (feature, round(abs(value) / total * 100, 1))
        for feature, value in imp_pairs[:top]
    ]

def gen_decision_exp(drivers):
    if not drivers:
        return ["Not enough information was available to identify key business drivers."]

    lines = []
    for feature, percentage in drivers:
        lines.append(f"{feature} contributes {percentage}% to the prediction.")
        lines.append(f"{feature} alone accounts for about {percentage}% of the decision.")
    return lines

def gen_decision(session_id, exp, created_on=None):
    created_on = created_on or datetime.datetime.now()
    for e in exp:
        print("-", e)
        phase1_database.run_query(
            """
INSERT INTO insights (session_id, insight_text, created_on)
VALUES (%s, %s, %s)
""",
            (session_id, e, created_on),
        )
        print("__________________________________________\n")
    return exp
