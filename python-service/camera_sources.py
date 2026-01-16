import cv2
from abc import ABC, abstractmethod


class CameraSource(ABC):
    """Abstract base class for camera sources"""
    
    @abstractmethod
    def get_frame(self):
        """Return the next frame from the camera"""
        pass
    
    @abstractmethod
    def release(self):
        """Release camera resources"""
        pass
    
    @abstractmethod
    def is_opened(self):
        """Check if camera is successfully opened"""
        pass


class iPhoneCamera(CameraSource):
    """iPhone camera via DroidCam or IP Webcam"""
    
    def __init__(self, url):
        self.url = url
        import time
        
        # Try to open the video stream
        print(f"Connecting to: {url}")
        self.cap = cv2.VideoCapture(url)
        
        # Wait for connection to establish
        time.sleep(2)
        
        # Set properties for better streaming
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Try to read a test frame
        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.cap.release()
            raise ConnectionError(f"Cannot connect to iPhone camera at {url}. Make sure DroidCam is running and showing 'Start' button pressed.")
        
        print(f"✓ Connected to iPhone camera at {url}")
    
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
    
    def release(self):
        self.cap.release()
    
    def is_opened(self):
        return self.cap.isOpened()


class RTSPCamera(CameraSource):
    """RTSP IP Camera"""
    
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        
        # Set buffer size to 1 for real-time streaming
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not self.cap.isOpened():
            raise ConnectionError(f"Cannot connect to RTSP camera at {rtsp_url}")
        
        print(f"✓ Connected to RTSP camera at {rtsp_url}")
    
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
    
    def release(self):
        self.cap.release()
    
    def is_opened(self):
        return self.cap.isOpened()


class WebcamCamera(CameraSource):
    """Local USB webcam"""
    
    def __init__(self, device_id=1):
        self.device_id = device_id
        self.cap = cv2.VideoCapture(device_id)
        
        if not self.cap.isOpened():
            raise ConnectionError(f"Cannot open webcam with device ID {device_id}")
        
        print(f"✓ Connected to USB webcam (device {device_id})")
    
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
    
    def release(self):
        self.cap.release()
    
    def is_opened(self):
        return self.cap.isOpened()


def get_camera_source(source_type, **kwargs):
    """Factory function to get the appropriate camera source"""
    
    if source_type.lower() == "iphone":
        from config import IPHONE_URL
        return iPhoneCamera(kwargs.get("url", IPHONE_URL))
    
    elif source_type.lower() == "rtsp":
        from config import RTSP_URL
        return RTSPCamera(kwargs.get("url", RTSP_URL))
    
    elif source_type.lower() == "webcam":
        return WebcamCamera(kwargs.get("device_id", 0))
    
    else:
        raise ValueError(f"Unknown camera source type: {source_type}")
