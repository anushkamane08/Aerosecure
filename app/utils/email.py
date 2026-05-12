import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email, subject, body):
    sender_email = "rbacpbl@gmail.com"
    sender_password = "opak cdvs fjnx evmv"  # 🔥 app password

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    msg.attach(MIMEText(body, 'plain'))
    

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully")

    except Exception as e:
        print("Email error:", e)