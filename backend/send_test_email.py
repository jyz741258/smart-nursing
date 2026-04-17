"""直接发送测试邮件到指定邮箱"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env')

# 目标邮箱
email_to = "2118422447@qq.com"
code = "123456"

mail_config = {
    'server': os.getenv('MAIL_SERVER'),
    'port': int(os.getenv('MAIL_PORT', 465)),
    'use_ssl': os.getenv('MAIL_USE_SSL', 'True').lower() == 'true',
    'username': os.getenv('MAIL_USERNAME'),
    'password': os.getenv('MAIL_PASSWORD'),
    'sender': os.getenv('MAIL_DEFAULT_SENDER')
}

print("Email config:")
print(f"  Server: {mail_config['server']}")
print(f"  Port: {mail_config['port']}")
print(f"  UseSSL: {mail_config['use_ssl']}")
print(f"  Username: {mail_config['username']}")
print(f"  Password: {'Set' if mail_config['password'] else 'Not set'}")
print()

# 创建邮件
msg = MIMEMultipart('alternative')
msg['Subject'] = 'Smart Nursing System - Verification Code'
msg['From'] = mail_config['sender']
msg['To'] = email_to

text_content = f"""Smart Nursing System - Verification Code

Your verification code is: {code}

Code valid for 5 minutes.

---
Smart Nursing System
"""

msg.attach(MIMEText(text_content, 'plain', 'utf-8'))

print(f"Sending email to {email_to}...")

try:
    if mail_config['use_ssl']:
        server = smtplib.SMTP_SSL(mail_config['server'], mail_config['port'])
    else:
        server = smtplib.SMTP(mail_config['server'], mail_config['port'])
        server.ehlo()
        server.starttls()

    server.login(mail_config['username'], mail_config['password'])
    server.sendmail(mail_config['sender'], [email_to], msg.as_string())
    server.quit()

    print("Email sent successfully!")
except smtplib.SMTPAuthenticationError as e:
    print(f"Auth failed: {e}")
    print("Check MAIL_PASSWORD in .env file")
except smtplib.SMTPConnectError as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"Failed: {type(e).__name__}: {e}")