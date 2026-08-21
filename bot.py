import time
import random
import requests
import cloudscraper
from fake_useragent import UserAgent

NIE = "Z4809947P"
NOMBRE = "TASNIME AJDID"
PAIS = "138"  # Marruecos
CANAL_NTFY = "https://ntfy.sh/citas_ajdid_barcelona"

URL_BASE = "https://sede.administracionespublicas.gob.es/icpplus/"

ua = UserAgent()
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

def notificar(mensaje, prioridad="default"):
    try:
        requests.post(CANAL_NTFY, data=mensaje.encode("utf-8"), headers={"Priority": prioridad})
    except Exception:
        pass
    print(f"\n[ALERTA]: {mensaje}\n")

def comprobar():
    print(f"[{time.strftime('%H:%M:%S')}] Comprobando citas con motor anti-bloqueo...")
    try:
        headers = {
            "User-Agent": ua.chrome,
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://sede.administracionespublicas.gob.es/icpplus/citar?locale=es"
        }
        
        res = scraper.get(f"{URL_BASE}citar?locale=es", headers=headers, timeout=20)
        
        if res.status_code == 403 or "Access Denied" in res.text:
            print("⚠️ Filtro de sede activo. Esperando siguiente salto...")
            return False

        # Datos del formulario
        datos_sede = {
            "form": "/icpplus/citar?locale=es",
            "tramiteGrupo[0]": "4036",
            "btnAceptar": "Aceptar"
        }
        res_sede = scraper.post(f"{URL_BASE}index.html", data=datos_sede, headers=headers, timeout=20)

        datos_persona = {
            "txtIdCitado": NIE,
            "txtDesCitado": NOMBRE,
            "txtPaisNac": PAIS,
            "btnEnviar": "Aceptar"
        }
        res_persona = scraper.post(f"{URL_BASE}datos.html", data=datos_persona, headers=headers, timeout=20)

        contenido = res_persona.text.lower()
        if "no hay citas disponibles" in contenido or "en este momento no hay citas" in contenido:
            print("❌ No hay citas disponibles actualmente.")
            return False
        elif "cita" in contenido and ("seleccionar" in contenido or "oficina" in contenido):
            notificar("🚨 ¡CITA DISPONIBLE EN EXTRANJERÍA! Entra a la web ya.", "urgent")
            return True
        else:
            print("ℹ️ Consulta procesada sin errores de bloqueo.")
            return False

    except Exception as e:
        print(f"Error de conexión: {e}")
        return False

print("=== BOT REFORZADO CON CLOUDSCRAPER ===")
notificar("🟢 Bot en la nube iniciado con motor avanzado.")

inicio = time.time()
while time.time() - inicio < 900:
    if comprobar():
        break
    espera = random.randint(20, 35)
    print(f"Esperando {espera} segundos...")
    time.sleep(espera)
