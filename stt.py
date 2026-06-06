from stt_manager import STTEngine

vosk = STTEngine(keyword="Lutier", silence_duration=1.5)

while not vosk.wait_for_keyword():
    pass
print("¡Keyword detectada! Comenzando transcripción...")