# Simulación de concientización "evil-twin" — Lab 8 (Grupo 114)

Portal de **simulación** de phishing con fines pedagógicos. Ejercicio
**ficticio**, en **entorno controlado** (localhost / red doméstica).
Diseñado para que sea **imposible capturar contraseñas**: solo registra
metadatos de interacción y redirige a material educativo.

> ⚠️ Uso exclusivamente educativo y en laboratorio. No apuntar a personas,
> dominios ni sistemas reales. Ver `privacidad.md`.

## Componentes

| Archivo | Rol |
|---|---|
| `app.py` | Portal señuelo (Flask): login falso → registro de metadatos → página educativa → portal legítimo |
| `templates/login.html` | Página señuelo que imita "Colombia Aprende" (entidad real; solo laboratorio contenido) |
| `templates/educativa.html` | Página educativa (reveal) + checklist |
| `mail/smtp_sink.py` | Servidor SMTP **local** que captura los correos (no reenvía a internet) |
| `mail/enviar_correo.py` | Envía el correo señuelo a destinatarios **ficticios** |
| `mail/plantilla_correo.html` | Plantilla del correo señuelo |
| `privacidad.md` | Qué se guarda, retención y borrado seguro |

## Instalación

```bash
pip install -r requirements.txt
```

## Cómo correrlo (flujo completo)

**Terminal 1 — portal:**
```bash
python3 app.py
# http://127.0.0.1:8080/
```

**Terminal 2 — buzón de correo local:**
```bash
python3 mail/smtp_sink.py
# escucha en 127.0.0.1:1025
```

**Terminal 3 — enviar la campaña señuelo (ficticia):**
```bash
python3 mail/enviar_correo.py
```

Luego:
1. Abre un `.eml` de `mail/buzon/` (es el correo recibido).
2. Haz clic en el enlace "Verificar mi cuenta" → abre el portal señuelo con tu token.
3. "Inicia sesión" con cualquier texto → el servidor **descarta** las credenciales
   y te redirige a la página educativa.
4. Revisa `logs/interacciones.log`: solo verás metadatos, nunca contraseñas.

## Flujo

```
Correo señuelo ─▶ Portal falso (login) ─▶ /registro (solo metadatos)
                                               │
                                               ▼
                                   Página educativa (reveal)
                                               │
                                               ▼
                                   Portal LEGÍTIMO de la organización
```

## Garantías de ética (verificables en el código)

- `app.py` **nunca** lee `request.form['password']`.
- Redirección inmediata a `/educacion` tras cualquier envío.
- El envío de correo va a un **buzón local**; nada sale a internet.
- Logs = solo `ts`, `campaign`, `evento`, `token` opaco.
