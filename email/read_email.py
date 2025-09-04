import imaplib
import email
from email.header import decode_header
import datetime
import json

# nt mail sever: nt1
mail_server = "ncmail.ntplc.co.th"

def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

def search_emails(email_user, email_password, sender=None, subject=None, body=None, since=None):
    """ search all email """
    # Connect to the server
    imap = imaplib.IMAP4_SSL(mail_server)  # Replace with your email provider's IMAP server
    # Login to your account
    imap.login(email_user, email_password)

    # Select the mailbox you want to check (e.g., inbox)
    imap.select("INBOX")

    # Construct the search criteria
    search_criteria = ['(ALL)']  # All email, Only unread emails use (UNSEEN)
    if sender:
        search_criteria.append(f'(FROM "{sender}")')
    if subject:
        search_criteria.append(f'(SUBJECT "{subject}")')
    if since:
        date_str = since.strftime("%d-%b-%Y")
        search_criteria.append(f'(SINCE "{date_str}")')
    search_criteria = " ".join(search_criteria)

    # Search for emails matching the criteria
    status, messages = imap.search(None, search_criteria)
    email_ids = messages[0].split()

    # Fetch emails
    for email_id in email_ids:
        # Fetch the email by ID
        status, msg_data = imap.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                # Decode email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # If it's a bytes, decode to str
                    subject = subject.decode(encoding if encoding else "utf-8")
                # Email sender
                from_ = msg.get("From")
                print("Subject:", subject)
                print("From:", from_)
                # Get the email body
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if "attachment" not in content_disposition:
                            # Print the plain text body
                            if content_type == "text/plain":
                                print(body)
                else:
                    # If the email is not multipart
                    body = msg.get_payload(decode=True).decode()
                    print(body)

    # Close the connection and logout
    imap.close()
    imap.logout()

def search_latest_email(email_user, email_password, sender=None, subject=None, body=None, since=None):
    """ search only last email """
    # Connect to the server
    imap = imaplib.IMAP4_SSL(mail_server)  # Replace with your email provider's IMAP server
    # Login to your account
    imap.login(email_user, email_password)

    # Select the mailbox you want to check (e.g., inbox)
    imap.select("inbox")

    # Construct the search criteria
    search_criteria = []
    if sender:
        search_criteria.append(f'(FROM "{sender}")')
    if subject:
        search_criteria.append(f'(SUBJECT "{subject}")')
    if since:
        date_str = since.strftime("%d-%b-%Y")
        search_criteria.append(f'(SINCE "{date_str}")')
    if not search_criteria:
        search_criteria = "ALL"  # If no criteria provided, search all emails
    else:
        search_criteria = " ".join(search_criteria)

    # Search for emails matching the criteria
    status, messages = imap.search(None, search_criteria)
    email_ids = messages[0].split()

    if email_ids:
        latest_email_id = email_ids[-1]  # Get the latest email ID (last in the list)

        # Fetch the latest email by ID
        status, msg_data = imap.fetch(latest_email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                # Decode email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # If it's a bytes, decode to str
                    subject = subject.decode(encoding if encoding else "utf-8")
                # Email sender
                from_ = msg.get("From")
                print("Subject:", subject)
                print("From:", from_)
                # Get the email body
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if "attachment" not in content_disposition:
                            # Print the plain text body
                            if content_type == "text/plain":
                                print(body)
                else:
                    # If the email is not multipart
                    body = msg.get_payload(decode=True).decode()
                    print(body)
                found = True
    else:
        print("No emails found.")
        found = None

    # Close the connection and logout
    imap.close()
    imap.logout()
    return(found)

# Example usage
config = load_config()
email_user = config["email_user"]
email_password = config["email_password"]

# search_emails(email_user, email_password, sender="xxx@ntplc.co.th", subject="แบบฟอร์มและรายการส่งมอบ โครงการเว็บแบบสั้นที่มีความปลอดภัย", since=datetime.date(2024, 9, 1))
search_emails(email_user, email_password, sender="xxx@ntplc.co.th", since=datetime.date(2024, 9, 1))
print("latest email: ")
search_latest_email(email_user, email_password, sender="xxx@ntplc.co.th", subject="We've Noticed a New Metabase Login, Pornthep", since=datetime.date(2024, 9, 1))

# กำหนดเป็นเดือนปัจจุบัน (เดือนที่โปรแกรมทำงาน)
# หาวันที่ปัจจุบัน

today = datetime.date.today()
# กำหนดให้ since เป็นวันที่ 1 ของเดือนปัจจุบัน
since = datetime.date(today.year, today.month, 1)
