def select_business_goal(name):
    options = {
        "1": "predict a numeric value",
        "2": "classify records into categories",
        "3": "group similar records together",
        "4": "just explore the dataset (no modeling)",
        "5": "comparing multiple machine learning models",
    }

    print(f"What do you want to achieve {name}")
    print()
    print("Choose one of the following......")
    for key, option in options.items():
        print(f"               {key}. {option}")

    choice = input("enter your choice (1/2/3/4/5): ").strip()
    goal = options.get(choice)
    if goal is None:
        print("Invalid choice.")
        return None

    print(f"Goal selected: {goal}")
    return goal
def select_workflow(goal):
    if goal == "predict a numeric value":
        workflow = "regression"
        reason = ("Regression is used because you want to predict a NUMBER, "
                   "such as a price, score, or amount.")

    elif goal == "classify records into categories":
        workflow = "classification"
        reason = ("Classification is used because you want to sort data into "
                   "CATEGORIES or LABELS, such as 'yes/no' or 'high/medium/low'.")

    elif goal == "group similar records together":
        workflow = "clustering"
        reason = ("Clustering (K-Means) is used because you want to find "
                   "NATURAL GROUPS in your data without any predefined labels.")

    elif goal == "comparing multiple machine learning models":
        workflow = "model_benchmarking"
        reason = ("Model Benchmarking is used because you want to train several "
                   "models and see which one performs best.")

    else:
        workflow = "data_analytics"
        reason = ("Data Analytics is used because you only want to explore and "
                   "understand your dataset, without building a prediction model.")

    print(f"\nWorkflow selected: {workflow}")
    print("Reason:", reason)
    return workflow
