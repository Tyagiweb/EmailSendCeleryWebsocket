import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = 'prashanttyagipt17@gmail.com'
EMAIL_PASSWORD = 'urop ebso unhx kvqe '

msg = EmailMessage()
msg['Subject'] = 'Test from Python'
msg['From'] = EMAIL_ADDRESS
msg['To'] = 'prashanttyagi5386748@gmail.com'
msg.set_content('This is a test email sent from Python using Gmail SMTP.')

try:
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Failed to send email:")
    print(e)
