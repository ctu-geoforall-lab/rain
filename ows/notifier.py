
import os
import sys
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE
from datetime import datetime

class Notifier:
    """E-mail notification.
    """
    def __init__(self, username, password, mailhost, mailport=None):
        self.username = username
        self.password = password
        self.mailhost = mailhost
        self.port = mailport if mailport is not None else smtplib.SMTP_PORT

        # attempt to login (rather fail now than later)
        smtp = smtplib.SMTP(self.mailhost, self.port)
        smtp.starttls()
        smtp.login(self.username, self.password)
        smtp.quit()

    def send(self, fromaddr, toaddrs, subject, body, logfile=None):
        smtp = smtplib.SMTP(self.mailhost, self.port)
        smtp.starttls()

        # create message
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = COMMASPACE.join(toaddrs)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if logfile:
            # add attachment
            with open(logfile) as fd:
                part = MIMEApplication(
                    fd.read(), logfile
                )

            part['Content-Disposition'] = 'attachment; filename="{}"'.format(
                os.path.splitext(logfile)[0] + '.txt'
            )
            msg.attach(part)

        smtp.login(self.username, self.password)
        smtp.sendmail(fromaddr, toaddrs, msg.as_string())
        print("E-mail sent to {}".format(','.join(toaddrs)))
        smtp.quit()

if __name__ == "__main__":
    username = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    mailhost = os.getenv("EMAIL_MAILHOST")
    mailport = os.getenv("EMAIL_MAILPORT")
    if username and password and mailhost:
        try:
            no = Notifier(username, password, mailhost, mailport)
            date = datetime.now()
            info = " SUCCEEDED" if sys.argv[1] == "0" else "FAILED"
            no.send(f"admin@lucas",
                    os.environ["EMAIL_TOADDRS"].split(","),
                    subject=f"[LUCAS] TESTS {info} {date.isoformat()}",
                    body=info,
                    logfile=sys.argv[2]
            )
        except smtplib.SMTPAuthenticationError as e:
            print(e)
    else:
        print("Notifier not set up")
