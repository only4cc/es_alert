''' 
Biblioteca para alertas
'''

import smtplib

SMTP_SERVER = "smtpinterno.e-contact.cl"
FROM = "logs@e-contact.cl"
TO = ["{{ es_alerts_to_high }}"]

# Interfaz al modulo de alarmas, por el momento solo simula desplegando por pantalla
def alarma (tenant, varname, variable_desc, value , umbral ):
    print("tenant:", tenant, " variable: ", variable_desc, "[", varname,"] con el valor ", value ," es mayor que el umbral (", umbral,")")
    SUBJECT = "tenant:", tenant, " variable: ", variable_desc, "[", varname,"] con el valor ", value ," es mayor que el umbral (", umbral,")"
    BODY = "tenant:", tenant, " variable: ", variable_desc, "[", varname,"] con el valor ", value ," es mayor que el umbral (", umbral,")"
#    sendMail(FROM,TO,SUBJECT,BODY,SMTP_SERVER)

def sendMail(FROM,TO,SUBJECT,BODY,SERVER):
    """ Envia mail con la alerta """
    message = textwrap.dedent("""\
        From: %s
        To: %s
        Subject: %s\n
        %s
        """ % (FROM, ", ".join(TO), SUBJECT, BODY))
    # Send the mail
    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, TO, message)
    server.quit()