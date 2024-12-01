import imaplib
import email
from email.header import decode_header
import time
import socket
import logging

# Email credentials
EMAIL = "exceptiondecoded@gmail.com"  # Replace with your email
PASSWORD = "fcrd gheb shjx jocq"
IMAP_SERVER = "imap.gmail.com"  # Replace with your IMAP server (e.g., imap.gmail.com)
CHECK_INTERVAL = 2  # Check interval in seconds

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Utility Functions
def is_internet_connected():
    """Check if the internet connection is available."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


def retry_on_internet_issue(func):
    """Retry a function if there's an internet connectivity issue."""
    while True:
        if not is_internet_connected():
            logging.warning("No internet connection. Retrying...")
            time.sleep(CHECK_INTERVAL)
            continue
        try:
            return func()
        except Exception as e:
            logging.error(f"Error: {e}. Retrying...")
            time.sleep(CHECK_INTERVAL)


# Email Functions
def connect_to_email():
    """Establish a connection to the email server."""
    logging.info("Attempting to connect to the email server...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    logging.info("Successfully connected to the email server.")
    return mail


def fetch_unread_emails(mail):
    """Fetch unread emails with a subject of 'idea'."""
    mail.select("inbox")
    status, messages = mail.search(None, '(UNSEEN SUBJECT "idea")')
    if status != "OK":
        logging.info("No new emails found.")
        return []

    email_ids = messages[0].split()
    return [parse_email(mail, email_id) for email_id in email_ids if email_id]


def parse_email(mail, email_id):
    """Parse an email and return its details."""
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    if status != "OK":
        logging.warning("Failed to fetch email.")
        return None

    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject = decode_header_value(msg["Subject"])
            sender = msg.get("From")
            body = extract_email_body(msg)

            # Mark email as read
            mail.store(email_id, "+FLAGS", "\\Seen")

            return {"subject": subject, "from": sender, "body": body}
    return None


def decode_header_value(header):
    """Decode a header value (e.g., subject or sender)."""
    value, encoding = decode_header(header)[0]
    if isinstance(value, bytes):
        return value.decode(encoding if encoding else "utf-8")
    return value


def extract_email_body(msg):
    """Extract the body of an email."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                return decode_payload(part.get_payload(decode=True), part.get_content_charset())
    else:
        return decode_payload(msg.get_payload(decode=True), msg.get_content_charset())
    return ""


def decode_payload(payload, charset):
    """Decode the payload using the specified charset."""
    charset = charset or "utf-8"
    try:
        return payload.decode(charset)
    except (LookupError, UnicodeDecodeError):
        return payload.decode("latin1", errors="replace")


# Main Functions
def reconnect_on_failure(func):
    """Reconnect and retry if a connection error occurs."""
    while True:
        mail = retry_on_internet_issue(connect_to_email)
        try:
            func(mail)
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, socket.error):
            logging.warning("Connection lost. Reconnecting...")
        finally:
            try:
                mail.logout()
            except Exception as e:
                logging.warning(f"Error during logout: {e}")


def listen_for_emails(mail):
    """Continuously listen for new emails."""
    logging.info("Listening for new emails...")
    while True:
        emails = fetch_unread_emails(mail)
        for email_data in filter(None, emails):
            logging.info("----- New Email -----")
            logging.info(f"From: {email_data['from']}")
            logging.info(f"Subject: {email_data['subject']}")
            logging.info(f"Body: {email_data['body']}")
            logging.info("---------------------")
        time.sleep(CHECK_INTERVAL)


# Entry Point
if __name__ == "__main__":
    reconnect_on_failure(listen_for_emails)
