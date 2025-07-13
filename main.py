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
SMTP_SERVER = config("SMTP_SERVER", default="smtp.gmail.com")
SMTP_PORT = config("SMTP_PORT", default=465)
SMTP_USER = config("SMTP_USER")  # Tu correo de desarrollador
SMTP_PASSWORD = config("SMTP_PASSWORD")  # Contraseña de aplicación
DEVELOPER_EMAIL = config("DEVELOPER_EMAIL")  # Correo donde recibirás los mensajes

@app.post("/send-feedback")
async def send_feedback(
    details: str = Form(...),
    contact: str = Form(""),
    files: List[UploadFile] = File([])
):
    try:
        # Validar y preparar el correo del remitente
        sender_email = contact if "@" in contact else "no-reply@snapnosh.com"
        recipient_email = DEVELOPER_EMAIL
        
        # Crear mensaje
        msg = EmailMessage()
        msg["Subject"] = "Nuevo comentario de SnapNosh"
        msg["From"] = f"SnapNosh App <{SMTP_USER}>"
        msg["To"] = recipient_email
        msg["Reply-To"] = sender_email
        
        # Cuerpo del mensaje
        body = f"""
        📝 Comentario:
        {details}
        
        📧 Contacto proporcionado: {contact if contact else "No especificado"}
        📩 Responder a: {sender_email}
        """
        msg.set_content(body)

        # Adjuntar archivos (máx. 5MB cada uno)
        for file in files:
            if file.size > 5 * 1024 * 1024:
                continue  # Omitir archivos muy grandes
            file_data = await file.read()
            msg.add_attachment(
                file_data,
                maintype=file.content_type,
                subtype=file.content_type.split("/")[-1],
                filename=file.filename
            )

        # Enviar email
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return {"status": "success", "message": "Comentario enviado"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el comentario: {str(e)}"
        )