import psycopg2
import logging
from config import DATABASE_CONFIG, TABLE_NAME


def insert_email_data(about, categories, tags):
    """Insert email data into the database."""
    query = f"""
    INSERT INTO {TABLE_NAME} (about, categories, tags)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    try:
        with psycopg2.connect(**DATABASE_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (about, categories, tags))
                email_id = cur.fetchone()[0]
                logging.info(f"Inserted email data with ID {email_id}.")
    except Exception as e:
        logging.error(f"Database insert failed: {e}")
