import os
import time
import smtplib
import requests
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

API_URL = os.getenv("COMPANY_API")
INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

def fetch_latest_company():
    try:
        response = session.post(API_URL, headers=HEADERS, json={})
        response.raise_for_status()
        data = response.json()
        return data.get("company_name")
    except Exception as e:
        print("❌ Error while fetching company:", e)
        return None

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

def main():
    seen = fetch_latest_company()
    if not seen:
        print("❌ Could not fetch initial company. Exiting.")
        return

    print(f"✅ Monitoring started. First company seen: {seen}")

    while True:
        time.sleep(INTERVAL)
        latest = fetch_latest_company()
        if latest and latest != seen:
            print(f"🔔 New company detected: {latest}")
            send_email(
                subject=f"🚨 New Company: {latest}",
                body=f"A new company is now listed: {latest}"
            )
            seen = latest
        else:
            print(f"⏳ No change. Still seeing: {seen}")

if __name__ == "__main__":
    main()
