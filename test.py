from get_image import capturar_imagenes_luthierbot
from n8n_request import ask_n8n_with_multiple_images

        # 1. Capturar las fotos usando la función interna de 3 fotos por cámara
print("📸 Solicitando captura de imágenes de los cuatros...")
lista_fotos = capturar_imagenes_luthierbot(capturas_por_camara=3)
if lista_fotos:
    print(f"📤 Enviando {len(lista_fotos)} imágenes recopiladas a n8n...")
    # 2. Enviar las imágenes en Base64 al servidor de n8n bajo la etiqueta "caja"
    respuesta_n8n = ask_n8n_with_multiple_images(lista_fotos, "caja")
    print(f"✅ Respuesta de n8n recibida con éxito: {respuesta_n8n}")
else:
        print("⚠️ No se pudieron recopilar fotos de las cámaras.")
