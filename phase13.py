import datetime
import phase1_database
import pandas as pd
def ask_user_input(columns):
    inp = {}
    for c in columns:
        while True:
            try:
                ch = float(input(f"enter value for {c}: ").strip())
                break
            except ValueError as e:
                print(f"ERROR: {e}")
        inp[c] = ch
    return inp
def sing_pred(model,col,inp):
    ir = pd.DataFrame([inp],columns=col)
    pred = model.predict(ir)
    return pred[0]
def what_if(model,columns,session_id):
    while True:
        uvs = ask_user_input(columns)
        pred = sing_pred(model,columns,uvs)
        print(f"\nPREDICTION RESULT: {pred}")

        # Save this simulation to the database for future reference
        now = datetime.datetime.now()
        phase1_database.run_query(
            """INSERT INTO predictions (session_id, input_values, predicted_value, created_on)
               VALUES (%s, %s, %s, %s)""",
            (session_id, str(uvs), str(pred), now)
        )

        again = input("\nTry another set of values? (yes/no): ").strip().lower()
        if again != "yes":
            break

    print("--------------------------------\n")