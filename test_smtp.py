import smtplib

# Configura tus credenciales reales aquí
SMTP_SERVER = "smtp.gmail.com" #smtp.mailersend.net"
SMTP_PORT = 465 #587  465# TLS
SMTP_USER = "snapnoshapp@gmail.com" #MS_odQ11s@test-51ndgwv1dz5lzqx8.mlsender.net"  # Copia esto desde MailerSend
SMTP_PASSWORD = "utwt zync asag peyy" #mssp.FQ6m2yQ.x2p03473ydygzdrn.o04es7w"  # Copia la contraseña que te dio MailerSend

try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        #server.starttls()  # Muy importante para MailerSend
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("✅ ¡Conexión SMTP exitosa con MailerSend!")
except Exception as e:
    print(f"❌ Error en la conexión: {e}")
