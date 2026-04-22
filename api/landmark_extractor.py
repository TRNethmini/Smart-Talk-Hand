
import mediapipe as mp
import cv2
import numpy as np
import base64

class LandmarkExtractor:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        # Using Hands model
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def extract(self, image_data, mirror=False):
        """
        Input: Base64 encoded image string.
        Output: List of 33 landmarks [[x, y, z], ...] or None if no hand detected.
        """
        try:
            # Decode Base64 to image bytes
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None

            if mirror:
                img = cv2.flip(img, 1)

            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe (Try multiple orientations)
            orientations = [
                (img_rgb, "original"),
                (cv2.rotate(img_rgb, cv2.ROTATE_90_COUNTERCLOCKWISE), "90_ccw"),
                (cv2.rotate(img_rgb, cv2.ROTATE_90_CLOCKWISE), "90_cw"),
                (cv2.rotate(img_rgb, cv2.ROTATE_180), "180")
            ]

            for image, rotation in orientations:
                results = self.hands.process(image)
                if results.multi_hand_landmarks:
                    print(f"Hand detected in {rotation} orientation", flush=True)
                    # Found a hand!
                    break
            
            if results.multi_hand_landmarks:
                # Get the first hand
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Extract landmarks
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append([lm.x, lm.y, lm.z])
                
                return landmarks
            
            return None
            
        except Exception as e:
            print(f"Error extracting landmarks: {e}")
            return None
