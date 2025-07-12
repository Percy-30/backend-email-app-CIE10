from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import smtplib
from email.message import EmailMessage

app = FastAPI()

# Permitir CORS desde Android u otros orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringirlo a ["https://tu-app.com"] si deseas
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/send-feedback")
async def send_feedback(
    details: str = Form(...),
    contact: Optional[str] = Form(""),
    files: Optional[List[UploadFile]] = File(None)
):
    try:
        # 📧 Configura tus credenciales de envío
        sender_email = "TUCORREO@gmail.com"
        sender_password = "CONTRASEÑA_GENERADA_APP"  # Usa contraseña de app de Gmail
        receiver_email = "TUCORREO@gmail.com"

        # 📨 Crear mensaje
        msg = EmailMessage()
        msg["Subject"] = "📝 Nuevo comentario desde SnapNosh"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.set_content(f"🗨 Comentario:\n{details}\n\n📞 Contacto: {contact}")

        # 📎 Adjuntar archivos si existen
        if files:
            for upload in files:
                file_data = await upload.read()
                msg.add_attachment(
                    file_data,
                    maintype="application",
                    subtype="octet-stream",
                    filename=upload.filename
                )

        # ✉️ Enviar el email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        return JSONResponse(content={"message": "✅ Comentario enviado con éxito"}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)