"""测试邮件发送功能"""
import os
from dotenv import load_dotenv
load_dotenv('.env')

print('邮件配置检查:')
print(f'  MAIL_SERVER: {os.getenv("MAIL_SERVER")}')
print(f'  MAIL_PORT: {os.getenv("MAIL_PORT")}')
print(f'  MAIL_USE_SSL: {os.getenv("MAIL_USE_SSL")}')
print(f'  MAIL_USE_TLS: {os.getenv("MAIL_USE_TLS")}')
print(f'  MAIL_USERNAME: {os.getenv("MAIL_USERNAME")}')
print(f'  MAIL_PASSWORD: {"已设置" if os.getenv("MAIL_PASSWORD") else "未设置"}')
print()

# 测试发送邮件
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

code = '123456'
email = input('请输入要测试的邮箱地址: ')

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
msg['To'] = email

# HTML邮件内容
html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #22c55e, #16a34a); padding: 30px; text-align: center; color: white; }
        .header h1 { margin: 0; font-size: 24px; }
        .content { padding: 40px 30px; text-align: center; }
        .code-box { background: linear-gradient(135deg, #f0fdf4, #dcfce7); border: 2px dashed #22c55e; border-radius: 16px; padding: 30px; margin: 20px 0; }
        .code { font-size: 42px; font-weight: bold; color: #16a34a; letter-spacing: 12px; font-family: 'Courier New', monospace; }
        .tips { color: #666; font-size: 14px; margin-top: 20px; line-height: 1.6; }
        .warning { color: #ef4444; font-size: 12px; margin-top: 30px; }
        .footer { background: #f9f9f9; padding: 20px; text-align: center; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>智慧养老系统</h1>
        </div>
        <div class="content">
            <p style="font-size: 18px; color: #333;">您好！</p>
            <p style="font-size: 16px; color: #666;">感谢您注册智慧养老系统，您的验证码是：</p>
            <div class="code-box">
                <div class="code">""" + code + """</div>
            </div>
            <p class="tips">
                验证码 <strong>5分钟</strong> 内有效，请尽快完成验证<br>
                如非本人操作，请忽略此邮件
            </p>
            <p class="warning">请勿向任何人透露此验证码，谨防诈骗！</p>
        </div>
        <div class="footer">
            <p>智慧养老系统 - 让科技守护每一位老人</p>
            <p>此邮件由系统自动发送，请勿回复</p>
        </div>
    </div>
</body>
</html>
"""

# 纯文本版本
text_content = """
智慧养老系统 - 注册验证码

您好！

感谢您注册智慧养老系统，您的验证码是：""" + code + """

验证码 5分钟 内有效，请尽快完成验证。
如非本人操作，请忽略此邮件。

请勿向任何人透露此验证码，谨防诈骗！

---
智慧养老系统
此邮件由系统自动发送，请勿回复
"""

# 添加邮件内容
msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
msg.attach(MIMEText(html_content, 'html', 'utf-8'))

try:
    if mail_config['use_ssl']:
        print(f"使用 SSL 连接 smtp.qq.com:465...")
        server = smtplib.SMTP_SSL(mail_config['server'], mail_config['port'])
    else:
        print(f"使用 STARTTLS 连接 smtp.qq.com:587...")
        server = smtplib.SMTP(mail_config['server'], mail_config['port'])
        server.ehlo()
        server.starttls()
    
    server.login(mail_config['username'], mail_config['password'])
    server.sendmail(mail_config['sender'], [email], msg.as_string())
    server.quit()
    print(f'邮件发送成功! 请检查邮箱 {email}')
except smtplib.SMTPAuthenticationError as e:
    print(f'SMTP 认证失败: {e}')
    print('提示: QQ邮箱需要使用授权码，而不是登录密码')
except smtplib.SMTPException as e:
    print(f'SMTP 发送失败: {e}')
except Exception as e:
    print(f'发送失败: {type(e).__name__}: {e}')
