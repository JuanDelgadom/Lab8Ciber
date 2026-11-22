"""
Laboratorio 8 - Grupo 114
Envío del correo SEÑUELO de la simulación (ficticio) contra el buzón LOCAL.

- Lee la plantilla HTML (plantilla_correo.html).
- Genera un token OPACO por cada destinatario ficticio.
- Construye el enlace al portal simulado con ese token (?t=...).
- Envía a 127.0.0.1:1025 (el sink local). NUNCA a internet.

Los destinatarios son una lista FICTICIA de laboratorio. No usar correos
de personas reales (el enunciado lo prohíbe explícitamente).

Uso:
    1) En una terminal:  python3 mail/smtp_sink.py
    2) En otra:          python3 mail/enviar_correo.py
"""

import csv
import json
import smtplib
import secrets
import datetime
from email.message import EmailMessage
from pathlib import Path

# -------------------- Configuración --------------------
SMTP_HOST, SMTP_PORT = "127.0.0.1", 1025
REMITENTE = "it-soporte@colombiaaprende.com.co"   # dominio parecido pero FALSO (parte del señuelo; el real es .edu.co)
ASUNTO = "[Acción requerida] Verifica tu cuenta de Colombia Aprende en 24h"
PORTAL_BASE = "http://127.0.0.1:8080/"            # portal simulado (app.py)

PLANTILLA = Path(__file__).parent / "plantilla_correo.html"
MAPEO = Path(__file__).parent / "mapeo_tokens.csv"  # token <-> destinatario (lo custodia RR.HH.)

DESTINATARIOS_FICTICIOS = [
    "david.torres@colombiaaprende.edu.co",
    "carlos.mejia@colombiaaprende.edu.co",
    "lucia.gomez@colombiaaprende.edu.co",
]


def construir_enlace(token: str) -> str:
    return f"{PORTAL_BASE}?t={token}"


def enviar():
    html = PLANTILLA.read_text(encoding="utf-8")
    filas_mapeo = []

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
        for correo in DESTINATARIOS_FICTICIOS:
            token = secrets.token_hex(6)           # token opaco, único por destinatario
            enlace = construir_enlace(token)
            cuerpo = html.replace("{{ENLACE}}", enlace)

            msg = EmailMessage()
            msg["From"] = REMITENTE
            msg["To"] = correo
            msg["Subject"] = ASUNTO
            msg.set_content(
                "Tu cliente no soporta HTML. Abre el portal en: " + enlace
            )
            msg.add_alternative(cuerpo, subtype="html")

            smtp.send_message(msg)
            print(f"[envio] -> {correo}  (token {token})")

            filas_mapeo.append({
                "token": token,
                "destinatario_ficticio": correo,
                "enviado_ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            })

    
    with MAPEO.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["token", "destinatario_ficticio", "enviado_ts"])
        w.writeheader()
        w.writerows(filas_mapeo)

    print(f"\n[envio] {len(filas_mapeo)} correos enviados al buzón local.")
    print(f"[envio] Mapeo de tokens guardado en: {MAPEO.name}")
    print("[envio] Resumen:", json.dumps(filas_mapeo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    enviar()
