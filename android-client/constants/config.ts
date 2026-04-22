
import { Platform } from 'react-native';

// UPDATE THIS with your machine's local IP address if running on a physical device
// Example: '192.168.1.15'
// You can find it by running `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
export const LOCAL_IP = '192.168.1.192'; // Default for Android Emulator

export const API_BASE_URL = Platform.OS === 'android'
    ? `http://${LOCAL_IP}:5000`
    : 'http://localhost:5000';

export const WS_URL = Platform.OS === 'android'
    ? `ws://${LOCAL_IP}:8000/ws/predict`
    : 'ws://localhost:8000/ws/predict';
