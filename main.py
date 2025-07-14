from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from email.message import EmailMessage
from decouple import config
from typing import List
import smtplib

app = FastAPI()

# CORS (permitir peticiones desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Configuración SMTP desde .env o variables de entorno
SMTP_SERVER = config("SMTP_SERVER", default="smtp.mailersend.net")
SMTP_PORT = config("SMTP_PORT", default=587, cast=int)
SMTP_USER = config("SMTP_USER")
SMTP_PASSWORD = config("SMTP_PASSWORD")
DEVELOPER_EMAIL = config("DEVELOPER_EMAIL", default="atp.dev000@gmail.com")

@app.post("/send-feedback")
async def send_feedback(
    details: str = Form(...),
    contact: str = Form(""),
    files: List[UploadFile] = File([])
):
    try:
        # Determinar remitente para responder
        sender_email = contact if "@" in contact else "no-reply@snapnosh.com"

        # Crear mensaje
        msg = EmailMessage()
        msg["Subject"] = "📩 Nuevo comentario recibido desde SnapNosh"
        msg["From"] = f"SnapNosh App <{SMTP_USER}>"
        msg["To"] = DEVELOPER_EMAIL
        msg["Reply-To"] = sender_email

        # Cuerpo del correo
        msg.set_content(f"""
📝 Comentario del usuario:
{details}

📧 Contacto proporcionado: {contact or "No especificado"}
📩 Email de respuesta: {sender_email}
        """)

        # Adjuntar archivos (máximo 5MB por archivo)
        # Adjuntar archivos
        for file in files:
            file_content = await file.read()
            msg.add_attachment(
                file_content,
                maintype="application",
                subtype="octet-stream",
                filename=file.filename
            )

        # Enviar el correo por SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return {"status": "success", "message": "Comentario enviado correctamente"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Error al enviar el correo: {str(e)}"
        )
