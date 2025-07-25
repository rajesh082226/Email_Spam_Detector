import streamlit as st
import imaplib
import email
from email.header import decode_header
import joblib
import matplotlib.pyplot as plt

# Load spam classifier and vectorizer
model = joblib.load("spam_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# Direct Gmail credentials (Hardcoded)
USERNAME = "rajeshsanagala551@gmail.com"
PASSWORD = "coly ntje maun hpsh"  # This is your Gmail App Password (keep secret)

# Function to fetch latest 5 emails
def fetch_recent_emails():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(USERNAME, PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        latest_ids = email_ids[-5:]

        emails = []
        for e_id in latest_ids:
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for part in msg_data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")

                    emails.append((subject.strip(), body.strip()))
        return emails
    except Exception as e:
        st.error(f"❌ Failed to fetch emails: {e}")
        return []

# Streamlit UI
st.title("📧 Spam Email Detector (Gmail Direct)")

if st.button("📥 Fetch and Analyze Emails"):
    emails = fetch_recent_emails()

    if not emails:
        st.warning("No emails retrieved.")
    else:
        spam_count = 0
        ham_count = 0

        for i, (subject, body) in enumerate(emails):
            with st.expander(f"✉️ Email {i+1}: {subject}"):
                st.write(body)

                combined_text = subject + " " + body
                features = vectorizer.transform([combined_text])
                prediction = model.predict(features)[0]

                if prediction == 1:
                    spam_count += 1
                else:
                    ham_count += 1

                st.markdown(f"**📨 Subject:** {subject}")
                st.markdown(f"**🔍 Prediction:** {'🚫 Spam' if prediction == 1 else '✅ Not Spam'}")

        # Summary
        total = spam_count + ham_count
        st.subheader("📊 Summary")
        st.write(f"✅ Not Spam: {ham_count}")
        st.write(f"🚫 Spam: {spam_count}")

        if total > 0:
            percent_spam = int((spam_count / total) * 100)
            st.progress(percent_spam, text=f"{percent_spam}% Spam")

            labels = ['Not Spam', 'Spam']
            sizes = [ham_count, spam_count]
            colors = ['#4CAF50', '#FF6347']
            explode = (0, 0.1)

            fig, ax = plt.subplots()
            ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='%1.1f%%', shadow=True, startangle=140)
            ax.axis('equal')
            st.pyplot(fig)
