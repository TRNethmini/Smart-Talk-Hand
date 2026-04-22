# Ridmi - Sinhala Sign Language Mobile Client 👋

This is the mobile frontend for the Ridmi SSL learning platform, built with **Expo** and **React Native**. It interfaces with a FastAPI backend to provide real-time gesture recognition.

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure API**
   Update `constants/config.ts` with your backend's IP address.

3. **Start the App**
   ```bash
   npx expo start
   ```

## 🛠 Architecture Overview

The app has been migrated from a legacy WebSocket-based system to a high-performance **HTTP Sequence Streaming** architecture:

- **Routing**: Uses `expo-router` for file-based navigation.
- **Camera**: Powered by `react-native-vision-camera`.
- **Capture Logic**: Uses `react-native-view-shot` to take 30 snapshots at 120ms intervals.
- **API Service**: `HttpInferenceService` handles dynamic model discovery and sequence uploads.

## 📱 Features

- **Category Discovery**: Automatically fetches all loaded ML models (Alphabet, Numbers, Colors, etc.) from the backend.
- **Sign Library**: Displays all support signs for a selected category before starting practice.
- **Gesture Learning**: An interactive camera view that provides instant feedback on gesture accuracy.
- **Front-Camera Mirroring**: Automatically mirrors capture data to align with user expectations and improve inference logic.

## 🏗 Key Components

- `app/(tabs)/index.tsx`: The main dashboard for model selection.
- `app/model-classes.tsx`: Dynamic screen showing available signs for a model.
- `app/gesture-learning.tsx`: The core inference and practice arena.
- `services/api.ts`: Centralized HTTP client for backend communication.
