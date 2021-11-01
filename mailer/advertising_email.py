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
REPLY_TO = "physgaap@mit.edu"

email_account_name = sys.argv[1]
with open(sys.argv[2], 'r') as file:
    message_content = file.read()
message_subject = "MIT Physics Graduate Application Assistance Program 2021"
message_cc = ""
message_bcc = "npaladin@mit.edu"

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
    next(data)
    for row in data:
        uni_name = row[0]
        contact_name = row[2]
        custom_message_subject = message_subject.replace('{{University}}', uni_name).replace('{{university}}', uni_name).replace('{{Recipient}}', contact_name).replace('{{recipient}}', contact_name)
        custom_message_content = message_content.replace('{{University}}', uni_name).replace('{{university}}', uni_name).replace('{{Recipient}}', contact_name).replace('{{recipient}}', contact_name)

        message_to = row[1]
        message_from = "%s@mit.edu" % email_account_name
        message_to_all = message_to.split(",") + message_cc.split(",") + message_bcc.split(",")

        message = MIMEMultipart()
        message.attach(MIMEText(custom_message_content, 'html'))
        message['From'] = message_from
        message['Reply-To'] = REPLY_TO
        message['To'] = message_to
        message['Cc'] = message_cc
        message['Subject'] = custom_message_subject

        for attachment in attachments:
            message.attach(attachment)

        server.send_message(message, message_from, message_to_all)

        time.sleep(2)
        
server.quit()