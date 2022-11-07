import logging
import email
import smtplib
import configparser
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import time
import os
import boto3
from git import Repo

logging.basicConfig(filename='AutomatedDIEdb.log', level=logging.NOTSET, format='%(asctime)s:%(levelname)s:%(message)s')
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

        logging.info("Sending e-mail: Success")

    except Exception as e:
        self.logger.exception(e)

def upload_folder_to_s3(s3bucket, inputDir, s3Path):
        logging.info("Uploading results to s3 initiated...")
        logging.info("Local Source:",inputDir)
        os.system("ls -ltR " + inputDir)

        logging.info("Dest  S3path:",s3Path)

        try:
            for path, subdirs, files in os.walk(inputDir):
                for file in files:
                    dest_path = path.replace(inputDir,"")
                    __s3file = os.path.normpath(s3Path + '/' + dest_path + '/' + file)
                    __local_file = os.path.join(path, file)
                    logging.info("upload : ", __local_file, " to Target: ", __s3file, end="")
                    s3bucket.upload_file(__local_file, __s3file)
                    logging.info(" ...Success")
        except Exception as e:
            logging.info("Failed! Quitting Upload.")
            print(e)
            raise e

def check_for_update(repo_path):
    Repo(repo_path).remotes.origin.fetch()
    diff = str(Repo(repo_path).git.diff('origin/master')).splitlines()
    
    #Function to check if there are any differences between the local repo and the original
    if len(diff) != 0:
        Repo(repo_path).remote().pull("master")
        logging.info("Commits detected. Pulling changes")
        upload_folder_to_s3(s3bucket, "D:/temp70/db/", "db/")
        send_email()
    else:
        logging.info("No commits detected.")

        #Timout for checking update in seconds (604800 seconds = 1 week)
        time.sleep(604800)

s3 = boto3.resource('s3', region_name='ap-southeast-1')
s3bucket = s3.Bucket("internproject1") 

try:
    Repo.clone_from("https://github.com/fingerboiii/test.git", "/temp70")
    upload_folder_to_s3(s3bucket, "D:/temp71/db", "db")
    logging.info("repository cloned")
except:
    logging.info("Local repository already created")



while True:
    check_for_update("/temp70")
