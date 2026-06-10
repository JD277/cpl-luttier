import pyttsx3


def speak(texto: str):
    """Recibe un texto en formato string y lo reproduce como audio."""
    # Inicializar el motor de texto a voz
    engine = pyttsx3.init()

    # Configurar propiedades (Opcional: velocidad del habla)
    # 200 es el valor por defecto, puedes bajarlo a 150 si habla muy rápido
    engine.setProperty("rate", 180)

    # Decir el texto configurado
    engine.say(texto)

    # Bloquear el programa hasta que termine de hablar (crucial para que se escuche)
    engine.runAndWait()


# --- EJEMPLO DE USO ---
# Texto que quieres que reproduzca
mensaje = "Hola. El sistema de diagnóstico está listo para iniciar."

# Llamada a la función
speak(mensaje)