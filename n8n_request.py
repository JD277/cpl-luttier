import requests
import base64
URL_TEXT = "https://newserver-n8n.5bxr29.easypanel.host/webhook-test/bc98f2bd-4775-4da7-adad-76e8d006d4b8"


def ask_n8n_with_imagefile(filename: str, tipo_de_foto: str) -> dict:
    """
    Send a request to the n8n API with an image file
    Args:
        filename (str): Name of the file to send
        tipo_de_foto (str): Type of photo to send to the API
    Returns:
        dict: Response from the API
    """
    headers = {"Content-Type": "application/json"}
    
    with open(filename, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    data = {
        "image_base64": img_b64,
        "tipoDeFoto": tipo_de_foto
    }
    
    response = requests.post(URL_TEXT, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

