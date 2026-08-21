import time
import random
import requests

NIE = "Z4809947P"
NOMBRE = "TASNIME AJDID"
PAIS = "138"  # Marruecos
CANAL_NTFY = "https://ntfy.sh/citas_ajdid_barcelona"

URL_BASE = "https://sede.administracionespublicas.gob.es/icpplus/"
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

def notificar(mensaje, prioridad="default"):
    try:
        requests.post(CANAL_NTFY, data=mensaje.encode("utf-8"), headers={"Priority": prioridad})
    except Exception:
        pass
    print(f"\n[ALERTA]: {mensaje}\n")

def comprobar():
    print(f"[{time.strftime('%H:%M:%S')}] Comprobando citas...")
    try:
        res = SESSION.get(f"{URL_BASE}citar?locale=es", timeout=15)
        if "Access Denied" in res.text or res.status_code == 403:
            print("⚠️ IP bloqueada temporalmente en servidor.")
            return False

        datos_sede = {
            "form": "/icpplus/citar?locale=es",
            "tramiteGrupo[0]": "4036",
            "btnAceptar": "Aceptar"
        }
        SESSION.post(f"{URL_BASE}index.html", data=datos_sede, timeout=15)

        datos_persona = {
            "txtIdCitado": NIE,
            "txtDesCitado": NOMBRE,
            "txtPaisNac": PAIS,
            "btnEnviar": "Aceptar"
        }
        res_persona = SESSION.post(f"{URL_BASE}datos.html", data=datos_persona, timeout=15)

        if "no hay citas disponibles" in res_persona.text.lower():
            print("❌ No hay citas en este intento.")
            return False
        else:
            notificar("🚨 ¡CITA DETECTADA EN EXTRANJERÍA! Entra a la web.", "urgent")
            return True

    except Exception as e:
        print(f"Error de red: {e}")
        return False

print("=== BOT INICIADO EN GITHUB ===")
notificar("🟢 Bot en la nube iniciado y funcionando.")

inicio = time.time()
while time.time() - inicio < 900:
    if comprobar():
        break
    espera = random.randint(30, 60)
    print(f"Esperando {espera} segundos...")
    time.sleep(espera)
