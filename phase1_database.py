import mysql.connector
from mysql.connector import Error
import phase1_config


def sql_server(use_db=False):
    try:
        config = {
            "host": phase1_config.db_host,
            "port": phase1_config.db_port,
            "user": phase1_config.db_user,
            "password": phase1_config.db_pass,
            "ssl_ca": phase1_config.db_ssl_ca,
            "ssl_verify_cert": True,
        }

        if use_db:
            config["database"] = phase1_config.db_name

        connections = mysql.connector.connect(**config)
        return connections

    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def connect_to_database():
    return sql_server(use_db=True)


def create_database_if_not_exists():
    """
    Aiven already provides the database (defaultdb),
    so there is no need to create it.
    """
    print(f"Using existing database: {phase1_config.db_name}")
    return True

def creating_all_tables():
    connections = connect_to_database()
    if connections is None:
        return False
    cursor = connections.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(50),
    password VARCHAR(255),
    created_on DATETIME
);
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    dataset_name VARCHAR(350),
    current_step VARCHAR(350),
    created_on DATETIME,
    last_updated DATETIME,
    is_completed VARCHAR(3) DEFAULT 'no'
);
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS DATASET_METADATA (
    Dataset_id INT AUTO_INCREMENT PRIMARY KEY,
    Session_ID INT,
    file_path VARCHAR(90),
    Missing_values INT,
    Duplicate_rows INT,
    Created_on DATETIME
);
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS CLEANED_LOGS (
    Log_id INT AUTO_INCREMENT PRIMARY KEY,
    Session_ID INT,
    Actions_taken VARCHAR(350),
    Created_on DATETIME
);
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS feature_engineering_logs (
    fe_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    pipeline_path VARCHAR(350),
    details TEXT,
    created_on DATETIME
);
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS models (
    tm_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    model_name VARCHAR(350),
    model_path VARCHAR(350),
    score FLOAT,
    created_on DATETIME
);
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    p_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    input_values VARCHAR(350),
    predicted_value VARCHAR(350),
    created_on DATETIME
);
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS insights (
    is_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    insight_text TEXT,
    created_on DATETIME
);
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (
    r_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    report_path VARCHAR(350),
    created_on DATETIME
);
""")

    connections.commit()
    cursor.close()
    connections.close()
    print("All tables are ready")
    return True


def run_query(query, values=None, fetch=False):
    connections = connect_to_database()
    if connections is None:
        return None
    cursor = connections.cursor(buffered=True)
    try:
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        if fetch:
            result = cursor.fetchall()
        else:
            connections.commit()
            result = cursor.lastrowid
        return result
    except Error as e:
        print(f"Query error: {e}")
        return None
    finally:
        cursor.close()
        connections.close()

