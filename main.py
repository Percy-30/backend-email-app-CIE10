# main.py
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.message import EmailMessage
from decouple import config
from typing import List, Optional

app = FastAPI()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Configuración de email
# Elimina los valores por defecto inseguros
SMTP_SERVER = config("SMTP_SERVER")  # Obligatorio
SMTP_PORT = config("SMTP_PORT", cast=int)  # Obligatorio
SMTP_USER = config("SMTP_USER")  # Obligatorio
SMTP_PASSWORD = config("SMTP_PASSWORD")  # Obligatorio (usar app password)
DEVELOPER_EMAIL = config("DEVELOPER_EMAIL")  # Obligatorio

#SMTP_SERVER = config("SMTP_SERVER", default="smtp.gmail.com")
#SMTP_PORT = config("SMTP_PORT", default=465)
#SMTP_USER = config("SMTP_USER")  # Tu correo de desarrollador
#SMTP_PASSWORD = config("SMTP_PASSWORD")  # Contraseña de aplicación
#DEVELOPER_EMAIL = config("DEVELOPER_EMAIL")  # Correo donde recibirás los mensajes

@app.post("/send-feedback")
async def send_feedback(
    details: str = Form(...),
    contact: str = Form(""),
    files: List[UploadFile] = File([])
):
    try:
        # Validación extra del email
        if not SMTP_USER.endswith("@gmail.com"):
            raise ValueError("El SMTP_USER debe ser un correo Gmail")

        
        # Crear mensaje
        msg = EmailMessage()
        msg["From"] = f"SnapNosh <{SMTP_USER}>"
        msg["To"] = DEVELOPER_EMAIL
        msg["Subject"] = "Nuevo Feedback"
        
        # Configuración SMTP con timeout
        with smtplib.SMTP_SSL(
            host=SMTP_SERVER, 
            port=SMTP_PORT,
            timeout=10
        ) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            
        return {"status": "success"}
    
        
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Error de autenticación con Gmail. Verifica tu contraseña de aplicación."
        )

        # Adjuntar archivos (máx. 5MB cada uno)
        #for file in files:
        #    if file.size > 5 * 1024 * 1024:
        #        continue  # Omitir archivos muy grandes
        #    file_data = await file.read()
        #    msg.add_attachment(
        #        file_data,
        #        maintype=file.content_type,
        #        subtype=file.content_type.split("/")[-1],
        #        filename=file.filename
        #    )
#
        ## Enviar email
        #with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        #    server.login(SMTP_USER, SMTP_PASSWORD)
        #    server.send_message(msg)
#
        #return {"status": "success", "message": "Comentario enviado"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error SMTP: {str(e)}. Verifica tu configuración."
        )