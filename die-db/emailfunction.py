import email
import smtplib
import configparser
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

date_today = datetime.utcnow().strftime('%m.%d.%Y')

def send_email(self):
    config = configparser.ConfigParser()
    config.read('credentials.ini') 

    name = config.get('FROM', 'name')  
    sender = config.get('FROM', 'sender') 
    recipients = config.get('TO', 'recipients')
    user = config.get('LOGIN', 'user')
    password = config.get('LOGIN', 'password')
    server_addr = config.get('CLIENT', 'server_addr')
    port = config.get('CLIENT', 'port')

    try:
        SUBJECT = 'TrID New Update on triddefs.trd ({})'.format(date_today)

        msg = """
        Hi Team,
        There is a new update on the Detect-It-Easy git repository as of <date>.
        The new file has been uploaded to the S3 bucket.
        Thank you.
        name of team
        """

        html = """
        <html>
        
        <style> 
          p {{ font-family: Calibri; font-size: 16;}}
          pre {{ font-family: Calibri; font-size: 16;}}
        </style>
        
        <body>
        <p>Hi Team,</p>
        <p>There is a new update on the Detect-It-Easy git repository as of {date_today}. <br> 
        <p> The new file has been uploaded to the S3 bucket. <br> 
        <p> Thank you.</p>
        <br><p>name of team</p>
        </body>
        
        </html>
        """
        date_body = datetime.utcnow().strftime('%m-%d-%Y')
        html = html.format(date_today=date_body)
        message = MIMEMultipart("alternative", None, [MIMEText(msg), MIMEText(html, 'html')])
        message['Subject'] = SUBJECT
        message['From'] = email.utils.formataddr((self.email[name], self.email[sender]))
        message['To'] = self.email[recipients]

        server = smtplib.SMTP(self.email[server_addr], self.email[port])
        server.ehlo()
        server.starttls()
        server.login(self.email[user], self.email[password])
        server.sendmail(self.email[sender], self.email[recipients], message.as_string())
        server.close()

        self.logger.info("Sending e-mail: Success")

    except Exception as e:
        self.logger.exception(e)