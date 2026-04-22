
import tensorflow as tf
import os

model_path = r"c:/Users/sayur/Downloads/Redmi/model-playground/slsl_model.h5"

if os.path.exists(model_path):
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"Input Shape: {model.input_shape}")
        
        # Also check expected output to confirm classes
        print(f"Output Shape: {model.output_shape}")
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print("Model file not found")
