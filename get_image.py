import os
import time
import requests


def capturar_imagenes_luthierbot(capturas_por_camara: int = 3):
    """Se conecta a las 3 cámaras IP utilizando /capture y guarda las fotos de

    cada una.

    Las IPs de las cámaras están configuradas directamente dentro de esta
    función.
    """
    # 📌 CONFIGURACIÓN INTERNA DE LAS CÁMARAS (Petición respetada)
    IP_CAMARA_1 = "http://192.168.137.219/capture?led=on"
    IP_CAMARA_2 = "http://192.168.137.219/capture?led=on"
    IP_CAMARA_3 = "http://192.168.137.219/capture?led=off"

    camaras = {
        "camara1": IP_CAMARA_1,
        "camara2": IP_CAMARA_2,
        "camara3": IP_CAMARA_3,
    }

    # 📁 Crea la carpeta "img" si no existe para evitar errores de guardado
    os.makedirs("img", exist_ok=True)

    archivos_guardados = []

    # Recorremos cada cámara del diccionario
    for nombre_camara, url_ip in camaras.items():
        print(f"📸 Iniciando captura en {nombre_camara}...")

        # Hacemos el bucle para tomar las fotos de esta cámara
        for i in range(1, capturas_por_camara + 1):
            # Creamos el nombre de archivo único dentro de la carpeta img/
            nombre_archivo = f"img/{nombre_camara}_foto{i}.jpg"

            try:
                # Hacer la petición GET a la IP de la cámara para traer la imagen fija
                respuesta = requests.get(url_ip, timeout=5)

                # Si la cámara responde correctamente (Código 200)
                if respuesta.status_code == 200:
                    # Guardamos el archivo binario en la computadora
                    with open(nombre_archivo, "wb") as f:
                        f.write(respuesta.content)

                    print(f"   ✅ Guardada: {nombre_archivo}")
                    archivos_guardados.append(nombre_archivo)
                else:
                    print(
                        f"   ❌ Error en {nombre_camara} (Foto {i}): Código {respuesta.status_code}"
                    )

            except requests.exceptions.RequestException as e:
                print(
                    f"   ❌ No se pudo conectar a {nombre_camara} (Foto {i}). Error: {e}"
                )

            # Un pequeño respiro de medio segundo entre capturas
            time.sleep(0.5)

    return archivos_guardados


# # --- EJECUCIÓN DEL CÓDIGO ---
# # Ahora la función se encarga de todo internamente, solo le dices cuántas fotos quieres por cámara
# lista_de_imagenes_listas = capturar_imagenes_luthierbot(capturas_por_camara=3)

# print("\n--- PROCESO TERMINADO ---")
# print(f"Total de imágenes listas para el diagnóstico: {lista_de_imagenes_listas}") 