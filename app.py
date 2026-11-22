import json
import secrets
import datetime
from pathlib import Path

from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    Response,
)

# --------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------
app = Flask(__name__)

CAMPAIGN_ID = "COLAPRENDE-2026-S14"

PORTAL_LEGITIMO_URL = "https://www.colombiaaprende.edu.co/"

LOG_PATH = Path(__file__).parent / "logs" / "interacciones.log"
LOG_PATH.parent.mkdir(exist_ok=True)


# --------------------------------------------------------------------
# Registro de interacciones  (METADATOS ÚNICAMENTE)
# --------------------------------------------------------------------
def registrar_evento(evento: str, token: str) -> None:
    registro = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "campaign": CAMPAIGN_ID,
        "evento": evento,
        "token": token or "anonimo",
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def token_de_request() -> str:
    t = request.args.get("t", "").strip()
    if not t:
        t = "anon-" + secrets.token_hex(4)
    # Saneamos: solo caracteres esperados, longitud acotada.
    return "".join(c for c in t if c.isalnum() or c in "-_")[:32]


# --------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------
@app.route("/", methods=["GET"])
def login():
    token = token_de_request()
    registrar_evento("vista_pagina", token)
    return render_template("login.html", token=token)


@app.route("/registro", methods=["POST"])
def registro():
    token = request.form.get("t", "") or token_de_request()
    token = "".join(c for c in token if c.isalnum() or c in "-_")[:32]

    registrar_evento("envio_formulario", token)

    # Redirección inmediata a la página educativa (reveal).
    return redirect(url_for("educacion", t=token))


@app.route("/educacion", methods=["GET"])
def educacion():
    token = token_de_request()
    return render_template(
        "educativa.html",
        portal_legitimo=PORTAL_LEGITIMO_URL,
        token=token,
    )


@app.route("/salud", methods=["GET"])
def salud():
    return Response("ok", mimetype="text/plain")


if __name__ == "__main__":
    # Solo escucha en localhost por defecto (entorno controlado).
    # Para una demo en la red doméstica del equipo, cambien host a "0.0.0.0"
    # DEJÁNDOLO siempre dentro del laboratorio y nunca expuesto a internet.
    app.run(host="127.0.0.1", port=8080, debug=False)
