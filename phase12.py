import datetime
import phase1_database
import pandas as pd
def rec_for_class(df,columns,label):
    rec = []
    # ensure we check values in the series
    if label not in df[columns].values:
        return rec
    # count matching records and compute percentage
    total = len(df)
    if total == 0:
        return rec
    count = len(df[df[columns] == label])
    per = (count / total) * 100
    if per > 0:
        rec.append(f"{per:.1f}% of records were predicted as {label}. \nConsider starting a targeted retention or follow-up campaign for this group")
    return rec
def rec_for_clus(cs):
    rec = []
    if cs is None or cs.empty:
        return rec
    comp_cl = cs.columns[0]
    best = cs[comp_cl].idxmax()
    worst = cs[comp_cl].idxmin()
    rec.append(f"Cluster {best} has the highest average {comp_cl}. "
                f"This group looks like the most valuable customers - consider offering them premium deals or loyalty rewards")

    rec.append(f"Cluster {worst} has the lowest average {comp_cl}. "
                f"This group may need extra marketing attention or a pricing review")
    return rec
def rec_for_reg(drivers):
    rec = []
    if not drivers:
        return rec
    name,pct= drivers[0]
    rec.append(f"Since {name} is the biggest driver ({pct} %) "
                f"focus improvement efforts there first for fastest business impact")
    return rec
def rec_for_dqs(dqs):
    rec = []
    if dqs < 60:
        rec.append(
            f"The Data Quality Score is only {dqs}/100. "
            f"It is recommended to collect cleaner data or fix missing values "
            f"before making big business decisions from this model."
        )

    return rec
def gen_rec(session_id,rec):
    if not rec:
        print("No recomendations found........")
        return []
    now = datetime.datetime.now()
    for r in rec:
        print("-",r)
        phase1_database.run_query("INSERT INTO insights (session_id, insight_text, created_on) VALUES (%s, %s, %s)",
            (session_id, r, now))
    print("_______________________________\n")
    return rec