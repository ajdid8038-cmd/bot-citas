import time
import random
import requests

NIE = "Z4809947P"
NOMBRE = "TASNIME AJDID"
PAIS = "138"  # Marruecos
CANAL_NTFY = "https://ntfy.sh/citas_ajdid_barcelona"

URL_BASE = "https://sede.administracionespublicas.gob.es/icpplus/"

SESSION = requests.Session()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://sede.administracionespublicas.gob.es/icpplus/citar?locale=es",
    "Origin": "https://sede.administracionespublicas.gob.es",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}
SESSION.headers.update(HEADERS)

def notificar(mensaje, prioridad="default"):
    try:
        requests.post(CANAL_NTFY, data=mensaje.encode("utf-8"), headers={"Priority": prioridad})
    except Exception:
        pass
    print(f"\n[ALERTA]: {mensaje}\n")

def comprobar():
    print(f"[{time.strftime('%H:%M:%S')}] Comprobando citas...")
    try:
        # 1. Visitar la portada para obtener cookies de sesión
        res_inicio = SESSION.get(f"{URL_BASE}citar?locale=es", timeout=20)
        
        if res_inicio.status_code == 403 or "Access Denied" in res_inicio.text:
            print("⚠️ Filtro WAF activo en esta IP. Reintentando...")
            return False

        # 2. Seleccionar provincia Barcelona (id 8) y trámite Toma de Huellas
        datos_sede = {
            "form": "/icpplus/citar?locale=es",
            "tramiteGrupo[0]": "4036",
            "btnAceptar": "Aceptar"
        }
        res_sede = SESSION.post(f"{URL_BASE}index.html", data=datos_sede, timeout=20)

        # 3. Enviar datos del solicitante
        datos_persona = {
            "txtIdCitado": NIE,
            "txtDesCitado": NOMBRE,
            "txtPaisNac": PAIS,
            "btnEnviar": "Aceptar"
        }
        res_persona = SESSION.post(f"{URL_BASE}datos.html", data=datos_persona, timeout=20)

        contenido = res_persona.text.lower()
        if "no hay citas disponibles" in contenido or "en este momento no hay citas" in contenido:
            print("❌ No hay citas en este intento.")
            return False
        elif "información" in contenido or "solicitar cita" in contenido:
            notificar("🚨 ¡CITA DISPONIBLE EN EXTRANJERÍA! Entra a la web ya.", "urgent")
            return True
        else:
            print("ℹ️ Respuesta recibida, analizando...")
            return False

    except Exception as e:
        print(f"Error de conexión: {e}")
        return False

print("=== BOT REFORZADO EN GITHUB ===")
notificar("🟢 Bot activo con bypass de cabeceras.")

inicio = time.time()
while time.time() - inicio < 900:
    if comprobar():
        break
    espera = random.randint(45, 80)
    print(f"Esperando {espera} segundos...")
    time.sleep(espera)
