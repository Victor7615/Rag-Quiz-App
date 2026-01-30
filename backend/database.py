import os
import sqlalchemy
from sqlalchemy.sql import text

def get_db_engine():
    db_user = os.environ.get("DB_USER", "admin")
    db_pass = os.environ.get("DB_PASS", "securepassword123")
    db_name = os.environ.get("DB_NAME", "quiz_db")
    
    # 1. Check for Cloud Run (Production)
    cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

    if cloud_sql_connection_name:
        # --- PROD: GCP CLOUD RUN ---
        db_socket_dir = "/cloudsql"
        url = sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={
                "unix_sock": f"{db_socket_dir}/{cloud_sql_connection_name}/.s.PGSQL.5432"
            }
        )
    else:
        # --- DEV: DOCKER or LOCAL ---
        # FIX IS HERE: Read 'DB_HOST' from env, default to 'localhost' only if missing
        db_host = os.environ.get("DB_HOST", "localhost") 
        
        url = sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            host=db_host,  # <--- Now it will use 'db' when running in Docker
            port=5432,
            database=db_name
        )

    return sqlalchemy.create_engine(url)
def save_score(user_id, resource_name, score, total):
    """Saves quiz result to the database."""
    engine = get_db_engine()
    # Simple insert query
    query = text("""
        INSERT INTO quiz_attempts (user_id, resource_id, score, total_questions) 
        VALUES (:uid, (SELECT resource_id FROM resources WHERE title=:rname LIMIT 1), :score, :total)
    """)
    
    with engine.connect() as conn:
        conn.execute(query, {"uid": user_id, "rname": resource_name, "score": score, "total": total})
        conn.commit()