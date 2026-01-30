from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy

# CONFIGURATION
INSTANCE_CONNECTION_NAME = "YOUR_PROJECT:REGION:INSTANCE" # UPDATE THIS!
DB_USER = "postgres"
DB_PASS = "YOUR_DB_PASSWORD" # UPDATE THIS!
DB_NAME = "quiz_db"

def init_db():
    # 1. Connect
    with Connector() as connector:
        conn = connector.connect(INSTANCE_CONNECTION_NAME, "pg8000", user=DB_USER, password=DB_PASS, db=DB_NAME, ip_type=IPTypes.PUBLIC)
        pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=lambda: conn)
        
        # 2. Create Tables
        with pool.connect() as db_conn:
            db_conn.execute(sqlalchemy.text("""
                CREATE TABLE IF NOT EXISTS users (user_id SERIAL PRIMARY KEY, username VARCHAR(50));
                CREATE TABLE IF NOT EXISTS resources (resource_id SERIAL PRIMARY KEY, title VARCHAR(255));
                CREATE TABLE IF NOT EXISTS quiz_attempts (attempt_id SERIAL PRIMARY KEY, user_id INT, score INT, total_questions INT);
                -- Insert dummy user for testing
                INSERT INTO users (username) VALUES ('test_user') ON CONFLICT DO NOTHING;
            """))
            db_conn.commit()
            print("✅ Tables Created!")

if __name__ == "__main__":
    init_db()