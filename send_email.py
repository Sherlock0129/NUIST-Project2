import smtplib
from email.message import EmailMessage

# Set sender and recipient information
from_email_addr = "1843017840@qq.com"  
from_email_pass = "dclxjjjrkmxfchfe"  
to_email_addr = "2025352914@qq.com"   

# Create an email object.
msg = EmailMessage()

# Set email content
body = "Hello from Raspberry Pi"
msg.set_content(body)

# Set sender, recipient and topic
msg['From'] = from_email_addr
msg['To'] = to_email_addr
msg['Subject'] = 'TEST EMAIL'

# 连接到SMTP服务器（以Outlook为例）
try:
    server = smtplib.SMTP('smtp.qq.com', 587)
    server.starttls()
    server.login(from_email_addr, from_email_pass)
    server.send_message(msg)
    print('Email sent successfully')
except Exception as e:
    print(f'Error sending email: {e}')
finally:
    server.quit()