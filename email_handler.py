import imaplib
import email
from email.header import decode_header
import logging
from config import IMAP_SERVER, EMAIL, PASSWORD

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
