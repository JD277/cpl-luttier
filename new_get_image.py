import cv2
import time
import requests
import base64
class Camera:
    def __init__(self, cameras_id=[0,1,3]):
        self.caps = [cv2.VideoCapture(id) for id in cameras_id]
        self.URL_TEXT = "https://newserver-n8n.5bxr29.easypanel.host/webhook/bc4d7057-9794-4b16-b90c-34e1d58d996a"
        self.images = []
        self.working = [False] * len(cameras_id)

# ===========================================================
#                           CAMERA METHODS
# ===========================================================
    def check_cameras(self) -> None:
        """
        Check if the cameras are opened successfully.
        Returns:
            bool: True if all cameras are opened, False otherwise."""
        for cap in self.caps:
            if not cap.isOpened():
                print("Error: Could not open camera.")
                self.working[self.caps.index(cap)] = False
            else:
                self.working[self.caps.index(cap)] = True
    
    def capture_frames(self, num_frames=3, delay=0.1) -> None:
        """
        Capture frames from the cameras.
        
        Args:
            num_frames (int): Number of frames to capture from each camera.
            delay (float): Delay in seconds between capturing frames.

        Returns:
            None    
        """
        for i in range(num_frames):
            for cap in self.caps:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture frame")
                    break
                self.images.append(f"images/frame_{i}.jpg")
                cv2.imwrite(f'images/frame_{i}.jpg', frame)
                print(f"Captured frame {i} from camera {self.caps.index(cap)}")
                time.sleep(delay)


    def release(self) -> None:
        """Release the camera resources."""
        for cap in self.caps:
            cap.release()
        cv2.destroyAllWindows()

# ===========================================================
#                           N8N REQUEST METHODS
# ===========================================================
    def ask_n8n_with_imagefile(self, filename: str, tipo_de_foto: str) -> dict:
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
        
        response = requests.post(self.URL_TEXT, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def ask_n8n_with_multiple_imagefiles(self, filenames: list, tipo_de_foto: str) -> dict:
        """
        Send a request to the n8n API with multiple image files
        Args:
            filenames (list): List of file names to send
            tipo_de_foto (str): Type of photo to send to the API
        Returns:
            dict: Response from the API
        """
        headers = {"Content-Type": "application/json"}
        
        images_b64 = []
        for filename in filenames:
            with open(filename, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
                images_b64.append(img_b64)
            
        data = {
            "images_base64": images_b64,
            "tipoDeFoto": tipo_de_foto
        }
        
        response = requests.post(self.URL_TEXT, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    camera = Camera([0])
    #camera.capture_frames(num_frames=5, delay=3)
    #camera.release()
    #camera.check_cameras()
    #print(camera.working)
    #camera.ask_n8n_with_imagefile("images/frame_4.jpg", "Caja")
    camera.ask_n8n_with_multiple_imagefiles(["images/frame_2.jpg", "images/frame_3.jpg", "images/frame_4.jpg"], "Caja")
