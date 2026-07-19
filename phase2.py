import phase1_database
from datetime import datetime


def create_new_session(user_id, dataset_name):
    now = datetime.now()
    # Insert a new session row: user_id, dataset_name, current_step, created_on, last_updated, is_completed
    new_session = phase1_database.run_query(
        """INSERT INTO sessions (user_id, dataset_name, current_step, created_on, last_updated, is_completed)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (user_id, dataset_name, "session_started", now, now, "no"),
    )
    print(f"New session created......\nsession ID: {new_session}")
    return new_session
def update_session_step(session_id, step_name):
    now = datetime.now()
    phase1_database.run_query(
        "UPDATE sessions SET current_step = %s, last_updated = %s WHERE session_id = %s",
        (step_name, now, session_id)
    )
    print("Progress saved. Current step:", step_name)


def mark_session_completed(session_id):
    phase1_database.run_query(
        "UPDATE sessions SET is_completed = 'yes' WHERE session_id = %s",
        (session_id,)
    )


def get_unfinished_sessions(user_id):
    rows = phase1_database.run_query(
        """SELECT session_id, dataset_name, current_step, last_updated
           FROM sessions
           WHERE user_id = %s AND is_completed = 'no'
           ORDER BY last_updated DESC""",
        (user_id,),
        fetch=True
    )
    return rows


def show_unfinished_sessions(user_id):
    sessions = get_unfinished_sessions(user_id)

    if not sessions:
        print("You have no unfinished sessions.")
        return []

    print("\nHere are your unfinished projects:")
    print("-" * 60)
    for row in sessions:
        session_id, dataset_name, current_step, last_updated = row
        print(f"Session ID: {session_id} | Dataset: {dataset_name} "
              f"| Last Step: {current_step} | Last Updated: {last_updated}")
    print("-" * 60)
    return sessions


def get_session_step(session_id):
    result = phase1_database.run_query(
        "SELECT current_step FROM sessions WHERE session_id = %s",
        (session_id,),
        fetch=True
    )
    if result:
        return result[0][0]
    return None
