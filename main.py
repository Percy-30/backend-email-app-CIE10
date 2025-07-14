from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from email.message import EmailMessage
from decouple import config
from typing import List
import smtplib
from email_validator import validate_email, EmailNotValidError
import re

app = FastAPI()

# CORS (permitir peticiones desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def is_valid_phone(phone: str) -> bool:
    """Valida si el string es un número de teléfono válido (soporta formatos internacionales)"""
    # Elimina espacios, guiones, paréntesis, etc.
    cleaned_phone = re.sub(r'[+\-\s()]', '', phone)
    # Verifica que solo contenga dígitos y tenga entre 7-15 dígitos
    return cleaned_phone.isdigit() and 7 <= len(cleaned_phone) <= 15

def normalize_phone(phone: str) -> str:
    return re.sub(r'[+\-\s()]', '', phone)

# Configuración SMTP desde .env o variables de entorno
SMTP_SERVER = config("SMTP_SERVER", default="smtp.gmail.com")
SMTP_PORT = config("SMTP_PORT", default=465, cast=int) ## 465 for SSL, 587 for TLS
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
        # Validar el contacto (si se proporcionó)
        if contact and not (is_valid_email(contact) or is_valid_phone(contact)):
            raise HTTPException(
                status_code=400,
                detail="El contacto debe ser un email válido o un número de teléfono"
            )

        # Determinar remitente para responder
        sender_email = contact if is_valid_email(contact) else "no-reply@snapnosh.com"

        # Crear mensaje (el resto sigue igual)
        msg = EmailMessage()
        msg["Subject"] = "📩 Nuevo comentario recibido desde SnapNosh"
        msg["From"] = f"SnapNosh App <{SMTP_USER}>"
        msg["To"] = DEVELOPER_EMAIL
        msg["Reply-To"] = sender_email

        # Cuerpo del correo (añade indicación del tipo de contacto)
        contact_type = "Email" if is_valid_email(contact) else "Teléfono" if is_valid_phone(contact) else "No especificado"
        
        msg.set_content(f"""
📝 Comentario del usuario:
{details}

📧 Contacto proporcionado ({contact_type}): {contact or "No especificado"}
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
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            #server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return {"status": "success", "message": "Comentario enviado correctamente"}

    except smtplib.SMTPException as e:
        raise HTTPException(status_code=500, detail=f"SMTP error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    #except Exception as e:
    #    raise HTTPException(
    #        status_code=500,
    #        detail=f"❌ Error al enviar el correo: {str(e)}"
    #    )
