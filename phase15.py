def check_small_datasets(df,rows = 100):
    if df.shape[0] < rows:
        return (f"WARNING: Your dataset only has {df.shape[0]} rows and is insufficient for model training. "
                f"Minimum rows required is {rows}.")
    return None
def check_miss_values(df,warn = 0.3):
    for col in df.columns:
        miss = df[col].isnull().sum()
        total = len(df)
        if total == 0:
            continue
        pct = (miss/total)
        if pct > warn:
            return (f"WARNING: {pct*100:.1f}% of '{col}' is missing; consider collecting or reviewing more data")
    return None
def check_class_imbalance(target,warn = 0.9):
    vc = target.value_counts(normalize = True)
    if len(vc) == 0:
        return None
    top = vc.iloc[0]
    if top > warn:
        return (f"WARNING: One category makes up {top * 100:.1f} % of target column \n Leading to class Imbalance......")
    return None
def check_high_correlation(pairs):
    if pairs:
        return(f"WARNING: {len(pairs)} are highly corellated columns \nModel may get confused \nConsider removing duplicates")
    return None
def check_overfitting(tscore,tescore,lim = 0.15):
    gap = tscore - tescore
    if  gap > lim:
        return(f"WARNING: Model scores {tscore:.2f} \nConsider getting more features or more data...")
    return None
def check_poor_perf(evs,mini = 0.5):
    if evs < mini:
        return(f"WARNING: The model's evaluation score is only {evs:.2f} which is quiet low \nConsider gathering more information")
    return None
def run_all(df,target,pairs,tscore,tescore,evs):
    print("__________SMART ALERTS__________\n")
    warn = []
    w = check_small_datasets(df)
    if w:
        warn.append(w)
    w = check_miss_values(df)
    if w:
        warn.append(w)
    w = check_class_imbalance(target)
    if w:
        warn.append(w)
    w = check_high_correlation(pairs)
    if w:
        warn.append(w)
    w = check_overfitting(tscore,tescore)
    if w:
        warn.append(w)
    w = check_poor_perf(evs)
    if w:
        warn.append(w)
    if warn:
        for i, wa in enumerate(warn, start=1):
            print(f"{i}. {wa}")
    else:
        print("No major issues detected.....")

