# Usage:
# python advertising_email.py username email_text.txt csv_of_emails.csv attachment1 attachment2 ...

import smtplib
from getpass import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sys
import csv
import time

SMTP_SERVER = "outgoing.mit.edu"
SMTP_SERVER_PORT = '465'

email_account_name = sys.argv[1]
with open(sys.argv[2], 'r') as file:
    message_content = file.read()
message_subject = ""
message_cc = ""

attachments = []
for arg in sys.argv[4:]:
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload(open(arg, 'rb').read())
    encoders.encode_base64(payload)
    payload.add_header('Content-Decomposition', 'attachment', filename=arg)
    attachments.append(payload)

server = smtplib.SMTP_SSL('%s:%s' % (SMTP_SERVER, SMTP_SERVER_PORT))
server.login(email_account_name, getpass(prompt="Email Password: "))

with open(sys.argv[3],'r') as csv_file:
    data = csv.reader(csv_file)
    for row in data:
        uni_name = row[0]
        custom_message_subject = message_subject.replace('<University>', uni_name).replace('<university>', uni_name)
        custom_message_content = message_content.replace('<University>', uni_name).replace('<university>', uni_name)

        message_to = ""
        for recipient in row[1:]:
            message_to += str(recipient) + ","
        message_to = message_to[:-1]

        message = MIMEMultipart()
        message.attach(MIMEText(custom_message_content, 'plain'))
        message['From'] = "%s@mit.edu" % email_account_name
        message['To'] = message_to
        message['Cc'] = message_cc
        message['Subject'] = custom_message_subject

        for attachment in attachments:
            message.attach(attachment)

        server.send_message(message.as_string())

        time.sleep(2)
        
server.quit()