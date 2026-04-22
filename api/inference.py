import os
import json
import numpy as np
import tensorflow as tf

class SLSLPredictor:
    def __init__(self, model_path, mapping_path):
        self.model_path = model_path
        self.mapping_path = mapping_path
        self.classes = {}
        self.model = None
        self.buffer = [] # Buffer to hold frames (sliding window)
        self.buffer_size = 30
        
        self.load_resources()
        
    def load_resources(self):
        # Load Mapping
        try:
            with open(self.mapping_path, 'r', encoding='utf-8') as f:
                self.classes = json.load(f)
            print(f"Loaded {len(self.classes)} classes.")
        except Exception as e:
            print(f"Error loading mapping: {e}")
            self.classes = {}

        # Load Model (H5)
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            print("Keras Model loaded successfully.")
        except Exception as e:
            print(f"Error loading Keras model: {e}")
            self.model = None
            
    def preprocess_sequence(self, sequence):
        """
        Input: List of 30 frames, each frame is (33, 3) list/array.
        Output: (1, 30, 198) array.
        Steps:
        1. Convert to numpy
        2. Normalize (relative to Nose - Point 0)
        3. Add Velocity
        4. Flatten
        """
        # 1. Convert to Numpy: (30, 33, 3)
        seq_np = np.array(sequence, dtype=np.float32)
        
        # 2. Normalize
        # seq_np structure: (Frames, Landmarks, Coords)
        # Point 0 is index 0
        nose = seq_np[:, 0, :] # (30, 3)
        # Broadcast subtraction
        # (30, 33, 3) - (30, 1, 3)
        seq_norm = seq_np - nose[:, np.newaxis, :]
        
        # 3. Velocity
        # velocity[t] = pos[t] - pos[t-1]
        # Pad first frame with 0
        velocity = np.zeros_like(seq_norm)
        velocity[1:] = seq_norm[1:] - seq_norm[:-1]
        
        # Concatenate: (30, 33, 6)
        seq_features = np.concatenate([seq_norm, velocity], axis=-1)
        
        # 4. Flatten: (30, 198)
        seq_flat = seq_features.reshape(30, -1)
        
        # Add batch dim: (1, 30, 198)
        return seq_flat[np.newaxis, ...]

    def predict(self, frame_landmarks):
        """
        Receives a single frame landmarks: list of 33 dicts or [[x,y,z], ...]
        Returns: Prediction dict or None if buffer not full.
        """
        # Ensure input is (33, 3)
        if len(frame_landmarks) != 33:
            return {"status": "error", "message": "Invalid landmark count"}
            
        # Add to buffer
        self.buffer.append(frame_landmarks)
        
        # Maintain buffer size
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)
            
        # Check if enough data
        if len(self.buffer) < self.buffer_size:
            return {"status": "buffering", "frames": len(self.buffer)}
            
        # Preprocess
        input_data = self.preprocess_sequence(self.buffer)
        
        if self.model is None:
             return {"status": "error", "message": "Model not loaded"}

        # Inference
        # Model returns [batch_size, num_classes]
        output_data = self.model.predict(input_data, verbose=0)
        
        # Decode
        pred_idx = np.argmax(output_data[0])
        confidence = float(output_data[0][pred_idx])
        
        label_info = self.classes.get(str(pred_idx), {"en": "Unknown"})
        
        return {
            "status": "prediction",
            "class_id": int(pred_idx),
            "label": label_info['en'],
            "confidence": confidence
        }
