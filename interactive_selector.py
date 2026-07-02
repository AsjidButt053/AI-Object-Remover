
import cv2
import numpy as np

class InteractiveSelector:
    def __init__(self):
        self.image = None
        self.clone = None
        self.mask = None
        self.drawing = False
        self.center = (-1, -1)
        self.radius = 0

    def select_object(self, image_path):
        """
        Opens a window and lets the user draw a circle.
        Returns: The generated binary mask.
        """
        self.image = cv2.imread(image_path)
        if self.image is None:
            return None
        
        # Create a copy to display visuals without ruining the original data
        self.clone = self.image.copy()
        # Create a black mask (same size as image)
        self.mask = np.zeros(self.image.shape[:2], dtype=np.uint8)

        cv2.namedWindow("CleanSweep AI: Draw Circle & Press ENTER")
        # Connect the mouse to our function
        cv2.setMouseCallback("CleanSweep AI: Draw Circle & Press ENTER", self._draw_circle)

        print("\n--- INSTRUCTIONS ---")
        print("1. Click and Drag to draw a circle over the object.")
        print("2. Press 'c' to Clear/Retry.")
        print("3. Press 'ENTER' to Confirm and Remove.")
        print("4. Press 'q' to Quit this image.")

        final_mask = None

        while True:
            # Show the image with the red circle being drawn
            cv2.imshow("CleanSweep AI: Draw Circle & Press ENTER", self.clone)
            key = cv2.waitKey(1) & 0xFF

            # Reset logic (Press 'c')
            if key == ord("c"):
                self.clone = self.image.copy()
                self.mask = np.zeros(self.image.shape[:2], dtype=np.uint8)
                print("Selection cleared.")

            # Confirm logic (Press ENTER)
            elif key == 13: 
                # Draw the final filled white circle on the mask
                if self.radius > 0:
                    cv2.circle(self.mask, self.center, self.radius, (255), -1)
                final_mask = self.mask
                break

            # Quit logic (Press 'q')
            elif key == ord("q"):
                final_mask = None
                break

        cv2.destroyAllWindows()
        return final_mask

    def _draw_circle(self, event, x, y, flags, param):
        """Handle Mouse Events"""
        # 1. User presses Mouse Button: Start Point
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.center = (x, y)
            self.radius = 0

        # 2. User moves Mouse: Update Radius and Visuals
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                # Calculate distance between center and current mouse (Pythagoras)
                self.radius = int(np.hypot(x - self.center[0], y - self.center[1]))
                
                # Refresh display
                self.clone = self.image.copy()
                # Draw red circle (Visual only)
                cv2.circle(self.clone, self.center, self.radius, (0, 0, 255), 2)
                # Draw small center point
                cv2.circle(self.clone, self.center, 3, (0, 255, 0), -1)

        # 3. User releases Mouse Button: Stop drawing
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            # Finalize the visual circle
            cv2.circle(self.clone, self.center, self.radius, (0, 0, 255), 2)