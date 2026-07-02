
import os
import json
import yaml
import shutil
from datetime import datetime

class FileManager:
    def __init__(self, config_path="config.yaml"):
        # Load Configuration safely
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self._setup_directories()

    def _setup_directories(self):
        """Creates necessary folders if they don't exist."""
        for path in self.config['directories'].values():
            os.makedirs(path, exist_ok=True)

    def get_input_images(self):
        """Generator to yield images one by one (Memory Efficient)."""
        input_dir = self.config['directories']['input']
        valid_exts = ('.jpg', '.jpeg', '.png')
        
        files = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_exts)]
        if not files:
            print(f"Warning: No images found in {input_dir}")
        
        for filename in files:
            yield os.path.join(input_dir, filename), filename

    def save_image(self, image, filename):
        """Saves the processed result."""
        import cv2
        output_path = os.path.join(self.config['directories']['output'], f"cleaned_{filename}")
        cv2.imwrite(output_path, image)
        return output_path

    def log_operation(self, filename, object_detected, confidence, success):
        """Advanced Logging: Appends structured data to a JSON log file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": filename,
            "object_removed": object_detected,
            "detection_confidence": float(confidence),
            "status": "SUCCESS" if success else "FAILED"
        }
        
        log_path = os.path.join(self.config['directories']['logs'], "process_history.json")
        
        # Read existing logs, append, and rewrite (Atomic simulation)
        data = []
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        
        data.append(log_entry)
        
        with open(log_path, 'w') as f:
            json.dump(data, f, indent=4)