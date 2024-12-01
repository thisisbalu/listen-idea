import time
import logging
from email_handler import connect_to_email, fetch_unread_emails
from db_handler import insert_email_data
from utils import retry_on_internet_issue, is_internet_available
from config import CHECK_INTERVAL

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def process_email(email_data):
    """Process the email data and insert it into the database."""
    body = email_data["body"]
    if "||" in body:
        parts = body.split("||")
        if len(parts) == 3:
            about, categories, tags = parts
            insert_email_data(about.strip(), categories.strip(), tags.strip())
        else:
            logging.warning("Email body does not have the correct format.")
    else:
        logging.warning("Email body does not contain '||' separators.")


def listen_for_emails():
    """Continuously listen for new emails and process them."""
    while True:
        try:
            mail = retry_on_internet_issue(connect_to_email, retry_interval=CHECK_INTERVAL)
            logging.info("Listening for new emails...")
            while True:
                if not is_internet_available():
                    raise ConnectionError("Lost internet connectivity. Reconnecting...")
                emails = fetch_unread_emails(mail)
                for email_data in filter(None, emails):
                    logging.info(f"Processing email: {email_data['subject']}")
                    process_email(email_data)
                    time.sleep(CHECK_INTERVAL)  # Check every interval for new emails
                time.sleep(CHECK_INTERVAL)
        except Exception as e:
            logging.error(f"Error while listening for emails: {e}")
            if isinstance(e, ConnectionError):
                logging.warning("Reconnecting to the email server...")
            time.sleep(CHECK_INTERVAL)  # Retry after a delay
        finally:
            try:
                if 'mail' in locals() and mail:
                    mail.logout()
            except Exception as logout_error:
                logging.warning(f"Error during logout: {logout_error}")


if __name__ == "__main__":
    listen_for_emails()
