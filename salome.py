import edge_tts
import asyncio
import pygame # Para reproducir el audio generado

TEXT = "Que deseas hacer hoy?"
VOICE = "es-CO-SalomeNeural" # Voz con acento venezolano
OUTPUT_FILE = "saludo.mp3"

async def speak(text):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(OUTPUT_FILE)
    
    # Reproducir el archivo
    pygame.mixer.init()
    pygame.mixer.music.load(OUTPUT_FILE)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)
