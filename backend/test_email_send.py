"""完整测试邮件发送"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env')

print("=" * 50)
print("邮件发送测试")
print("=" * 50)

# 检查配置
print("\n1. 配置检查:")
print(f"   MAIL_SERVER: {os.getenv('MAIL_SERVER')}")
print(f"   MAIL_PORT: {os.getenv('MAIL_PORT')}")
print(f"   MAIL_USE_SSL: {os.getenv('MAIL_USE_SSL')}")
print(f"   MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
print(f"   MAIL_PASSWORD: {'已设置' if os.getenv('MAIL_PASSWORD') else '未设置'}")

# 尝试发送邮件
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

code = "123456"
email_to = input("\n2. 请输入目标邮箱地址: ")

mail_config = {
    'server': os.getenv('MAIL_SERVER'),
    'port': int(os.getenv('MAIL_PORT', 465)),
    'use_ssl': os.getenv('MAIL_USE_SSL', 'True').lower() == 'true',
    'username': os.getenv('MAIL_USERNAME'),
    'password': os.getenv('MAIL_PASSWORD'),
    'sender': os.getenv('MAIL_DEFAULT_SENDER')
}

# 创建邮件
msg = MIMEMultipart('alternative')
msg['Subject'] = '【智慧养老系统】注册验证码'
msg['From'] = mail_config['sender']
msg['To'] = email_to

# HTML邮件内容
html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 20px auto; padding: 20px;">
        <h2 style="color: #22c55e;">智慧养老系统</h2>
        <p>您好！</p>
        <p>您的验证码是: <strong style="font-size: 24px; color: #16a34a;">""" + code + """</strong></p>
        <p>验证码 5分钟 内有效。</p>
        <p style="color: #666; font-size: 12px;">请勿向任何人透露此验证码。</p>
    </div>
</body>
</html>"""

text_content = """智慧养老系统 - 注册验证码

您好！

您的验证码是: """ + code + """

验证码 5分钟 内有效。

请勿向任何人透露此验证码。
"""

msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
msg.attach(MIMEText(html_content, 'html', 'utf-8'))

print("\n3. 尝试发送邮件...")

try:
    if mail_config['use_ssl']:
        print(f"   使用 SSL 连接 {mail_config['server']}:{mail_config['port']}")
        server = smtplib.SMTP_SSL(mail_config['server'], mail_config['port'])
    else:
        print(f"   使用 STARTTLS 连接 {mail_config['server']}:{mail_config['port']}")
        server = smtplib.SMTP(mail_config['server'], mail_config['port'])
        server.ehlo()
        server.starttls()

    print("   尝试登录...")
    server.login(mail_config['username'], mail_config['password'])

    print("   发送邮件...")
    server.sendmail(mail_config['sender'], [email_to], msg.as_string())
    server.quit()

    print("\n✅ 邮件发送成功!")
    print(f"   请检查邮箱 {email_to} (可能在垃圾箱)")
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ SMTP 认证失败: {e}")
    print("\n提示: QQ邮箱需要使用授权码，而不是登录密码")
    print("获取授权码方法:")
    print("  1. 登录 QQ 邮箱")
    print("  2. 设置 -> 账户 -> POP3/SMTP服务")
    print("  3. 开启服务并生成授权码")
    print("  4. 将授权码填入 .env 文件的 MAIL_PASSWORD")
except smtplib.SMTPConnectError as e:
    print(f"\n❌ 连接失败: {e}")
    print("\n可能是:")
    print("  - 端口 465 被防火墙阻止")
    print("  - 网络连接问题")
except TimeoutError as e:
    print(f"\n❌ 连接超时: {e}")
except Exception as e:
    print(f"\n❌ 发送失败: {type(e).__name__}: {e}")
