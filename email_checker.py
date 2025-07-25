import imaplib
import email
from email.header import decode_header
import joblib

# Load model and vectorizer
model = joblib.load("spam_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# Your Gmail credentials
USERNAME = "rajeshsanagala551@gmail.com"       # <-- Replace with your Gmail address
PASSWORD = "qqyhemkjsuztviiq"     # <-- Paste your 16-digit app password here

# Connect to Gmail IMAP server
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(USERNAME, PASSWORD)
mail.select("inbox")  # Select inbox

# Search for unseen (unread) emails
status, messages = mail.search(None, "(UNSEEN)")
email_ids = messages[0].split()

print(f"📬 Found {len(email_ids)} new email(s)\n")

# Loop through each unseen email
for e_id in email_ids:
    _, msg_data = mail.fetch(e_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])

            # Decode subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")

            # Get plain text body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                        except:
                            continue
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            # Combine subject and body
            full_text = subject + " " + body

            # Predict spam or ham
            vector = vectorizer.transform([full_text])
            prediction = model.predict(vector)[0]

            print("📨 Subject:", subject.strip())
            print("🔍 Prediction:", "🚫 Spam" if prediction == 1 else "✅ Not Spam")
            print("="*50)
