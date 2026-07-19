import phase1_database
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(name, password):
    existing = phase1_database.run_query(
        "select user_id from Users where user_name = %s", (name,), fetch=True
    )
    if existing:
        print("User already exists")
        return None

    now = datetime.now()
    hashed_password = generate_password_hash(password)
    new_user = phase1_database.run_query(
        "insert into Users (user_name, password, created_on) values (%s, %s, %s)",
        (name, hashed_password, now),
    )
    print(f"User registered successfully. Your user ID is {new_user}")
    return new_user


def login(name, password):
    existing = phase1_database.run_query(
        "select user_id, password from Users where user_name = %s",
        (name,),
        fetch=True,
    )
    if existing and check_password_hash(existing[0][1], password):
        print("User found. Welcome back")
        return [(existing[0][0],)]

    print("Incorrect username or password")
    return None
