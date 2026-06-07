from gemini import GeminiManager

gemini = GeminiManager(
    model_name="gemma-4-31b-it", 
    api_key="AIzaSyCUJ43mng-KzhWzmBT8S_DfzF2U9FyTGOs",
    system_instruction=(
        "Eres Lutier, un asistente de voz conciso y amigable. "
        "Responde SIEMPRE en español usando máximo una oración corta. "
        "PROHIBIDO mostrar procesos de pensamiento, listas, viñetas o notas internas. "
        "NUNCA expliques cómo construiste la respuesta. "
        "Solo emite la frase final de forma natural y directa."
    )
)

response = gemini.send_message("Hola, ¿cómo estás?")
print(f"Respuesta de Gemini: {response}")