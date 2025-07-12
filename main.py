from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import smtplib
from email.message import EmailMessage

app = FastAPI()

# CORS si lo usas desde Android
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/send-feedback")
async def send_feedback(
    details: str = Form(...),
    contact: str = Form(""),
    media: UploadFile = File(None)
):
    try:
        # Configura tu correo
        sender_email = "TUCORREO@gmail.com"
        sender_password = "CONTRASEÑA_GENERADA_APP"  # Usar contraseña de aplicación
        receiver_email = "TUCORREO@gmail.com"

        # Crear el email
        msg = EmailMessage()
        msg["Subject"] = "Nuevo comentario desde SnapNosh"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.set_content(f"Comentario:\n{details}\n\nContacto: {contact}")

        # Si hay archivo adjunto
        if media:
            file_data = await media.read()
            msg.add_attachment(file_data, filename=media.filename)

        # Enviar
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        return JSONResponse(content={"message": "Enviado correctamente"}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
