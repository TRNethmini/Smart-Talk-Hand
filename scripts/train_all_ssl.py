import sys
import os
import pickle
from pathlib import Path
import numpy as np

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, callbacks
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix

PROJECT_ROOT = Path("C:/Redmi")
PROCESSED_DIR = PROJECT_ROOT / "dataset" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

EPOCHS = 100
BATCH_SIZE = 32

def train_for_dataset(ssl_name):
    base_name = ssl_name.replace("-", "_")
    data_path = PROCESSED_DIR / ssl_name / f"{base_name}_sequences.pkl"
    
    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        return False
        
    # Read the pickle file
    with open(data_path, "rb") as f:
        data = pickle.load(f)
        
    X_train = data["X_train"]
    X_val   = data["X_val"]
    X_test  = data["X_test"]
    y_train = data["y_train"]
    y_val   = data["y_val"]
    y_test  = data["y_test"]
    le      = data["label_encoder"]
    num_classes = data["num_classes"]
    seq_len = int(data["seq_len"])
    stride  = int(data["stride"])
    
    n_train, n_steps, n_feats = X_train.shape
    
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train.reshape(-1, n_feats)).reshape(n_train, n_steps, n_feats)
    X_val_s   = scaler.transform(X_val.reshape(-1, n_feats)).reshape(X_val.shape)
    X_test_s  = scaler.transform(X_test.reshape(-1, n_feats)).reshape(X_test.shape)
    
    # Define model
    model = keras.Sequential([
        layers.Input(shape=(seq_len, n_feats)),
        layers.LSTM(128, return_sequences=True),
        layers.Dropout(0.3),
        layers.LSTM(64),
        layers.Dropout(0.3),
        layers.Dense(64, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation="softmax"),
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    
    # Class weights for unbalanced datasets
    unique_classes = np.unique(y_train)
    weights = compute_class_weight("balanced", classes=unique_classes, y=y_train)
    class_weight = dict(zip(unique_classes.astype(int), weights))
    
    cb_list = [
        callbacks.EarlyStopping(
            monitor="val_accuracy",
            mode="max",
            patience=15,
            restore_best_weights=True,
            verbose=0,
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_accuracy",
            mode="max",
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=0,
        ),
    ]
    
    print(f"Training LSTM model for '{ssl_name}'...")
    history = model.fit(
        X_train_s, y_train,
        validation_data=(X_val_s, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weight,
        callbacks=cb_list,
        verbose=0
    )
    
    test_loss, test_acc = model.evaluate(X_test_s, y_test, verbose=0)
    print(f" -> Test loss: {test_loss:.4f}, Test accuracy: {test_acc:.4f}")
    
    # Save model and metadata
    model_out_dir = MODELS_DIR / base_name
    model_out_dir.mkdir(parents=True, exist_ok=True)
    
    model_path  = model_out_dir / f"{base_name}_lstm.keras"
    scaler_path = model_out_dir / f"{base_name}_lstm_scaler.pkl"
    meta_path   = model_out_dir / f"{base_name}_sequences.pkl"
    
    model.save(model_path)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    with open(meta_path, "wb") as f:
        pickle.dump(data, f)
        
    print(f"Saved artifacts to {model_out_dir}")
    return True

def main():
    if not PROCESSED_DIR.exists():
        print(f"Processed directory '{PROCESSED_DIR}' not found. Run preprocess_all_ssl.py first.")
        return
        
    # Get all processed ssl subdirectories
    dataset_dirs = [d for d in PROCESSED_DIR.iterdir() if d.is_dir() and d.name.startswith("ssl-")]
    
    if len(dataset_dirs) == 0:
        print("No processed datasets found.")
        return
        
    print(f"Found {len(dataset_dirs)} processed datasets to train on.")
    
    for count, d in enumerate(dataset_dirs, 1):
        ssl_name = d.name
        base_name = ssl_name.replace("-", "_")
        
        # Check if model already trained
        expected_model = MODELS_DIR / base_name / f"{base_name}_lstm.keras"
        if expected_model.exists():
            print(f"\n[{count}/{len(dataset_dirs)}] Skipping '{ssl_name}' - model already exists: {expected_model}")
            continue
            
        print(f"\n[{count}/{len(dataset_dirs)}] Starting training process for '{ssl_name}'")
        try:
            train_for_dataset(ssl_name)
        except Exception as e:
            print(f"Error training {ssl_name}: {e}")

if __name__ == "__main__":
    main()
