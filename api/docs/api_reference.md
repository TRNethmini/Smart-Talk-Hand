# SSL Multi-Model LSTM API

This API provides inference for multiple Sinhala Sign Language (SSL) sign categories (Alphabet, Numbers, Colors, etc.) using LSTM models.

The core flow for clients (Web or Android) is:

1. **Discovery**: Get the list of available categories (models).
2. **Setup**: Fetch the classes (signs) supported by a specific category.
3. **Capture**: Capture a short sequence of 30 frames (approx. 1-2 seconds).
4. **Inference**: Send the frames to the API and receive the predicted sign with confidence scores.

## Base URL

- **Local Development**: `http://localhost:5000`
- **Mobile Access**: `http://<local-ip>:5000` (e.g., `http://192.168.1.5:5000`)

---

## Data Model & Preprocessing

The system utilizes MediaPipe Hands for landmark extraction and an LSTM network for sequence classification:

- **Sequence Length**: 30 frames.
- **Features**: 63 features per frame (21 landmarks × 3 coordinates x, y, z).
- **Normalization**: Landmarks are wrist-relative (landmark 0 is shifted to (0,0,0)).
- **Auto-Orientation**: The server automatically attempts to rotate frames (90 CCW, 90 CW, 180) to detect hands correctly, prioritizing 90 CCW for mobile landscape captures.
- **Mirroring**: Optional horizontal flipping for front-facing camera usage.

---

## API Endpoints (v1)

### 1. Global Endpoints

#### GET `/api/v1/health`
Checks if the server and `LandmarkExtractor` are operational.

#### GET `/api/v1/models`
Returns a list of all loaded model categories.
```json
{ "models": ["ssl_alphabet", "ssl_colors", "ssl_numbers", ...] }
```

---

### 2. Model-Specific Endpoints

These endpoints use `{model_name}` (e.g., `ssl_alphabet`) in the URL path.

#### GET `/api/v1/models/{model_name}/classes`
Returns the list of signs supported by the specific model.
```json
{ "classes": ["අ", "ආ", "ඇ", ...] }
```

#### POST `/api/v1/models/{model_name}/webcam-sequence`
The primary inference endpoint for streaming frames.

**Request Body**:
```json
{
  "frames": ["data:image/jpeg;base64,...", "..."],
  "mirror": true
}
```
- `frames`: Array of 30 base64-encoded image strings.
- `mirror` (optional): Set to `true` to horizontally flip frames (recommended for mobile front cameras).

**Response**:
```json
{
  "predicted_label": "අ",
  "topk": [
    { "label": "අ", "prob": 0.98 },
    { "label": "ආ", "prob": 0.01 },
    ...
  ],
  "seq_len": 30,
  "num_sequences": 1
}
```

---

## User Interfaces

### Web (Admin/Test)
- **Model Discovery**: `/api/multi-models` - Select a category.
- **Class Grid**: `/api/multi-classes?model=...` - Select a target sign.
- **Webcam Tester**: `/api/multi-webcam?model=...&target=...` - Perform inference.

### Android (Expo/React Native)
- **Capture Strategy**: Uses `react-native-view-shot` + `VisionCamera` to capture 30 snapshots.
- **API Communication**: Uses `HttpInferenceService` inside `services/api.ts` to POST sequences with `mirror: true`.
- **Target Tracking**: Supports dynamic routing for specific categories and target sign verification.
