"""
Laboratorio 8 - Grupo 114
Servidor SMTP LOCAL de captura ("sink").

Recibe los correos de la simulación y los guarda como archivos .eml en
mail/buzon/, SIN reenviarlos a ningún lado. Esto garantiza que NINGÚN
correo sale hacia internet: todo queda en la máquina del equipo.

Hace las veces de "cola de correo" (mail queue) para la evidencia del lab.

Uso:
    python3 mail/smtp_sink.py
Deja la terminal abierta; escucha en 127.0.0.1:1025.
"""

import asyncio
import datetime
from pathlib import Path

from aiosmtpd.controller import Controller

BUZON = Path(__file__).parent / "buzon"
BUZON.mkdir(exist_ok=True)
LOG = Path(__file__).parent / "cola_envios.log"


class ManejadorBuzon:
    """Guarda cada mensaje recibido como .eml y registra metadatos de la cola."""

    async def handle_DATA(self, server, session, envelope):
        ts = datetime.datetime.now(datetime.timezone.utc)
        nombre = ts.strftime("%Y%m%dT%H%M%S_") + \
            envelope.rcpt_tos[0].replace("@", "_at_").replace("/", "_")
        destino = BUZON / f"{nombre}.eml"
        destino.write_bytes(envelope.content)

        linea = (
            f'{ts.isoformat()} | de={envelope.mail_from} '
            f'| para={",".join(envelope.rcpt_tos)} '
            f'| bytes={len(envelope.content)} | archivo={destino.name}\n'
        )
        with LOG.open("a", encoding="utf-8") as f:
            f.write(linea)
        print("[sink] Capturado ->", destino.name)

        # 250 = aceptado. NO se reenvía a ningún servidor externo.
        return "250 Mensaje capturado en el buzon local de laboratorio"


def main():
    controller = Controller(ManejadorBuzon(), hostname="127.0.0.1", port=1025)
    controller.start()
    print("[sink] Servidor SMTP de captura escuchando en 127.0.0.1:1025")
    print("[sink] Los correos se guardan en:", BUZON.resolve())
    print("[sink] Ctrl+C para detener.")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        controller.stop()
        print("\n[sink] Detenido.")


if __name__ == "__main__":
    main()
