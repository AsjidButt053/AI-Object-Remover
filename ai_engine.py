
import cv2
import numpy as np
from ultralytics import YOLO
from simple_lama_inpainting import SimpleLama
from PIL import Image

class AIEngine:
    def __init__(self, target_label="manual"):
        print("Loading AI Models... (This may take a moment)")
        # We load YOLO even for manual mode to keep the code simple, 
        # though it's mostly used for auto-detection.
        self.detector = YOLO('yolov8n-seg.pt') 
        self.inpainter = SimpleLama()
        self.target_label = target_label

    def process_image(self, image_path):
        """
        AUTOMATED MODE: Detects object by name and removes it.
        """
        original_img = cv2.imread(image_path)
        if original_img is None:
            return None, 0.0

        # Detect Object
        results = self.detector(original_img, verbose=False)
        
        mask = np.zeros(original_img.shape[:2], dtype=np.uint8)
        max_conf = 0.0
        found = False

        for result in results:
            if result.masks is None: continue
            
            for box, mask_data in zip(result.boxes, result.masks.data):
                class_id = int(box.cls[0])
                class_name = self.detector.names[class_id]
                confidence = float(box.conf[0])

                if class_name == self.target_label:
                    found = True
                    max_conf = max(max_conf, confidence)
                    binary_mask = mask_data.cpu().numpy()
                    binary_mask = cv2.resize(binary_mask, (original_img.shape[1], original_img.shape[0]))
                    mask = cv2.bitwise_or(mask, (binary_mask * 255).astype(np.uint8))

        if not found:
            print(f"Object '{self.target_label}' not found.")
            return original_img, 0.0

        # Dilate Mask
        kernel = np.ones((10, 10), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # Inpaint
        return self._inpaint_process(original_img, mask), max_conf

    def remove_with_mask(self, image_path, mask):
        """
        INTERACTIVE MODE: Uses the manual user-drawn mask.
        """
        original_img = cv2.imread(image_path)
        
        # Ensure mask is strictly binary
        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        
        return self._inpaint_process(original_img, mask)

    def _inpaint_process(self, image, mask):
        """Internal helper function to run the LaMa Inpainting model"""
        img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        mask_pil = Image.fromarray(mask)

        print("⚡ Inpainting selected area...")
        result_pil = self.inpainter(img_pil, mask_pil)

        return cv2.cvtColor(np.array(result_pil), cv2.COLOR_RGB2BGR)