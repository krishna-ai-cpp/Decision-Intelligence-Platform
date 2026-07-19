def get_conf(model,inp):
    if hasattr(model,"predict_proba"):
        p = model.predict_proba(inp)
        confidence = max(p[0])*100
        return round(confidence,2)
    return None
def model_reliability(evaluation):
    if evaluation  >= 0.85:
        return "Very High"
    elif evaluation >= 0.70:
        return "High"
    elif evaluation >= 0.50:
        return "Moderate"
    else:
        return "Low"
def exp_pred(model,inp,pred,evaluation):
    print(f"Predictions: {pred}")
    try:
        conf = get_conf(model, inp)
    except Exception:
        conf = None
    if conf is None:
        print("Confidence Score not available.....")
    else:
        print(f"Confidence score: {conf}")
    rel = model_reliability(evaluation)
    print(f"Model Reliability: {rel} of {evaluation:.2f}")
    if inp and isinstance(inp, list):
        for f,imp in inp[:5]:
            print(f"- {f} has an importance of {imp}")
    print("------------------------------\n")
