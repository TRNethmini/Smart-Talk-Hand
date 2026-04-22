# Ridmi - User Manual for Local Development & Testing

> **Project**: Ridmi — Sinhala Sign Language Learning Platform  
> **Type**: BSc Academic Project  
> **Last Updated**: April 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Prerequisites](#3-prerequisites)
4. [Step 1 — Clone / Obtain the Repository](#4-step-1--clone--obtain-the-repository)
5. [Step 2 — Backend (API Server) Setup](#5-step-2--backend-api-server-setup)
6. [Step 3 — MongoDB Setup](#6-step-3--mongodb-setup)
7. [Step 4 — Ollama Setup (AI Tutor)](#7-step-4--ollama-setup-ai-tutor)
8. [Step 5 — Start the API Server](#8-step-5--start-the-api-server)
9. [Step 6 — Android Client Setup](#9-step-6--android-client-setup)
10. [Step 7 — Configure the API Address](#10-step-7--configure-the-api-address)
11. [Step 8 — Build & Run on a Physical Android Device (USB)](#11-step-8--build--run-on-a-physical-android-device-usb)
12. [Step 9 — Using the Application](#12-step-9--using-the-application)
13. [Troubleshooting](#13-troubleshooting)
14. [Appendix A — Project Directory Structure](#appendix-a--project-directory-structure)
15. [Appendix B — API Endpoint Quick Reference](#appendix-b--api-endpoint-quick-reference)

---

## 1. Project Overview

Ridmi is a mobile-first educational platform that teaches Sinhala Sign Language (SSL) through real-time gesture recognition. The system consists of:

- **Android Client** — An Expo / React Native mobile app that captures hand gestures via the device camera.
- **FastAPI Backend** — A Python server that receives image frames, extracts hand landmarks using MediaPipe, and classifies signs using LSTM deep learning models.
- **AI Tutor (RAG)** — A retrieval-augmented generation pipeline powered by Ollama that provides corrective feedback when the user performs an incorrect sign.

The platform currently supports **16 sign categories**: Alphabet, Numbers, Colors, Greetings, Days, Months, Nouns, Verbs, Adjectives, Adverbs, Conjunctions, Interjections, People, Places, Prepositions, and Vehicles.

---

## 2. System Architecture

```
┌─────────────────────┐         HTTP (POST frames)        ┌──────────────────────────┐
│   Android Device    │ ──────────────────────────────────>│   FastAPI Backend        │
│   (Expo/React       │                                    │   (Python, port 5000)    │
│    Native App)      │<───────────────────────────────────│                          │
│                     │         JSON (prediction)          │  ┌──────────────────┐    │
└─────────────────────┘                                    │  │  MediaPipe       │    │
                                                           │  │  (Landmarks)     │    │
                                                           │  └────────┬─────────┘    │
                                                           │           │              │
                                                           │  ┌────────▼─────────┐    │
                                                           │  │  LSTM Models     │    │
                                                           │  │  (TensorFlow)    │    │
                                                           │  └──────────────────┘    │
                                                           │                          │
                                                           │  ┌──────────────────┐    │
                                                           │  │  Ollama (RAG)    │    │
                                                           │  │  AI Tutor        │    │
                                                           │  └──────────────────┘    │
                                                           │                          │
                                                           │  ┌──────────────────┐    │
                                                           │  │  MongoDB         │    │
                                                           │  │  (User/Auth)     │    │
                                                           │  └──────────────────┘    │
                                                           └──────────────────────────┘
```

**Inference Flow:**
1. The mobile app captures 30 frames (~1–2 seconds of video).
2. Frames are base64-encoded and POSTed to the backend.
3. The backend uses MediaPipe to extract 21 hand landmarks (63 features) per frame.
4. The LSTM model processes the 30-frame sequence and returns the predicted sign with confidence scores.

---

## 3. Prerequisites

Ensure the following software is installed on your development machine **before** proceeding.

### 3.1 Required Software

| Software | Minimum Version | Purpose | Download |
|---|---|---|---|
| **Python** | 3.10 or 3.11 | Backend API server | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18 LTS or later | Android client toolchain | [nodejs.org](https://nodejs.org/) |
| **Git** | Any recent | Source control | [git-scm.com](https://git-scm.com/) |
| **Android Studio** | Latest stable | Android SDK, platform tools, ADB | [developer.android.com](https://developer.android.com/studio) |
| **MongoDB Community** | 7.0+ | User authentication & community data | [mongodb.com](https://www.mongodb.com/try/download/community) |
| **Ollama** | Latest | Local LLM for AI Tutor (RAG) | [ollama.com](https://ollama.com/) |

> **Important (Python):** TensorFlow 2.16.1 requires Python **3.10 or 3.11**. It does **not** support Python 3.13+. Verify with `python --version`.

> **Important (Node.js):** Expo SDK 54 requires Node.js **18 or later**. Verify with `node --version`.

### 3.2 Hardware Requirements

| Component | Requirement |
|---|---|
| **Development PC** | Windows 10/11 (64-bit), 16 GB RAM recommended |
| **Android Phone** | Android 10 (API 29) or higher, with a working front camera |
| **USB Cable** | A data-capable USB cable (not charge-only) connecting the phone to the PC |

### 3.3 Android Studio — SDK & Tools Setup

After installing Android Studio:

1. Open **Android Studio** > **Settings** (or **File > Settings**).
2. Navigate to **Languages & Frameworks > Android SDK**.
3. Under the **SDK Platforms** tab, ensure at least **Android 14 (API 34)** is checked and installed.
4. Under the **SDK Tools** tab, ensure the following are installed:
   - **Android SDK Build-Tools** (latest)
   - **Android SDK Command-line Tools** (latest)
   - **Android SDK Platform-Tools** (includes `adb`)
5. Click **Apply** and let it download.
6. Note the **Android SDK Location** displayed at the top of this panel (e.g., `C:\Users\<you>\AppData\Local\Android\Sdk`).

### 3.4 Environment Variables (Windows)

Add the following to your system `PATH` environment variable:

```
C:\Users\<you>\AppData\Local\Android\Sdk\platform-tools
```

This makes the `adb` command available globally. Verify:

```powershell
adb --version
```

---

## 4. Step 1 — Clone / Obtain the Repository

If you received the project as a ZIP file, extract it. If cloning from a repository:

```powershell
git clone <repository-url>
cd "Smart TalkHand Application"
```

The project root (`Smart TalkHand Application/`) should contain:

```
Smart TalkHand Application/
├── android-client/       # Expo/React Native mobile app
├── api/                  # FastAPI backend + ML models
├── dataset/              # Raw & processed training data
├── notebooks/            # Jupyter notebooks (training)
├── models/               # (reference models)
├── scripts/              # Utility scripts
└── README.md
```

---

## 5. Step 2 — Backend (API Server) Setup

### 5.1 Create a Python Virtual Environment

Open a terminal and navigate to the API directory from the project root:

```powershell
cd api
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> **Note:** If you get an execution policy error on PowerShell, run:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```
> Then retry the activation command.

### 5.2 Install Python Dependencies

With the virtual environment activated:

```powershell
pip install -r requirements.txt
```

This installs FastAPI, TensorFlow, MediaPipe, scikit-learn, MongoDB driver, LangChain, and all other dependencies. The install may take several minutes due to TensorFlow's size (~500 MB).

### 5.3 Verify Installation

```powershell
python -c "import tensorflow as tf; print(tf.__version__)"
python -c "import mediapipe; print(mediapipe.__version__)"
python -c "import fastapi; print(fastapi.__version__)"
```

Expected output:
```
2.16.1
0.10.11
0.115.0
```

### 5.4 Verify ML Models Are Present

The pre-trained LSTM models must be present in `api/models/`. Each category has its own subdirectory containing three files:

```
api/models/
├── ssl_alphabet/
│   ├── ssl_alphabet_lstm.keras       # Trained LSTM model
│   ├── ssl_alphabet_lstm_scaler.pkl  # Feature scaler
│   └── ssl_alphabet_sequences.pkl    # Label encoder & metadata
├── ssl_numbers/
│   ├── ssl_numbers_lstm.keras
│   ├── ssl_numbers_lstm_scaler.pkl
│   └── ssl_numbers_sequences.pkl
├── ssl_colors/
│   └── ...
└── (14 more categories)
```

If any model directory is missing or incomplete, that category will not be available in the app. The server logs which models loaded successfully on startup.

---

## 6. Step 3 — MongoDB Setup

The backend uses MongoDB to store user accounts, community posts, and chat messages.

### 6.1 Install & Start MongoDB

**Option A — MongoDB as a Windows Service (recommended):**

If you chose the "Install as a Service" option during MongoDB installation, it starts automatically. Verify:

```powershell
mongosh --eval "db.runCommand({ ping: 1 })"
```

**Option B — Start manually:**

```powershell
mongod --dbpath "C:\data\db"
```

> Create the `C:\data\db` directory first if it doesn't exist:
> ```powershell
> mkdir C:\data\db
> ```

### 6.2 Verify Connectivity

The API connects to MongoDB at `mongodb://localhost:27017` and uses a database named `ridmi_db`. No manual database or collection creation is needed — the server creates them on first startup.

---

## 7. Step 4 — Ollama Setup (AI Tutor)

The AI Tutor feature uses a local LLM via Ollama to provide corrective feedback when the user performs an incorrect gesture. This is **optional** — the app works without it, but the AI Tutor feature will be unavailable.

### 7.1 Install Ollama

Download and install from [ollama.com](https://ollama.com/). After installation, verify:

```powershell
ollama --version
```

### 7.2 Pull the Required Models

The backend requires two Ollama models:

```powershell
ollama pull gemma3:4b
ollama pull nomic-embed-text:latest
```

- `gemma3:4b` — The language model used for generating corrective feedback.
- `nomic-embed-text:latest` — The embedding model used for semantic search over the SSL textbook PDF.

### 7.3 Start the Ollama Server

Ollama typically runs as a background service after installation. If it's not running:

```powershell
ollama serve
```

> The Ollama server runs on `http://localhost:11434` by default.

### 7.4 RAG Corpus

The backend expects a PDF file at:

```
api/rag/Hand Gesture Description.pdf
```

This PDF contains textbook descriptions of each sign's hand shape. If this file is missing, the server will print a warning and the AI Tutor will be disabled (all other features remain functional).

---

## 8. Step 5 — Start the API Server

With all prerequisites running (MongoDB, Ollama), start the FastAPI backend:

```powershell
cd api
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

**Flags explained:**
- `--reload` — Auto-restarts the server when code changes (development mode).
- `--host 0.0.0.0` — Listens on all network interfaces (required so the Android device can reach the server).
- `--port 5000` — The port the API runs on.

### 8.1 Verify the Server Started Successfully

You should see log output similar to:

```
INFO:     Loading multi-model: ssl_alphabet
INFO:     Successfully loaded ssl_alphabet (hands=1, seq=30)
INFO:     Loading multi-model: ssl_colors
INFO:     Successfully loaded ssl_colors (hands=2, seq=30)
...
INFO:     LandmarkExtractor initialized for multi-model webcam frames.
INFO:     Loading RAG Corpus from: Hand Gesture Description.pdf
INFO:     Uvicorn running on http://0.0.0.0:5000
```

Open a browser and visit:
- **Health check:** [http://localhost:5000/api/v1/health](http://localhost:5000/api/v1/health)
- **Loaded models:** [http://localhost:5000/api/v1/models](http://localhost:5000/api/v1/models)
- **Interactive API docs:** [http://localhost:5000/docs](http://localhost:5000/docs) (Swagger UI)

---

## 9. Step 6 — Android Client Setup

### 9.1 Install Node.js Dependencies

Open a **new terminal** (keep the API server running in its own terminal):

```powershell
cd android-client
npm install
```

This installs Expo, React Native, NativeWind, Vision Camera, and all other JavaScript dependencies.

### 9.2 Install Expo CLI (if not already)

```powershell
npm install -g expo-cli
```

---

## 10. Step 7 — Configure the API Address

The Android app needs to know your PC's local IP address to communicate with the backend.

### 10.1 Find Your PC's Local IP

```powershell
ipconfig
```

Look for the **IPv4 Address** under your active network adapter (Wi-Fi or Ethernet). For example:

```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 192.168.1.6
```

### 10.2 Update the Config File

Open the file:

```
android-client/constants/config.ts
```

Update `LOCAL_IP` to your machine's IP:

```typescript
export const LOCAL_IP = '192.168.1.6'; // <-- Replace with YOUR IP
```

> **Critical:** The Android phone and the development PC **must be on the same Wi-Fi network** for the app to reach the backend. USB connection alone is not sufficient for network communication — the API traffic goes over Wi-Fi.

---

## 11. Step 8 — Build & Run on a Physical Android Device (USB)

This section explains how to build a development APK and install it directly onto your Android phone via USB.

### 11.1 Enable USB Debugging on Your Android Phone

1. Open **Settings** on your phone.
2. Go to **About Phone** (may be under **System** on some devices).
3. Tap **Build Number** 7 times rapidly. You'll see a toast message: *"You are now a developer!"*
4. Go back to **Settings > System > Developer Options** (location varies by manufacturer).
5. Enable **USB Debugging**.
6. (Recommended) Enable **Install via USB** if the option exists.
7. (Recommended) Set **Default USB Configuration** to **File Transfer / MTP**.

### 11.2 Connect the Phone to Your PC

1. Connect the phone to the PC with a USB data cable.
2. On the phone, a dialog will appear: **"Allow USB debugging?"** — Tap **Allow** (optionally check "Always allow from this computer").
3. Verify the connection in a terminal:

```powershell
adb devices
```

Expected output:

```
List of devices attached
XXXXXXXXXXXXXXX    device
```

If the status shows `unauthorized`, re-check the dialog on your phone and tap **Allow**.

### 11.3 Generate the Native Android Project

Since this is an Expo project without a pre-existing `android/` directory, you need to generate the native project first:

```powershell
cd android-client
npx expo prebuild --platform android
```

This generates the `android/` folder with all the native Android project files (Gradle build scripts, manifest, etc.) based on the Expo configuration in `app.json`.

### 11.4 Build and Install the Development Build

Run the following command to compile a debug APK and install it directly on the connected device:

```powershell
npx expo run:android
```

**What this does:**
1. Compiles the native Android project using Gradle.
2. Builds a debug APK.
3. Installs the APK on the connected device via `adb`.
4. Launches the app on the device.

> **First build takes 5–15 minutes** depending on your machine. Subsequent builds are much faster due to Gradle caching.

> **Note:** If you have multiple devices/emulators connected, it will prompt you to select one. Choose your physical device.

### 11.5 Grant Camera Permission

On first launch, the app will request camera permission. **You must allow this** — the entire sign recognition flow depends on the front camera.

### 11.6 Start the Expo Dev Server (for Hot Reload)

After the initial build, you can start the Expo development server for live reloading:

```powershell
npx expo start --dev-client
```

The app on your phone will connect to this dev server for hot reload during development. If the app can't connect, ensure:
- The phone and PC are on the same network.
- No firewall is blocking the Expo dev server port (default: 8081).

---

## 12. Step 9 — Using the Application

### 12.1 Login / Register

1. On first launch, you'll see the login screen.
2. Register a new account with an email and password.
3. Log in with your credentials.

### 12.2 Selecting a Sign Category

1. The home screen (Dashboard) displays all available sign categories fetched from the backend (e.g., Alphabet, Numbers, Colors).
2. Tap a category to view all the signs (classes) it supports.

### 12.3 Viewing the Sign Library

1. After selecting a category, you'll see a grid of all supported signs.
2. Each sign may have a reference video demonstrating the correct gesture.
3. Tap a sign to start practicing it.

### 12.4 Gesture Practice (Inference)

1. The app opens the front camera.
2. Position your hand in the camera frame and perform the sign.
3. The app captures 30 frames (~1–2 seconds) and sends them to the backend.
4. The backend returns the predicted sign and confidence score.
5. If the prediction is **correct**, success feedback is shown.
6. If the prediction is **incorrect**, the AI Tutor (if Ollama is running) provides a corrective explanation describing what to adjust in your hand positioning.

### 12.5 Community & Chat

- The **Community** tab allows posting and interacting with other users.
- The **Chat** tab provides messaging functionality.

### 12.6 Web-Based Testing (Admin/Debug)

The backend also serves web-based testing pages accessible from your PC's browser:

| URL | Description |
|---|---|
| `http://localhost:5000/api/multi-models` | Select a model category |
| `http://localhost:5000/api/multi-classes?model=ssl_alphabet` | View signs for a category |
| `http://localhost:5000/api/multi-webcam?model=ssl_alphabet&target=අ` | Webcam-based inference tester |

These pages use your PC's webcam and are useful for quickly testing models without the mobile app.

---

## 13. Troubleshooting

### Backend Issues

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'tensorflow'` | Ensure the virtual environment is activated (`.\venv\Scripts\Activate.ps1`) before running the server. |
| `No models loaded` warning on startup | Verify that the `api/models/` directory contains subdirectories with `.keras`, `_scaler.pkl`, and `_sequences.pkl` files. |
| `Connection refused` when accessing `localhost:5000` | Ensure `uvicorn` is running. Check for port conflicts with `netstat -ano | findstr :5000`. |
| MongoDB connection error | Ensure MongoDB is running (`mongosh --eval "db.runCommand({ping:1})"`) on port 27017. |
| RAG/AI Tutor not working | Ensure Ollama is running (`ollama serve`) and the required models are pulled (`ollama list` should show `gemma3:4b` and `nomic-embed-text:latest`). Also verify the PDF exists at `api/rag/Hand Gesture Description.pdf`. |
| `WARNING: RAG PDF missing` | Place the `Hand Gesture Description.pdf` file in `api/rag/`. The AI Tutor is optional; all other features still work. |

### Android Build Issues

| Problem | Solution |
|---|---|
| `adb devices` shows empty list | Ensure USB debugging is enabled. Try a different USB cable (some cables are charge-only). Try a different USB port. |
| `adb devices` shows `unauthorized` | Unlock your phone and accept the USB debugging authorization dialog. |
| `expo prebuild` fails | Delete the `android/` folder and retry. Ensure Android SDK is properly installed in Android Studio. |
| `expo run:android` — Gradle build fails | Ensure `ANDROID_HOME` or `ANDROID_SDK_ROOT` environment variable is set. Check that the SDK path in `android/local.properties` is correct. |
| Build fails with Java errors | Ensure JDK 17 is installed (bundled with recent Android Studio). Verify with `java -version`. |
| App installs but crashes immediately | Check that the Expo dev server is running (`npx expo start --dev-client`). Check `adb logcat` for crash logs. |

### Network / Connectivity Issues

| Problem | Solution |
|---|---|
| App shows "Failed to fetch models" | 1. Verify the API server is running. 2. Check that `LOCAL_IP` in `config.ts` matches your PC's current IP (`ipconfig`). 3. Ensure the phone and PC are on the **same Wi-Fi network**. 4. Temporarily disable Windows Firewall or add an inbound rule for port 5000. |
| Phone can't reach PC despite same Wi-Fi | Some routers have "AP isolation" / "Client isolation" enabled which blocks device-to-device traffic. Check router settings or try a different network. |
| Inference is slow or times out | TensorFlow first-inference is slow due to model warm-up. Subsequent predictions should be faster. Ensure the PC meets RAM requirements. |

### Quick Connectivity Test

From your Android phone's browser, navigate to:

```
http://<YOUR_PC_IP>:5000/api/v1/health
```

If you see a JSON response like `{"status": "ok"}`, the connection is working. If not, resolve network/firewall issues before proceeding with the app.

---

## Appendix A — Project Directory Structure

```
Smart TalkHand Application/           # Project Root
├── android-client/                    # Mobile App (Expo / React Native)
│   ├── app/                           # Screens (file-based routing)
│   │   ├── (tabs)/                    # Tab navigation screens
│   │   │   ├── index.tsx              #   Dashboard (model selection)
│   │   │   ├── community.tsx          #   Community feed
│   │   │   ├── chat.tsx               #   Chat
│   │   │   └── settings.tsx           #   Settings
│   │   ├── gesture-learning.tsx       # Core inference screen
│   │   ├── model-classes.tsx          # Sign library for a model
│   │   ├── lesson.tsx                 # Lesson view
│   │   ├── login.tsx                  # Authentication
│   │   └── _layout.tsx                # Root layout
│   ├── constants/
│   │   └── config.ts                  # API_BASE_URL & LOCAL_IP config
│   ├── services/
│   │   └── api.ts                     # HTTP inference service
│   ├── app.json                       # Expo configuration
│   └── package.json                   # Node.js dependencies
│
├── api/                               # Backend (FastAPI + Python)
│   ├── main.py                        # App entry point & startup
│   ├── config.py                      # Paths & feature constants
│   ├── database.py                    # MongoDB connection & indexes
│   ├── landmark_extractor.py          # MediaPipe hand extraction
│   ├── inference.py                   # Single-model inference logic
│   ├── routers/                       # API route handlers
│   │   ├── health.py                  #   /api/v1/health
│   │   ├── classes.py                 #   /api/v1/models/{name}/classes
│   │   ├── predict.py                 #   Single model prediction
│   │   ├── multi_predict.py           #   Multi-model prediction
│   │   ├── auth.py                    #   User auth endpoints
│   │   ├── community.py              #   Community posts
│   │   ├── chat.py                    #   Chat messages
│   │   └── rag.py                     #   AI Tutor feedback
│   ├── services/
│   │   ├── multi_inference.py         # Multi-model loader & predictor
│   │   ├── rag_service.py             # Ollama RAG pipeline
│   │   ├── auth_service.py            # JWT auth logic
│   │   └── preprocessing.py           # Frame preprocessing
│   ├── models/                        # Pre-trained LSTM models
│   │   ├── ssl_alphabet/              #   (3 files per category)
│   │   ├── ssl_numbers/
│   │   ├── ssl_colors/
│   │   └── ... (16 categories)
│   ├── rag/
│   │   └── Hand Gesture Description.pdf
│   └── requirements.txt               # Python dependencies
│
├── dataset/                           # Training data (video files)
│   ├── ssl-alphabet/
│   ├── ssl-numbers/
│   ├── processed/                     # Preprocessed .pkl sequences
│   └── ...
│
├── notebooks/                         # Jupyter notebooks for training
├── scripts/                           # Utility scripts
└── README.md
```

---

## Appendix B — API Endpoint Quick Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Server health check |
| GET | `/api/v1/models` | List all loaded model categories |
| GET | `/api/v1/models/{name}/classes` | List signs for a model |
| POST | `/api/v1/models/{name}/webcam-sequence` | Submit 30 frames for inference |
| POST | `/api/v1/rag/feedback` | Get AI Tutor corrective feedback |
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Log in and receive a JWT token |
| GET | `/api/v1/community/posts` | Fetch community posts |
| POST | `/api/v1/community/posts` | Create a community post |

For full request/response schemas, visit the Swagger UI at `http://localhost:5000/docs` while the server is running.

---

## Summary — Quick-Start Checklist

Use this checklist to verify everything is ready:

- [ ] Python 3.10/3.11 installed
- [ ] Node.js 18+ installed
- [ ] Android Studio installed with SDK 34 and platform-tools
- [ ] `adb` is on your system PATH
- [ ] MongoDB is running on port 27017
- [ ] Ollama is running with `gemma3:4b` and `nomic-embed-text` models pulled
- [ ] Python venv created and `requirements.txt` installed
- [ ] ML model files present in `api/models/` (16 subdirectories)
- [ ] API server started with `uvicorn main:app --reload --host 0.0.0.0 --port 5000`
- [ ] `http://localhost:5000/api/v1/health` returns `{"status": "ok"}`
- [ ] `LOCAL_IP` in `config.ts` updated to your PC's Wi-Fi IP address
- [ ] USB debugging enabled on Android phone
- [ ] `adb devices` shows your device as `device` (not `unauthorized`)
- [ ] `npm install` completed in `android-client/`
- [ ] `npx expo prebuild --platform android` completed
- [ ] `npx expo run:android` built and installed the app on the phone
- [ ] Phone can reach `http://<YOUR_IP>:5000/api/v1/health` from its browser
- [ ] Camera permission granted in the app
