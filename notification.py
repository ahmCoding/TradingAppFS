import smtplib, ssl
import appConfig
import datetime

#password = input("Type your password and press enter: ")
def sendEmailNotification(message):
    #if message list is not empty
    if message:
        today= datetime.date.today().isoformat()
        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(appConfig.emailServer, appConfig.emailPort, context=context) as server:
            server.login(appConfig.myEmailAdress,appConfig.myEmailPass)
            formatedMessage=f"Subject: new Trades on {today}\n\n"
            #seprate the list of trades with 2 newline charakter
            formatedMessage+="\n\n".join(message)
            server.sendmail(appConfig.myEmailAdress, appConfig.myEmailAdress, formatedMessage)

